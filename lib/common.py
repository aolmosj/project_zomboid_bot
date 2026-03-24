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
