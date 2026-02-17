# RAG Demo Stabilization Roadmap

Date: 2026-02-15
Owner: rag-demo app + namel3ss runtime

## Goal
Ship a production-first `rag-demo` with a user-focused chat surface, deterministic indexing/retrieval behavior, and no studio/debug leakage in production.

## Phase 1 (Done)
- Move upload + source selection into the chat experience (`Chat` page sidebar).
- Add fallback-safe answer handling for weak/empty PDF extraction.
- Keep assistant trust/actions aligned with grounded citations.
- Keep app implementation in Namel3ss DSL flows (`.ai`) for product logic.

## Phase 2 (Done)
- Mark developer pages as debug-only:
  - `Library`
  - `Tuning`
  - `Explain`
- Production runtime now exposes only user page(s) while Studio still shows developer tooling.
- Chat page uses a wider main chat region with citations moved to right drawer.

## Phase 3 (Done)
- Fix PDF probe false-block behavior in runtime ingestion:
  - `null_bytes` / UTF-8 probe blockers now apply to text-like uploads, not known PDF payloads.
  - OCR fallback can proceed for PDF uploads that previously got blocked too early.

## Phase 4 (Validation Checklist)
- App parse/lint/manifest:
  - `n3 check apps/rag-demo/app.ai`
- Production mode page surface check:
  - `n3 run apps/rag-demo/app.ai --port 7360 --no-open --production`
  - `curl -sS http://127.0.0.1:7360/api/ui | jq '.mode, (.pages|map(.name))'`
- Renderer registry health:
  - `curl -sS http://127.0.0.1:7360/api/renderer-registry/health | jq .ok,.registry.ok,.parity.ok`
- Ingestion regression tests:
  - `pytest tests/runtime/test_ingestion_quality_gate.py tests/ingestion/test_fallback.py -q`

## Remaining Platform Follow-ups (if still seen)
- If `Run History / Audit Viewer` appears in production, verify launch mode is production and not studio.
- If `N3E_RENDERER_REGISTRY_INVALID` appears, capture:
  - `GET /api/renderer-registry/health`
  - runtime startup logs
  - `namel3ss --version`
  and escalate as runtime/platform defect.

## Non-negotiables
- App behavior changes stay in Namel3ss DSL (`.ai`) unless runtime core fix is required.
- No `.sh` workflow dependency is required for app behavior.
- Every newly found limitation must be reported in a structured incident note with repro and expected vs actual behavior.
