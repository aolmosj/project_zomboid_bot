import discord
from discord import app_commands, ui
from discord.ext import commands
from lib.common import rcon_interaction_command, is_channel_allowed, require_config
from lib.guild_config import get_guild_config, get_pz_user, add_pz_user
from lib.i18n import t


class RequestAccessModal(ui.Modal):
    def __init__(self, whitelist_role_ids, config, locale):
        super().__init__(title=t(locale, "modal_title"))
        self.whitelist_role_ids = whitelist_role_ids
        self.config = config
        self.locale = locale
        self.username = ui.TextInput(
            label=t(locale, "modal_username_label"),
            placeholder=t(locale, "modal_username_placeholder"),
            required=True,
            max_length=50,
        )
        self.password = ui.TextInput(
            label=t(locale, "modal_password_label"),
            placeholder=t(locale, "modal_password_placeholder"),
            required=True,
            max_length=50,
        )
        self.add_item(self.username)
        self.add_item(self.password)

    async def on_submit(self, interaction: discord.Interaction):
        locale = interaction.locale
        await interaction.response.defer(ephemeral=True)

        user_role_ids = [r.id for r in interaction.user.roles]
        if not any(rid in user_role_ids for rid in self.whitelist_role_ids):
            await interaction.followup.send(
                t(locale, "no_whitelist_permission"), ephemeral=True
            )
            return

        guild_id = interaction.guild.id
        discord_user_id = interaction.user.id
        existing = await get_pz_user(guild_id, discord_user_id)
        if existing:
            await interaction.followup.send(
                t(locale, "already_has_account", username=existing['pz_username']),
                ephemeral=True,
            )
            return

        pz_username = self.username.value.strip()
        pz_password = self.password.value.strip()
        response = await rcon_interaction_command(
            interaction, f"adduser {pz_username} {pz_password}"
        )
        if response is None:
            return

        if "exists" in response:
            await interaction.followup.send(
                t(locale, "user_exists_on_server"), ephemeral=True
            )
            return

        if "created" in response:
            await add_pz_user(guild_id, discord_user_id, pz_username)

            await interaction.channel.send(
                t(locale, "user_created_public",
                  display_name=interaction.user.display_name,
                  username=pz_username)
            )

            server_address = self.config.get('server_address') or t(locale, "address_not_set")
            await interaction.followup.send(
                t(locale, "user_created_private",
                  username=pz_username,
                  password=pz_password,
                  address=server_address),
                ephemeral=True,
            )
            return

        await interaction.followup.send(
            t(locale, "unexpected_response", response=response), ephemeral=True
        )


class RequestAccessView(ui.View):
    def __init__(self, whitelist_role_ids, config, locale):
        super().__init__(timeout=None)
        self.whitelist_role_ids = whitelist_role_ids
        self.config = config
        self.locale = locale

        button = ui.Button(
            label=t(locale, "create_user_button"),
            style=discord.ButtonStyle.primary,
        )
        button.callback = self.create_user_callback
        self.add_item(button)

    async def create_user_callback(self, interaction: discord.Interaction):
        modal = RequestAccessModal(self.whitelist_role_ids, self.config, interaction.locale)
        await interaction.response.send_modal(modal)


class UserCommands(commands.Cog):
    """Commands open to users"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pzplayers", description="Show current active players on the server")
    async def pzplayers(self, interaction: discord.Interaction):
        if not await is_channel_allowed(interaction):
            return
        await interaction.response.defer()
        c_run = await rcon_interaction_command(interaction, "players")
        if not c_run:
            return
        players = "\n".join(c_run.split('\n')[1:-1])
        await interaction.followup.send(
            t(interaction.locale, "players_title", players=players)
        )

    @app_commands.command(name="pzgetoption", description="Get the value of a server option")
    @app_commands.describe(option="The option name to search for")
    async def pzgetoption(self, interaction: discord.Interaction, option: str):
        if not await is_channel_allowed(interaction):
            return
        await interaction.response.defer()
        copt = await rcon_interaction_command(interaction, "showoptions")
        if not copt:
            return
        copt_split = copt.split('\n')
        match = list(filter(lambda x: option.lower() in x.lower(), copt_split))
        match = '\n'.join(list(map(lambda x: x.replace('* ', ''), match)))
        await interaction.followup.send(
            t(interaction.locale, "option_results", options=match)
        )

    @app_commands.command(name="whatareyou", description="What is this bot?")
    async def whatareyou(self, interaction: discord.Interaction):
        if not await is_channel_allowed(interaction):
            return
        await interaction.response.send_message(
            t(interaction.locale, "whatareyou")
        )

    @app_commands.command(name="pzrequestaccess", description="Request access to the PZ server")
    async def pzrequestaccess(self, interaction: discord.Interaction):
        config = await require_config(interaction)
        if config is None:
            return
        whitelist_roles = config.get('whitelist_roles') or ''
        role_ids = [int(rid) for rid in whitelist_roles.split(',') if rid.strip()]
        locale = interaction.locale
        view = RequestAccessView(role_ids, config, locale)
        await interaction.response.send_message(
            t(locale, "request_access_prompt"), view=view
        )


async def setup(bot):
    await bot.add_cog(UserCommands(bot=bot))
