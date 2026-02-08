# namel3ss Constitution

Status: Active
Scope: Language, runtime, Studio, templates, contracts, and reference apps

## Preamble

namel3ss exists to build AI systems that can be governed like critical infrastructure.

The platform is designed for environments where failure is expensive: regulated operations, customer trust surfaces, and long-lived knowledge systems.

This Constitution defines permanent guarantees, non-negotiable boundaries, and the process for change.

Features may change. This document is the stability contract.

## Article I - Determinism Is a First-Class Invariant

1. Equal inputs must produce equal outputs unless nondeterminism is explicitly declared.
2. Ordering that affects behavior must be stable and inspectable.
3. Replay is a required capability, not an optional debugging feature.
4. Deterministic checks must run in CI for reference implementations.

Permanent tradeoff:
- We prefer predictable behavior over opportunistic adaptation.

## Article II - AI Boundaries Must Be Explicit

1. Models operate inside bounded program steps.
2. Control flow is defined by code and contracts, not by free-form model decisions.
3. Hidden loops, implicit retries, and silent tool selection are forbidden in governed modes.

Permanent tradeoff:
- We limit autonomy to preserve inspectability and legal accountability.

## Article III - Citations and Provenance Are Product Requirements

1. Claims that require evidence must carry citations.
2. Citation objects must remain human-verifiable (source, location, snippet when available).
3. If support is missing, the system must say so explicitly.

Permanent tradeoff:
- We reject fluent but unverifiable answers as a default product behavior.

## Article IV - Explainability Over Opaque Optimization

1. Systems must expose retrieval and selection decisions in human-readable form.
2. Explain surfaces are product interfaces, not internal debugging artifacts.
3. Changes that improve headline quality while reducing explainability are disallowed by default.

Permanent tradeoff:
- We optimize for legibility under audit, not only benchmark peaks.

## Article V - Regression Prevention Over Unbounded "Learning"

1. Baselines, golden sets, and regression gates are mandatory for reference apps.
2. Behavioral changes must be intentional, reviewable, and attributable to a specific change.
3. Silent behavior drift is a defect.

Permanent tradeoff:
- We accept slower iteration velocity to preserve long-term reliability.

## Article VI - Failure Must Be Honest and Visible

1. Invariant violations must stop execution of the governed path.
2. Failure reasons must be inspectable by humans and machines.
3. Recovery steps must be explicit; no silent degradation.

Permanent tradeoff:
- We choose explicit failure over hidden partial success.

## Article VII - Human-Readable Governance

1. Major architecture decisions must be recorded in the decision log.
2. Rejected alternatives must be documented when they affect safety or predictability.
3. Governance documents must be understandable by maintainers who did not author the system.

Permanent tradeoff:
- We treat institutional memory as core infrastructure.

## Non-Amendable Clauses

The following clauses cannot be removed without declaring the result a different system:

- Determinism as the default governing mode (Article I)
- Explicit AI boundaries (Article II)
- Evidence-first claim policy (Article III)
- Honest, explicit failure semantics (Article VI)

If these are removed, downstream users must be told they are no longer using constitutional namel3ss.

## Amendment Process

Amendments are allowed only for additive clarity or demonstrable safety improvements.

### Who may propose

- Language stewards
- Runtime stewards
- Archetype stewards

### Required evidence

Every amendment proposal must include:

1. Problem statement and affected constitutional article(s)
2. At least one rejected alternative and why it fails
3. Invariant impact analysis (principle -> enforcement impact)
4. Migration plan for existing reference implementations
5. Rollback plan and blast-radius assessment

### Approval threshold

- Unanimous approval by language and runtime stewards
- Majority approval by archetype stewards
- Green constitutional invariant gate in CI

### Prohibited amendments

- Amendments that make determinism optional by default
- Amendments that allow uncited evidence-required answers by default
- Amendments that permit silent degradation in governed flows

## Principle-to-Enforcement Binding

The executable mapping is maintained in `invariants/README.md` and enforced by `invariants/check_invariants.py`.

A constitutional principle without an executable check is incomplete.
