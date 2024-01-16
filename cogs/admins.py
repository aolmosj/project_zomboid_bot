import string
import os
import socket
import asyncio
from concurrent.futures import ThreadPoolExecutor
import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
from subprocess import Popen
import glob
import subprocess
import psutil
import schedule
import random
from subprocess import check_output, STDOUT
import time
from datetime import datetime
from SourceRcon import SourceRcon

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RCONPASS = os.getenv('RCON_PASS')
RCONSERVER = os.getenv('RCON_SERVER')
RCONPORT = os.getenv('RCON_PORT')
GUILD = os.getenv('DISCORD_GUILD')
ADMIN_ROLES = os.getenv('ADMIN_ROLES')
MODERATOR_ROLES = os.getenv('MODERATOR_ROLES')
WHITELIST_ROLES = os.getenv('WHITELIST_ROLES')
LOG_PATH = os.getenv('LOG_PATH', "/home/steam/Zomboid/Logs")
SERVER_PATH = os.getenv('SERVER_PATH', "C:\Program Files (x86)\Steam\steamapps\common\Project Zomboid Dedicated Server")
RCON_PATH = os.getenv('RCON_PATH','./')
ADMIN_ROLES = ADMIN_ROLES.split(',')
WHITELIST_ROLES = WHITELIST_ROLES.split(',')
IGNORE_CHANNELS = os.getenv('IGNORE_CHANNELS')
SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
NOTIFICATION_CHANNEL = os.getenv('NOTIFICATION_CHANNEL')
RESTART_CMD = os.getenv('RESTART_CMD', 'sudo systemctl restart Project-Zomboid')

access_levels = ['admin', 'none', 'moderator']
block_notified = list()

async def GetDeathCount(ctx, player):
    deathcount = 0
    logs = list()
    for root, dirs, files in os.walk(LOG_PATH):
        for f in files:
            if "_user.txt" in f:
                lpath = os.path.join(root,f)
                logs.append(lpath)
    for log in logs:
        with open(log, 'r') as file:
            for line in file:
                if player.lower() in line.lower():
                    if "died" in line:
                        deathcount += 1

    t = await lookuptime(ctx, player)
    return f"{player} has died {deathcount} times. Playtime: {t}"

async def pretty_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%s%dd, %dh, %dm, %ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh, %dm, %ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%dm, %ds' % (sign_string, minutes, seconds)
    else:
        return '%s%ds' % (sign_string, seconds)

async def getallplaytime(ctx):
    logs = list()
    user_time = {}
    for root, dirs, files in os.walk(LOG_PATH):
        for f in files:
            if "_user.txt" in f:
                lpath = os.path.join(root,f)
                logs.append(lpath)
    connect_time = {}
    fc_last_date = {}
    dc_last_date = {}
    for log in logs:
        with open(log, 'r') as file:
            for line in file:
                if "fully connected" in line:
                    c_sl = line.split()
                    c_username = c_sl[3].strip('"')
                    c_etime = " ".join(c_sl[:2]).strip("[]")
                    c_dt = datetime.strptime(c_etime, '%d-%m-%y %H:%M:%S.%f')
                    connect_time[c_username] = c_dt
                    if fc_last_date.get(c_username, datetime.min) < c_dt:
                        fc_last_date[c_username] = c_dt

                if "removed connection" in line:
                    r_sl = line.split()
                    r_username = r_sl[3].strip('"')
                    r_etime = " ".join(r_sl[:2]).strip("[]")
                    r_dt = datetime.strptime(r_etime, '%d-%m-%y %H:%M:%S.%f')
                    if r_username in connect_time:
                        time_segment = r_dt - connect_time[r_username]
                        time_segment = time_segment
                        if r_username not in user_time.keys():
                            user_time[r_username] = time_segment
                        else:
                            user_time[r_username] = time_segment + user_time[r_username]
                        del connect_time[r_username]
                    if dc_last_date.get(r_username, datetime.min) < r_dt:
                        dc_last_date[r_username] = r_dt

    for user in dc_last_date:
        if user in fc_last_date:
            if dc_last_date[user] < fc_last_date[user]:
                user_time[user] = user_time[user] + (datetime.now() - fc_last_date[user])
                print(f"User {user} probably still connected")
                u = user + "(active)"
                user_time[u] = user_time[user]
                del user_time[user]
    user_time = dict(reversed(sorted(user_time.items(), key=lambda item: item[1])))
    for user in user_time:
        time_pretty = await pretty_time_delta(user_time[user].total_seconds())
        user_time[user] = time_pretty
    return user_time


async def lookuptime(ctx, username):
    pl = await getallplaytime(ctx)
    for user in pl:
        if username == user.replace("(active)",""):
            return pl[user]

async def getalldeaths(ctx):
    deathcount = 0
    logs = list()
    deathdict = {}
    for root, dirs, files in os.walk(LOG_PATH):
        for f in files:
            if "_user.txt" in f:
                lpath = os.path.join(root,f)
                logs.append(lpath)
    for log in logs:
        with open(log, 'r') as file:
            for line in file:
                if "died at (" in line:
                    player = line.split()[3]
                    if player in deathdict:
                        deathdict[player] += 1
                    else:
                        deathdict[player] = 1
    rstring = ""
    deathdict = dict(reversed(sorted(deathdict.items(), key=lambda item: item[1])))
    for x in deathdict:
        p = x
        c = deathdict[x]
        t = await lookuptime(ctx, p)
        rstring += f"{p} has died {c} times. Playtime: {t}\n"
    return rstring


async def getmods():
    modlist = list()
    with open(os.path.join(os.path.split(LOG_PATH)[0],"Server","servertest.ini"), 'r') as file:
        for line in file:
            if "Mods=" in line:
                mods_split = line.split("=")
                if len(mods_split) > 1:
                    mods_list_split = mods_split[1].split(';')
                    for mod in mods_list_split:
                        modlist.append(mod)
    return "\n".join(modlist)


async def lookupsteamid(name):
    for root, dirs, files in os.walk(LOG_PATH):
        for f in files:
            if "_user.txt" in f:
                lpath = os.path.join(root,f) 
                with open(lpath, 'r') as file:
                    for line in file:
                        if "fully connected" in line:
                            if name in line:
                                return line.split()[2]
    
async def IsAdmin(ctx):
    is_present = [i for i in ctx.author.roles if i.name in ADMIN_ROLES]
    return is_present

async def IsMod(ctx):
    is_present = [i for i in ctx.author.roles if i.name in MODERATOR_ROLES]
    return is_present

async def IsServerRunning():
    for proc in psutil.process_iter():
        lname = proc.name().lower()
        if "projectzomboid" in lname:
           return True
    return False

async def restart_server(ctx):
    await ctx.send("Shutting server down, please wait...")
    await rcon_command(ctx,[f"save"])
    co = check_output(RESTART_CMD, shell=True)
    await ctx.send(f"Server restarted, it may take a minute to be fully ready")
    server_down = False
    while not server_down:
        d = await rcon_command(ctx, [f"players"])
        if "refused" in d:
            server_down = True
        await asyncio.sleep(5)
    
    if os.name == 'nt':
        terminate_zom = '''wmic PROCESS where "name like '%java.exe%' AND CommandLine like '%zomboid.steam%'" Call Terminate'''
        terminate_shell = '''wmic PROCESS where "name like '%cmd.exe%' AND CommandLine like '%StartServer64.bat%'" Call Terminate'''
        check_output(terminate_zom, shell=True)
        check_output(terminate_shell, shell=True)
        server_start = [os.path.join(SERVER_PATH,"StartServer64.bat")]
        p = Popen(server_start, creationflags=subprocess.CREATE_NEW_CONSOLE)
        r = p.stdout.read()
        r = r.decode("utf-8")
    else:
        check_output(RESTART_CMD, shell=True)

    await ctx.send("Server restarted, it may take a minute to be fully ready")

async def rcon_command(ctx, command):
    try:
        sr = SourceRcon(RCONSERVER, int(RCONPORT), RCONPASS)
        r = sr.rcon(" ".join(command))
        return r.decode('utf-8')
    except Exception as e:
        print(e)

async def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


async def IsChannelAllowed(ctx):
    channel_name = str(ctx.message.channel)
    is_present = [i for i in IGNORE_CHANNELS if i.lower() == channel_name.lower()]
    if channel_name in IGNORE_CHANNELS:
        if channel_name not in block_notified:
            await ctx.send("Not allowed to run commands in this channel")
            block_notified.append(channel_name)
        raise Exception("Not allowed to operate in channel")

class AdminCommands(commands.Cog):
    """Admin Server Commands"""
    def __init__(self, bot):
        self.bot = bot    

    @commands.command()

    async def pzsetaccess(self, ctx):
        """Set the access level of a specific user."""
        await IsChannelAllowed(ctx)
        if await IsAdmin(ctx):
            print(ctx.message.content)
            access_split = ctx.message.content.split()
            user = ""
            level = ""
            try:
                user = access_split[1]
                access_level = access_split[2]
            except IndexError as ie:
                response = f"Invalid command. Try !pzsetaccess USER ACCESSLEVEL"
                await ctx.send(response)
                return
            if access_level not in access_levels:
                response = f"Invalid access level {level}. Muse be one of {access_levels}"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx, [f"setaccesslevel", f"{user}", f"{access_level}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(AdminCommands(bot=bot))        