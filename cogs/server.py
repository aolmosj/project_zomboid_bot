import asyncio
import logging

import discord
from discord import app_commands, ui
from discord.ext import commands

from lib.common import (
    RCON_SAVE_TIMEOUT, RconError, can_restart, deliver, is_channel_allowed,
    run_rcon, servermsg_command,
)
from lib.guild_config import get_guild_config
from lib.i18n import t
from lib.nitrado import NitradoError, restart_gameserver

log = logging.getLogger(__name__)

# Minutes before the restart at which players get a warning, descending.
WARNING_MARKS = [10, 5, 1]
# Used when /pzrestart is invoked without picking a delay.
DEFAULT_DELAY = 1
# Nitrado records this on the service activity log; keep it short enough to be
# accepted while still saying why.
NITRADO_MESSAGE_MAX = 200

# create_task keeps only a weak reference, so a running countdown can be
# garbage collected mid-flight unless something holds on to it.
_running = set()


def _spawn(coro):
    task = asyncio.create_task(coro)
    _running.add(task)
    task.add_done_callback(_running.discard)
    task.add_done_callback(_log_task_result)
    return task


def _log_task_result(task):
    if task.cancelled():
        return
    error = task.exception()
    if error is not None:
        log.error("restart task crashed", exc_info=error)


class ConfirmRestartView(ui.View):
    """Confirmation gate shown before touching the Nitrado API."""

    def __init__(self, author_id: int, delay: int, reason: str, locale):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.delay = delay
        self.reason = reason
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
        log.exception("confirm view failed", exc_info=error)
        if not interaction.response.is_done():
            await deliver(
                interaction.response.send_message(f"Error: {error}", ephemeral=True),
                what="confirm view error",
            )

    @ui.button(label="Confirm", style=discord.ButtonStyle.danger, emoji="\U0001f504")
    async def confirm_button(self, interaction: discord.Interaction, button: ui.Button):
        self.stop()
        await interaction.response.edit_message(
            content=t(interaction.locale, "restart_confirmed"), view=None
        )
        # The countdown can run for minutes; never block the gateway on it.
        _spawn(_run_restart(interaction, self.delay, self.reason))

    @ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: ui.Button):
        self.stop()
        await interaction.response.edit_message(
            content=t(interaction.locale, "restart_cancelled"), view=None
        )


async def _announce(interaction, config, text):
    """Post to the configured notification channel, falling back to a followup.

    A countdown outlives the interaction that started it, so the channel is the
    reliable destination and the followup only a last resort.
    """
    channel_id = (config or {}).get('notification_channel') or ''
    channel_id = channel_id.split(',')[0].strip() if channel_id else ''
    if channel_id:
        channel = interaction.guild.get_channel(int(channel_id))
        if channel is not None and await deliver(channel.send(text), what="announcement"):
            return
    await deliver(interaction.followup.send(text), what="announcement followup")


async def _run_restart(interaction, delay, reason):
    """Top-level guard: no failure in the sequence may pass without a word."""
    try:
        await _restart_sequence(interaction, delay, reason)
    except Exception as e:
        log.exception("restart sequence failed unexpectedly")
        config = await get_guild_config(interaction.guild.id)
        await _announce(
            interaction, config,
            t(interaction.locale, "restart_failed", error=f"{type(e).__name__}: {e}"),
        )


async def _restart_sequence(interaction, delay, reason):
    locale = interaction.locale
    config = await get_guild_config(interaction.guild.id)
    user = interaction.user.display_name

    if delay > 0:
        await _announce(interaction, config, t(
            locale, "restart_scheduled", delay=delay, user=user, reason=reason))
        marks = [m for m in WARNING_MARKS if m <= delay]
        remaining = delay
        for i, mark in enumerate(marks):
            await asyncio.sleep((remaining - mark) * 60)
            remaining = mark
            warning = t(locale, "restart_warning", minutes=mark)
            try:
                sent = await run_rcon(config, servermsg_command(warning))
                log.info("servermsg(%s min) -> %r", mark, sent)
            except RconError as e:
                log.warning("restart warning at %s min failed: %s", mark, e.key)
                if i == 0:
                    # Nobody was warned, so nobody may be restarted on.
                    await _announce(interaction, config, t(
                        locale, "restart_aborted", error=e.localized(locale)))
                    return
        await asyncio.sleep(remaining * 60)

        try:
            saved = await run_rcon(config, "save", timeout=RCON_SAVE_TIMEOUT)
            log.info("save -> %r", saved)
        except RconError as e:
            # Restarting on top of a save that did not happen is how a world
            # loses everything held in loaded chunks.
            await _announce(interaction, config, t(
                locale, "restart_save_failed", error=e.localized(locale)))
            return

    note = f"{user} via Discord: {reason}"[:NITRADO_MESSAGE_MAX]
    try:
        await restart_gameserver(
            config['nitrado_token'], config['nitrado_service_id'], message=note,
        )
    except NitradoError as e:
        await _announce(interaction, config, t(locale, "restart_failed", error=e))
        return

    log.info("restart requested by %s: %s", user, reason)
    await _announce(interaction, config, t(
        locale, "restart_requested", user=user, reason=reason))


class ServerCommands(commands.Cog):
    """Game server lifecycle commands (Nitrado)"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pzrestart", description="Restart the game server")
    @app_commands.describe(
        reason="Why the server is being restarted",
        delay="Minutes to warn players before restarting",
    )
    @app_commands.choices(delay=[
        app_commands.Choice(name="1 minute", value=1),
        app_commands.Choice(name="5 minutes", value=5),
        app_commands.Choice(name="10 minutes", value=10),
        app_commands.Choice(name="Now (no warning, no save)", value=0),
    ])
    async def pzrestart(self, interaction: discord.Interaction,
                        reason: app_commands.Range[str, 3, 200],
                        delay: app_commands.Choice[int] = None):
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

        reason = reason.strip()
        minutes = delay.value if delay is not None else DEFAULT_DELAY
        if minutes > 0 and not config.get('rcon_pass'):
            # A delayed restart warns players and saves, both of which need RCON.
            await interaction.response.send_message(
                t(interaction.locale, "restart_no_rcon"), ephemeral=True
            )
            return
        prompt = (t(interaction.locale, "restart_confirm_delay", delay=minutes, reason=reason)
                  if minutes > 0 else t(interaction.locale, "restart_confirm_now", reason=reason))
        view = ConfirmRestartView(interaction.user.id, minutes, reason, interaction.locale)
        await interaction.response.send_message(prompt, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(ServerCommands(bot=bot))
