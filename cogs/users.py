import discord
from discord.ext import commands
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

class UserCommands(commands.Cog):
    """Commands open to users"""
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()

    async def pzplayers(self, ctx):
        """Show current active players on the server"""
        await IsChannelAllowed(ctx)
        c_run = ""
        c_run = await rcon_command(ctx, ["players"])
        print(c_run)
        if not c_run:
            return
        c_run = "\n".join(c_run.split('\n')[1:-1])
        results = f"Current players in game:\n{c_run}"
        await ctx.send(results)


    @commands.command(pass_context=True)
    async def pzgetoption(self, ctx):
        """Get the value of a server option"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        option_find = ""
        try:
            option_find = cmd_split[1]
        except IndexError as ie:
            response = f"Invalid command. Try !pzgetoption OPTIONNAME"
            await ctx.send(response)
            return
        copt = await rcon_command(ctx,'showoptions')
        copt_split = copt.split('\n')
        match = list(filter(lambda x: option_find.lower() in x.lower(), copt_split))
        match = '\n'.join(list(map(lambda x: x.replace('* ',''),match)))
        results = f"Server options:\n{match}"
        await ctx.send(results)


    @commands.command(pass_context=True)
    async def pzdeathcount(self, ctx):
        """Get the total death count of a player"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        option_find = ""
        try:
            username = cmd_split[1]
        except IndexError as ie:
            response = f"Invalid command. Try !pzdeathcount USERNAME"
            await ctx.send(response)
            return
        dc = await GetDeathCount(ctx, username)
        results = dc
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzplaytime(self, ctx):
        """Get the total playtime of all players"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        dc = await getallplaytime(ctx)
        pt_list = list()
        for user in dc:
            upt = dc[user]
            pt_list.append(f"{user} has played for {upt}")
        clist = chunks(pt_list, 100)
        async for c in clist:
            await ctx.send('\n'.join(c))

    @commands.command(pass_context=True)
    async def pzdeaths(self, ctx):
        """Get the total death count of all players"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        dc = await getalldeaths(ctx)
        results = dc.split('\n')
        clist = chunks(results, 100) 
        async for c in clist: 
            await ctx.send('\n'.join(c))


    @commands.command(pass_context=True)
    async def whatareyou(self, ctx):
        """What is the bot"""
        await IsChannelAllowed(ctx)
        results = f"I'm a bot for managing Project Zomboid servers, I'm written in python 3.\nRead more here: https://rfalias.github.io/project_zomboid_bot/"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzlistmods(self, ctx):
        """List currently installed mods"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        gm = await getmods()
        results = f"Currently installed mods:\n{gm}"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzrequestaccess(self, ctx):
        """Request access to the PZ server. A password will be DMd to you. These are hashed and can only be sent once"""
        is_present = [i for i in ctx.author.roles if i.name in WHITELIST_ROLES]
        if is_present:
            access_split = ctx.message.content.split()
            user = ""
            try:
                user = access_split[1]
            except IndexError as ie:
                response = f"Invalid command. Try !pzrequestaccess USER"
                await ctx.send(response)
                return 
            password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(8))
            
            c_run = await rcon_command(ctx,[f"adduser {user} {password}"])
            response = f"{c_run}"
            if "exists" in response:
                await ctx.message.author.send(f"Unable to create user, try another name")
                return
            if "created" in response:
                await ctx.message.author.send(f"Your request was accepted.\nUsername: {user}\nPassword: {password}\nAddress: {SERVER_ADDRESS}")
                return
        else:
            await ctx.message.author.send(f"You have not been given access to the server yet\nPlease wait for an admin to authorize you")
            return
            #await ctx.message.author.send(f"Your request user {user} has been created\nPassword: password\nServer Address: {SERVER_ADDRESS}")
        
async def setup(bot):
    # finally, adding the cog to the bot
    await bot.add_cog(UserCommands(bot=bot))              