# Evaluation and Regression Workflow

Deterministic quality checks live under `apps/rag-demo/eval/`.

## Artifacts

- `eval/golden.json`: golden questions and expected evidence constraints
- `eval/report_baseline.json`: committed baseline metrics
- `eval/report.json`: generated local run report

## Run eval

```bash
cd apps/rag-demo
python3 eval/run_eval.py --offline --fail-on-regression --baseline eval/report_baseline.json
```

## Metrics

- `citation_coverage`: sourced cases returned citations
- `citation_correctness`: returned citations are selected retrieval candidates
- `expected_citation_constraints`: expected source/page constraints are met
- `helpfulness`: expected themes appear in answer or cited snippets
- `no_source_behavior`: no-support cases fail gracefully
- `deterministic_replay`: repeated query produces same answer/citations

## Add a new golden case

1. Edit `eval/golden.json`.
2. Add `id`, `question`, expected themes, citation constraints, and ambiguity note.
3. Run eval offline.
4. Review `eval/report.json`.

## Update baseline deliberately

```bash
cd apps/rag-demo
python3 eval/run_eval.py --offline
cp eval/report.json eval/report_baseline.json
```

Only update baseline when changes are intentional and reviewed.
