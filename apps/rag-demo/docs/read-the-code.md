# Read the Code (5-minute map)

If you are evaluating this as a production reference, start here.

## 1) Ingestion and source quality

File: `app.ai`

- Flow: `ingest_selected`
- Flow: `ingest_document`
- Runtime pipeline used: `ingestion`

What to look for:

- quality gate outcomes become explicit source statuses (`Indexed` or `Blocked`)
- no hidden side-effects: source records are rewritten deterministically
- blocked sources keep clear quality notes for users

## 2) Retrieval and selection

File: `app.ai`

- Flow: `ask_question`
- Helper flow: `prepare_query_profile`
- Runtime pipeline used: `retrieval`

What to look for:

- query normalization and deterministic route hints (`lookup`, `summary`, `comparison`, `definition`)
- hybrid retrieval merge: semantic candidates + lexical overlap rows
- stable selection order and explicit top-k policy
- all ranking decisions are recorded, not implied

## 3) Answer generation and validation

File: `app.ai`

- Flow: `ask_question`
- Runtime pipeline used: `answer` (when provider mode is available)

What to look for:

- deterministic offline path (`citations_only`) when no provider is configured
- provider fallback path with explicit user messaging (no bluffing)
- citation ordering is stable and persisted in `Answer` and `CitationCard`

## 4) Explain bundle formation

File: `app.ai`

Records populated during each question:

- `QueryProfile`
- `RetrievalCandidate`
- `RankingDecision`
- `ExplainCandidate`
- `ExplainSummary`

What to look for:

- ranking reasons are explicit text, not hidden in model output
- retrieval mode, ordering, and citation status are visible
- Explain is optional in UX, but complete in data

## 5) Deterministic tests and quality gates

Files:

- `tests/test_rag_demo_smoke.py`
- `eval/run_eval.py`
- `eval/golden.json`
- `.github/workflows/rag-demo-ci.yml`

What to look for:

- smoke test runs fully offline
- eval report is deterministic and baseline-gated
- CI fails when determinism or citation quality regresses

## 6) Deployment and local reproducibility

Files:

- `Dockerfile`
- `docker-compose.yml`
- `docs/deploy-render.md`

What to look for:

- same app contract in local studio, Docker, and hosted deploy
- no provider keys required for a usable demo path
- deterministic persistence path (`N3_PERSIST_ROOT`)
