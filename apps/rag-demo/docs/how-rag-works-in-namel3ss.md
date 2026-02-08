# How RAG Works in namel3ss

This app is a deterministic RAG reference implementation with four product steps:

1. Upload: users add PDF, Markdown, or TXT files.
2. Ingest: runtime ingestion builds indexed chunks and applies quality gates.
3. Ask: the app runs deterministic query preparation and hybrid retrieval.
4. Verify: every answer is backed by citations that can open source previews.

## What this demo proves

This app does not treat RAG as a prompt experiment. It treats RAG as a program:

- control flow is explicit
- ranking rules are explicit
- citations are explicit
- failure modes are explicit

The model is used inside governed steps. It does not decide the product contract.

## Runtime Pipelines

Core RAG behavior remains runtime-native:

- `ingestion`: quality gate and index build
- `retrieval`: candidate retrieval over indexed chunks
- `answer`: grounded answer generation with citation validation (when provider is configured)

## Retrieval and Ranking Flow

For each question, the app performs:

1. Query normalization (lowercase, punctuation/whitespace cleanup).
2. Deterministic route detection (`lookup`, `definition`, `summary`, `comparison`).
3. Semantic retrieval from the runtime retrieval pipeline.
4. Lexical retrieval from keyword overlap against chunk keywords.
5. Stable merge/rerank with explicit policy:
   - hybrid + weighted sources
   - semantic + weighted sources
   - lexical-only fallback
6. Small-to-big context expansion (neighbor chunks with window `1`).

All decisions are recorded into Explain records:

- `RetrievalCandidate`
- `RankingDecision`
- `ExplainSummary`
- `ExplainCandidate`

## Source-First Answers

Answer UX is designed for verification:

- citations are pinned as cards under each answer
- citation IDs are stable and deterministic
- chat citations support source preview/highlight UX
- if provider is unavailable, the app still returns citations-only mode
