#!/usr/bin/env bash
# One origin for frontend, API and cookies; no external service required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-8080}"
[[ "$PORT" =~ ^[0-9]+$ ]] && ((PORT > 0 && PORT < 65536)) || { echo 'PORT must be 1–65535' >&2; exit 1; }
PYTHON="$ROOT/backend/.venv/bin/python"
[[ -x "$PYTHON" ]] || { echo 'Install backend/.venv and backend/requirements.txt first (see README).' >&2; exit 1; }
export FRONTEND_DIST="$ROOT/barakah-ui/dist"
export ALLOWED_ORIGINS="${ALLOWED_ORIGINS:-http://127.0.0.1:$PORT,http://localhost:$PORT}"
export RESET_URL="${RESET_URL:-http://127.0.0.1:$PORT/reset-password}"
export AI_MODE="${AI_MODE:-unavailable}"
cd "$ROOT/barakah-ui"
VITE_API_BASE_URL=/api/v1 npm run build
cd "$ROOT/backend"
# Additive migrations only. Back up existing databases before running (see audit/DEMO_GUIDE.md).
"$PYTHON" -m alembic upgrade head
exec "$PYTHON" -m uvicorn app.main:app --host 127.0.0.1 --port "$PORT" --no-access-log
