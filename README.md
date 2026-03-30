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

## Requirements

- Python 3.10+
- A Project Zomboid dedicated server with RCON enabled

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

Dependencies: `discord.py`, `python-dotenv`, `rcon`, `aiosqlite`

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

### User Commands
| Command | Description |
|---------|-------------|
| `/pzplayers` | Show current active players on the server |
| `/pzgetoption` | Get the value of a server option |
| `/pzrequestaccess` | Request access to the PZ server |
| `/whatareyou` | Bot info |
