from rcon.source import rcon
from lib.guild_config import get_guild_config

block_notified = list()

async def require_config(ctx):
    if ctx.guild is None:
        return None
    config = await get_guild_config(ctx.guild.id)
    if config is None:
        await ctx.send("This server hasn't been configured yet. An admin needs to run `!pzsetup`.")
    return config

async def rcon_command(ctx, command):
    config = await require_config(ctx)
    if config is None:
        return None
    if not config.get('rcon_pass'):
        await ctx.send("RCON is not configured yet. An admin needs to configure it via `!pzsetup`.")
        return None
    try:
        response = await rcon(
            " ".join(command),
            host=config['rcon_host'],
            port=int(config['rcon_port']),
            passwd=config['rcon_pass']
        )
        return response
    except Exception as e:
        print(e)

async def IsChannelAllowed(ctx):
    if ctx.guild is None:
        await ctx.send("Commands can only be used in a server, not in DMs.")
        return False
    config = await get_guild_config(ctx.guild.id)
    if config is None:
        return True
    ignore_channels = config.get('ignore_channels') or ''
    if not ignore_channels:
        return True
    ignore_list = [int(cid) for cid in ignore_channels.split(',') if cid.strip()]
    channel_id = ctx.message.channel.id
    if channel_id in ignore_list:
        if channel_id not in block_notified:
            await ctx.send("Not allowed to run commands in this channel")
            block_notified.append(channel_id)
        return False
    return True

async def IsAdmin(ctx):
    config = await get_guild_config(ctx.guild.id)
    if config is None:
        return False
    admin_roles = config.get('admin_roles') or ''
    role_ids = [int(rid) for rid in admin_roles.split(',') if rid.strip()]
    is_present = [r for r in ctx.author.roles if r.id in role_ids]
    return is_present

async def IsMod(ctx):
    config = await get_guild_config(ctx.guild.id)
    if config is None:
        return False
    mod_roles = config.get('moderator_roles') or ''
    role_ids = [int(rid) for rid in mod_roles.split(',') if rid.strip()]
    is_present = [r for r in ctx.author.roles if r.id in role_ids]
    return is_present

async def pretty_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%s%dd, %dh, %dm, %ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh, %dm, %ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%dm, %ds' % (sign_string, minutes, seconds)
    else:
        return '%s%ds' % (sign_string, seconds)
