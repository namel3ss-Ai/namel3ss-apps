# RAG Demo (Namel3ss 0.1.0a20)

Premium deterministic RAG demo built in Namel3ss with:

- Upload -> ingest -> chat -> citations -> explain
- Deterministic retrieval tuning controls
- Source drawer + snippet/page fallback previews
- Studio diagnostics for retrieval traces and ranking decisions

## Dependency Pin

- `namel3ss==0.1.0a20` (see `pyproject.toml`)

## Quickstart

```bash
cd apps/rag-demo
python3.14 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install "namel3ss==0.1.0a20"
python -m pip install pytest
python tools/ensure_provider_manifests.py
python -m namel3ss app.ai check
./run.sh
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
./run.sh
```

Studio instrumentation mode:

```bash
n3 run studio app.ai --port 7360 --no-open
```

In Studio, the diagnostics slot shows:

- retrieval tuning effects
- filtered candidate tables
- ranking rationale and explain records

## Known Runtime Limits

Platform-level runtime limits and Namel3ss-only feasibility notes are tracked in:

- `apps/rag-demo/LIMITATIONS_REPORT.md`

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
