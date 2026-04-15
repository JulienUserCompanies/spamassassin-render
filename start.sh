#!/usr/bin/env bash
set -e

PORT="${PORT:-10000}"

spamd --listen localhost --port 783 --pidfile /tmp/spamd.pid --create-prefs

exec uvicorn app:app --host 0.0.0.0 --port "$PORT"
