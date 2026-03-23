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
