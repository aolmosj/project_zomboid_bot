import discord
from discord.ext import commands
from lib.common import rcon_command, rcon_interaction_command, IsChannelAllowed, require_config
from lib.guild_config import get_pz_user, add_pz_user


class RequestAccessModal(discord.ui.Modal, title="Crear usuario de Project Zomboid"):
    username = discord.ui.TextInput(
        label="Nombre de usuario",
        placeholder="Tu nombre de usuario para el servidor",
        required=True,
        max_length=50,
    )
    password = discord.ui.TextInput(
        label="Contraseña",
        placeholder="Tu contraseña para el servidor",
        required=True,
        max_length=50,
    )

    def __init__(self, whitelist_role_ids, config):
        super().__init__()
        self.whitelist_role_ids = whitelist_role_ids
        self.config = config

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Verify whitelist roles
        user_role_ids = [r.id for r in interaction.user.roles]
        if not any(rid in user_role_ids for rid in self.whitelist_role_ids):
            await interaction.followup.send(
                "No tienes permisos para crear un usuario. "
                "Espera a que un admin te autorice.",
                ephemeral=True,
            )
            return

        # Check if user already has a PZ account
        guild_id = interaction.guild.id
        discord_user_id = interaction.user.id
        existing = await get_pz_user(guild_id, discord_user_id)
        if existing:
            await interaction.followup.send(
                f"Ya tienes una cuenta creada: **{existing['pz_username']}**",
                ephemeral=True,
            )
            return

        # Execute RCON adduser
        pz_username = self.username.value.strip()
        pz_password = self.password.value.strip()
        response = await rcon_interaction_command(
            interaction, f"adduser {pz_username} {pz_password}"
        )
        if response is None:
            return

        if "exists" in response:
            await interaction.followup.send(
                "El usuario ya existe en el servidor, prueba otro nombre.",
                ephemeral=True,
            )
            return

        if "created" in response:
            # Register in DB
            await add_pz_user(guild_id, discord_user_id, pz_username)

            # Public message in channel
            await interaction.channel.send(
                f"**{interaction.user.display_name}** ha creado el usuario **{pz_username}**"
            )

            # Ephemeral response with credentials
            server_address = self.config.get('server_address') or 'No configurada'
            await interaction.followup.send(
                f"Usuario creado correctamente.\n"
                f"**Usuario:** {pz_username}\n"
                f"**Contraseña:** {pz_password}\n"
                f"**Dirección del servidor:** {server_address}",
                ephemeral=True,
            )
            return

        # Unexpected response
        await interaction.followup.send(
            f"Respuesta inesperada del servidor: {response}",
            ephemeral=True,
        )


class RequestAccessView(discord.ui.View):
    def __init__(self, whitelist_role_ids, config):
        super().__init__(timeout=None)
        self.whitelist_role_ids = whitelist_role_ids
        self.config = config

    @discord.ui.button(label="Crear usuario", style=discord.ButtonStyle.primary)
    async def create_user_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = RequestAccessModal(self.whitelist_role_ids, self.config)
        await interaction.response.send_modal(modal)


class UserCommands(commands.Cog):
    """Commands open to users"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def pzplayers(self, ctx):
        """Show current active players on the server"""
        if not await IsChannelAllowed(ctx):
            return
        c_run = await rcon_command(ctx, ["players"])
        if not c_run:
            return
        c_run = "\n".join(c_run.split('\n')[1:-1])
        results = f"Current players in game:\n{c_run}"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzgetoption(self, ctx):
        """Get the value of a server option"""
        if not await IsChannelAllowed(ctx):
            return
        cmd_split = ctx.message.content.split()
        try:
            option_find = cmd_split[1]
        except IndexError:
            await ctx.send("Invalid command. Try !pzgetoption OPTIONNAME")
            return
        copt = await rcon_command(ctx, 'showoptions')
        if not copt:
            return
        copt_split = copt.split('\n')
        match = list(filter(lambda x: option_find.lower() in x.lower(), copt_split))
        match = '\n'.join(list(map(lambda x: x.replace('* ', ''), match)))
        results = f"Server options:\n{match}"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def whatareyou(self, ctx):
        """What is the bot"""
        if not await IsChannelAllowed(ctx):
            return
        results = "I'm a bot for managing Project Zomboid servers, I'm written in python 3.\nRead more here: https://github.com/aolmosj/project_zomboid_bot"
        await ctx.send(results)

    @commands.command(pass_context=True)
    async def pzrequestaccess(self, ctx):
        """Request access to the PZ server via a form."""
        config = await require_config(ctx)
        if config is None:
            return
        whitelist_roles = config.get('whitelist_roles') or ''
        role_ids = [int(rid) for rid in whitelist_roles.split(',') if rid.strip()]
        view = RequestAccessView(role_ids, config)
        await ctx.send(
            "Pulsa el botón para crear tu usuario de Project Zomboid:",
            view=view,
        )


async def setup(bot):
    await bot.add_cog(UserCommands(bot=bot))
