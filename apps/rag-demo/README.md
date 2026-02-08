# RAG Demo (namel3ss)

![Deterministic](https://img.shields.io/badge/Deterministic-Yes-2f855a)
![Offline Testable](https://img.shields.io/badge/Offline%20Testable-Yes-2563eb)
![Citations Enforced](https://img.shields.io/badge/Citations-Enforced-0f766e)
![Eval Gated](https://img.shields.io/badge/Eval-Gated-b45309)

Reference implementation for building RAG systems that are **trustworthy under pressure**.

Promise: **Chat with your documents. Every claim is cited.**

## Why this demo exists

Many demos optimize for quick answers. Production teams need stronger guarantees:

- deterministic behavior you can replay exactly
- citations users can open and verify
- explainability that shows how retrieval and ranking decisions were made
- graceful failure modes instead of bluffing

This app shows the namel3ss position clearly: **programs control AI systems, not the other way around.**

## 5-minute quickstart

```bash
python3 -m pip install --upgrade namel3ss
cd apps/rag-demo
cp .env.example .env
export N3_PERSIST_ROOT=./data
n3 studio app.ai
```

Then in Studio:

1. Upload `assets/sample.pdf`.
2. Click `Run library sync`.
3. Click `Run indexing`.
4. Ask `runtime enforces citations`.
5. Open source cards and `Explain` to verify evidence and ranking.

## Demo mode (no keys required)

No provider keys are required to run a complete product flow.

When provider config is missing or unavailable:

- retrieval still runs
- citations stay visible and clickable
- Explain still records retrieval/ranking decisions

Use this mode for offline tests, clean-laptop demos, and YC recordings.

## What you'll see

Placeholders for screenshots:

- `docs/images/01-upload-ingest.png` (Upload + Library + Index)
- `docs/images/02-answer-citations.png` (Answer + pinned source cards)
- `docs/images/03-explain-ranking.png` (Explain summary + ranking decisions)

## Calm comparison (facts only)

This demo intentionally favors reliability over improvisation:

| Concern | Typical pattern | This demo |
|---|---|---|
| Control flow | Dynamic prompt/chains | Replayable program flows |
| Evidence | Best-effort references | Citation-first, source cards always visible |
| Debuggability | Opaque internals | Explicit Explain records and ranking decisions |
| Regression safety | Manual spot checks | Offline smoke + golden eval + CI gate |
| Failure behavior | Vague fallback text | Honest no-support / provider-fallback messages |

## Environment variables

Use `.env.example` as the template.

Core vars:

- `N3_ANSWER_PROVIDER`
- `N3_ANSWER_MODEL`
- `NAMEL3SS_OPENAI_API_KEY` or `OPENAI_API_KEY`
- `NAMEL3SS_ANTHROPIC_API_KEY` or `ANTHROPIC_API_KEY`

Install strategy:

```bash
python3 -m pip install --upgrade namel3ss
```

Optional pin:

```bash
python3 -m pip install "namel3ss==<version>"
```

Details: `docs/configuration.md`.

## Deterministic tests

Smoke test:

```bash
cd apps/rag-demo
pytest -q tests/test_rag_demo_smoke.py
```

Eval regression gate:

```bash
cd apps/rag-demo
python3 eval/run_eval.py --offline --fail-on-regression --baseline eval/report_baseline.json
```

Outputs:

- `eval/golden.json`
- `eval/report.json`
- `eval/report_baseline.json`

Metric details: `docs/evaluation.md`.

## CI gate

Workflow: `.github/workflows/rag-demo-ci.yml`

Runs:

1. `n3 check app.ai`
2. deterministic smoke test
3. deterministic eval regression gate (offline)

## Supported inputs

Upload supports:

- PDF (`application/pdf`)
- Markdown (`text/markdown`)
- Plain text (`text/plain`)

Optional URL snapshot flow (allowlisted + deterministic):

```bash
export RAG_URL_ALLOWLIST=example.com,docs.example.com
python3 scripts/fetch_url_snapshot.py https://docs.example.com/page
```

Upload generated snapshot `.txt` files through the same ingestion flow.

Details: `docs/url-snapshots.md`.

## One-command run paths

Local Studio:

```bash
cd apps/rag-demo
n3 studio app.ai
```

Container:

```bash
cd apps/rag-demo
docker compose up --build
```

Open `http://localhost:7340`.

Hosted deploy (Render): `docs/deploy-render.md`.

## Troubleshooting

- Port `7340` busy: `lsof -nP -iTCP:7340 -sTCP:LISTEN` and stop the conflicting process.
- Python missing: install Python 3.11+ and ensure `python3` is on `PATH`.
- Missing provider vars: leave provider fields empty for demo mode, or set provider/model/key triplet.
- Source blocked during indexing: open library quality note, upload cleaner source, then re-index.

## Read and extend

- `docs/read-the-code.md`
- `docs/how-rag-works-in-namel3ss.md`
- `docs/determinism-and-citations.md`
- `docs/evaluation.md`
- `docs/how-to-extend-the-demo.md`
- `docs/recipes/add-source-type.md`
- `docs/recipes/add-eval-metric.md`
- `docs/recipes/customize-ui-copy.md`
- `docs/yc-faq.md`
- `docs/yc-demo-script.md`
- `CHANGELOG.md`
- `ROADMAP.md`
