"""The failure this suite exists for: a countdown that announced itself and then
said nothing at all — no warning, no abort, no restart."""
import pytest
from rcon.exceptions import EmptyResponse

import cogs.server as server
import lib.common as common
from tests.conftest import CHANNEL_ID

CONFIG = dict(
    rcon_host='1.2.3.4', rcon_port=27015, rcon_pass='secret',
    nitrado_token='t', nitrado_service_id='11772929',
    notification_channel=str(CHANNEL_ID),
)


@pytest.fixture
async def configured(db):
    await db.init_db()
    await db.set_guild_config(42, **CONFIG)
    return db


@pytest.fixture
def nitrado(monkeypatch):
    """Records the restarts requested, so a test can assert none happened."""
    calls = []

    async def restart(token, service_id, message=None):
        calls.append(message)
        return 'ok'

    monkeypatch.setattr(server, 'restart_gameserver', restart)
    return calls


def rcon_that(monkeypatch, behaviour):
    sent = []

    async def fake(command, **kwargs):
        sent.append(command)
        result = behaviour(command)
        if isinstance(result, Exception):
            raise result
        return result

    monkeypatch.setattr(common, 'rcon', fake)
    return sent


async def test_the_failure_that_went_silent(
        monkeypatch, configured, nitrado, interaction, channel, followup, no_sleep):
    """RCON returns an empty packet and the followup 401s, exactly as in production.

    Before the fix this announced the countdown and then nothing: the exception
    raised while reporting replaced the one being reported and escaped into a
    task nobody was watching.
    """
    rcon_that(monkeypatch, lambda cmd: EmptyResponse())
    followup.fail = True

    await server._run_restart(interaction, 1, 'mods nuevos')

    assert len(channel.sent) == 2, channel.sent
    assert 'no se pudo enviar el aviso' in channel.sent[1]
    assert 'no respondió' in channel.sent[1]          # the cause, not just the effect
    assert '`Now`' in channel.sent[1]                 # and the way out
    assert nitrado == []                              # nothing was restarted


async def test_a_failed_save_aborts_the_restart(
        monkeypatch, configured, nitrado, interaction, channel, no_sleep):
    """Restarting on a save that did not happen is how a world loses loaded chunks."""
    rcon_that(monkeypatch, lambda cmd: EmptyResponse() if cmd == 'save' else 'Message sent.')

    await server._run_restart(interaction, 1, 'prueba')

    assert 'no se pudo guardar' in channel.sent[-1]
    assert nitrado == []


async def test_an_unexpected_failure_is_still_announced(
        monkeypatch, configured, interaction, channel, no_sleep):
    """The top-level guard: nothing may escape into an unwatched task."""
    rcon_that(monkeypatch, lambda cmd: 'ok')

    async def boom(*args, **kwargs):
        raise RuntimeError('Nitrado returned nonsense')

    monkeypatch.setattr(server, 'restart_gameserver', boom)

    await server._run_restart(interaction, 1, 'prueba')

    assert 'RuntimeError' in channel.sent[-1]


async def test_the_happy_path_warns_saves_and_restarts(
        monkeypatch, configured, nitrado, interaction, channel, no_sleep):
    sent = rcon_that(monkeypatch, lambda cmd: 'World saved.' if cmd == 'save' else 'Message sent.')

    await server._run_restart(interaction, 5, 'mods nuevos')

    assert sent == ['servermsg "El servidor se reiniciará en 5 minuto(s). Busca un lugar seguro."',
                    'servermsg "El servidor se reiniciará en 1 minuto(s). Busca un lugar seguro."',
                    'save']
    assert nitrado == ['Juan via Discord: mods nuevos']
    assert 'mods nuevos' in channel.sent[0] and 'mods nuevos' in channel.sent[-1]


async def test_now_touches_no_rcon(
        monkeypatch, configured, nitrado, interaction, channel, no_sleep):
    """Now is the escape hatch for a server that stopped answering; it must not
    block on the very thing that is stuck."""
    sent = rcon_that(monkeypatch, lambda cmd: EmptyResponse())

    await server._run_restart(interaction, 0, 'servidor colgado')

    assert sent == []
    assert len(nitrado) == 1


async def test_a_later_warning_failing_does_not_abort(
        monkeypatch, configured, nitrado, interaction, channel, no_sleep):
    """Players were already told once; losing the one-minute call is not a reason
    to leave the server broken."""
    seen = []

    def behaviour(cmd):
        seen.append(cmd)
        return EmptyResponse() if len(seen) == 2 else 'ok'

    rcon_that(monkeypatch, behaviour)

    await server._run_restart(interaction, 5, 'prueba')

    assert len(nitrado) == 1


@pytest.mark.parametrize('delay, marks', [(1, [1]), (5, [5, 1]), (10, [10, 5, 1])])
def test_countdown_adds_up_to_the_requested_delay(delay, marks):
    chosen = [m for m in server.WARNING_MARKS if m <= delay]
    assert chosen == marks

    remaining, total = delay, 0
    for mark in chosen:
        total += (remaining - mark) * 60
        remaining = mark
    total += remaining * 60
    assert total == delay * 60


def test_default_delay_is_a_real_choice():
    """A default that is not offered in the dropdown would be a surprise."""
    assert server.DEFAULT_DELAY in server.WARNING_MARKS
