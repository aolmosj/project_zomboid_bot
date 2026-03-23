from discord.ext import commands
from lib.common import rcon_command, IsChannelAllowed, IsMod


class ModeratorCommands(commands.Cog):
    """Moderator Server Commands"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pzsteamban(self, ctx):
        """Steam ban a user"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
            except IndexError:
                await ctx.send("Invalid command. Try !pzsteamban USER")
                return
            c_run = await rcon_command(ctx, [f"banid", f"{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzsteamunban(self, ctx):
        """Steam unban a user"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
            except IndexError:
                await ctx.send("Invalid command. Try !pzsteamunban USER")
                return
            c_run = await rcon_command(ctx, [f"unbanid", "{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzteleport(self, ctx):
        """Teleport a user to another user"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                usera = access_split[1]
                userb = access_split[2]
            except IndexError:
                await ctx.send("Invalid command. Try !pzteleport USERA to USERB")
                return
            c_run = await rcon_command(ctx, [f"teleport", f"{usera}", f"{userb}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzadditem(self, ctx):
        """Adds an item to the specified user's inventory"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
                item = access_split[2]
            except IndexError:
                await ctx.send("Invalid command. Try !pzadditem USER ITEM")
                return
            c_run = await rcon_command(ctx, [f"additem", f"{user}", f"{item}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzkick(self, ctx):
        """Kick a user"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
            except IndexError:
                await ctx.send("Invalid command. Try !pzkick USER")
                return
            c_run = await rcon_command(ctx, [f"kickuser", f"{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzwhitelist(self, ctx):
        """Whitelist a user"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
            except IndexError:
                await ctx.send("Invalid command. Try !pzwhitelist USER")
                return
            c_run = await rcon_command(ctx, [f"addusertowhitelist", f"{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzadduser(self, ctx):
        """Add a user with pass"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
                pwd = access_split[2]
            except IndexError:
                await ctx.send("Invalid command. Try !pzadduser 'USER' 'PASS'")
                return
            c_run = await rcon_command(ctx, [f"adduser", f"{user}", f"{pwd}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzservermsg(self, ctx):
        """Broadcast a server message"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                access_split = access_split[1:]
                smsg = " ".join(access_split)
            except IndexError:
                await ctx.send("Invalid command. Try !pzservermsg My cool message")
                return
            c_run = await rcon_command(ctx, [f'servermsg', f"{smsg}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzunwhitelist(self, ctx):
        """Remove a whitelisted user"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            access_split = ctx.message.content.split()
            try:
                user = access_split[1]
            except IndexError:
                await ctx.send("Invalid command. Try !pzunwhitelist USER")
                return
            c_run = await rcon_command(ctx, [f"removeuserfromwhitelist", f"{user}"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzwhitelistall(self, ctx):
        """Whitelist all active users"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            c_run = await rcon_command(ctx, [f"addalltowhitelist"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)

    @commands.command(pass_context=True)
    async def pzsave(self, ctx):
        """Save the current world"""
        if not await IsChannelAllowed(ctx):
            return
        if await IsMod(ctx):
            c_run = await rcon_command(ctx, [f"save"])
            response = f"{c_run}"
        else:
            response = f"{ctx.author}, you don't have admin rights."
        await ctx.send(response)


async def setup(bot):
    await bot.add_cog(ModeratorCommands(bot=bot))
