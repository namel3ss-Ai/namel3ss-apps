# Anti-Patterns namel3ss Rejects

This list is normative for governed applications.

## 1) Adaptive prompt mutation as control flow

Rejected behavior:
- runtime behavior changes through hidden prompt rewriting without explicit program changes

Why rejected:
- cannot be reliably reviewed, diffed, or replayed

Approved alternative:
- deterministic program branches with explicit contracts

## 2) Hidden agent loops

Rejected behavior:
- model-driven retries/tool loops that are not visible in program flow

Why rejected:
- prevents clear reasoning about failure boundaries and cost behavior

Approved alternative:
- explicit bounded loops encoded in language/runtime contracts

## 3) Best-effort truth

Rejected behavior:
- presenting unsupported claims when retrieval evidence is weak or absent

Why rejected:
- harms user trust and breaks auditable product behavior

Approved alternative:
- explicit no-support responses and actionable recovery guidance

## 4) Silent retries and silent degradation

Rejected behavior:
- failing provider paths that auto-fallback without user-visible disclosure

Why rejected:
- destroys operator visibility and post-incident traceability

Approved alternative:
- explicit mode/state labels and visible notices for fallback behavior

## 5) Opaque scoring logic

Rejected behavior:
- ranking/selection based on implicit heuristics not represented in explain data

Why rejected:
- governance is impossible when decisions cannot be inspected

Approved alternative:
- stable, explainable scoring with recorded decision reasons
