# Constitutional Invariants

This directory translates constitutional principles into executable checks.

## Mapping: Principle -> Check -> Failure Mode

| Principle | Check ID | Enforcement | Failure Mode | Recovery |
|---|---|---|---|---|
| Article I: Determinism default | `deterministic_replay_required` | `invariants/check_invariants.py` reads eval report metric `deterministic_replay` | CI and local gate fail with explicit reason | run offline eval, inspect drift, update logic or baseline intentionally |
| Article I: No nondeterminism without opt-in | `nondeterministic_tokens_forbidden` | scans `app.ai` for forbidden nondeterministic tokens unless explicit opt-in flag is set | gate fails and reports matched tokens | remove nondeterministic construct or add explicit opt-in context |
| Article III: Citation-first answers | `citation_contract_required` | verifies `citation_coverage` and `citation_correctness` are 1.0 in eval report | gate fails and prints metric deltas | fix retrieval/answer/citation wiring, regenerate eval report |
| Article VI: No silent degradation | `explicit_failure_modes_required` | checks app contract strings/modes for `provider_fallback`, `citations_only`, `no_support`, explicit notices | gate fails with missing mode/message list | add explicit mode fields and user-visible notices |
| Governance integrity | `constitution_present` | validates constitution document exists and includes mandatory constitutional sections | gate fails with missing sections | restore constitution sections or amend through process |

## Violation Handling Contract

When a check fails:

1. execution stops (non-zero exit)
2. failure reasons are emitted as machine-readable JSON
3. recovery guidance is included per failed check

No silent pass is allowed.
