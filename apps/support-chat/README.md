# Support Chat (namel3ss)

A production-grade customer-support chat app built with namel3ss. It provides a chat UI, persists conversation history, and exposes a deterministic knowledge-base search tool backed by `kb.json`.

## Features
- Customer support chat UI with history, composer, and thinking indicator
- Deterministic KB search tool (`search_kb`) using local data
- Persisted conversation history with TTL cleanup
- Real OpenAI provider support with graceful fallback when keys are missing

## Project layout
- `app.ai`: main namel3ss application (spec, records, flows, UI, AI)
- `kb.json`: local FAQ data used by the KB tool
- `search_kb.py`: deterministic KB lookup implementation
- `tools/search_kb.py`: thin wrapper used by tool bindings
- `.namel3ss/tools.yaml`: tool bindings + sandboxing (used by runtime)
- `tools.yaml`: convenience mirror of tool bindings
- `smoke.sh`: CI-safe smoke test script

## Setup

Install namel3ss (CLI: `n3`):
```
pip install namel3ss
```

Set your OpenAI API key (either name works):
```
export NAMEL3SS_OPENAI_API_KEY="your-key"
# or
export OPENAI_API_KEY="your-key"
```

## Run

From this folder:
```
cd apps/support-chat
n3 app.ai check
n3 app.ai studio
```

Open the Studio URL printed in the terminal (localhost).

## Use the app
1. Click **Start Over** to create a new system marker.
2. Type your question in the chat composer and send.
3. The assistant will use the KB tool for factual answers and fall back gracefully if an API key is missing.

## Smoke test
The smoke test is deterministic and CI-safe. It avoids external calls by unsetting API keys and uses SQLite persistence.
```
./smoke.sh
```

## Notes
- `kb.json` is used by the tool; the `seed_kb` flow inserts the same entries into the KBEntry record on first run.
- If you want to validate real model calls in CI, set `NAMEL3SS_OPENAI_API_KEY` before running the smoke test.

## Good first issues
- Add a simple feedback flow with a `Feedback` record and "Was this helpful?" buttons.
- Add an analytics page that summarizes the most common questions.
- Add a handoff flow for escalation to human agents.
