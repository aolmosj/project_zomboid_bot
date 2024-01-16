import discord
from discord.ext import commands

class ModeratorCommands(commands.Cog):
    """Moderator Server Commands"""
    def __init__(self, bot):
        self.bot = bot    

    @commands.command(pass_context=True)
    async def pzsteamban(self, ctx):
        """Steam ban a user"""
        await IsChannelAllowed(ctx)
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            user = ""
            try:
                user = access_split[1]
            except IndexError as ie:
                response = f"Invalid command. Try !pzsteamban USER"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx,[f"banid", f"{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzsteamunban(self, ctx):
        """Steam unban a user"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            user = ""
            try:
                user = access_split[1]
            except IndexError as ie:
                response = f"Invalid command. Try !pzsteamunban USER"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx,[f"unbanid", "{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)


    @commands.command(pass_context=True)
    async def pzteleport(self, ctx):
        """Teleport a user to another user"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            user = ""
            try:
                usera = access_split[1]
                userb = access_split[2]  
            except IndexError as ie:
                response = f"Invalid command. Try !pzteleport USERA to USERB"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx,[f"teleport", f"{usera}",f"{userb}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzadditem(self, ctx):
        """Adds an item to the specified user's inventory"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            print(ctx.message.content)
            access_split = ctx.message.content.split()
            user = ""
            item = ""
            try:
                user = access_split[1]
                item = access_split[2]
            except IndexError as ie:
                response =f"Invalid command. Try !pzadditem USER ITEM"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx,[f"additem", f"{user}", f"{item}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzkick(self, ctx):
        """Kick a user"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            user = ""
            try:
                user = access_split[1]
            except IndexError as ie:
                response = f"Invalid command. Try !pzkick USER"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx,[f"kickuser", f"{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzwhitelist(self, ctx):
        """Whitelist a user"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            user = ""
            try:
                user = access_split[1]
            except IndexError as ie:
                response = f"Invalid command. Try !pzwhitelist USER"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx,[f"addusertowhitelist", f"{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)


    @commands.command(pass_context=True)
    async def pzservermsg(self, ctx):
        """Broadcast a server message"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                access_split = access_split[1:]
                smsg = " ".join(access_split)
            except IndexError as ie:
                response = f"Invalid command. Try !pzservermsg My cool message"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx,[f'servermsg', f"{smsg}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzunwhitelist(self, ctx):
        """Remove a whitelisted user"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            user = ""
            try:
                user = access_split[1]
            except IndexError as ie:
                response = f"Invalid command. Try !pzunwhitelist USER"
                await ctx.send(response)
                return
            c_run = await rcon_command(ctx,[f"removeuserfromwhitelist", f"{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)


    @commands.command(pass_context=True)
    async def pzwhitelistall(self, ctx):
        """Whitelist all active users"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            c_run = await rcon_command(ctx,[f"addalltowhitelist"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)


    @commands.command(pass_context=True)
    async def pzsave(self, ctx):
        """Save the current world"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            c_run = await rcon_command(ctx,[f"save"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzgetsteamid(self,ctx):
        """Lookup steamid of user"""
        await IsChannelAllowed(ctx)
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            user = ""
            try:
                user = access_split[1]
            except IndexError as ie:
                response = f"Invalid command. Try !pzunwhitelist USER"
                await ctx.send(response)
                return
            c_run = await lookupsteamid(user)
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)  

async def setup(bot):
    await bot.add_cog(ModeratorCommands(bot))        