# URL Snapshots

URL snapshots convert web pages into deterministic local text sources.

## Why snapshots

Direct live web fetches are unstable. Snapshots keep retrieval deterministic by storing:

- normalized text content
- content hash
- stable manifest entries

## Allowlist

Set host allowlist before fetching:

```bash
export RAG_URL_ALLOWLIST=example.com,docs.example.com
```

Only URLs in that host allowlist are accepted.

## Fetch a snapshot

```bash
cd apps/rag-demo
python3 scripts/fetch_url_snapshot.py https://docs.example.com/page
```

Outputs:

- `assets/url_snapshots/<host>-<hash>.txt`
- `assets/url_snapshots/manifest.json`

## Use in demo

1. Upload snapshot `.txt` files through normal upload.
2. Click `Update library`.
3. Run ingestion.
4. Ask questions and verify citations as usual.
