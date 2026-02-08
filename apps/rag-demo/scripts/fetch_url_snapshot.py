#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ALLOWLIST_ENV = "RAG_URL_ALLOWLIST"
USER_AGENT = "namel3ss-rag-demo-snapshot/1.0"


def _normalize_allowlist(raw: str) -> list[str]:
    items = [item.strip().lower() for item in (raw or "").split(",") if item.strip()]
    return sorted(set(items))


def _is_allowed(hostname: str, allowlist: list[str]) -> bool:
    host = (hostname or "").lower()
    if not host or not allowlist:
        return False
    for allowed in allowlist:
        if host == allowed or host.endswith(f".{allowed}"):
            return True
    return False


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return cleaned or "snapshot"


def _fetch_text(url: str, timeout: int) -> str:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=timeout) as response:
        content_type = response.headers.get("Content-Type", "")
        if "text" not in content_type and "json" not in content_type:
            raise ValueError(f"unsupported content-type: {content_type}")
        data = response.read()
    return data.decode("utf-8", errors="replace")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a deterministic URL snapshot for rag-demo.")
    parser.add_argument("url", help="HTTP(S) URL to snapshot")
    parser.add_argument("--out-dir", default="apps/rag-demo/assets/url_snapshots", help="snapshot directory")
    parser.add_argument("--timeout", type=int, default=15, help="request timeout seconds")
    args = parser.parse_args()

    parsed = urlparse(args.url)
    if parsed.scheme not in {"http", "https"}:
        raise SystemExit("Only http/https URLs are supported")

    allowlist = _normalize_allowlist(os.getenv(ALLOWLIST_ENV, ""))
    if not _is_allowed(parsed.hostname or "", allowlist):
        raise SystemExit(
            f"URL host is not allowlisted. Set {ALLOWLIST_ENV}=example.com,docs.example.com and retry."
        )

    text = _fetch_text(args.url, timeout=args.timeout)
    normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip() + "\n"

    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    host_slug = _slug(parsed.hostname or "snapshot")
    name = f"{host_slug}-{digest[:16]}.txt"

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = out_dir / name
    snapshot_path.write_text(normalized, encoding="utf-8")

    manifest_path = out_dir / "manifest.json"
    manifest: dict[str, object]
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    else:
        manifest = {"version": 1, "entries": []}

    entries = manifest.get("entries")
    if not isinstance(entries, list):
        entries = []

    entry = {
        "url": args.url,
        "host": (parsed.hostname or "").lower(),
        "path": snapshot_path.as_posix(),
        "sha256": digest,
        "content_type": "text/plain",
    }

    dedup: dict[str, dict] = {}
    for item in entries:
        if isinstance(item, dict) and isinstance(item.get("url"), str):
            dedup[item["url"]] = item
    dedup[args.url] = entry

    ordered = [dedup[key] for key in sorted(dedup.keys())]
    manifest_out = {"version": 1, "entries": ordered}
    manifest_path.write_text(json.dumps(manifest_out, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(snapshot_path.as_posix())
    print(manifest_path.as_posix())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
