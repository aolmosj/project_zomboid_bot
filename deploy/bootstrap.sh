#!/usr/bin/env bash
# Provision the bot on a Debian/Ubuntu host. Idempotent: safe to re-run, and
# re-running it is also how you apply a dependency or unit change.
#
#   sudo /opt/pzbot/deploy/bootstrap.sh
#
# Expects the checkout to already be at /opt/pzbot. The location is fixed on
# purpose: it is what lets the unit carry absolute paths without those paths
# being one particular machine's.
#
# Secrets are never generated here. A placeholder token that silently "works"
# is worse than a service that refuses to start.
set -euo pipefail

APP_DIR=/opt/pzbot
STATE_DIR=/var/lib/pzbot
CONF_DIR=/etc/pzbot
ENV_FILE="$CONF_DIR/env"
APP_USER=pzbot
UNIT=/etc/systemd/system/pzbot.service
PLACEHOLDER=PutTheRealTokenHere

die() { echo "error: $*" >&2; exit 1; }

# --- preflight ---------------------------------------------------------------
# Fail before touching the system rather than half-way through.
[ "$(id -u)" -eq 0 ] || die "run as root"
REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
[ "$REPO_ROOT" = "$APP_DIR" ] || die "expected the checkout at $APP_DIR, found it at $REPO_ROOT"
[ -f "$APP_DIR/pzbot.py" ] || die "$APP_DIR does not look like the bot checkout"

apt-get update -qq
apt-get install -y -qq python3-venv

# --- user and directories ----------------------------------------------------
# A system account with no shell: the bot never needs to log in anywhere.
id -u "$APP_USER" >/dev/null 2>&1 || \
    useradd --system --home-dir "$STATE_DIR" --shell /usr/sbin/nologin "$APP_USER"

install -d -o "$APP_USER" -g "$APP_USER" -m 750 "$STATE_DIR"
install -d -o root -g "$APP_USER" -m 750 "$CONF_DIR"

# --- application -------------------------------------------------------------
# A venv bakes in absolute paths, so it is built where it will run and rebuilt
# rather than moved. Pinned requirements keep a rebuild from changing versions.
[ -x "$APP_DIR/.venv/bin/python" ] || python3 -m venv "$APP_DIR/.venv"
"$APP_DIR/.venv/bin/pip" install -q --upgrade pip
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

# Owned by root, run by pzbot: the service cannot rewrite its own code.
chown -R root:root "$APP_DIR"

# --- secrets -----------------------------------------------------------------
if [ ! -f "$ENV_FILE" ]; then
    install -o root -g "$APP_USER" -m 640 "$APP_DIR/deploy/env.example" "$ENV_FILE"
    echo "created $ENV_FILE from the example"
fi
grep -q "^DISCORD_TOKEN=" "$ENV_FILE" || die "$ENV_FILE has no DISCORD_TOKEN line"
if grep -q "^DISCORD_TOKEN=$PLACEHOLDER\$" "$ENV_FILE"; then
    die "$ENV_FILE still holds the placeholder token; put the real one in it and re-run"
fi

# --- state -------------------------------------------------------------------
# Refuse to start alongside a database still inside the checkout: two files
# named guild_config.db, only one of them read, is a trap worth failing on.
if [ -f "$APP_DIR/guild_config.db" ]; then
    die "$APP_DIR/guild_config.db still exists. Move it to $STATE_DIR/guild_config.db (see the README) so there is only one database"
fi
[ -f "$STATE_DIR/guild_config.db" ] || echo "note: no database yet at $STATE_DIR; it will be created empty on first start"

# --- service -----------------------------------------------------------------
install -o root -g root -m 644 "$APP_DIR/deploy/pzbot.service" "$UNIT"
systemctl daemon-reload
systemctl enable -q pzbot
systemctl restart pzbot

sleep 3
systemctl is-active --quiet pzbot || die "pzbot failed to start: journalctl -u pzbot -n 30"
echo "pzbot is running. Logs: journalctl -u pzbot -f"
