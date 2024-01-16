#!/usr/bin/env python3
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
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

import logging
import sys

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)


# Setup environment
load_dotenv()
cogs = ["admins", "moderator", "users"]
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

try:
    IGNORE_CHANNELS = IGNORE_CHANNELS.split(',')
except: 
    IGNORE_CHANNELS = ""
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
#bot.load_extension('./cogs/users.py')
#for filename in os.listdir('./cogs'):
#    if filename.endswith('.py'):
#        await bot.load_extension(f'cogs.{filename[:-3]}')
access_levels = ['admin', 'none', 'moderator']
block_notified = list()
client = discord.Client(intents=intents)

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            print("HOLA")
            await bot.load_extension(f"cogs.{filename[:-3]}")

#bot.add_cog(AdminCommands(bot))
#bot.add_cog(ModeratorCommands(bot))

@bot.event
async def on_ready():
    bot.loop.create_task(status_task())

#print("Starting bot")
#bot.run(TOKEN)

async def main():
    async with bot:
        print("Starting bot IMPROV")
        await load_extensions()
        await bot.start(TOKEN)

asyncio.run(main())
