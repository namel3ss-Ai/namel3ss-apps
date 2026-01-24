#!/usr/bin/env bash
set -euo pipefail

# Delegate to the root smoke test for consistency.
exec "$(cd "$(dirname "$0")/.." && pwd)/smoke.sh"
