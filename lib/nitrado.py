import aiohttp

NITRADO_API = "https://api.nitrado.net"
TIMEOUT = aiohttp.ClientTimeout(total=15)


class NitradoError(Exception):
    """Nitrado API failure, carrying a message safe to show to users."""


# The unmapped branch forwards the API's own words into a Discord message, so
# it is bounded and scrubbed rather than trusted: the length is not ours to
# choose, and a token must never travel back out however it got in there.
DETAIL_MAX = 200


def _detail(payload, status, token):
    detail = str(payload.get("message") or "").strip() or f"HTTP {status}"
    if token and token in detail:
        detail = detail.replace(token, "<token>")
    return detail[:DETAIL_MAX]


def _headers(token):
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


async def _request(method, path, token, **kwargs):
    url = f"{NITRADO_API}{path}"
    try:
        async with aiohttp.ClientSession(timeout=TIMEOUT) as session:
            async with session.request(method, url, headers=_headers(token), **kwargs) as resp:
                try:
                    payload = await resp.json(content_type=None)
                except Exception:
                    payload = {}
                if resp.status == 401:
                    raise NitradoError("Invalid or expired Nitrado token")
                if resp.status == 403:
                    raise NitradoError("The Nitrado token has no access to this service")
                if resp.status == 404:
                    raise NitradoError("Service ID not found")
                if resp.status == 429:
                    raise NitradoError("Nitrado API rate limit reached, try again later")
                if resp.status >= 400 or payload.get("status") != "success":
                    raise NitradoError(_detail(payload, resp.status, token))
                return payload
    except aiohttp.ClientError as e:
        raise NitradoError(f"Could not reach the Nitrado API: {e}")
    except TimeoutError:
        raise NitradoError("The Nitrado API did not respond in time")


async def restart_gameserver(token, service_id, message=None):
    """Request a restart of the gameserver. Returns the API status message."""
    data = {}
    if message:
        data["message"] = message
        data["restart_message"] = message
    payload = await _request(
        "POST", f"/services/{service_id}/gameservers/restart", token, data=data or None
    )
    return payload.get("message") or "Restart requested"


async def get_gameserver_status(token, service_id):
    """Return the gameserver status string (started, stopped, restarting, ...)."""
    payload = await _request("GET", f"/services/{service_id}/gameservers", token)
    return payload.get("data", {}).get("gameserver", {}).get("status", "unknown")
