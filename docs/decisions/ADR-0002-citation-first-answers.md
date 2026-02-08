# ADR-0002: Citation-First Answer Contract

Status: Accepted
Date: 2026-02-07

## Context

Users must be able to verify claims without reading internal traces.

## Decision

Evidence-bearing answers must include citations or explicitly declare no support.

## Alternatives Considered

1. Optional citations for "high confidence" answers
- Rejected: confidence is not evidence.

2. Citations only in debug mode
- Rejected: trust surface must exist in normal operation.

## Consequences

- UI and runtime design prioritize provenance
- evaluation gates include citation coverage and correctness
