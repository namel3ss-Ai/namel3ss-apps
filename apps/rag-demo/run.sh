#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

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
  exec n3 run app.ai --port "$PORT" --no-open
fi

exec n3 run app.ai --port "$PORT" --api-token "$API_TOKEN" --no-open
