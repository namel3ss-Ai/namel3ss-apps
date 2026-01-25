# Support Chat (namel3ss)

A fully native AI support assistant built in the [namel3ss](https://github.com/namel3ss-Ai/namel3ss) DSL — no Python, no plugins.

## Features
- 💬 Chat UI with AI + KB fallback
- 🧠 OpenAI support via `run agent`
- 🧾 Session history
- 🗂️ Inline KB seeding
- 👍 Feedback buttons

## Run the App

```bash
pip install namel3ss

export N3_IDENTITY_ID=demo-user
export OPENAI_API_KEY=sk-...  # optional

cd apps/support-chat
n3 run app.ai
```

Open:
```
http://localhost:7340/?page=SupportChat
```

## Test

```bash
./tests/smoke.sh
```

## Screenshot
(Optional: add image of app in browser)
