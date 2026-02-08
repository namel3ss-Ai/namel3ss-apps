# Recipe: Customize UI Copy Safely

Goal: change wording without weakening trust signals.

## Keep these invariants

- citations are always visible on answer surfaces
- no-support states are explicit and honest
- provider fallback states are explicit and honest
- Explain remains optional but complete

## Where to edit

File: `app.ai`

- `Notice` messages for action outcomes and failures
- section titles/text in the Chat and Explain tabs
- button/action labels in Library and first-run flow

## Copy style

- short sentences
- calm confidence
- no internal jargon on primary surfaces
- no bluffing language

## Verify

```bash
cd apps/rag-demo
n3 check app.ai
pytest -q tests/test_rag_demo_smoke.py
```
