import discord
from discord.ext import commands
from lib.common import rcon_command, IsChannelAllowed, IsAdmin
from lib.guild_config import get_all_pz_users

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


    @commands.command()
    async def pzusers(self, ctx):
        """Muestra todos los usuarios PZ registrados en el servidor."""
        if not await IsChannelAllowed(ctx):
            return
        if not await IsAdmin(ctx):
            await ctx.send(f"{ctx.author}, you don't have admin rights.")
            return

        users = await get_all_pz_users(ctx.guild.id)

        if not users:
            embed = discord.Embed(
                title="Usuarios de Project Zomboid",
                description="No hay usuarios registrados",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
            return

        # Paginar en embeds de 25 fields cada uno
        for i in range(0, len(users), 25):
            chunk = users[i:i + 25]
            embed = discord.Embed(
                title="Usuarios de Project Zomboid",
                color=discord.Color.green()
            )
            for user in chunk:
                embed.add_field(
                    name=user['pz_username'],
                    value=f"<@{user['discord_user_id']}> — {user['created_at']}",
                    inline=False
                )
            await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCommands(bot=bot))
