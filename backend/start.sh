#!/usr/bin/env bash
set -o errexit
set -o pipefail

exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 2 --proxy-headers --forwarded-allow-ips='*' 2>&1
