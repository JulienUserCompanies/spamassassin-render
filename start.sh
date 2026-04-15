#!/usr/bin/env bash
set -e

spamd --listen localhost --port 783 --pidfile /tmp/spamd.pid --create-prefs

exec uvicorn app --host 0.0.0.0 --port $PORT
