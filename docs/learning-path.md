# Canonical Learning Path

Goal: teach governed AI engineering progressively, from fundamentals to stewardship.

## Level 1 - Beginner: Determinism Fundamentals

Audience:
- engineers new to governed AI systems

Outcomes:
- explain deterministic replay in plain language
- run reference apps in offline deterministic mode
- identify citation and no-support behavior in UI

Path:
1. Read `docs/why-namel3ss-exists.md`
2. Read `docs/constitution.md` (Articles I-III)
3. Run `apps/rag-demo` in demo mode
4. Run smoke + eval gates locally

## Level 2 - Intermediate: Governed App Construction

Audience:
- product and platform engineers building production paths

Outcomes:
- design explicit control boundaries for model usage
- add/modify retrieval and explain surfaces without breaking invariants
- maintain golden eval sets and regression baselines

Path:
1. Read `docs/read-the-code.md` in `apps/rag-demo/docs`
2. Read `docs/anti-patterns.md`
3. Add one eval case and pass invariant gates
4. Update one reference flow with explicit failure semantics

## Level 3 - Advanced: Invariants and Stewardship

Audience:
- maintainers and architectural owners

Outcomes:
- map constitutional principles to machine checks
- author ADRs for breaking/strategic changes
- evaluate amendment proposals using evidence requirements

Path:
1. Read `docs/stewardship.md`
2. Read `docs/decisions/` ADRs
3. Extend `invariants/check_invariants.py` with one new constitutional check
4. Propose a mock amendment with full evidence package

## Reference Implementations (Constitutional Archetypes)

Each archetype must:
- comply with `docs/constitution.md`
- use shared eval report contracts
- pass constitutional invariant gate in CI

1. RAG Demo (`apps/rag-demo`) - Active
2. Support Inbox (derived from support chat patterns) - Planned
3. Knowledge Base Assistant - Planned
4. Compliance Assistant - Planned

The RAG demo is proof of constitutional behavior, not a special case.
