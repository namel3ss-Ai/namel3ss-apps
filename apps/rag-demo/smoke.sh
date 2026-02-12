#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required for smoke tests." >&2
  exit 1
fi

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

PY_BIN="${PY_BIN:-}"
if [[ -z "$PY_BIN" ]]; then
  if [[ -x "$ROOT_DIR/.venv/bin/python" ]]; then
    PY_BIN="$ROOT_DIR/.venv/bin/python"
  else
    PY_BIN="python3"
  fi
fi

unset NAMEL3SS_OPENAI_API_KEY
unset OPENAI_API_KEY
export N3_IDENTITY_ID=rag-demo-tester

manifest_file="$(mktemp)"
manifest_summary_file="$(mktemp)"
ask_file="$(mktemp)"
ask_second_file="$(mktemp)"
guided_file="$(mktemp)"
guided_second_file="$(mktemp)"
citation_open_file="$(mktemp)"
trap 'rm -f "$manifest_file" "$manifest_summary_file" "$ask_file" "$ask_second_file" "$guided_file" "$guided_second_file" "$citation_open_file"' EXIT

"$PY_BIN" tools/ensure_provider_manifests.py >/dev/null
"$N3_BIN" app.ai check >/dev/null

"$N3_BIN" app.ai ui > "$manifest_file"

composer_action_id="$(jq -r '.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.ask_question")) | .[0].key // empty' "$manifest_file")"
guided_action_id="$(jq -r '.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.run_demo_mode_path")) | .[0].key // empty' "$manifest_file")"
citation_open_action_id="$(jq -r '.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.open_citation" and (.key | contains("open_in_source_drawer")))) | if length > 0 then .[0].key else empty end' "$manifest_file")"
if [[ -z "$citation_open_action_id" ]]; then
  citation_open_action_id="$(jq -r '.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.open_citation")) | .[0].key // empty' "$manifest_file")"
fi

if [[ -z "$composer_action_id" || -z "$guided_action_id" || -z "$citation_open_action_id" ]]; then
  echo "Required action ids could not be resolved from manifest." >&2
  exit 1
fi

jq '{
  page_slug: .pages[0].slug,
  layout_slots: (.pages[0].layout | keys | sort),
  diagnostics_blocks: (.pages[0].diagnostics_blocks | length),
  upload_request: .upload_requests[0],
  theme_name: .theme.theme_name,
  theme_css_hash: .theme.css_hash,
  scope_selector: {
    options_source: "state.tag.options",
    active_source: "state.tag.active"
  },
  chats: (
    [.. | objects | select(.type=="chat") | {
      style,
      show_avatars,
      group_messages,
      actions,
      attachments,
      streaming
    }]
    | sort_by(.streaming)
  ),
  composer_action: (.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.ask_question")) | .[0].value | {id, type, flow}),
  run_guided_action: (.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.run_demo_mode_path")) | .[0].value | {id, type, flow}),
  reset_chat_action: (.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.reset_chat")) | .[0].value | {id, type, flow}),
  clear_drawer_action: (.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.clear_sources_drawer")) | .[0].value | {id, type, flow}),
  upload_actions: {
    select: (.actions | to_entries | map(select(.value.type=="upload_select")) | .[0].value.type // null),
    clear: (.actions | to_entries | map(select(.value.type=="upload_clear")) | .[0].value.type // null),
    ingestion: (.actions | to_entries | map(select(.value.type=="ingestion_review")) | .[0].value.type // null)
  }
}' "$manifest_file" > "$manifest_summary_file"

diff -u tests/snapshots/manifest_core.json "$manifest_summary_file"

"$N3_BIN" app.ai "$composer_action_id" --json '{"message":"what is this doc about"}' | jq '{
  mode: .result.mode,
  answer: .result.answer_text,
  citations: .state.answer.citations,
  trusted: .state.answer.trusted,
  trust_score: .state.answer.trust_score,
  source_count: .state.answer.source_count
}' > "$ask_file"

diff -u tests/snapshots/composer_no_selection.json "$ask_file"

"$N3_BIN" app.ai "$composer_action_id" --json '{"message":"what is this doc about"}' | jq '{
  mode: .result.mode,
  answer: .result.answer_text,
  citations: .state.answer.citations,
  trusted: .state.answer.trusted,
  trust_score: .state.answer.trust_score,
  source_count: .state.answer.source_count
}' > "$ask_second_file"

diff -u "$ask_file" "$ask_second_file"

"$N3_BIN" app.ai "$guided_action_id" --json '{}' | jq '{
  status: .result.status,
  mode: .result.mode,
  answer: .result.answer_text,
  citation_count: (.state.answer.citations | length),
  trusted: .state.answer.trusted,
  trust_score: .state.answer.trust_score,
  source_count: .state.answer.source_count,
  selected_source: .state.selected_citation_source,
  ready_documents: .state.ready_documents,
  total_documents: .state.total_documents,
  chunk_count: .state.chunk_count,
  tag_product_count: .state.tag_product_count
}' > "$guided_file"

diff -u tests/snapshots/guided_flow.json "$guided_file"

"$N3_BIN" app.ai "$guided_action_id" --json '{}' | jq '{
  status: .result.status,
  mode: .result.mode,
  answer: .result.answer_text,
  citation_count: (.state.answer.citations | length),
  trusted: .state.answer.trusted,
  trust_score: .state.answer.trust_score,
  source_count: .state.answer.source_count,
  selected_source: .state.selected_citation_source,
  ready_documents: .state.ready_documents,
  total_documents: .state.total_documents,
  chunk_count: .state.chunk_count,
  tag_product_count: .state.tag_product_count
}' > "$guided_second_file"

diff -u "$guided_file" "$guided_second_file"

"$N3_BIN" app.ai "$citation_open_action_id" --json '{"row":{"source_id":"guided-product","chunk_id":"guided-product-1","page_number":1}}' | jq '{
  result: .result,
  selected_source: .state.selected_citation_source,
  drawer: .state.drawer.has_selection
}' > "$citation_open_file"

diff -u tests/snapshots/citation_open.json "$citation_open_file"

echo "RAG demo smoke test passed."
