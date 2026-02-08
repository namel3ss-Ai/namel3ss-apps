# RAG Demo (Namel3ss 0.1.0a15)

This demo now runs end-to-end in **Namel3ss**:

- Backend logic (ingestion, retrieval, ranking, answer generation) in `app.ai`
- Frontend UI (layout, chat, uploads, citations, diagnostics) in `app.ai`
- Query profiling and routing in `app.ai` (no Python helper tools)

No external frontend is required for normal use.

## Dependency

Pinned in `pyproject.toml`:

- `namel3ss==0.1.0a15`

## Run (Namel3ss UI + Backend)

```bash
cd apps/rag-demo
python3 -m pip install -e .[dev]

n3 app.ai check
./run.sh
```

Open:

- `http://127.0.0.1:7360/`

## Configure Real OpenAI APIs

Recommended local secret workflow:

1. Create `.env` from `.env.example`
2. Put your keys in `.env`
3. Start with `./run.sh` (it auto-loads `.env`)

```bash
cd apps/rag-demo
cp .env.example .env
```

`.env` values:

```bash
N3_API_TOKEN=dev-token
N3_DISABLE_API_TOKEN=1
NAMEL3SS_OPENAI_API_KEY=sk-...
# OR
# OPENAI_API_KEY=sk-...
```

`N3_DISABLE_API_TOKEN=1` is recommended for local preview and avoids browser auth issues during upload/actions.

Security note:

- `.env` is gitignored and should not be committed.

## What the UI Includes (All from Namel3ss)

- Sidebar document management with upload + scope selection
- Main chat with grouped bubbles, message actions, citations, trust indicator
- Source drawer for citation evidence cards
- Sticky composer for prompt input
- Diagnostics panel (separate from product UI)
- Theme tokens and modern layout slots

## How to Test Quickly

1. Upload a `.txt` or `.pdf`
2. Click `Synchronize uploads`
3. Click `Index selected sources`
4. Ask a question in chat

## Troubleshooting

If browser says connection refused:

```bash
lsof -nP -iTCP:7360 -sTCP:LISTEN
```

If it is not listening, re-run:

```bash
cd apps/rag-demo
./run.sh
```

## Headless API

If you want to build a custom UI later, run this same app with headless endpoints:

- `GET /api/v1/ui`
- `POST /api/v1/actions/<action_id>`
