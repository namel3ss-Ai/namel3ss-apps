# namel3ss-apps

This repository contains demo and reference applications built using the [namel3ss](https://github.com/namel3ss-Ai/namel3ss) AI-native DSL.

## Governance and Long-Term Contracts

- Constitution: `docs/constitution.md`
- Anti-patterns: `docs/anti-patterns.md`
- Learning path: `docs/learning-path.md`
- Stewardship and succession: `docs/stewardship.md`
- Decision log (ADRs): `docs/decisions/`
- Invariant gate: `invariants/check_invariants.py`

## Apps

### 📞 Support Chat
A fully native, deterministic customer support assistant with:
- Inline KB matching
- Session history
- Optional OpenAI fallback
- UI feedback

→ [apps/support-chat/README.md](apps/support-chat/README.md)

### 📚 Deterministic RAG Demo
A full Retrieval-Augmented Generation app in a single `.ai` file with:
- Document ingestion
- Deterministic retrieval
- AI answers grounded in retrieved context
- Explainable execution

→ [apps/rag-demo/README.md](apps/rag-demo/README.md)

## How to Contribute

1. Clone this repo
2. Install `namel3ss`: `pip install namel3ss`
3. Navigate to an app and run: `n3 run app.ai`
