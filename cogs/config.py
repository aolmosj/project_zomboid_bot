import discord
from discord import app_commands, ui
from discord.ext import commands
from lib.guild_config import get_guild_config, set_guild_config, delete_guild_config, CONFIG_KEYS
from lib.i18n import t


class RconModal(ui.Modal):
    def __init__(self, locale):
        super().__init__(title="RCON Configuration")
        self.locale = locale
        self.rcon_host = ui.TextInput(label="Host", placeholder="127.0.0.1", default="127.0.0.1")
        self.rcon_port = ui.TextInput(label="Port", placeholder="27015", default="27015")
        self.rcon_pass = ui.TextInput(label="Password", placeholder="Your RCON password")
        self.server_address = ui.TextInput(label="Server address (shown to players)", placeholder="1.2.3.4:16261", required=False)
        self.add_item(self.rcon_host)
        self.add_item(self.rcon_port)
        self.add_item(self.rcon_pass)
        self.add_item(self.server_address)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            port = int(self.rcon_port.value)
        except ValueError:
            await interaction.response.send_message("Invalid port number.", ephemeral=True)
            return
        kwargs = dict(
            rcon_host=self.rcon_host.value,
            rcon_port=port,
            rcon_pass=self.rcon_pass.value,
        )
        if self.server_address.value:
            kwargs['server_address'] = self.server_address.value
        await set_guild_config(interaction.guild.id, **kwargs)
        await interaction.response.send_message("RCON configured successfully.", ephemeral=True)


def _parse_role_ids(value):
    if not value:
        return []
    return [int(rid) for rid in value.split(',') if rid.strip()]


def _build_defaults(guild, role_ids):
    defaults = []
    for rid in role_ids:
        role = guild.get_role(rid)
        if role:
            defaults.append(role)
    return defaults


class ConfigView(ui.View):
    """A view with a single select item for configuration."""
    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the person who ran the command can use these buttons.", ephemeral=True)
            return False
        return True


class ConfigRoleSelect(ui.RoleSelect):
    def __init__(self, config_key: str, display_name: str, **kwargs):
        super().__init__(**kwargs)
        self.config_key = config_key
        self.display_name = display_name

    async def callback(self, interaction: discord.Interaction):
        role_ids = ','.join(str(r.id) for r in self.values)
        if self.values:
            await set_guild_config(interaction.guild.id, **{self.config_key: role_ids})
            names = ', '.join(r.name for r in self.values)
            await interaction.response.send_message(f"{self.display_name} set to: {names}", ephemeral=True)
        else:
            await set_guild_config(interaction.guild.id, **{self.config_key: ''})
            await interaction.response.send_message(f"{self.display_name} cleared.", ephemeral=True)


class ConfigChannelSelect(ui.ChannelSelect):
    def __init__(self, config_key: str, display_name: str, **kwargs):
        super().__init__(**kwargs)
        self.config_key = config_key
        self.display_name = display_name

    async def callback(self, interaction: discord.Interaction):
        channel_ids = ','.join(str(c.id) for c in self.values)
        if self.values:
            await set_guild_config(interaction.guild.id, **{self.config_key: channel_ids})
            names = ', '.join(c.name for c in self.values)
            await interaction.response.send_message(f"{self.display_name} set to: {names}", ephemeral=True)
        else:
            await set_guild_config(interaction.guild.id, **{self.config_key: ''})
            await interaction.response.send_message(f"{self.display_name} cleared.", ephemeral=True)


def _make_role_view(author_id, guild, config, config_key, display_name, placeholder):
    select = ConfigRoleSelect(config_key, display_name, placeholder=placeholder, min_values=0, max_values=10)
    if config:
        defaults = _build_defaults(guild, _parse_role_ids(config.get(config_key)))
        if defaults:
            select.default_values = defaults
    view = ConfigView(author_id)
    view.add_item(select)
    return view


def _make_channel_view(author_id, guild, config, config_key, display_name, placeholder, max_values=10):
    select = ConfigChannelSelect(config_key, display_name, placeholder=placeholder,
                                 channel_types=[discord.ChannelType.text], min_values=0, max_values=max_values)
    if config:
        defaults = _build_channel_defaults(guild, _parse_channel_ids(config.get(config_key)))
        if defaults:
            select.default_values = defaults
    view = ConfigView(author_id)
    view.add_item(select)
    return view


def _parse_channel_ids(value):
    if not value:
        return []
    return [int(cid) for cid in value.split(',') if cid.strip()]


def _build_channel_defaults(guild, channel_ids):
    defaults = []
    for cid in channel_ids:
        channel = guild.get_channel(cid)
        if channel:
            defaults.append(channel)
    return defaults


class SetupView(ui.View):
    def __init__(self, author_id: int, locale):
        super().__init__(timeout=120)
        self.author_id = author_id
        self.locale = locale
        self.message = None

    async def on_timeout(self):
        if self.message:
            try:
                await self.message.delete()
            except discord.NotFound:
                pass

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Only the person who ran the command can use these buttons.", ephemeral=True)
            return False
        return True

    async def on_error(self, interaction: discord.Interaction, error: Exception, item):
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)
        if not interaction.response.is_done():
            await interaction.response.send_message(f"Error: {error}", ephemeral=True)

    @ui.button(label="RCON", style=discord.ButtonStyle.primary, emoji="\U0001f50c")
    async def rcon_button(self, interaction: discord.Interaction, button: ui.Button):
        config = await get_guild_config(interaction.guild.id)
        modal = RconModal(locale=interaction.locale)
        if config:
            modal.rcon_host.default = config.get('rcon_host') or '127.0.0.1'
            modal.rcon_port.default = str(config.get('rcon_port') or '27015')
            modal.server_address.default = config.get('server_address') or ''
        await interaction.response.send_modal(modal)

    @ui.button(label="Roles", style=discord.ButtonStyle.secondary, emoji="\U0001f465")
    async def roles_button(self, interaction: discord.Interaction, button: ui.Button):
        config = await get_guild_config(interaction.guild.id)
        guild = interaction.guild
        uid = interaction.user.id

        admin_view = _make_role_view(uid, guild, config, 'admin_roles', 'Admin roles', "Select admin roles...")
        await interaction.response.send_message(
            "**Admin roles** \u2014 Full access: can configure the bot, manage the server, and use all commands",
            view=admin_view, ephemeral=True
        )

        mod_view = _make_role_view(uid, guild, config, 'moderator_roles', 'Moderator roles', "Select moderator roles...")
        await interaction.followup.send(
            "**Moderator roles** \u2014 Can kick/ban players, manage whitelist, and use moderation commands",
            view=mod_view, ephemeral=True
        )

        wl_view = _make_role_view(uid, guild, config, 'whitelist_roles', 'Whitelist roles', "Select whitelist roles...")
        await interaction.followup.send(
            "**Whitelist roles** \u2014 Users with these roles are automatically whitelisted on the server",
            view=wl_view, ephemeral=True
        )

    @ui.button(label="Channels", style=discord.ButtonStyle.secondary, emoji="\U0001f4e2")
    async def channels_button(self, interaction: discord.Interaction, button: ui.Button):
        config = await get_guild_config(interaction.guild.id)
        guild = interaction.guild
        uid = interaction.user.id

        ignore_view = _make_channel_view(uid, guild, config, 'ignore_channels', 'Ignore channels',
                                         "Select channels to ignore...")
        await interaction.response.send_message(
            "**Ignore channels** \u2014 Bot commands will be disabled in these channels",
            view=ignore_view, ephemeral=True
        )

        notif_view = _make_channel_view(uid, guild, config, 'notification_channel', 'Notification channel',
                                        "Select notification channel...", max_values=1)
        await interaction.followup.send(
            "**Notification channel** \u2014 Server events (player joins, restarts, etc.) will be posted here",
            view=notif_view, ephemeral=True
        )

    @ui.button(label="Show config", style=discord.ButtonStyle.success, emoji="\U0001f4cb")
    async def show_button(self, interaction: discord.Interaction, button: ui.Button):
        config = await get_guild_config(interaction.guild.id)
        if config is None:
            await interaction.response.send_message("No configuration found yet.", ephemeral=True)
            return
        role_keys = ('admin_roles', 'moderator_roles', 'whitelist_roles')
        channel_keys = ('ignore_channels', 'notification_channel')
        lines = [f"Configuration for **{interaction.guild.name}**:\n"]
        for key in CONFIG_KEYS:
            val = config.get(key)
            if key == 'rcon_pass':
                val = '********' if val else 'Not set'
            elif key in role_keys and val:
                role_ids = [int(rid) for rid in val.split(',') if rid.strip()]
                role_names = []
                for rid in role_ids:
                    role = interaction.guild.get_role(rid)
                    role_names.append(role.name if role else f'Unknown ({rid})')
                val = ', '.join(role_names)
            elif key in channel_keys and val:
                channel_ids = _parse_channel_ids(val)
                channel_names = []
                for cid in channel_ids:
                    channel = interaction.guild.get_channel(cid)
                    channel_names.append(f'#{channel.name}' if channel else f'Unknown ({cid})')
                val = ', '.join(channel_names)
            elif val is None:
                val = 'Not set'
            lines.append(f"**{key}**: `{val}`")
        await interaction.response.send_message('\n'.join(lines), ephemeral=True)

    @ui.button(label="Reset", style=discord.ButtonStyle.danger, emoji="\U0001f5d1")
    async def reset_button(self, interaction: discord.Interaction, button: ui.Button):
        config = await get_guild_config(interaction.guild.id)
        if config is None:
            await interaction.response.send_message("No configuration to reset.", ephemeral=True)
            return
        await delete_guild_config(interaction.guild.id)
        await interaction.response.send_message("Configuration has been reset.", ephemeral=True)


class ConfigCommands(commands.Cog):
    """Guild configuration commands for server owners"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pzsetup", description="Open the bot configuration panel")
    async def pzsetup(self, interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message(
                t(interaction.locale, "dm_not_allowed"), ephemeral=True
            )
            return
        if not interaction.user.guild_permissions.administrator and interaction.guild.owner_id != interaction.user.id:
            await interaction.response.send_message(
                t(interaction.locale, "need_admin"), ephemeral=True
            )
            return
        view = SetupView(author_id=interaction.user.id, locale=interaction.locale)
        await interaction.response.send_message(
            t(interaction.locale, "setup_title"), view=view
        )
        view.message = await interaction.original_response()


async def setup(bot):
    await bot.add_cog(ConfigCommands(bot=bot))
