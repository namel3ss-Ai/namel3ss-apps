# Recipe: Add a New Eval Metric

Goal: extend quality gates without making runs nondeterministic.

## Steps

1. Edit `eval/run_eval.py` and add a pure function metric.
2. Derive metric only from deterministic artifacts:
   - golden case data
   - retrieval candidates
   - answer text/citations
3. Add metric to report output with stable key ordering.
4. Update `eval/report_baseline.json` only after review.

## Guardrails

- No network calls in default eval path.
- No randomness or clock-based logic.
- Keep metric definitions easy to explain in `docs/evaluation.md`.

## Verify

```bash
cd apps/rag-demo
python3 eval/run_eval.py --offline --report eval/report.json
python3 eval/run_eval.py --offline --fail-on-regression --baseline eval/report_baseline.json
```
