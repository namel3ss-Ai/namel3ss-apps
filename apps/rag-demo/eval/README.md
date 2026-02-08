# Eval Directory

This folder contains deterministic evaluation artifacts used by local runs and CI regression gates.

## Files

- `golden.json`: curated cases with expected themes and citation constraints.
- `run_eval.py`: offline-capable evaluator.
- `report_baseline.json`: committed baseline metrics.
- `report.json`: generated per-run report (ignored in git).

## Local run

```bash
cd apps/rag-demo
python3 eval/run_eval.py --offline --fail-on-regression --baseline eval/report_baseline.json
```

## Determinism guarantees

- sorted case execution by `id`
- stable JSON serialization (`sort_keys=True`)
- offline default (no provider calls)
- deterministic replay check for repeated query

See `docs/evaluation.md` for the full update workflow.
