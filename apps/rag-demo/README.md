# RAG Demo (Namel3ss 0.1.0a21)

Premium deterministic RAG demo built in Namel3ss with:

- Upload -> ingest -> chat -> citations -> explain
- Deterministic retrieval tuning controls
- Source drawer + snippet/page fallback previews
- Studio diagnostics for retrieval traces and ranking decisions

## Dependency Pin

- `namel3ss==0.1.0a21` (see `pyproject.toml`)

## Quickstart

```bash
python3.14 -m venv apps/rag-demo/.venv
source apps/rag-demo/.venv/bin/activate
python -m pip install -U pip
python -m pip install -U "namel3ss==0.1.0a21" pytest
python apps/rag-demo/tools/ensure_provider_manifests.py
python -m namel3ss check apps/rag-demo/app.ai
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

## Troubleshooting (Deterministic)

Run from repo root and always include `apps/rag-demo/app.ai` in `n3` commands.

1. Preflight (required runtime + explicit app path)

```bash
apps/rag-demo/.venv/bin/python -m pip install -U "namel3ss==0.1.0a21"
apps/rag-demo/.venv/bin/n3 check apps/rag-demo/app.ai
apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open
```

2. Startup parity + banner fields
- Use one-shot startup verification:

```bash
apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7361 --no-open --dry 2>&1 | tee /tmp/rag-start.log
rg "Runtime startup|manifest_hash|renderer_registry_status|lock_path|lock_pid" /tmp/rag-start.log
```
- Expected: a `Runtime startup` line containing `app_path`, `manifest_hash`, `renderer_registry_status`, `lock_path`, and `lock_pid`.

3. Renderer registry health
- Check the runtime endpoint directly:

```bash
curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .
```
- Expected: `"ok": true`, `"parity": {"ok": true}`, and `"registry": {"status": "validated"}`.

4. Port conflict and lock handling
- Check listener ownership:

```bash
lsof -nP -iTCP:7360 -sTCP:LISTEN
```
- If a stale run exists, a second launch on the same port now fails with lock-owner details:

```bash
apps/rag-demo/.venv/bin/n3 run apps/rag-demo/app.ai --port 7360 --no-open
```

5. Multi-app path mis-targeting
- Confirm guardrails, then use explicit target:

```bash
apps/rag-demo/.venv/bin/n3 check app.ai
apps/rag-demo/.venv/bin/n3 check apps/rag-demo/app.ai
```
- The first command should fail from repo root (`App file not found`), while the explicit path command should pass.

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

Run full local validation:

```bash
cd apps/rag-demo
.venv/bin/python -m compileall . -q
.venv/bin/python -m pytest -q
./smoke.sh
```

## Headless API

This same app can be called headlessly:

- `GET /api/v1/ui`
- `POST /api/v1/actions/<action_id>`
