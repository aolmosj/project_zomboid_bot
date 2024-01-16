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
# Setup environment
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
RCONPASS = os.getenv('RCON_PASS')
RCONSERVER = os.getenv('RCON_SERVER')
RCONPORT = os.getenv('RCON_PORT')
GUILD = os.getenv('DISCORD_GUILD')
ADMIN_ROLES = os.getenv('ADMIN_ROLES')
MODERATOR_ROLES = os.getenv('MODERATOR_ROLES')
WHITELIST_ROLES = os.getenv('WHITELIST_ROLES')
ADMIN_ROLES = ADMIN_ROLES.split(',')
WHITELIST_ROLES = WHITELIST_ROLES.split(',')
IGNORE_CHANNELS = os.getenv('IGNORE_CHANNELS')
SERVER_ADDRESS = os.getenv('SERVER_ADDRESS')
NOTIFICATION_CHANNEL = os.getenv('NOTIFICATION_CHANNEL')

try:
    IGNORE_CHANNELS = IGNORE_CHANNELS.split(',')
except: 
    IGNORE_CHANNELS = ""
intents = discord.Intents.default()
intents.members = True
access_levels = ['admin', 'none', 'moderator']
block_notified = list()

# Below cogs represents our folder our cogs are in. Following is the file name. So 'meme.py' in cogs, would be cogs.meme
# Think of it like a dot path import
initial_extensions = ['cogs.users',
                      'cogs.moderators',
                      'cogs.admins']

class PZBot(commands.Bot):
    def __init__(self):
        # initialize our bot instance, make sure to pass your intents!
        # for this example, we'll just have everything enabled
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.all()
        )
    
    # the method to override in order to run whatever you need before your bot starts
    async def setup_hook(self):
        initial_extensions = ['cogs.users',
                            'cogs.moderators',
                            'cogs.admins']

        # Here we load our extensions(cogs) listed above in [initial_extensions].
        for extension in initial_extensions:
            await self.load_extension(extension)
        
print("Starting bot")
PZBot().run(TOKEN)