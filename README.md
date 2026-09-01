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

- A Discord application with a bot token, and the bot invited to your guild
- A Project Zomboid dedicated server with RCON enabled
- A Debian/Ubuntu host with systemd, to run `deploy/bootstrap.sh`
- A Nitrado API token and service ID — only for `/pzrestart`; every other command
  works without them
- Python 3.10+ only for local development; a deployment builds its own virtualenv

## Creating the Discord application

1. Open the [Developer Portal](https://discord.com/developers/applications) and create
   a **New Application**.
2. Under **Bot**, press **Reset Token** and copy it. That value is `DISCORD_TOKEN`, and
   it is shown only once.
3. Under **Bot → Privileged Gateway Intents**, leave **all three off**. The bot
   registers no gateway event handlers and works entirely through slash commands, so
   it needs none of them. Enabling them would only widen what a leaked token reaches.
4. Under **OAuth2 → URL Generator**, tick the `bot` and `applications.commands` scopes,
   then the **View Channels** and **Send Messages** permissions. Nothing else: the bot
   never edits or deletes anyone else's messages, and deleting its own needs no
   permission. That is the URL you open to invite it.

The ready-made equivalent, with your application's ID:

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_APP_ID&permissions=3072&scope=bot%20applications.commands
```

Guild-wide permissions are not the whole story: a channel can override them. If the bot
is silent in the notification channel while working everywhere else, check that channel's
own permissions for the bot's role.

## Deployment

Run the bot under systemd rather than a terminal multiplexer: it comes back after a
crash or a reboot, and its output goes somewhere that outlives a scrollback buffer.

The layout keeps the three things apart that a single checkout used to hold at once —
code, secrets and state — so that deploying can never put the database at risk:

| | Where | Owner |
|---|---|---|
| Code | `/opt/pzbot` (fixed location) | `root`, read-only to the service |
| Secrets | `/etc/pzbot/env` | `root:pzbot`, mode 640 |
| State | `/var/lib/pzbot/guild_config.db` | `pzbot` |
| Service account | `pzbot`, system user, no shell | |

`/opt/pzbot` is a convention, not one machine's path. That is what lets
`deploy/pzbot.service` carry absolute paths without anyone having to edit a tracked
file — which would otherwise conflict on the next pull.

### First install

```bash
sudo git clone https://github.com/aolmosj/project_zomboid_bot.git /opt/pzbot
sudo /opt/pzbot/deploy/bootstrap.sh          # creates the user, venv, dirs and unit
sudo vi /etc/pzbot/env                       # put the real DISCORD_TOKEN in
sudo /opt/pzbot/deploy/bootstrap.sh          # re-run: it is idempotent
```

The first run stops at the placeholder token on purpose. A token that silently
"works" is worse than a service that refuses to start.

### Update

```bash
cd /opt/pzbot && sudo git pull
sudo systemctl restart pzbot
```

Re-run `bootstrap.sh` instead when `requirements.txt` or `deploy/pzbot.service`
changed; it is idempotent and ends by restarting the service.

### Verify

```bash
systemctl status pzbot --no-pager
journalctl -u pzbot -n 30 --no-pager
systemd-cgls -u pzbot.service --no-pager     # exactly one process
```

A healthy start logs `logging in using static token` and then `Shard ID None has
connected to Gateway`. Use `systemd-cgls` rather than `pgrep` to count instances:
`pgrep -f pzbot` matches its own command line.

### Logs

Everything goes to the journal, which handles rotation and retention:

```bash
journalctl -u pzbot -f
journalctl -u pzbot --since today
```

The bot passes `root_logger=True` to `run()`, so discord.py's own messages, anything
logged by the cogs, and unhandled exceptions raised inside background tasks all land
there. That last one matters: a restart countdown runs detached from the interaction
that started it, and the only trace of one dying is asyncio's "Task exception was
never retrieved".

### Troubleshooting

`Failed to determine user credentials: No such process` — the unit sets `User=` to an
account that does not exist. systemd reports the NSS lookup failure with that errno,
so read it as "no such user". It is logged as `(python3)` rather than the unit's
identifier because the process is forked but has not exec'd yet.

`The unit files have no installation config` — the unit is missing its `[Install]`
section, so it cannot be enabled. Usually means an older copy of the file is
installed than the one you edited.

`ModuleNotFoundError` on start — the venv is missing dependencies, or was moved
rather than rebuilt: a venv bakes in absolute paths. Delete `/opt/pzbot/.venv` and
re-run `bootstrap.sh`.

`Read-only file system` writing anything under `/opt/pzbot` — expected.
`ProtectSystem=strict` keeps the service from rewriting its own code. Anything the
bot needs to write belongs in `/var/lib/pzbot`.

## Setting up the bot in Discord

Deploying gets the bot online; everything else is configured from Discord and stored
per guild, so one instance can serve several servers with different settings.

Run `/pzsetup` as a guild administrator. The panel is ephemeral — only you see it — and
deletes itself after two minutes of inactivity.

| Button | What it stores |
|---|---|
| **RCON** | Host, port, password, and the public server address shown to players |
| **Nitrado** | API token and service ID, required by `/pzrestart` |
| **Roles** | Which roles count as admin, moderator, whitelist and restart |
| **Channels** | Channels where the bot stays quiet, and the one it posts events to |
| **Show config** | The current values, with the RCON password and Nitrado token masked |
| **Reset** | Discards this guild's configuration |

Set the **notification channel**: restarts announce their progress there, and it is
where a countdown reports a failure. Without it those messages fall back to the
interaction that started them, which expires.

For the Nitrado token, go to [server.nitrado.net](https://server.nitrado.net) and find
the developer/API section. The token needs permission to **manage** the gameserver, not
just read it — a read-only token passes every status check and then fails the restart
with a 403.

## Commands

All commands are Discord slash commands — type `/` in any channel to see the available options.

### Setup
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

## Development

For running the bot locally against a test guild. Production does not use this path:
`deploy/bootstrap.sh` builds its own virtualenv and reads its token from
`/etc/pzbot/env`.

```bash
git clone https://github.com/aolmosj/project_zomboid_bot.git
cd project_zomboid_bot
python3 -m venv .venv
source .venv/bin/activate          # .venv\Scripts\activate on Windows
pip install -r requirements.txt

cp .env.sample .env                # then put your DISCORD_TOKEN in it
python pzbot.py
```

`.env` is read by python-dotenv and is development-only. Under systemd the token comes
from the environment instead, and `load_dotenv()` does not override it.

The database defaults to `guild_config.db` next to the checkout, and `PZBOT_DB`
overrides that — which is how a deployment keeps its state outside the code. Point it
at a scratch file to avoid touching a real one:

```bash
PZBOT_DB=/tmp/pzbot-dev.db python pzbot.py
```

Schema changes go in `init_db()` in `lib/guild_config.py`, in both the `CREATE TABLE`
and `NEW_COLUMNS`: `CREATE TABLE IF NOT EXISTS` never alters an existing database, so
new columns are added by the idempotent `ALTER TABLE` loop.

There is no test suite. Verification is manual, against a test guild.
