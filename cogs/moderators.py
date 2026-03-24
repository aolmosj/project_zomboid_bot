import discord
from discord import app_commands
from discord.ext import commands
from lib.common import rcon_interaction_command, is_channel_allowed, is_mod
from lib.i18n import t


class ModeratorCommands(commands.Cog):
    """Moderator Server Commands"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pzsteamban", description="Steam ban a user")
    @app_commands.describe(user="Steam ID to ban")
    async def pzsteamban(self, interaction: discord.Interaction, user: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"banid {user}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzsteamunban", description="Steam unban a user")
    @app_commands.describe(user="Steam ID to unban")
    async def pzsteamunban(self, interaction: discord.Interaction, user: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"unbanid {user}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzteleport", description="Teleport a user to another user")
    @app_commands.describe(user_a="User to teleport", user_b="Destination user")
    async def pzteleport(self, interaction: discord.Interaction, user_a: str, user_b: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"teleport {user_a} {user_b}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzadditem", description="Add an item to a user's inventory")
    @app_commands.describe(user="Target user", item="Item to add")
    async def pzadditem(self, interaction: discord.Interaction, user: str, item: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"additem {user} {item}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzkick", description="Kick a user from the server")
    @app_commands.describe(user="User to kick")
    async def pzkick(self, interaction: discord.Interaction, user: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"kickuser {user}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzwhitelist", description="Whitelist a user")
    @app_commands.describe(user="User to whitelist")
    async def pzwhitelist(self, interaction: discord.Interaction, user: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"addusertowhitelist {user}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzadduser", description="Add a user with a password")
    @app_commands.describe(user="Username", password="Password")
    async def pzadduser(self, interaction: discord.Interaction, user: str, password: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"adduser {user} {password}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzservermsg", description="Broadcast a server message")
    @app_commands.describe(message="Message to broadcast")
    async def pzservermsg(self, interaction: discord.Interaction, message: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"servermsg {message}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzunwhitelist", description="Remove a user from the whitelist")
    @app_commands.describe(user="User to remove from whitelist")
    async def pzunwhitelist(self, interaction: discord.Interaction, user: str):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, f"removeuserfromwhitelist {user}")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzwhitelistall", description="Whitelist all active users")
    async def pzwhitelistall(self, interaction: discord.Interaction):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, "addalltowhitelist")
        if c_run is not None:
            await interaction.followup.send(c_run)

    @app_commands.command(name="pzsave", description="Save the current world")
    async def pzsave(self, interaction: discord.Interaction):
        if not await is_channel_allowed(interaction):
            return
        if not await is_mod(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, "save")
        if c_run is not None:
            await interaction.followup.send(c_run)


async def setup(bot):
    await bot.add_cog(ModeratorCommands(bot=bot))
