# YC FAQ (skeptical partner edition)

## Why not just use a quick RAG chain?

Quick chains optimize for first success, not reliable behavior over time.
This demo optimizes for replayability, explicit evidence, and regression gates.

## LLMs are flaky. How is this different?

The product contract does not depend on model behavior alone.
Retrieval, ranking order, citation wiring, and fallback modes are controlled by code paths that replay exactly.

## Isn't this extra engineering work?

Yes, and it is deliberate.
You trade a small amount of upfront structure for lower production risk:

- fewer support escalations from unverifiable answers
- faster incident debugging (Explain records)
- safer iteration (offline eval regression gate)

## What happens when provider keys are missing or the API is down?

The app remains usable in citations-only mode:

- retrieval still runs
- source cards remain clickable
- Explain still records decisions

No silent degradation and no invented confidence.

## Can a team actually onboard to this quickly?

Yes. The intended path is:

1. 5-minute quickstart in `README.md`
2. architecture skim in `docs/read-the-code.md`
3. deterministic tests via `pytest` and `eval/run_eval.py`

## Is this only for demos?

No. It is a reference for shipping.
The same constraints that make demos credible (determinism, citations, eval gates) are what reduce risk in production.

## What does this prove in 2 minutes?

- every answer is source-verifiable
- failure modes are honest
- behavior is repeatable and test-gated
