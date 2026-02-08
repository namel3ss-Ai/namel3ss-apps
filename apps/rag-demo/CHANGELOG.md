# Changelog

All notable changes to `apps/rag-demo` are documented in this file.

## [2026-02-07] Phase 5 - Credibility and Adoption Polish

### Added

- `docs/read-the-code.md` with a 5-minute architecture map.
- `docs/yc-faq.md` for skeptical partner questions.
- `docs/recipes/` extension guides:
  - `add-source-type.md`
  - `add-eval-metric.md`
  - `customize-ui-copy.md`
- `ROADMAP.md` with post-Phase-5 priorities.

### Changed

- Rewrote app UI copy for calmer, product-grade wording.
- Added a compact trust surface in Chat: source count + citation status + retrieval mode.
- Reframed README around trust, determinism, citations, and eval gates.
- Added factual contrast section (replayable programs vs dynamic prompt chaining).

### Kept intentionally stable

- Core runtime pipelines: `ingestion`, `retrieval`, `answer`.
- Deterministic smoke and offline eval gates.
- Citations-first behavior and explain records.

## [2026-02-07] Phase 4 - Product Packaging and Reliability

- Demo mode defaults and first-run resilience.
- Offline deterministic smoke/eval workflow.
- Docker + Render deployment docs.
- URL snapshot tooling and deterministic manifest flow.
