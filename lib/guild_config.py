import aiosqlite
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'guild_config.db')

_cache = {}

CONFIG_KEYS = [
    'rcon_host', 'rcon_port', 'rcon_pass',
    'server_address', 'admin_roles', 'moderator_roles',
    'whitelist_roles', 'ignore_channels', 'notification_channel'
]

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS guild_config (
                guild_id        INTEGER PRIMARY KEY,
                rcon_host       TEXT DEFAULT '127.0.0.1',
                rcon_port       INTEGER DEFAULT 27015,
                rcon_pass       TEXT,
                server_address  TEXT,
                admin_roles     TEXT,
                moderator_roles TEXT,
                whitelist_roles TEXT,
                ignore_channels TEXT,
                notification_channel TEXT
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pz_users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id        INTEGER NOT NULL,
                discord_user_id INTEGER NOT NULL,
                pz_username     TEXT NOT NULL,
                created_at      TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, discord_user_id)
            )
        ''')
        await db.commit()
    _cache.clear()


async def get_guild_config(guild_id):
    if guild_id in _cache:
        return _cache[guild_id]

    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM guild_config WHERE guild_id = ?', (guild_id,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        config = dict(row)
        _cache[guild_id] = config
        return config


async def set_guild_config(guild_id, **kwargs):
    existing = await get_guild_config(guild_id)

    if existing is None:
        columns = ['guild_id'] + list(kwargs.keys())
        placeholders = ', '.join(['?'] * len(columns))
        values = [guild_id] + list(kwargs.values())
        sql = f"INSERT INTO guild_config ({', '.join(columns)}) VALUES ({placeholders})"
    else:
        set_clause = ', '.join(f"{k} = ?" for k in kwargs)
        values = list(kwargs.values()) + [guild_id]
        sql = f"UPDATE guild_config SET {set_clause} WHERE guild_id = ?"

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(sql, values)
        await db.commit()

    _cache.pop(guild_id, None)


async def delete_guild_config(guild_id):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('DELETE FROM guild_config WHERE guild_id = ?', (guild_id,))
        await db.commit()
    _cache.pop(guild_id, None)


async def get_pz_user(guild_id, discord_user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM pz_users WHERE guild_id = ? AND discord_user_id = ?',
            (guild_id, discord_user_id)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_all_pz_users(guild_id):
    """Retorna lista de dicts con todos los usuarios PZ del guild."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            'SELECT * FROM pz_users WHERE guild_id = ? ORDER BY created_at',
            (guild_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]


async def add_pz_user(guild_id, discord_user_id, pz_username):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            'INSERT INTO pz_users (guild_id, discord_user_id, pz_username) VALUES (?, ?, ?)',
            (guild_id, discord_user_id, pz_username)
        )
        await db.commit()
