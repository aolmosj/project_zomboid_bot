"""The two failures that shipped: an unquoted servermsg, and an error message
with an empty cause."""
import asyncio

import pytest
from rcon.exceptions import EmptyResponse, SessionTimeout, WrongPassword

import lib.common as common

CONFIG = {'rcon_host': '1.2.3.4', 'rcon_port': 27015, 'rcon_pass': 'secret'}


@pytest.mark.parametrize('typed, seen', [
    ('hola mundo', 'hola mundo'),
    ('"hola mundo"', 'hola mundo'),          # the Discord field already delimits
    ('  "con espacios"  ', 'con espacios'),
    ('dijo "hola" y se fue', "dijo 'hola' y se fue"),
    ('"hola" y "adios"', "'hola' y 'adios'"),  # not one pair around everything
    ("don't panic", "don't panic"),
])
def test_servermsg_is_quoted_for_pz(typed, seen):
    """PZ answers an unquoted call with its usage help instead of broadcasting."""
    assert common.servermsg_command(typed) == f'servermsg "{seen}"'
    assert common.normalize_servermsg(typed) == seen


@pytest.mark.parametrize('raised, key', [
    (EmptyResponse(), 'rcon_empty_response'),
    (WrongPassword(), 'rcon_wrong_password'),
    (SessionTimeout(), 'rcon_session_timeout'),
    (asyncio.TimeoutError(), 'rcon_timeout'),
    (ConnectionRefusedError(111, 'Connection refused'), 'rcon_unreachable'),
    (ValueError(), 'rcon_error'),
])
async def test_every_rcon_failure_maps_to_a_key(monkeypatch, raised, key):
    async def boom(*args, **kwargs):
        raise raised

    monkeypatch.setattr(common, 'rcon', boom)
    with pytest.raises(common.RconError) as caught:
        await common.run_rcon(CONFIG, 'save')
    assert caught.value.key == key


@pytest.mark.parametrize('raised', [EmptyResponse(), ValueError(), RuntimeError('')])
async def test_no_failure_renders_an_empty_message(monkeypatch, raised):
    """EmptyResponse carries no text and rendered as 'could not connect: '."""
    async def boom(*args, **kwargs):
        raise raised

    monkeypatch.setattr(common, 'rcon', boom)
    with pytest.raises(common.RconError) as caught:
        await common.run_rcon(CONFIG, 'players')
    message = caught.value.localized('es')
    assert message.strip()
    assert not message.rstrip().endswith(':')


async def test_run_rcon_is_time_bounded(monkeypatch):
    """The library's own timeout= covers only the TCP connect."""
    async def never_answers(*args, **kwargs):
        await asyncio.sleep(30)

    monkeypatch.setattr(common, 'rcon', never_answers)
    with pytest.raises(common.RconError) as caught:
        await common.run_rcon(CONFIG, 'save', timeout=0.05)
    assert caught.value.key == 'rcon_timeout'


async def test_deliver_never_raises():
    """A failing report must not replace the failure it was reporting."""
    async def boom():
        raise RuntimeError('401 Invalid Webhook Token')

    assert await common.deliver(boom(), what='test') is False

    async def fine():
        return None

    assert await common.deliver(fine(), what='test') is True
