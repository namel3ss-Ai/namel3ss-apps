# Docker

## Local container run

```bash
cd apps/rag-demo
docker compose up --build
```

Open `http://localhost:7340`.

## Compose behavior

- container port: `7340`
- host port: `7340`
- persistence volume: `./data:/app/data`
- runtime persistence env: `N3_PERSIST_ROOT=/app/data`

## .env support

`docker compose` reads `.env` in `apps/rag-demo` for variable substitution.

Recommended:

```bash
cd apps/rag-demo
cp .env.example .env
```

Leave provider keys empty for demo mode.
