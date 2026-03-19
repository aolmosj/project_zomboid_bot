from rcon.source import rcon
import os

RCONPASS = os.getenv('RCON_PASS')
RCONSERVER = os.getenv('RCON_SERVER')
RCONPORT = os.getenv('RCON_PORT')
IGNORE_CHANNELS = os.getenv('IGNORE_CHANNELS')
ADMIN_ROLES = os.getenv('ADMIN_ROLES')
MODERATOR_ROLES = os.getenv('MODERATOR_ROLES')
ADMIN_ROLES = ADMIN_ROLES.split(',')
block_notified = list()

async def rcon_command(ctx, command):
    try:
        response = await rcon(
            " ".join(command),
            host=RCONSERVER, port=int(RCONPORT), passwd=RCONPASS
        )
        return response
    except Exception as e:
        print(e)

async def IsChannelAllowed(ctx):
    channel_name = str(ctx.message.channel)
    is_present = [i for i in IGNORE_CHANNELS if i.lower() == channel_name.lower()]
    if channel_name in IGNORE_CHANNELS:
        if channel_name not in block_notified:
            await ctx.send("Not allowed to run commands in this channel")
            block_notified.append(channel_name)
        raise Exception("Not allowed to operate in channel")

async def IsAdmin(ctx):
    is_present = [i for i in ctx.author.roles if i.name in ADMIN_ROLES]
    return is_present

async def IsMod(ctx):
    is_present = [i for i in ctx.author.roles if i.name in MODERATOR_ROLES]
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