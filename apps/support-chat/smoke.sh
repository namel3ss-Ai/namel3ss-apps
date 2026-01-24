#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required for smoke tests." >&2
  exit 1
fi

# CI-safe defaults: no external model calls.
unset NAMEL3SS_OPENAI_API_KEY
unset OPENAI_API_KEY

# Persist across UI actions in this script.
export N3_PERSIST_TARGET=sqlite

n3 app.ai check

# Reset local store to ensure deterministic counts.
if n3 app.ai data reset --yes >/dev/null 2>&1; then
  :
fi

manifest=$(n3 app.ai ui)
seed_action=$(echo "$manifest" | jq -r '.actions | to_entries[] | select(.value.type=="call_flow" and .value.flow=="seed_kb") | .key' | head -n1)
start_action=$(echo "$manifest" | jq -r '.actions | to_entries[] | select(.value.type=="call_flow" and .value.flow=="start_conversation") | .key' | head -n1)
send_action=$(echo "$manifest" | jq -r '.actions | to_entries[] | select(.value.type=="call_flow" and .value.flow=="handle_message") | .key' | head -n1)

if [[ -z "$seed_action" || "$seed_action" == "null" ]]; then
  echo "Seed KB action not found." >&2
  exit 1
fi
if [[ -z "$start_action" || "$start_action" == "null" ]]; then
  echo "Start conversation action not found." >&2
  exit 1
fi
if [[ -z "$send_action" || "$send_action" == "null" ]]; then
  echo "Handle message action not found." >&2
  exit 1
fi

n3 app.ai "$seed_action" --json "{}" >/dev/null
n3 app.ai "$start_action" --json "{}" >/dev/null

response=$(n3 app.ai "$send_action" --json '{"message":"How do I reset my password?"}')
reply=$(echo "$response" | jq -r '.result')

echo "$reply" | grep -qi "reset password" || {
  echo "Reply did not include expected KB text." >&2
  echo "$reply" >&2
  exit 1
}

data=$(n3 app.ai data export)
count=$(echo "$data" | jq -r '.records[] | select(.name=="Conversation") | .count')
if [[ -z "$count" || "$count" -lt 3 ]]; then
  echo "Expected at least 3 Conversation rows, got: $count" >&2
  exit 1
fi

echo "Smoke test passed."
