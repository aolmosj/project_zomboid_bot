import discord
from discord.ext import commands

#from IsChannelAllowed import IsChannelAllowed
#from common import Common

import os
from SourceRcon import SourceRcon

block_notified = list()

IGNORE_CHANNELS = os.getenv('IGNORE_CHANNELS')
RCONPASS = os.getenv('RCON_PASS')
RCONSERVER = os.getenv('RCON_SERVER')
RCONPORT = os.getenv('RCON_PORT')

class UserCommands(commands.Cog):
    """Commands open to users"""
    def __init__(self, bot):
        self.bot = bot
        #self.common = Common()
    
    @commands.command(pass_context=True)
    async def pzplayers(self, ctx):
        """Show current active players on the server"""
        #await self.common.IsChannelAllowed(ctx)
        await IsChannelAllowed(ctx)
        c_run = ""
        c_run = await rcon_command(ctx, ["players"])
        print(c_run)
        if not c_run:
            return
        c_run = "\n".join(c_run.split('\n')[1:-1])
        results = f"Current players in game:\n{c_run}"
        await ctx.send(results)


    @commands.command(pass_context=True)
    async def pzgetoption(self, ctx):
        """Get the value of a server option"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        option_find = ""
        try:
            option_find = cmd_split[1]
        except IndexError as ie:
            response = f"Invalid command. Try !pzgetoption OPTIONNAME"
            await ctx.send(response)
            return
        copt = await rcon_command(ctx,'showoptions')
        copt_split = copt.split('\n')
        match = list(filter(lambda x: option_find.lower() in x.lower(), copt_split))
        match = '\n'.join(list(map(lambda x: x.replace('* ',''),match)))
        results = f"Server options:\n{match}"
        await ctx.send(results)


    @commands.command(pass_context=True)
    async def pzdeathcount(self, ctx):
        """Get the total death count of a player"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        option_find = ""
        try:
            username = cmd_split[1]
        except IndexError as ie:
            response = f"Invalid command. Try !pzdeathcount USERNAME"
            await ctx.send(response)
            return
        dc = await GetDeathCount(ctx, username)
        results = dc
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzplaytime(self, ctx):
        """Get the total playtime of all players"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        dc = await getallplaytime(ctx)
        pt_list = list()
        for user in dc:
            upt = dc[user]
            pt_list.append(f"{user} has played for {upt}")
        clist = chunks(pt_list, 100)
        async for c in clist:
            await ctx.send('\n'.join(c))

    @commands.command(pass_context=True)
    async def pzdeaths(self, ctx):
        """Get the total death count of all players"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        dc = await getalldeaths(ctx)
        results = dc.split('\n')
        clist = chunks(results, 100) 
        async for c in clist: 
            await ctx.send('\n'.join(c))


    @commands.command(pass_context=True)
    async def whatareyou(self, ctx):
        """What is the bot"""
        await IsChannelAllowed(ctx)
        results = f"I'm a bot for managing Project Zomboid servers, I'm written in python 3.\nRead more here: https://rfalias.github.io/project_zomboid_bot/"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzlistmods(self, ctx):
        """List currently installed mods"""
        await IsChannelAllowed(ctx)
        cmd_split = ctx.message.content.split()
        gm = await getmods()
        results = f"Currently installed mods:\n{gm}"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzrequestaccess(self, ctx):
        """Request access to the PZ server. A password will be DMd to you. These are hashed and can only be sent once"""
        is_present = [i for i in ctx.author.roles if i.name in WHITELIST_ROLES]
        if is_present:
            access_split = ctx.message.content.split()
            user = ""
            try:
                user = access_split[1]
            except IndexError as ie:
                response = f"Invalid command. Try !pzrequestaccess USER"
                await ctx.send(response)
                return 
            password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(8))
            
            c_run = await rcon_command(ctx,[f"adduser {user} {password}"])
            response = f"{c_run}"
            if "exists" in response:
                await ctx.message.author.send(f"Unable to create user, try another name")
                return
            if "created" in response:
                await ctx.message.author.send(f"Your request was accepted.\nUsername: {user}\nPassword: {password}\nAddress: {SERVER_ADDRESS}")
                return
        else:
            await ctx.message.author.send(f"You have not been given access to the server yet\nPlease wait for an admin to authorize you")
            return
            #await ctx.message.author.send(f"Your request user {user} has been created\nPassword: password\nServer Address: {SERVER_ADDRESS}")

async def rcon_command(ctx, command):
    try:
        sr = SourceRcon(RCONSERVER, int(RCONPORT), RCONPASS)
        r = sr.rcon(" ".join(command))
        return r.decode('utf-8')
    except Exception as e:
        print(e)

async def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

async def IsChannelAllowed(ctx):
    channel_name = str(ctx.message.channel)
    is_present = [i for i in IGNORE_CHANNELS if i.lower() == channel_name.lower()]
    if channel_name in IGNORE_CHANNELS:
        if channel_name not in block_notified:
            await ctx.send("Not allowed to run commands in this channel")
            block_notified.append(channel_name)
        raise Exception("Not allowed to operate in channel")
    
async def pzplayers():
    plist = list()
    c_run = ""
    c_run = await rcon_command(None, ["players"])
    c_run = c_run.split('\n')[1:-1]
    return len(c_run)            


async def setup(bot):
    await bot.add_cog(UserCommands(bot))