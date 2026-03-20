from discord.ext import commands
from lib.common import rcon_command, IsChannelAllowed, IsAdmin

access_levels = ['admin', 'none', 'moderator']


class AdminCommands(commands.Cog):
    """Admin Server Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pzsetaccess(self, ctx):
        """Set the access level of a specific user."""
        if not await IsChannelAllowed(ctx):
            return
        if await IsAdmin(ctx):
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
                access_level = access_split[2]
            except IndexError:
                await ctx.send("Invalid command. Try !pzsetaccess USER ACCESSLEVEL")
                return
            if access_level not in access_levels:
                await ctx.send(f"Invalid access level {access_level}. Must be one of {access_levels}")
                return
            c_run = await rcon_command(ctx, [f"setaccesslevel", f"{user}", f"{access_level}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(AdminCommands(bot=bot))
