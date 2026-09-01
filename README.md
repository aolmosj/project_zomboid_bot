# Project Zomboid Discord Bot
Discord bot for managing your Project Zomboid server with multi-guild support and interactive configuration.

## Features

- **Slash commands** — all commands use Discord slash commands (`/pzsetup`, `/pzkick`, etc.) with autocomplete.
- **Internationalization (i18n)** — bot responses are available in English and Spanish, automatically matching each user's Discord locale.
- **Multi-guild support** — each Discord server stores its own configuration (RCON, roles, channels) in a local SQLite database.
- **Interactive setup** — `/pzsetup` launches a panel with buttons and dropdown selectors to configure the bot without editing files. The panel auto-deletes after 2 minutes of inactivity.
- **Role-based commands** — admin, moderator and user commands are gated by configurable Discord roles.
- **User self-service** — players with the correct role can request PZ server access via `/pzrequestaccess`. The bot creates their account and DMs them the credentials.
- **RCON integration** — commands are sent to the PZ server using the Source RCON protocol via the `rcon` Python library (no external binary needed).
- **Server restarts** — `/pzrestart` warns players in game, saves the world and restarts the server through the Nitrado API, which RCON cannot do on its own.

## Requirements

- Python 3.10+
- A Project Zomboid dedicated server with RCON enabled
- A Nitrado API token and service ID — only for `/pzrestart`; every other command works without them

## Getting started

```bash
# Clone the repository
git clone https://github.com/aolmosj/project_zomboid_bot.git
cd project_zomboid_bot

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Linux / macOS
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt
```

Dependencies: `discord.py`, `python-dotenv`, `rcon`, `aiosqlite`, `aiohttp`

## Configuration

1. Create a `.env` file from the template:
   ```bash
   cp .env.sample .env
   ```
2. Add your Discord bot token to `.env`:
   ```
   DISCORD_TOKEN=YourTokenHere
   ```
3. Start the bot:
   ```bash
   source .venv/bin/activate
   python pzbot.py
   ```
4. In your Discord server, run `/pzsetup` to open the interactive configuration panel where you can set RCON connection, roles and channels.

To enable `/pzrestart`, use the same panel: the **Nitrado** button stores the API token and
service ID, and the **Roles** button sets which roles may restart the server. The token is
stored per guild and is masked in *Show config*. Create the token at
[server.nitrado.net](https://server.nitrado.net) under the developer/API section; it needs
permission to manage the gameserver, not just read it.

## Deployment

Run the bot under systemd rather than a terminal multiplexer: it comes back after a
crash or a reboot, and its output goes somewhere that outlives a scrollback buffer.

### Install

`PZ-Command-Bot.service` ships the unit. It hardcodes the paths of one particular
host, so **edit `WorkingDirectory` and `ExecStart` to match your checkout before
copying it**, then:

```bash
sudo cp PZ-Command-Bot.service /etc/systemd/system/pzbot.service
sudo systemctl daemon-reload
sudo systemctl enable --now pzbot
```

`ExecStart` must point at the **virtualenv's** interpreter, not the system one — the
bot's dependencies are not installed system-wide. `-u` keeps output unbuffered so log
lines reach the journal as they happen.

If the bot was previously started by hand (a `screen` or `tmux` session, a bare
`python pzbot.py`), **stop it first**. Two instances answer the same slash command
twice and both act on it.

### Verify

```bash
systemctl status pzbot --no-pager
journalctl -u pzbot -n 30 --no-pager
```

A healthy start logs `logging in using static token` and then
`Shard ID None has connected to Gateway`. To confirm there is exactly one instance —
`pgrep` matches its own command line, so ask systemd instead:

```bash
systemd-cgls -u pzbot.service --no-pager
```

### Logs

Everything goes to the journal, which handles rotation and retention:

```bash
journalctl -u pzbot -f            # follow
journalctl -u pzbot --since today
```

The bot passes `root_logger=True` to `run()`, so discord.py's own messages, anything
logged by the cogs, and unhandled exceptions raised inside background tasks all land
there. That last one matters: a restart countdown runs detached from the interaction
that started it, and the only trace of one dying is asyncio's "Task exception was
never retrieved".

### Update

```bash
cd /path/to/checkout && git pull
sudo systemctl restart pzbot
```

Re-copy the unit and `daemon-reload` only when `PZ-Command-Bot.service` itself
changed. `guild_config.db` lives in `WorkingDirectory` and is never touched by a pull;
back it up separately, since it holds the RCON password, the Nitrado token and the
registered users, and is gitignored.

### Troubleshooting

`Failed to determine user credentials: No such process` — the unit sets `User=` to an
account that does not exist. systemd reports the NSS lookup failure with that errno,
so read it as "no such user". The message is logged as `(python3)` rather than the
unit's identifier because the process is forked but has not exec'd yet.

`The unit files have no installation config` — the unit is missing its `[Install]`
section, so it cannot be enabled. Usually means an older copy of the file was
installed than the one you edited.

`ModuleNotFoundError` on start — `ExecStart` is using the system interpreter instead
of the venv, or the venv is missing dependencies: `.venv/bin/pip install -r
requirements.txt`.

## Commands

All commands are Discord slash commands — type `/` in any channel to see the available options.

### Configuration
| Command | Description |
|---------|-------------|
| `/pzsetup` | Open the interactive bot configuration panel |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/pzsetaccess` | Set the access level of a user |
| `/pzusers` | List all registered PZ users |

### Moderator Commands
| Command | Description |
|---------|-------------|
| `/pzsteamban` | Steam ban a user |
| `/pzsteamunban` | Steam unban a user |
| `/pzkick` | Kick a user from the server |
| `/pzwhitelist` | Whitelist a user |
| `/pzunwhitelist` | Remove a user from the whitelist |
| `/pzwhitelistall` | Whitelist all active users |
| `/pzadduser` | Add a user with a password |
| `/pzadditem` | Add an item to a user's inventory |
| `/pzteleport` | Teleport a user to another user |
| `/pzservermsg` | Broadcast a server message |
| `/pzsave` | Save the current world |

### Server Control
Gated by the **restart roles** configured in `/pzsetup`, plus guild administrators.

| Command | Description |
|---------|-------------|
| `/pzrestart` | Restart the server via Nitrado. Requires a **reason**, recorded in the notification channel and in Nitrado's activity log. Warns players over RCON and saves the world first; the delay defaults to 1 minute, and the `Now` option skips both the warning and the save |

### User Commands
| Command | Description |
|---------|-------------|
| `/pzplayers` | Show current active players on the server |
| `/pzgetoption` | Get the value of a server option |
| `/pzrequestaccess` | Request access to the PZ server |
| `/whatareyou` | Bot info |
