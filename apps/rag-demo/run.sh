#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

N3_BIN="${N3_BIN:-}"
if [[ -z "$N3_BIN" ]]; then
  if [[ -x "$ROOT_DIR/.venv/bin/n3" ]]; then
    N3_BIN="$ROOT_DIR/.venv/bin/n3"
  else
    N3_BIN="n3"
  fi
fi

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PORT="${PORT:-7360}"
API_TOKEN="${N3_API_TOKEN:-dev-token}"

# Leave API token optional for local preview to avoid auth/renderer mismatches.
if [[ "${N3_DISABLE_API_TOKEN:-1}" == "1" ]]; then
  exec "$N3_BIN" run app.ai --port "$PORT" --no-open
fi

exec "$N3_BIN" run app.ai --port "$PORT" --api-token "$API_TOKEN" --no-open
