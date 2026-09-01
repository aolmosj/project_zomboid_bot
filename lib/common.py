import asyncio
import logging

from rcon.exceptions import EmptyResponse, SessionTimeout, WrongPassword
from rcon.source import rcon

from lib.guild_config import get_guild_config
from lib.i18n import t

log = logging.getLogger(__name__)

# Most PZ commands answer in well under a second. save is the outlier: on a
# large world it legitimately takes tens of seconds, and aborting one that was
# about to finish is worse than waiting.
RCON_TIMEOUT = 10
RCON_SAVE_TIMEOUT = 60


class RconError(Exception):
    """A command could not be delivered, carrying a key that renders for users."""

    def __init__(self, key, **params):
        super().__init__(key)
        self.key = key
        self.params = params

    def localized(self, locale):
        return t(locale, self.key, **self.params)


def normalize_servermsg(message):
    """The text players will actually see in game.

    The Discord field already delimits the text, so quotes typed around the
    whole message are the PZ syntax leaking through and get dropped. Any that
    remain become single quotes: a double quote would end the argument early
    and PZ has no escape for it, so it can never be shown either way.
    """
    message = message.strip()
    # Exactly one pair, around everything: 'a "b" c' and '"a" y "b"' keep theirs.
    if message.count('"') == 2 and message.startswith('"') and message.endswith('"'):
        message = message[1:-1]
    return message.replace('"', "'")


def servermsg_command(message):
    """PZ expects the broadcast text in double quotes; unquoted it just replies
    with its usage help instead of telling anyone anything."""
    return 'servermsg "{}"'.format(normalize_servermsg(message))


async def run_rcon(config, command, *, timeout=RCON_TIMEOUT):
    """Send one command to the game server.

    Raises RconError and reports nothing: the caller knows where its user is
    listening. The library's own timeout= only covers the TCP connect, so the
    whole exchange is wrapped instead.
    """
    try:
        return await asyncio.wait_for(
            rcon(
                command,
                host=config['rcon_host'],
                port=int(config['rcon_port']),
                passwd=config['rcon_pass'],
            ),
            timeout=timeout,
        )
    except EmptyResponse:
        # Socket accepted, game loop silent: a frozen, starting or overloaded
        # server looks exactly like this.
        raise RconError("rcon_empty_response")
    except WrongPassword:
        raise RconError("rcon_wrong_password")
    except SessionTimeout:
        raise RconError("rcon_session_timeout")
    except asyncio.TimeoutError:
        # Must precede OSError: TimeoutError is a subclass of it.
        raise RconError("rcon_timeout", seconds=timeout)
    except OSError as e:
        raise RconError(
            "rcon_unreachable",
            host=config.get('rcon_host'), port=config.get('rcon_port'), error=e,
        )
    except Exception as e:
        # EmptyResponse taught us that an exception with no message renders as
        # "failed: ", so fall back to the class name rather than nothing.
        raise RconError("rcon_error", error=f"{type(e).__name__}: {e}" if str(e) else type(e).__name__)


async def deliver(coro, *, what):
    """Send a Discord message, or record why it could not be sent.

    Reporting must never raise. A failure here would replace the error being
    reported and take the caller down with it, which is how a restart countdown
    once died leaving nothing behind but an unretrieved task exception.
    """
    try:
        await coro
        return True
    except Exception as e:
        log.warning("could not deliver %s: %s: %s", what, type(e).__name__, e)
        return False


async def require_config(interaction):
    if interaction.guild is None:
        await deliver(
            interaction.response.send_message(t(interaction.locale, "dm_not_allowed"), ephemeral=True),
            what="dm_not_allowed notice",
        )
        return None
    config = await get_guild_config(interaction.guild.id)
    if config is None:
        await deliver(
            interaction.response.send_message(t(interaction.locale, "not_configured"), ephemeral=True),
            what="not_configured notice",
        )
    return config


async def rcon_interaction_command(interaction, command, *, timeout=RCON_TIMEOUT):
    """Run a command for a slash command that is waiting on its own reply."""
    locale = interaction.locale
    config = await get_guild_config(interaction.guild.id)
    if config is None:
        await deliver(
            interaction.followup.send(t(locale, "not_configured"), ephemeral=True),
            what="not_configured notice",
        )
        return None
    if not config.get('rcon_pass'):
        await deliver(
            interaction.followup.send(t(locale, "rcon_not_configured"), ephemeral=True),
            what="rcon_not_configured notice",
        )
        return None
    try:
        return await run_rcon(config, command, timeout=timeout)
    except RconError as e:
        log.warning("rcon %r failed: %s %s", command, e.key, e.params)
        await deliver(
            interaction.followup.send(e.localized(locale), ephemeral=True),
            what="rcon error notice",
        )
        return None


async def servermsg(interaction, message):
    """Broadcast an in-game message to every connected player."""
    return await rcon_interaction_command(interaction, servermsg_command(message))


async def is_channel_allowed(interaction):
    if interaction.guild is None:
        await deliver(
            interaction.response.send_message(t(interaction.locale, "dm_not_allowed"), ephemeral=True),
            what="dm_not_allowed notice",
        )
        return False
    config = await get_guild_config(interaction.guild.id)
    if config is None:
        return True
    ignore_channels = config.get('ignore_channels') or ''
    if not ignore_channels:
        return True
    ignore_list = [int(cid) for cid in ignore_channels.split(',') if cid.strip()]
    if interaction.channel_id in ignore_list:
        await deliver(
            interaction.response.send_message(t(interaction.locale, "channel_blocked"), ephemeral=True),
            what="channel_blocked notice",
        )
        return False
    return True


async def is_admin(interaction):
    config = await get_guild_config(interaction.guild.id)
    if config is None:
        return False
    admin_roles = config.get('admin_roles') or ''
    role_ids = [int(rid) for rid in admin_roles.split(',') if rid.strip()]
    return any(r.id in role_ids for r in interaction.user.roles)


async def is_mod(interaction):
    config = await get_guild_config(interaction.guild.id)
    if config is None:
        return False
    mod_roles = config.get('moderator_roles') or ''
    role_ids = [int(rid) for rid in mod_roles.split(',') if rid.strip()]
    return any(r.id in role_ids for r in interaction.user.roles)


async def can_restart(interaction):
    """Guild administrators, or members holding a role from restart_roles.

    Falls back to admin_roles when restart_roles has not been configured.
    """
    if interaction.guild is None:
        return False
    if interaction.user.guild_permissions.administrator:
        return True
    if interaction.guild.owner_id == interaction.user.id:
        return True
    config = await get_guild_config(interaction.guild.id)
    if config is None:
        return False
    roles = config.get('restart_roles') or config.get('admin_roles') or ''
    role_ids = [int(rid) for rid in roles.split(',') if rid.strip()]
    return any(r.id in role_ids for r in interaction.user.roles)
