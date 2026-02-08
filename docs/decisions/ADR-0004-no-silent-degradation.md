# ADR-0004: No Silent Degradation

Status: Accepted
Date: 2026-02-07

## Context

Silent fallbacks hide quality and operational risk.

## Decision

When behavior degrades (for example provider failure), the system must signal mode changes explicitly in state and user-visible notices.

## Alternatives Considered

1. Silent fallback for smoother UX
- Rejected: creates false confidence and poor incident observability.

2. Hard fail for every upstream issue
- Rejected: unnecessary downtime when deterministic fallback is safe and explicit.

## Consequences

- users and operators see truthful mode transitions
- product behavior remains inspectable under degraded conditions
