#!/usr/bin/env bash
set -euo pipefail

if ! command -v jq >/dev/null 2>&1; then
  echo "jq is required for smoke tests." >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

unset NAMEL3SS_OPENAI_API_KEY
unset OPENAI_API_KEY
export N3_IDENTITY_ID=rag-demo-tester

manifest_file="$(mktemp)"
manifest_summary_file="$(mktemp)"
ask_file="$(mktemp)"
ask_second_file="$(mktemp)"
trap 'rm -f "$manifest_file" "$manifest_summary_file" "$ask_file" "$ask_second_file"' EXIT

n3 app.ai check >/dev/null

n3 app.ai ui > "$manifest_file"
jq '{
  page_slug: .pages[0].slug,
  layout_slots: (.pages[0].layout | keys | sort),
  diagnostics_blocks: (.pages[0].diagnostics_blocks | length),
  upload_request: .upload_requests[0],
  theme_name: .theme.theme_name,
  theme_css_hash: .theme.css_hash,
  has_source_preview_component: (
    (
      (.pages[0].layout.drawer_right[0].children // [])
      | map(select(.type=="source_preview"))
      | length
    ) > 0
  ),
  scope_selector: (
    (
      (.pages[0].layout.sidebar_left[0].children // [])
      | map(select(.type=="scope_selector"))
      | .[0]
    ) | if . == null then null else {options_source, active_source} end
  ),
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
  composer_action: (.actions["page.rag_demo.composer.4.0.1.composer"] // null),
  clear_drawer_action: (
    .actions["page.rag_demo.button.reset_source_drawer"]
    // .actions["page.rag_demo.button.clear_sources_drawer"]
    // null
  ),
  upload_actions: {
    select: (.actions["page.rag_demo.upload.documents"].type),
    clear: (.actions["page.rag_demo.upload.documents.clear"].type),
    ingestion: (.actions["page.rag_demo.upload.documents.ingestion"].type)
  }
}' "$manifest_file" > "$manifest_summary_file"

diff -u tests/snapshots/manifest_core.json "$manifest_summary_file"

n3 app.ai page.rag_demo.composer.4.0.1.composer --json '{"message":"what is this doc about"}' | jq '{
  mode: .result.mode,
  answer: .result.answer_text,
  citations: .state.answer.citations,
  trusted: .state.answer.trusted,
  trust_score: .state.answer.trust_score,
  source_count: .state.answer.source_count
}' > "$ask_file"

diff -u tests/snapshots/composer_no_selection.json "$ask_file"

n3 app.ai page.rag_demo.composer.4.0.1.composer --json '{"message":"what is this doc about"}' | jq '{
  mode: .result.mode,
  answer: .result.answer_text,
  citations: .state.answer.citations,
  trusted: .state.answer.trusted,
  trust_score: .state.answer.trust_score,
  source_count: .state.answer.source_count
}' > "$ask_second_file"

diff -u "$ask_file" "$ask_second_file"

echo "RAG demo smoke test passed."
