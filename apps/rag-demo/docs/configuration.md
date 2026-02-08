# Configuration

## Provider and model

`N3_ANSWER_PROVIDER` and `N3_ANSWER_MODEL` configure runtime answer generation.

Common provider values:

- `openai`
- `anthropic`
- empty (demo mode)

## API key naming

OpenAI keys:

- `NAMEL3SS_OPENAI_API_KEY`
- `OPENAI_API_KEY`

Anthropic keys:

- `NAMEL3SS_ANTHROPIC_API_KEY`
- `ANTHROPIC_API_KEY`

Set one matching key name for the selected provider.

## Offline / demo mode behavior

If provider settings are missing or unavailable:

- app continues with retrieval
- answer path degrades to citations-first mode
- explain records still capture retrieval and ranking

This is the default mode for deterministic tests and YC recording safety.

## Latest vs pinned installs

Recommended:

```bash
python3 -m pip install --upgrade namel3ss
```

Pinned reproducibility:

```bash
python3 -m pip install "namel3ss==<version>"
```

Use pinned installs for strict replay across teams or CI environments.
