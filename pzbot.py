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
            # There are no prefix commands: every command is a slash command.
            # Mention-only is the one prefix discord.py accepts without the
            # message content intent, so this keeps a spurious warning off
            # every start-up log line.
            command_prefix=commands.when_mentioned,
            activity=discord.Activity(type=discord.ActivityType.custom,
            name="custom",
            state="Project Zomboid"),
            # Slash commands only, no gateway event handlers: none of the three
            # privileged intents is used, and asking for them would make a fresh
            # install refuse to connect until they were enabled in the portal.
            intents=discord.Intents.default()
        )

    async def setup_hook(self):
        await init_db()

        extensions = [
            'cogs.config',
            'cogs.users',
            'cogs.moderators',
            'cogs.admins',
            'cogs.server',
        ]
        for extension in extensions:
            await self.load_extension(extension)

        await self.tree.sync()

PZBot().run(TOKEN, root_logger=True)
