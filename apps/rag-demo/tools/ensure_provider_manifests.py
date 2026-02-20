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
    providers_root = Path(namel3ss.__file__).resolve().parent / "runtime" / "providers"
    created = 0

    for provider_name in PROVIDERS:
        manifest_path = providers_root / provider_name / "pack_manifest.json"
        if manifest_path.exists():
            continue
        payload = {
            "name": provider_name,
            "capability_token": provider_name,
            "supported_modes": ["text", "image", "audio"],
            "models": [f"{provider_name}:mock-text-v1"],
        }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        created += 1

    print(f"provider_manifests_created={created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
