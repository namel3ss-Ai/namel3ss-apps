# Recipe: Add a New Source Type

Goal: add a source type without breaking determinism.

## Steps

1. Accept MIME type in `app.ai` upload intake.
2. Map source type label deterministically in `sync_library`.
3. Keep ingestion through runtime `ingestion` pipeline.
4. Keep source status updates explicit (`uploaded/indexed/blocked`).
5. Add at least one offline eval case in `eval/golden.json`.

## Guardrails

- Do not bypass ingestion pipeline.
- Do not add random IDs or time-based ordering.
- Ensure source list ordering remains stable for equal inputs.

## Verify

```bash
cd apps/rag-demo
n3 check app.ai
pytest -q tests/test_rag_demo_smoke.py
python3 eval/run_eval.py --offline --fail-on-regression --baseline eval/report_baseline.json
```
