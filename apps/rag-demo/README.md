# RAG Demo (namel3ss)

A complete, end-to-end Retrieval-Augmented Generation demo built for the namel3ss runtime. It uses only runtime pipelines for uploads, ingestion, retrieval, and answering. The UI exposes citations, PDF preview with highlights, and an explain view.

## What This Demo Shows
- Upload a PDF and ingest it with the runtime quality gate.
- Ask questions in a chat UI.
- Receive cited answers (citations are enforced by the runtime).
- Click citations to open PDF page previews with highlight overlays.
- Inspect a deterministic explain bundle for retrieval and answer validation.

## Install / Upgrade namel3ss

Install the exact version:

```bash
pip install namel3ss==0.1.0a13
```

Or upgrade to latest:

```bash
pip install namel3ss --upgrade
```

## Run

```bash
cd apps/rag-demo
n3 studio app.ai
```

Studio launches and renders the app UI in the browser.

## How To Use

1. Upload `assets/sample.pdf` using the Upload control.
1. Click `Run ingestion`.
1. Ask a question such as `runtime enforces citations`.
1. Or ask `what does this demo show`.
1. Review the answer and citations.
1. Click `Open page` in a citation to preview the PDF and highlights.
1. Scroll to the Explain section to inspect retrieval mode, candidate counts, and citation validation.

## LLM Configuration (Runtime-Side)

- The runtime reads LLM provider and model from environment configuration.
- The app does not contain prompts or model tuning; the runtime constructs prompts and enforces citations.

Common environment variables:
- `N3_ANSWER_PROVIDER` and `N3_ANSWER_MODEL`
- Provider keys such as `NAMEL3SS_OPENAI_API_KEY` (or `OPENAI_API_KEY`)

Example (OpenAI):

```bash
export N3_ANSWER_PROVIDER=openai
export N3_ANSWER_MODEL=gpt-4o-mini
export NAMEL3SS_OPENAI_API_KEY="sk-..."
```

## Testing Notes

The smoke test runs deterministically without external network calls. It uses the retrieval pipeline to build a stable answer and citations for validation.
