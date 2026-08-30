from rcon.source import rcon
from lib.guild_config import get_guild_config
from lib.i18n import t


async def require_config(interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            t(interaction.locale, "dm_not_allowed"), ephemeral=True
        )
        return None
    config = await get_guild_config(interaction.guild.id)
    if config is None:
        await interaction.response.send_message(
            t(interaction.locale, "not_configured"), ephemeral=True
        )
    return config


async def rcon_interaction_command(interaction, command):
    config = await get_guild_config(interaction.guild.id)
    if config is None:
        await interaction.followup.send(
            t(interaction.locale, "not_configured"), ephemeral=True
        )
        return None
    if not config.get('rcon_pass'):
        await interaction.followup.send(
            t(interaction.locale, "rcon_not_configured"), ephemeral=True
        )
        return None
    try:
        response = await rcon(
            command,
            host=config['rcon_host'],
            port=int(config['rcon_port']),
            passwd=config['rcon_pass']
        )
        return response
    except Exception as e:
        print(e)
        await interaction.followup.send(
            t(interaction.locale, "rcon_error", error=e), ephemeral=True
        )
        return None


def _quote(message):
    """Wrap a message for PZ's servermsg, which expects it in double quotes.

    The Discord field already delimits the text, so quotes typed around the
    whole message are the PZ syntax leaking through and get dropped. Any that
    remain become single quotes: a double quote would end the argument early
    and PZ has no escape for it, so it can never be shown either way.
    """
    message = message.strip()
    # Exactly one pair, around everything: 'a "b" c' and '"a" y "b"' keep theirs.
    if message.count('"') == 2 and message.startswith('"') and message.endswith('"'):
        message = message[1:-1]
    return 'servermsg "{}"'.format(message.replace('"', "'"))


async def servermsg(interaction, message):
    """Broadcast an in-game message to every connected player."""
    return await rcon_interaction_command(interaction, _quote(message))


async def is_channel_allowed(interaction):
    if interaction.guild is None:
        await interaction.response.send_message(
            t(interaction.locale, "dm_not_allowed"), ephemeral=True
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
        await interaction.response.send_message(
            t(interaction.locale, "channel_blocked"), ephemeral=True
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
