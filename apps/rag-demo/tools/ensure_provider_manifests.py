#!/usr/bin/env python3
"""Create missing provider pack manifests for local namel3ss installs."""

from __future__ import annotations

import json
from pathlib import Path

import namel3ss

PROVIDERS = (
    "huggingface",
    "local_runner",
    "vision_gen",
    "speech",
    "third_party_apis",
)


def main() -> int:
    root = Path(namel3ss.__file__).resolve().parent / "runtime" / "providers"
    changed = 0

    for name in PROVIDERS:
        path = root / name / "pack_manifest.json"
        if path.exists():
            continue

        payload = {
            "name": name,
            "capability_token": name,
            "supported_modes": ["text", "image", "audio"],
            "models": [f"{name}:mock-text-v1"],
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        changed += 1

    print(f"provider_manifests_created={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
