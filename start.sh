#!/usr/bin/env bash
set -e

PORT="${PORT:-10000}"
SPAMD_PORT="${SPAMD_PORT:-1783}"

spamd --listen 127.0.0.1 --port "$SPAMD_PORT" --pidfile /tmp/spamd.pid --create-prefs

exec uvicorn app:app --host 0.0.0.0 --port "$PORT"
