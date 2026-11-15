#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$ROOT/scripts/bin:$PATH"
export AGENT_BROWSER_IDLE_TIMEOUT_MS=3600000
exec agent-browser "$@"
