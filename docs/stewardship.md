# Stewardship and Succession Model

## Steward Roles

### 1) Language Stewards

Authority:
- DSL grammar and semantic contract
- constitutional compatibility of language changes

Duties:
- prevent ambiguous constructs that weaken inspectability
- maintain backwards-compatible migration paths where possible

### 2) Runtime Stewards

Authority:
- execution engine, invariant enforcement, CI/runtime contracts

Duties:
- maintain deterministic and auditable runtime behavior
- ensure violation handling is explicit and machine-readable

### 3) Archetype Stewards

Authority:
- reference implementations and teaching quality

Duties:
- keep archetypes constitutional and reproducible
- maintain evaluation baselines and user-facing failure honesty

## Succession Rules

1. No single-steward critical paths
- at least two maintainers must understand each critical subsystem.

2. Steward handover packets
- each outgoing steward leaves a concise handover: open risks, pending ADRs, and rollback procedures.

3. Release authority
- constitutional changes require steward quorum per `docs/constitution.md`.

4. Incident authority
- runtime stewards may block releases on invariant failures without escalation delay.

## Compatible Fork Ethics

A fork may call itself constitution-compatible only if it preserves:
- default determinism
- explicit AI boundaries
- citation requirements for evidence-bearing claims
- explicit, inspectable failure semantics

A fork must signal divergence clearly when these guarantees are changed.

Minimum signaling requirements for divergent forks:
1. public statement of diverged constitutional clauses
2. renamed compatibility profile in docs/CI output
3. migration guidance for users expecting constitutional guarantees
