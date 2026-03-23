# Project Zomboid Discord Bot
Discord bot for managing your Project Zomboid server with multi-guild support and interactive configuration.

## Features

- **Multi-guild support** — each Discord server stores its own configuration (RCON, roles, channels) in a local SQLite database.
- **Interactive setup** — `!pzsetup` launches a panel with buttons and dropdown selectors to configure the bot without editing files.
- **Role-based commands** — admin, moderator and user commands are gated by configurable Discord roles.
- **User self-service** — players with the correct role can request PZ server access via `!pzrequestaccess`. The bot creates their account and DMs them the credentials.
- **RCON integration** — commands are sent to the PZ server using the Source RCON protocol via the `rcon` Python library (no external binary needed).

## Requirements

- Python 3.8+
- A Project Zomboid dedicated server with RCON enabled

Install dependencies:

```
pip install -r requirements.txt
```

Dependencies: `discord.py`, `python-dotenv`, `rcon`, `aiosqlite`, `file-read-backwards`, `watchgod`

## Setup

1. Create a `.env` file from the template:
   ```
   cp .env.sample .env
   ```
2. Add your Discord bot token to `.env`:
   ```
   DISCORD_TOKEN=YourTokenHere
   ```
3. Start the bot:
   ```
   python pzbot.py
   ```
4. In your Discord server, run `!pzsetup` to open the interactive configuration panel where you can set RCON connection, roles and channels.

## Commands

### Configuration
| Command | Description |
|---------|-------------|
| `!pzsetup` | Open the interactive bot configuration panel |

### Admin Commands
| Command | Description |
|---------|-------------|
| `!pzsetaccess` | Set the access level of a user |
| `!pzusers` | Show all registered PZ users in the server |

### Moderator Commands
| Command | Description |
|---------|-------------|
| `!pzsteamban` | Steam ban a user |
| `!pzsteamunban` | Steam unban a user |
| `!pzkick` | Kick a user |
| `!pzwhitelist` | Whitelist a user |
| `!pzunwhitelist` | Remove a whitelisted user |
| `!pzwhitelistall` | Whitelist all active users |
| `!pzadduser` | Add a user with password |
| `!pzadditem` | Add an item to a user's inventory |
| `!pzteleport` | Teleport a user to another user |
| `!pzservermsg` | Broadcast a server message |
| `!pzsave` | Save the current world |

### User Commands
| Command | Description |
|---------|-------------|
| `!pzplayers` | Show current active players |
| `!pzgetoption` | Get the value of a server option (fuzzy lookup) |
| `!pzrequestaccess` | Request access to the PZ server |
| `!whatareyou` | Bot info |