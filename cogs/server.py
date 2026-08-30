import asyncio
import discord
from discord import app_commands, ui
from discord.ext import commands
from lib.common import is_channel_allowed, can_restart, rcon_interaction_command, servermsg
from lib.guild_config import get_guild_config
from lib.i18n import t
from lib.nitrado import restart_gameserver, NitradoError

# Minutes before the restart at which players get a warning, descending.
WARNING_MARKS = [10, 5, 1]
# Used when /pzrestart is invoked without picking a delay. Restarts are always
# announced, so there is no zero-delay option to fall back to.
DEFAULT_DELAY = 5


class ConfirmRestartView(ui.View):
    """Confirmation gate shown before touching the Nitrado API."""

    def __init__(self, author_id: int, delay: int, locale):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.delay = delay
        self.confirm_button.label = t(locale, "btn_confirm")
        self.cancel_button.label = t(locale, "btn_cancel")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                t(interaction.locale, "only_invoker"), ephemeral=True
            )
            return False
        return True

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

    @ui.button(label="Confirm", style=discord.ButtonStyle.danger, emoji="\U0001f504")
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button):
        self.stop()
        await interaction.response.edit_message(
            content=t(interaction.locale, "restart_confirmed"), view=None
        )
        # The countdown can run for minutes; never block the gateway on it.
        asyncio.create_task(_run_restart(interaction, self.delay))

    @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button):
        self.stop()
        await interaction.response.edit_message(
            content=t(interaction.locale, "restart_cancelled"), view=None
        )


async def _announce(interaction, config, text):
    """Post to the configured notification channel, falling back to a followup."""
    channel_id = config.get('notification_channel') or ''
    channel_id = channel_id.split(',')[0].strip() if channel_id else ''
    if channel_id:
        channel = interaction.guild.get_channel(int(channel_id))
        if channel is not None:
            try:
                await channel.send(text)
                return
            except discord.HTTPException as e:
                print(e)
    try:
        await interaction.followup.send(text)
    except discord.HTTPException as e:
        print(e)


async def _run_restart(interaction, delay):
    locale = interaction.locale
    config = await get_guild_config(interaction.guild.id)
    user = interaction.user.display_name
    await _announce(interaction, config, t(locale, "restart_scheduled", delay=delay, user=user))
    marks = [m for m in WARNING_MARKS if m <= delay]
    remaining = delay
    for i, mark in enumerate(marks):
        await asyncio.sleep((remaining - mark) * 60)
        remaining = mark
        warning = t(locale, "restart_warning", minutes=mark)
        sent = await servermsg(interaction, warning)
        # The reply is the only evidence the broadcast landed; keep it in the
        # journal so a silent no-op can be diagnosed afterwards.
        print(f"servermsg({mark} min) -> {sent!r}")
        if sent is None and i == 0:
            # RCON is unreachable: the players would get no warning at all.
            await _announce(interaction, config, t(locale, "restart_aborted"))
            return
    await asyncio.sleep(remaining * 60)

    await rcon_interaction_command(interaction, "save")

    try:
        await restart_gameserver(
            config['nitrado_token'],
            config['nitrado_service_id'],
            message=f"Restart requested by {user} via Discord",
        )
    except NitradoError as e:
        await _announce(interaction, config, t(locale, "restart_failed", error=e))
        return
    except Exception as e:
        print(e)
        await _announce(interaction, config, t(locale, "restart_failed", error=e))
        return

    await _announce(interaction, config, t(locale, "restart_requested", user=user))


class ServerCommands(commands.Cog):
    """Game server lifecycle commands (Nitrado)"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pzrestart", description="Restart the game server")
    @app_commands.describe(delay="Minutes to warn players before restarting")
    @app_commands.choices(delay=[
        app_commands.Choice(name="1 minute", value=1),
        app_commands.Choice(name="5 minutes", value=5),
        app_commands.Choice(name="10 minutes", value=10),
    ])
    async def pzrestart(self, interaction: discord.Interaction, delay: app_commands.Choice[int] = None):
        if not await is_channel_allowed(interaction):
            return
        if not await can_restart(interaction):
            await interaction.response.send_message(
                t(interaction.locale, "no_permission"), ephemeral=True
            )
            return
        config = await get_guild_config(interaction.guild.id)
        if config is None:
            await interaction.response.send_message(
                t(interaction.locale, "not_configured"), ephemeral=True
            )
            return
        if not config.get('nitrado_token') or not config.get('nitrado_service_id'):
            await interaction.response.send_message(
                t(interaction.locale, "nitrado_not_configured"), ephemeral=True
            )
            return
        if not config.get('rcon_pass'):
            # Every restart warns players and saves first, so RCON is required.
            await interaction.response.send_message(
                t(interaction.locale, "restart_no_rcon"), ephemeral=True
            )
            return

        minutes = delay.value if delay is not None else DEFAULT_DELAY
        prompt = t(interaction.locale, "restart_confirm_delay", delay=minutes)
        view = ConfirmRestartView(interaction.user.id, minutes, interaction.locale)
        await interaction.response.send_message(prompt, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ServerCommands(bot=bot))
