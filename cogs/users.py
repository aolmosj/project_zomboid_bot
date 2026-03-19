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
from lib.common import *

load_dotenv()
ADMIN_ROLES = os.getenv('ADMIN_ROLES')
MODERATOR_ROLES = os.getenv('MODERATOR_ROLES')
WHITELIST_ROLES = os.getenv('WHITELIST_ROLES')
ADMIN_ROLES = ADMIN_ROLES.split(',')
WHITELIST_ROLES = WHITELIST_ROLES.split(',')
IGNORE_CHANNELS = os.getenv('IGNORE_CHANNELS')
SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
NOTIFICATION_CHANNEL = os.getenv('NOTIFICATION_CHANNEL')

access_levels = ['admin', 'none', 'moderator']
block_notified = list()

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
    async def whatareyou(self, ctx):
        """What is the bot"""
        await IsChannelAllowed(ctx)
        results = f"I'm a bot for managing Project Zomboid servers, I'm written in python 3.\nRead more here: https://github.com/aolmosj/project_zomboid_bot"
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