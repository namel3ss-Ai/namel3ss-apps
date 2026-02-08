# YC Demo Script (60-90 seconds)

## Version A: Demo mode (no keys)

1. Open app: "This is a deterministic RAG reference app."
2. Upload `sample.pdf`: "Single flow, no hidden backend steps."
3. Click `Update library`, then `Run guided demo path`.
4. Point to generated answer: "Even without keys, retrieval still runs."
5. Open citation cards: "Every claim is source-backed."
6. Open Explain tab: "Ranking decisions and selection order are explicit."
7. Show CI/eval mention: "Regression gates keep this behavior stable."

## Version B: Live provider mode (keys set)

1. Mention provider vars are configured.
2. Run same flow (Upload -> Update library -> Run ingestion).
3. Ask a second question in chat.
4. Show answer quality and the same citation verification loop.
5. Open Explain summary and point to citation validation status.

## Talking points

- Every claim is cited.
- Explain shows retrieval decisions, not black-box output.
- Deterministic regression gates protect quality over time.
- Demo mode guarantees a reliable fallback for every environment.
