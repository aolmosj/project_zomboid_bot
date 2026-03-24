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
import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from lib.guild_config import init_db

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


class PZBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            activity=discord.Activity(type=discord.ActivityType.custom,
            name="custom",
            state="Project Zomboid"),
            intents=discord.Intents.all()
        )

    async def setup_hook(self):
        await init_db()

        extensions = [
            'cogs.config',
            'cogs.users',
            'cogs.moderators',
            'cogs.admins',
        ]
        for extension in extensions:
            await self.load_extension(extension)

        await self.tree.sync()

print("Starting bot")
PZBot().run(TOKEN)
