# Support Chat (namel3ss)

A fully native customer support chat app built in pure namel3ss grammar (spec 1.0). It runs without external tools, persists conversations, and keeps behavior deterministic while optionally using OpenAI for responses.

## Features
- Chat UI with persisted messages and a typing indicator
- Session history via `ConversationSession`
- Deterministic KB matching (exact-match against seeded FAQ entries)
- Optional OpenAI responses when a key is present
- Feedback buttons (👍/👎) stored in `Feedback`
- Search history (exact-match search, results stored in `SearchResult`)

## Setup

Install the CLI:
```
pip install namel3ss
```

Set identity (required by flows):
```
export N3_IDENTITY_ID=demo-user
```

Optionally set OpenAI for AI responses:
```
export OPENAI_API_KEY=sk-...
```

## Run

From this folder:
```
cd apps/support-chat
n3 app.ai check
n3 run app.ai
```

Open the URL printed by the CLI. If needed:
```
http://127.0.0.1:7340/?page=SupportChat
```

## Testing
```
./smoke.sh
```

## Notes
- KB entries are seeded inline on first run; no external data files are required.
- Search is exact-match due to current DSL string constraints.
- Upload UI is not available in the current UI grammar; the `process_upload` flow stores metadata if invoked via API/CLI.

## Good first issues
- Add session renaming/editing.
- Add a lightweight analytics page with counts by session.
- Add “helpful” summaries for search results.
