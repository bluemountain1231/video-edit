#!/usr/bin/env python3
"""Import video-talkcraft's card catalog without importing its renderer code.

The upstream skill is PolyForm Noncommercial.  We therefore copy only the
machine-readable catalog and the required notices into a clearly isolated
bridge directory.  Card TSX, demos, and runtime dependencies stay in the
upstream checkout and are never bundled into koubo-edit automatically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path


def revision(source: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def copy_required(source: Path, dest: Path, name: str) -> None:
    src = source / name
    if not src.is_file():
        raise SystemExit(f"missing video-talkcraft file: {src}")
    shutil.copy2(src, dest / Path(name).name)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True, help="video-talkcraft checkout")
    ap.add_argument("--destination", type=Path, required=True, help="talkcraft-bridge directory")
    args = ap.parse_args()
    source = args.source.resolve()
    dest = args.destination.resolve()
    catalog = source / "references/cards-index.json"
    if not catalog.is_file():
        raise SystemExit(f"not a video-talkcraft checkout: {source}")
    dest.mkdir(parents=True, exist_ok=True)
    copy_required(source, dest, "references/cards-index.json")
    copy_required(source, dest, "LICENSE")
    copy_required(source, dest, "THIRD_PARTY_NOTICES.md")

    data = json.loads(catalog.read_text(encoding="utf-8"))
    cards = data.get("cards", [])
    sha = hashlib.sha256(catalog.read_bytes()).hexdigest()
    manifest = {
        "schemaVersion": 1,
        "source": {
            "repository": "https://github.com/Vincentwei1021/video-talkcraft",
            "commit": revision(source),
            "catalogSha256": sha,
        },
        "counts": {"cards": len(cards), "vocab": len(data.get("vocab", []))},
        "policy": {
            "rendererCodeBundled": False,
            "license": "PolyForm Noncommercial 1.0.0; see LICENSE and THIRD_PARTY_NOTICES.md",
            "commercialUse": "Obtain authorization from Vincent Wei before using upstream toolkit code or cards commercially.",
        },
    }
    (dest / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
