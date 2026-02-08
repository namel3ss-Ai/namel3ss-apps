# ADR-0003: Explainability Is a Product Surface

Status: Accepted
Date: 2026-02-07

## Context

Teams need to understand retrieval and ranking behavior during normal operation, not only during incidents.

## Decision

Explain data is modeled as first-class records and rendered as an optional but supported user surface.

## Alternatives Considered

1. Keep explain data internal-only
- Rejected: increases operator dependence on hidden tooling.

2. Generate free-form explain text only
- Rejected: weak machine-checkability and unstable structure.

## Consequences

- additional schema and UI overhead
- materially better governance and onboarding
