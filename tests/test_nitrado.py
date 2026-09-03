"""Exercised against a local stub rather than the real API, so the error paths
are testable at all. The token assertion is the point: an error message travels
to Discord."""
import pytest
from aiohttp import web

import lib.nitrado as nitrado

TOKEN = 'a-secret-token-that-must-never-be-echoed'
SERVICE = 11772929


@pytest.fixture
async def api(monkeypatch, aiohttp_unused_port=None):
    """A stand-in Nitrado whose behaviour each test sets through `plan`."""
    plan = {'status': 200, 'body': {'status': 'success',
                                    'data': {'gameserver': {'status': 'started'}},
                                    'message': 'ok'}}

    async def handler(request):
        return web.json_response(plan['body'], status=plan['status'])

    app = web.Application()
    app.router.add_get('/services/{sid}/gameservers', handler)
    app.router.add_post('/services/{sid}/gameservers/restart', handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 0)
    await site.start()
    port = runner.addresses[0][1]
    monkeypatch.setattr(nitrado, 'NITRADO_API', f'http://127.0.0.1:{port}')
    yield plan
    await runner.cleanup()


async def test_reads_the_gameserver_status(api):
    assert await nitrado.get_gameserver_status(TOKEN, SERVICE) == 'started'


async def test_restart_returns_the_api_message(api):
    api['body'] = {'status': 'success', 'message': 'restart queued'}
    assert await nitrado.restart_gameserver(TOKEN, SERVICE, message='why') == 'restart queued'


@pytest.mark.parametrize('status, expected', [
    (401, 'Invalid or expired'),
    (403, 'no access'),
    (404, 'not found'),
    (429, 'rate limit'),
])
async def test_http_failures_become_readable_errors(api, status, expected):
    api['status'] = status
    api['body'] = {'status': 'error', 'message': 'whatever'}
    with pytest.raises(nitrado.NitradoError) as caught:
        await nitrado.get_gameserver_status(TOKEN, SERVICE)
    assert expected in str(caught.value)


@pytest.mark.parametrize('status', [401, 403, 404, 429, 500])
async def test_the_token_never_appears_in_an_error(api, status):
    api['status'] = status
    api['body'] = {'status': 'error', 'message': f'context {TOKEN} leaked'}
    with pytest.raises(nitrado.NitradoError) as caught:
        await nitrado.restart_gameserver(TOKEN, SERVICE)
    assert TOKEN not in str(caught.value)


async def test_unreachable_host_is_reported(monkeypatch):
    monkeypatch.setattr(nitrado, 'NITRADO_API', 'http://127.0.0.1:1')
    with pytest.raises(nitrado.NitradoError) as caught:
        await nitrado.get_gameserver_status(TOKEN, SERVICE)
    assert 'Could not reach' in str(caught.value)
    assert TOKEN not in str(caught.value)
