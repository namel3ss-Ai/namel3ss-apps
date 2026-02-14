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
python -m pip install "namel3ss==0.1.0a21"
python -m pip install pytest
python apps/rag-demo/tools/ensure_provider_manifests.py
python -m namel3ss apps/rag-demo/app.ai check
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

Use repo-root commands with explicit app path:

```bash
n3 check apps/rag-demo/app.ai
n3 apps/rag-demo/app.ai ui > /tmp/rag-static-ui.json
shasum -a 256 /tmp/rag-static-ui.json
```

Start runtime with explicit path:

```bash
n3 run apps/rag-demo/app.ai --port 7360 --no-open
```

1. Static-vs-runtime manifest drift
- Capture runtime UI payload and compare with static output:
```bash
curl -sS http://127.0.0.1:7360/api/v1/ui > /tmp/rag-runtime-ui.json || \
curl -sS http://127.0.0.1:7360/api/ui > /tmp/rag-runtime-ui.json
shasum -a 256 /tmp/rag-runtime-ui.json
diff -u /tmp/rag-static-ui.json /tmp/rag-runtime-ui.json
```
- If drift exists: stop runtime, ensure a single listener, rerun explicit-path launch.

2. Renderer-registry diagnostics visibility
- Probe both known endpoints:
```bash
curl -i http://127.0.0.1:7360/api/renderer-registry
curl -i http://127.0.0.1:7360/api/renderer_registry
```
- `404` is a known platform limitation; record result in incident notes and continue with app-level checks.

3. Multiple runtimes on same host/port
- Detect listeners:
```bash
lsof -nP -iTCP:7360 -sTCP:LISTEN
```
- If more than one runtime is active, terminate extras and relaunch one explicit `n3 run apps/rag-demo/app.ai ...`.

4. Multi-app path mis-targeting
- Always include full target path in commands:
```bash
n3 check apps/rag-demo/app.ai
n3 run apps/rag-demo/app.ai --port 7360 --no-open
n3 apps/rag-demo/app.ai ui
```

5. Startup observability gaps
- Capture startup identity and hash manually:
```bash
echo "app=apps/rag-demo/app.ai"
n3 --version
python -m namel3ss --version
python -m pip show namel3ss | rg '^Version:'
n3 apps/rag-demo/app.ai ui | shasum -a 256
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

Run full local validation:

```bash
python3 -m compileall . -q
python3 -m pytest -q
./smoke.sh
```

## Headless API

This same app can be called headlessly:

- `GET /api/v1/ui`
- `POST /api/v1/actions/<action_id>`
