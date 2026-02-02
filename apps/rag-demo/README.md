# Deterministic RAG Demo (namel3ss)

A complete Retrieval-Augmented Generation demo built in a single `.ai` file. No Python glue, no frameworks, no hidden state.

## What this demo shows
- 📄 Document ingestion via namel3ss records + UI form
- 🔎 Deterministic retrieval (exact-match scoring, top-N selection)
- 🤖 AI answers grounded in retrieved context
- 🔍 End-to-end explainability with `n3 explain`

## Install namel3ss

Use the latest namel3ss version from PyPI.

Recommended install (isolated CLI):

```bash
python -m pip install -U pipx
pipx install namel3ss
pipx upgrade namel3ss
```

Verify:

```bash
n3 --version
```

Alternative (venv / pip):

```bash
python -m pip install -U namel3ss
n3 --version
```

## Configure secrets

This demo uses a namel3ss secret for the OpenAI key and the built-in OpenAI provider.

```bash
# namel3ss secret (used by secret("openai_api_key"))
export N3_SECRET_OPENAI_API_KEY="sk-..."

# provider key (used by the OpenAI provider)
export NAMEL3SS_OPENAI_API_KEY="sk-..."
# or: export OPENAI_API_KEY="sk-..."
```

## Run the demo

```bash
cd apps/rag-demo
n3 run app.ai
```

Open:

```
http://localhost:7340/?page=home
```

## Inspect behavior

After asking a question, run:

```bash
n3 explain
```

You will see:
- Which documents were scored and selected
- The JSON prompt sent to the AI
- The AI response

## Notes on retrieval

Retrieval is deterministic and intentionally simple: a document scores if the question exactly matches the title or content. The first 3 matches (in record order) become the retrieved context.
