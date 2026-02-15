# RAG Demo (Namel3ss 0.1.0a22)

Premium deterministic RAG demo built in Namel3ss with:

- Upload -> ingest -> chat -> citations -> explain
- Deterministic retrieval tuning controls
- Source drawer + snippet/page fallback previews
- Studio diagnostics for retrieval traces and ranking decisions

## Dependency Pin

- `namel3ss==0.1.0a22` (see `pyproject.toml`)

## Quickstart

```bash
python3.14 -m venv apps/rag-demo/.venv
source apps/rag-demo/.venv/bin/activate
python -m pip install -U pip
python -m pip install -U "namel3ss==0.1.0a22" pytest
python apps/rag-demo/tools/ensure_provider_manifests.py
python -m namel3ss check apps/rag-demo/app.ai
apps/rag-demo/.venv/bin/n3 check apps/rag-demo/app.ai
n3 run apps/rag-demo/app.ai --port 7360 --no-open
```

Open:

- `http://127.0.0.1:7360/`

## Environment Variables

Create `.env` from `.env.example`:

```bash
cd apps/rag-demo
cp .env.example .env
```

Common values:

```bash
N3_API_TOKEN=dev-token
N3_DISABLE_API_TOKEN=1
NAMEL3SS_OPENAI_API_KEY=sk-...
# or
OPENAI_API_KEY=sk-...
```

Notes:

- `N3_DISABLE_API_TOKEN=1` is recommended for local preview.
- Set `NAMEL3SS_OPENAI_API_KEY` (or `OPENAI_API_KEY`) to use real OpenAI responses in chat.
- If no API key is set, the demo falls back to deterministic compiled answers.
- `.env` is gitignored and must stay local.

## Studio vs Production

Production preview (default browser UX):

```bash
n3 run apps/rag-demo/app.ai --port 7360 --no-open
```

Studio instrumentation mode:

```bash
n3 run studio apps/rag-demo/app.ai --port 7360 --no-open
```

In Studio, the diagnostics slot shows:

- retrieval tuning effects
- filtered candidate tables
- ranking rationale and explain records

## Known Runtime Limits

Platform-level runtime limits and Namel3ss-only feasibility notes are tracked in:

- `apps/rag-demo/LIMITATIONS_REPORT.md`

## Troubleshooting (Current Runtime)

Use explicit app path in every command:

```bash
n3 check apps/rag-demo/app.ai
n3 run apps/rag-demo/app.ai --port 7360 --no-open
n3 apps/rag-demo/app.ai ui > /tmp/rag-static-ui.json
```

Renderer registry health (correct endpoint):

```bash
curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .
```

Do not use `/api/renderer-registry` or `/api/renderer_registry` for health checks.

Startup banner fields check:

```bash
n3 run apps/rag-demo/app.ai --port 7360 --no-open 2>&1 | tee /tmp/rag-start.log
rg "Runtime startup|manifest_hash|renderer_registry_status|lock_path|lock_pid" /tmp/rag-start.log
```

Port conflict check:

```bash
lsof -nP -iTCP:7360 -sTCP:LISTEN
```

If browser shows `N3E_RENDERER_REGISTRY_INVALID`, run:

```bash
n3 doctor --json --app apps/rag-demo/app.ai | jq '.checks[] | select(.id=="cli_entrypoint" or .id=="import_path" or .id=="python_version" or .id=="contract_renderer_registry")'
curl -I http://127.0.0.1:7360/renderer_registry.js
```

## What To Expect In UX

1. **First run**
- Primary `Upload documents` CTA.
- Clear file type guidance (`PDF`, `TXT`).
- 3-line usage onboarding in the left panel.

2. **Ingestion**
- Deterministic statuses (`queued`, `indexing`, `indexed`, `failed`).
- Asking a question auto-syncs uploads and auto-indexes selected sources.
- Index summary card (document/chunk counts + tag breakdown).
- Actionable notices for retry/fallback states.

3. **Chat + citations**
- Bubble chat with deterministic thinking indicator.
- `Reset chat` and `Reset source drawer` controls.
- Citation list + source drawer selection mapping.
- Deterministic page/snippet fallback labels when preview rendering is unavailable.

4. **Explain + diagnostics**
- Explain summary with retrieval parameter snapshot.
- Candidate and ranking tables for deterministic debugging.
- Tuning controls for `semantic_weight`, `semantic_k`, `lexical_k`, `final_top_k`, and tag filtering.

## Tests

Run full local validation (no shell wrappers):

```bash
python -m pip install -U "namel3ss==0.1.0a22"
python -m pip install pytest
python apps/rag-demo/tools/ensure_provider_manifests.py
n3 check apps/rag-demo/app.ai
n3 run apps/rag-demo/app.ai --port 7360 --no-open
curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .
python -m pytest -q apps/rag-demo/tests
```

Deterministic snapshot regression commands (direct `n3` + `jq`):

```bash
n3 apps/rag-demo/app.ai ui > /tmp/rag-manifest.json

composer_action_id="$(jq -r '.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.ask_question")) | .[0].key // empty' /tmp/rag-manifest.json)"
guided_action_id="$(jq -r '.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.run_demo_mode_path")) | .[0].key // empty' /tmp/rag-manifest.json)"
citation_open_action_id="$(jq -r '.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.open_citation" and (.key | contains("open_in_source_drawer")))) | if length > 0 then .[0].key else empty end' /tmp/rag-manifest.json)"
if [ -z "$citation_open_action_id" ]; then
  citation_open_action_id="$(jq -r '.actions | to_entries | map(select(.value.type=="call_flow" and .value.flow=="rag_engine.open_citation")) | .[0].key // empty' /tmp/rag-manifest.json)"
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
}' /tmp/rag-manifest.json > /tmp/rag-manifest-summary.json
diff -u apps/rag-demo/tests/snapshots/manifest_core.json /tmp/rag-manifest-summary.json

n3 apps/rag-demo/app.ai "$composer_action_id" --json '{"message":"what is this doc about"}' | jq '{
  mode: .result.mode,
  answer: .result.answer_text,
  citations: .state.answer.citations,
  trusted: .state.answer.trusted,
  trust_score: .state.answer.trust_score,
  source_count: .state.answer.source_count
}' > /tmp/rag-composer.json
diff -u apps/rag-demo/tests/snapshots/composer_no_selection.json /tmp/rag-composer.json

n3 apps/rag-demo/app.ai "$guided_action_id" --json '{}' | jq '{
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
}' > /tmp/rag-guided.json
diff -u apps/rag-demo/tests/snapshots/guided_flow.json /tmp/rag-guided.json

n3 apps/rag-demo/app.ai "$citation_open_action_id" --json '{"row":{"source_id":"guided-product","chunk_id":"guided-product-1","page_number":1}}' | jq '{
  result: .result,
  selected_source: .state.selected_citation_source,
  drawer: .state.drawer.has_selection
}' > /tmp/rag-citation-open.json
diff -u apps/rag-demo/tests/snapshots/citation_open.json /tmp/rag-citation-open.json
```

## Headless API

This same app can be called headlessly:

- `GET /api/v1/ui`
- `POST /api/v1/actions/<action_id>`
