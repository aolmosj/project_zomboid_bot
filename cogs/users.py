import string
import random
import discord
from discord.ext import commands
from lib.common import rcon_command, IsChannelAllowed, require_config


class UserCommands(commands.Cog):
    """Commands open to users"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pzplayers(self, ctx):
        """Show current active players on the server"""
        if not await IsChannelAllowed(ctx):
            return
        c_run = await rcon_command(ctx, ["players"])
        if not c_run:
            return
        c_run = "\n".join(c_run.split('\n')[1:-1])
        results = f"Current players in game:\n{c_run}"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzgetoption(self, ctx):
        """Get the value of a server option"""
        if not await IsChannelAllowed(ctx):
            return
        cmd_split = ctx.message.content.split()
        try:
            option_find = cmd_split[1]
        except IndexError:
            await ctx.send("Invalid command. Try !pzgetoption OPTIONNAME")
            return
        copt = await rcon_command(ctx, 'showoptions')
        if not copt:
            return
        copt_split = copt.split('\n')
        match = list(filter(lambda x: option_find.lower() in x.lower(), copt_split))
        match = '\n'.join(list(map(lambda x: x.replace('* ', ''), match)))
        results = f"Server options:\n{match}"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def whatareyou(self, ctx):
        """What is the bot"""
        if not await IsChannelAllowed(ctx):
            return
        results = "I'm a bot for managing Project Zomboid servers, I'm written in python 3.\nRead more here: https://github.com/aolmosj/project_zomboid_bot"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzrequestaccess(self, ctx):
        """Request access to the PZ server. A password will be DMd to you."""
        config = await require_config(ctx)
        if config is None:
            return
        whitelist_roles = config.get('whitelist_roles') or ''
        role_ids = [int(rid) for rid in whitelist_roles.split(',') if rid.strip()]
        is_present = [r for r in ctx.author.roles if r.id in role_ids]
        if is_present:
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
            except IndexError:
                await ctx.send("Invalid command. Try !pzrequestaccess USER")
                return
            password = ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits + string.ascii_lowercase
            ) for _ in range(8))
            c_run = await rcon_command(ctx, [f"adduser {user} {password}"])
            response = f"{c_run}"
            if "exists" in response:
                await ctx.message.author.send("Unable to create user, try another name")
                return
            if "created" in response:
                server_address = config.get('server_address') or 'Not configured'
                await ctx.message.author.send(
                    f"Your request was accepted.\n"
                    f"Username: {user}\n"
                    f"Password: {password}\n"
                    f"Address: {server_address}"
                )
                return
        else:
            await ctx.message.author.send(
                "You have not been given access to the server yet\n"
                "Please wait for an admin to authorize you"
            )


async def setup(bot):
    await bot.add_cog(UserCommands(bot=bot))
