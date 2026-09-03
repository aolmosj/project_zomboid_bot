"""Fixtures shared by the suite.

Nothing under lib/ imports discord, so most of it needs no test doubles at all.
The cogs do, and the fakes here are the minimum those need: enough of an
interaction, guild and channel for the permission gates and _announce.
"""
import asyncio
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import discord  # noqa: E402

import lib.guild_config as guild_config  # noqa: E402

LOCALE = discord.Locale.spain_spanish
GUILD_ID = 42
CHANNEL_ID = 555


@pytest.fixture
def db(tmp_path, monkeypatch):
    """Point the database at a scratch file and clear the module-level cache."""
    monkeypatch.setattr(guild_config, 'DB_PATH', str(tmp_path / 'guild_config.db'))
    monkeypatch.setattr(guild_config, '_cache', {})
    return guild_config


class FakeChannel:
    def __init__(self):
        self.sent = []
        self.fail = False

    async def send(self, text):
        if self.fail:
            raise discord.HTTPException(
                types.SimpleNamespace(status=500, reason='Server Error'), 'nope')
        self.sent.append(text)


class FakeFollowup:
    def __init__(self):
        self.sent = []
        self.fail = False

    async def send(self, text, **kwargs):
        if self.fail:
            # The 401 that killed a countdown in production: an interaction token
            # that is no longer accepted by the time the background task reports.
            raise discord.HTTPException(
                types.SimpleNamespace(status=401, reason='Unauthorized'),
                {'code': 50027, 'message': 'Invalid Webhook Token'})
        self.sent.append(text)


class FakeGuild:
    def __init__(self, channel):
        self.id = GUILD_ID
        self.owner_id = 1
        self._channel = channel

    def get_channel(self, cid):
        return self._channel if cid == CHANNEL_ID else None


class FakeInteraction:
    def __init__(self, channel, followup, user_name='Juan'):
        self.locale = LOCALE
        self.guild = FakeGuild(channel)
        self.followup = followup
        self.user = types.SimpleNamespace(display_name=user_name, id=7)


@pytest.fixture
def channel():
    return FakeChannel()


@pytest.fixture
def followup():
    return FakeFollowup()


@pytest.fixture
def interaction(channel, followup):
    return FakeInteraction(channel, followup)


@pytest.fixture
def no_sleep(monkeypatch):
    """Collapse the countdown without breaking the loop's scheduling."""
    real = asyncio.sleep
    slept = []

    async def fast(delay, *args, **kwargs):
        slept.append(delay)
        await real(0)

    monkeypatch.setattr(asyncio, 'sleep', fast)
    return slept
