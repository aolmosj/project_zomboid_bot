"""CREATE TABLE IF NOT EXISTS never alters an existing table, so the ALTER TABLE
loop is the only thing keeping databases written by older versions working."""
import aiosqlite
import pytest

LEGACY_SCHEMA = '''
    CREATE TABLE guild_config (
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
'''


async def columns(path):
    async with aiosqlite.connect(path) as conn:
        cursor = await conn.execute('PRAGMA table_info(guild_config)')
        return {row[1] for row in await cursor.fetchall()}


async def test_creates_the_schema_from_nothing(db):
    await db.init_db()
    assert set(db.CONFIG_KEYS) <= await columns(db.DB_PATH)


async def test_upgrades_a_legacy_database_without_losing_rows(db):
    async with aiosqlite.connect(db.DB_PATH) as conn:
        await conn.execute(LEGACY_SCHEMA)
        await conn.execute(
            "INSERT INTO guild_config (guild_id, rcon_pass) VALUES (42, 'secret')")
        await conn.commit()

    await db.init_db()

    assert {name for name, _ in db.NEW_COLUMNS} <= await columns(db.DB_PATH)
    config = await db.get_guild_config(42)
    assert config['rcon_pass'] == 'secret'
    assert config['nitrado_token'] is None


async def test_migration_is_idempotent(db):
    for _ in range(3):
        await db.init_db()          # a second ALTER TABLE would raise duplicate column
    assert set(db.CONFIG_KEYS) <= await columns(db.DB_PATH)


async def test_roundtrip_and_cache_invalidation(db):
    await db.init_db()
    await db.set_guild_config(42, nitrado_token='t', nitrado_service_id='11772929')
    assert (await db.get_guild_config(42))['nitrado_token'] == 't'

    await db.set_guild_config(42, nitrado_token='other')
    assert (await db.get_guild_config(42))['nitrado_token'] == 'other'

    await db.delete_guild_config(42)
    assert await db.get_guild_config(42) is None


async def test_config_keys_match_the_table(db):
    """CONFIG_KEYS drives the Show config panel; a column missing from it is invisible."""
    await db.init_db()
    present = await columns(db.DB_PATH)
    assert set(db.CONFIG_KEYS) <= present
    assert present - set(db.CONFIG_KEYS) == {'guild_id'}
