import discord
from discord import app_commands
from discord.ext import commands
from lib.common import rcon_interaction_command, is_channel_allowed, is_admin
from lib.guild_config import get_all_pz_users
from lib.i18n import t


class AdminCommands(commands.Cog):
    """Admin Server Commands"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pzsetaccess", description="Set the access level of a user")
    @app_commands.describe(user="Target user", access_level="Access level to set")
    @app_commands.choices(access_level=[
        app_commands.Choice(name="Admin", value="admin"),
        app_commands.Choice(name="Moderator", value="moderator"),
        app_commands.Choice(name="None", value="none"),
    ])
    async def pzsetaccess(self, interaction: discord.Interaction, user: str, access_level: app_commands.Choice[str]):
        if not await is_channel_allowed(interaction):
            return
        if not await is_admin(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"setaccesslevel {user} {access_level.value}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzusers", description="List all registered PZ users")
    async def pzusers(self, interaction: discord.Interaction):
        if not await is_channel_allowed(interaction):
            return
        if not await is_admin(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()

        users = await get_all_pz_users(interaction.guild.id)
        locale = interaction.locale

        if not users:
            embed = discord.Embed(
                title=t(locale, "pz_users_title"),
                description=t(locale, "no_registered_users"),
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)
            return

        for i in range(0, len(users), 25):
            chunk = users[i:i + 25]
            embed = discord.Embed(
                title=t(locale, "pz_users_title"),
                color=discord.Color.green()
            )
            for user in chunk:
                embed.add_field(
                    name=user['pz_username'],
                    value=f"<@{user['discord_user_id']}> — {user['created_at']}",
                    inline=False
                )
            await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminCommands(bot=bot))
