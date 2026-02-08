# Deploy on Render

This app is deployed as a Docker-based Web Service.

## Service setup

1. Push repository to GitHub.
2. In Render, create `New -> Web Service`.
3. Connect repo and pick branch.
4. Set **Root Directory** to `apps/rag-demo`.
5. Runtime: **Docker**.

## Build and start

With Docker runtime:

- Build command: not required (Render builds from `Dockerfile`).
- Start command: not required (uses Docker `CMD`).

`Dockerfile` starts:

```bash
n3 studio app.ai --port ${PORT:-7340}
```

## Environment variables

Set these in Render:

- `PORT=10000`
- `N3_PERSIST_ROOT=/app/data`
- `N3_ANSWER_PROVIDER` (optional)
- `N3_ANSWER_MODEL` (optional)
- provider key (`NAMEL3SS_OPENAI_API_KEY` / `OPENAI_API_KEY` / Anthropic equivalents)

## Persistence

Attach a persistent disk and mount it at:

- `/app/data`

## Demo mode fallback

If provider vars/keys are omitted, the app remains usable in citations-only demo mode:

- retrieval still runs
- citations remain visible/clickable
- explain view still records retrieval/ranking decisions

## Verify after deploy

1. Upload `assets/sample.pdf`.
2. Click `Update library`.
3. Click `Run guided demo path`.
4. Verify citations and Explain tables.
