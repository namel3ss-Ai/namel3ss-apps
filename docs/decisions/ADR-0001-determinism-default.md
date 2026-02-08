# ADR-0001: Determinism by Default

Status: Accepted
Date: 2026-02-07

## Context

Ungoverned nondeterminism makes incident response and regression analysis unreliable.

## Decision

Determinism is the default operating mode for reference implementations and constitutional flows.

## Alternatives Considered

1. Best-effort determinism as guidance only
- Rejected: no enforceable reliability contract.

2. Determinism only in tests, not runtime behavior
- Rejected: runtime drift still undermines operator trust.

## Consequences

- Strong replay and CI discipline
- Slower but safer iteration cadence
