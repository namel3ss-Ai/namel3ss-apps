# Determinism and Citations

Determinism is the product contract for this demo.

Design stance: programs control AI behavior. Models fill bounded tasks inside that program.

## What is deterministic here

- stable ordering for retrieval candidates and final citations
- deterministic query normalization and routing
- deterministic reranking and tie-breaking
- deterministic replay checks in smoke + eval
- fixed offline test mode (no external model calls)

## Why citations are first-class

Citations are not decoration. They are the trust surface:

- every answer path is expected to produce source references when support exists
- no-source responses are explicit and actionable
- citation cards retain chunk IDs and page metadata for direct verification

## Graceful answer modes

The app records answer mode explicitly:

- `answer`: provider-backed grounded answer
- `citations_only`: explicit offline mode
- `provider_fallback`: provider unavailable, deterministic citation fallback
- `no_support`: no supporting chunks found in selected scope

This keeps behavior inspectable in production and replay.

## Regression gates

`eval/run_eval.py` enforces deterministic quality gates:

- citation coverage
- citation correctness
- expected citation constraints
- helpfulness heuristic over golden themes
- no-source behavior correctness
- deterministic replay consistency

CI fails when threshold violations or baseline regressions are detected.
