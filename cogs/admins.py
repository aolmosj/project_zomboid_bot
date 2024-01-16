import discord
from discord.ext import commands

class AdminCommands(commands.Cog):
    """Admin Server Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
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

    @commands.command(pass_context=True)
    async def pzrestartserver(self, ctx):
        """Restart the PZ server"""
        await IsChannelAllowed(ctx)
        if await IsAdmin(ctx):
            bot.loop.create_task(restart_server(ctx))

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))            
