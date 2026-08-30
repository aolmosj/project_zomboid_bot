MESSAGES = {
    # Common errors
    "not_configured": {
        "en": "This server hasn't been configured yet. An admin needs to run `/pzsetup`.",
        "es": "Este servidor aún no está configurado. Un admin debe ejecutar `/pzsetup`.",
    },
    "rcon_not_configured": {
        "en": "RCON is not configured yet. An admin needs to configure it via `/pzsetup`.",
        "es": "RCON aún no está configurado. Un admin debe configurarlo con `/pzsetup`.",
    },
    "rcon_error": {
        "en": "Could not connect to the game server: {error}",
        "es": "No se pudo conectar al servidor de juego: {error}",
    },
    "no_permission": {
        "en": "You don't have permission to use this command.",
        "es": "No tienes permisos para usar este comando.",
    },
    "channel_blocked": {
        "en": "Commands are not allowed in this channel.",
        "es": "No se permiten comandos en este canal.",
    },
    "dm_not_allowed": {
        "en": "Commands can only be used in a server, not in DMs.",
        "es": "Los comandos solo se pueden usar en un servidor, no en DMs.",
    },

    # Users
    "players_title": {
        "en": "Current players in game:\n{players}",
        "es": "Jugadores actuales en partida:\n{players}",
    },
    "option_results": {
        "en": "Server options:\n{options}",
        "es": "Opciones del servidor:\n{options}",
    },
    "whatareyou": {
        "en": "I'm a bot for managing Project Zomboid servers, written in Python 3.\nRead more here: https://github.com/aolmosj/project_zomboid_bot",
        "es": "Soy un bot para gestionar servidores de Project Zomboid, escrito en Python 3.\nMás información aquí: https://github.com/aolmosj/project_zomboid_bot",
    },
    "request_access_prompt": {
        "en": "Press the button to create your Project Zomboid user:",
        "es": "Pulsa el botón para crear tu usuario de Project Zomboid:",
    },
    "create_user_button": {
        "en": "Create user",
        "es": "Crear usuario",
    },
    "modal_title": {
        "en": "Create Project Zomboid user",
        "es": "Crear usuario de Project Zomboid",
    },
    "modal_username_label": {
        "en": "Username",
        "es": "Nombre de usuario",
    },
    "modal_username_placeholder": {
        "en": "Your username for the server",
        "es": "Tu nombre de usuario para el servidor",
    },
    "modal_password_label": {
        "en": "Password",
        "es": "Contraseña",
    },
    "modal_password_placeholder": {
        "en": "Your password for the server",
        "es": "Tu contraseña para el servidor",
    },
    "no_whitelist_permission": {
        "en": "You don't have permission to create a user. Wait for an admin to authorize you.",
        "es": "No tienes permisos para crear un usuario. Espera a que un admin te autorice.",
    },
    "already_has_account": {
        "en": "You already have an account: **{username}**",
        "es": "Ya tienes una cuenta creada: **{username}**",
    },
    "user_exists_on_server": {
        "en": "That username already exists on the server, try a different name.",
        "es": "El usuario ya existe en el servidor, prueba otro nombre.",
    },
    "user_created_public": {
        "en": "**{display_name}** has created the user **{username}**",
        "es": "**{display_name}** ha creado el usuario **{username}**",
    },
    "user_created_private": {
        "en": "User created successfully.\n**Username:** {username}\n**Password:** {password}\n**Server address:** {address}",
        "es": "Usuario creado correctamente.\n**Usuario:** {username}\n**Contraseña:** {password}\n**Dirección del servidor:** {address}",
    },
    "address_not_set": {
        "en": "Not set",
        "es": "No configurada",
    },
    "unexpected_response": {
        "en": "Unexpected server response: {response}",
        "es": "Respuesta inesperada del servidor: {response}",
    },

    # Admins
    "pz_users_title": {
        "en": "Project Zomboid Users",
        "es": "Usuarios de Project Zomboid",
    },
    "no_registered_users": {
        "en": "No registered users",
        "es": "No hay usuarios registrados",
    },
    "invalid_access_level": {
        "en": "Invalid access level `{level}`. Must be one of: {levels}",
        "es": "Nivel de acceso inválido `{level}`. Debe ser uno de: {levels}",
    },

    # Config
    "setup_title": {
        "en": "**PZ Bot Configuration**\nSelect what you want to configure:",
        "es": "**Configuración del Bot PZ**\nSelecciona qué quieres configurar:",
    },
    "need_admin": {
        "en": "You need administrator permissions to use this command.",
        "es": "Necesitas permisos de administrador para usar este comando.",
    },
    "btn_channels": {
        "en": "Channels",
        "es": "Canales",
    },
    "btn_show_config": {
        "en": "Show config",
        "es": "Mostrar config",
    },
    "btn_reset": {
        "en": "Reset",
        "es": "Restablecer",
    },
    "only_invoker": {
        "en": "Only the person who ran the command can use these buttons.",
        "es": "Solo la persona que ejecutó el comando puede usar estos botones.",
    },

    # RCON modal
    "rcon_modal_title": {
        "en": "RCON Configuration",
        "es": "Configuración RCON",
    },
    "rcon_password_placeholder": {
        "en": "Your RCON password",
        "es": "Tu contraseña RCON",
    },
    "rcon_server_address_label": {
        "en": "Server address (shown to players)",
        "es": "Dirección del servidor (para jugadores)",
    },
    "rcon_invalid_port": {
        "en": "Invalid port number.",
        "es": "Número de puerto inválido.",
    },
    "rcon_configured": {
        "en": "RCON configured successfully.",
        "es": "RCON configurado correctamente.",
    },

    # Roles button
    "admin_roles_name": {
        "en": "Admin roles",
        "es": "Roles de admin",
    },
    "admin_roles_placeholder": {
        "en": "Select admin roles...",
        "es": "Selecciona roles de admin...",
    },
    "admin_roles_desc": {
        "en": "**Admin roles** \u2014 Full access: can configure the bot, manage the server, and use all commands",
        "es": "**Roles de admin** \u2014 Acceso total: pueden configurar el bot, gestionar el servidor y usar todos los comandos",
    },
    "mod_roles_name": {
        "en": "Moderator roles",
        "es": "Roles de moderador",
    },
    "mod_roles_placeholder": {
        "en": "Select moderator roles...",
        "es": "Selecciona roles de moderador...",
    },
    "mod_roles_desc": {
        "en": "**Moderator roles** \u2014 Can kick/ban players, manage whitelist, and use moderation commands",
        "es": "**Roles de moderador** \u2014 Pueden expulsar/banear jugadores, gestionar la whitelist y usar comandos de moderación",
    },
    "wl_roles_name": {
        "en": "Whitelist roles",
        "es": "Roles de whitelist",
    },
    "wl_roles_placeholder": {
        "en": "Select whitelist roles...",
        "es": "Selecciona roles de whitelist...",
    },
    "wl_roles_desc": {
        "en": "**Whitelist roles** \u2014 Users with these roles are automatically whitelisted on the server",
        "es": "**Roles de whitelist** \u2014 Los usuarios con estos roles se añaden automáticamente a la whitelist del servidor",
    },

    # Channels button
    "ignore_channels_name": {
        "en": "Ignore channels",
        "es": "Canales ignorados",
    },
    "ignore_channels_placeholder": {
        "en": "Select channels to ignore...",
        "es": "Selecciona canales a ignorar...",
    },
    "ignore_channels_desc": {
        "en": "**Ignore channels** \u2014 Bot commands will be disabled in these channels",
        "es": "**Canales ignorados** \u2014 Los comandos del bot estarán desactivados en estos canales",
    },
    "notif_channel_name": {
        "en": "Notification channel",
        "es": "Canal de notificaciones",
    },
    "notif_channel_placeholder": {
        "en": "Select notification channel...",
        "es": "Selecciona canal de notificaciones...",
    },
    "notif_channel_desc": {
        "en": "**Notification channel** \u2014 Server events (player joins, restarts, etc.) will be posted here",
        "es": "**Canal de notificaciones** \u2014 Los eventos del servidor (conexiones, reinicios, etc.) se publicarán aquí",
    },

    # Select callbacks
    "select_set_to": {
        "en": "{name} set to: {values}",
        "es": "{name} establecido a: {values}",
    },
    "select_cleared": {
        "en": "{name} cleared.",
        "es": "{name} limpiado.",
    },

    # Show config
    "no_config_found": {
        "en": "No configuration found yet.",
        "es": "Aún no hay configuración.",
    },
    "config_header": {
        "en": "Configuration for **{guild}**:\n",
        "es": "Configuración de **{guild}**:\n",
    },
    "not_set": {
        "en": "Not set",
        "es": "No configurado",
    },

    # Reset
    "no_config_to_reset": {
        "en": "No configuration to reset.",
        "es": "No hay configuración que restablecer.",
    },
    "config_reset": {
        "en": "Configuration has been reset.",
        "es": "La configuración se ha restablecido.",
    },
    "servermsg_sent": {
        "en": "\U0001f4e2 **Broadcast to the server:**\n> {message}\n*{reply}*",
        "es": "\U0001f4e2 **Enviado al servidor:**\n> {message}\n*{reply}*",
    },

    # Nitrado / restart
    "btn_nitrado": {
        "en": "Nitrado",
        "es": "Nitrado",
    },
    "nitrado_modal_title": {
        "en": "Nitrado API settings",
        "es": "Ajustes de la API de Nitrado",
    },
    "nitrado_token_label": {
        "en": "Nitrado token",
        "es": "Token de Nitrado",
    },
    "nitrado_token_placeholder": {
        "en": "Long-lived token from the Nitrado developer portal",
        "es": "Token de larga duraci\u00f3n del portal de Nitrado",
    },
    "nitrado_service_id_label": {
        "en": "Service ID",
        "es": "ID de servicio",
    },
    "nitrado_service_id_placeholder": {
        "en": "e.g. 1234567",
        "es": "ej. 1234567",
    },
    "nitrado_configured": {
        "en": "Nitrado settings saved.",
        "es": "Ajustes de Nitrado guardados.",
    },
    "nitrado_invalid_service_id": {
        "en": "The service ID must be a number.",
        "es": "El ID de servicio debe ser un n\u00famero.",
    },
    "nitrado_not_configured": {
        "en": "Nitrado is not configured. Run `/pzsetup` and use the Nitrado button.",
        "es": "Nitrado no est\u00e1 configurado. Usa `/pzsetup` y el bot\u00f3n Nitrado.",
    },
    "nitrado_error": {
        "en": "Nitrado API error: {error}",
        "es": "Error de la API de Nitrado: {error}",
    },
    "restart_confirm_now": {
        "en": "\u26a0\ufe0f This restarts the server **right now**, with no warning to players and **without saving**. Continue?",
        "es": "\u26a0\ufe0f Esto reinicia el servidor **ahora mismo**, sin avisar a los jugadores y **sin guardar**. \u00bfContinuar?",
    },
    "restart_confirm_delay": {
        "en": "\u26a0\ufe0f Players will be warned and the server will restart in **{delay} min**. Continue?",
        "es": "\u26a0\ufe0f Se avisar\u00e1 a los jugadores y el servidor se reiniciar\u00e1 en **{delay} min**. \u00bfContinuar?",
    },
    "btn_confirm": {
        "en": "Confirm",
        "es": "Confirmar",
    },
    "btn_cancel": {
        "en": "Cancel",
        "es": "Cancelar",
    },
    "restart_confirmed": {
        "en": "Restart confirmed.",
        "es": "Reinicio confirmado.",
    },
    "restart_cancelled": {
        "en": "Restart cancelled.",
        "es": "Reinicio cancelado.",
    },
    "restart_scheduled": {
        "en": "Restart scheduled in {delay} min by {user}. Players are being warned.",
        "es": "Reinicio programado en {delay} min por {user}. Se est\u00e1 avisando a los jugadores.",
    },
    "restart_warning": {
        "en": "Server restarting in {minutes} minute(s). Please find a safe spot.",
        "es": "El servidor se reiniciar\u00e1 en {minutes} minuto(s). Busca un lugar seguro.",
    },
    "restart_no_rcon": {
        "en": "RCON is not configured, so players cannot be warned and the world cannot be saved. Configure it with `/pzsetup`, or pick `Now` to restart without either.",
        "es": "RCON no est\u00e1 configurado, as\u00ed que no se puede avisar a los jugadores ni guardar la partida. Config\u00faralo con `/pzsetup`, o elige `Now` para reiniciar sin ninguna de las dos cosas.",
    },
    "restart_aborted": {
        "en": "Restart aborted: the warning could not be sent over RCON.",
        "es": "Reinicio abortado: no se pudo enviar el aviso por RCON.",
    },
    "restart_requested": {
        "en": "\U0001f504 Restart requested by {user}. The server will be back shortly.",
        "es": "\U0001f504 Reinicio solicitado por {user}. El servidor volver\u00e1 en breve.",
    },
    "restart_failed": {
        "en": "The restart could not be requested: {error}",
        "es": "No se pudo solicitar el reinicio: {error}",
    },
    "restart_roles_name": {
        "en": "Restart roles",
        "es": "Roles de reinicio",
    },
    "restart_roles_placeholder": {
        "en": "Select roles allowed to restart...",
        "es": "Selecciona roles que pueden reiniciar...",
    },
    "restart_roles_desc": {
        "en": "**Restart roles** \u2014 These roles can run `/pzrestart` (guild admins always can)",
        "es": "**Roles de reinicio** \u2014 Estos roles pueden usar `/pzrestart` (los administradores siempre pueden)",
    },
}


def get_lang(locale):
    lang = str(locale).split("-")[0].lower()
    if lang in ("es",):
        return lang
    return "en"


def t(locale, key, **kwargs):
    msg = MESSAGES.get(key, {})
    lang = get_lang(locale)
    text = msg.get(lang, msg.get("en", key))
    if kwargs:
        text = text.format(**kwargs)
    return text
