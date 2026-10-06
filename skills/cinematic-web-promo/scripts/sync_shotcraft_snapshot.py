#!/usr/bin/env python3
"""Build a version-locked, offline Shotcraft snapshot for this Skill."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

from shotcraft_router import (
    DEFAULT_REF,
    REPO_URL,
    RouterError,
    Upstream,
    atomic_write,
    candidate_rows,
    import_previews,
    import_source_files,
    load_library,
    utc_now,
)


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_DESTINATION = SCRIPT_DIR.parent / "assets" / "shotcraft-snapshot"
EXACT_FILES = {
    "LICENSE",
    "SKILL.md",
    "gallery/api/library.json",
}
INCLUDED_PREFIXES = (
    "assets/lib",
    "demos",
    "references/shots",
    "template",
)


def collect_snapshot_paths(upstream: Upstream) -> list[str]:
    wanted = {item for item in EXACT_FILES if item in upstream.path_set}
    for prefix in INCLUDED_PREFIXES:
        wanted.update(upstream.matching(prefix))
    missing = sorted(EXACT_FILES - wanted)
    if missing:
        raise RouterError(f"Upstream snapshot is missing required files: {', '.join(missing)}")
    return sorted(wanted)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default=DEFAULT_REF, help="Branch, tag, or exact upstream commit.")
    parser.add_argument("--offline-root", type=Path, help="Authorized local upstream checkout/archive root.")
    parser.add_argument("--destination", type=Path, default=DEFAULT_DESTINATION)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--no-previews", action="store_true", help="Build a source-only development snapshot.")
    parser.add_argument("--force", action="store_true", help="Back up and replace an existing snapshot.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.workers < 1 or args.workers > 16:
        raise RouterError("--workers must be between 1 and 16.")
    destination = args.destination.resolve()
    if destination.exists() and not args.force:
        raise RouterError(f"Snapshot already exists: {destination}. Pass --force to back it up and replace it.")
    destination.parent.mkdir(parents=True, exist_ok=True)

    upstream = Upstream(args.ref, args.offline_root)
    library = load_library(upstream)
    paths = collect_snapshot_paths(upstream)
    stage = Path(tempfile.mkdtemp(prefix=".shotcraft-snapshot-", dir=destination.parent))
    try:
        source_files = import_source_files(upstream, paths, stage / "repo", args.workers)
        preview_files = []
        if not args.no_previews:
            rows = [{**row, "kind": "recipe"} for row in candidate_rows(library)]
            revision = str(library.get("revision", "unversioned"))
            preview_files = import_previews(rows, stage / "previews", revision, args.workers)
            expected = int(library.get("stats", {}).get("previewCount", len(rows)))
            if len(preview_files) != expected:
                raise RouterError(f"Preview count mismatch: expected {expected}, downloaded {len(preview_files)}")

        license_text = (stage / "repo" / "LICENSE").read_text(encoding="utf-8", errors="replace")
        if "Apache License" not in license_text or "Version 2.0" not in license_text:
            raise RouterError("The embedded upstream license is not the expected Apache-2.0 text.")

        manifest = {
            "schemaVersion": 1,
            "generatedAt": utc_now(),
            "upstream": {
                "repository": REPO_URL,
                "requestedRef": args.ref,
                "resolvedCommit": upstream.commit,
                "libraryRevision": str(library.get("revision", "unknown")),
                "libraryGeneratedAt": library.get("generatedAt"),
                "license": "Apache-2.0",
            },
            "scope": {
                "exactFiles": sorted(EXACT_FILES),
                "prefixes": list(INCLUDED_PREFIXES),
                "includesAllRecipeCards": True,
                "includesAllDemoSource": True,
                "includesReusableComponents": True,
                "includesInkPressTemplate": True,
                "includesAllGalleryPreviews": not args.no_previews,
            },
            "stats": {
                "cardCount": int(library.get("stats", {}).get("cardCount", 0)),
                "styleCount": int(library.get("stats", {}).get("styleCount", 0)),
                "sourceFileCount": len(source_files),
                "previewCount": len(preview_files),
                "sourceBytes": sum(item["bytes"] for item in source_files),
                "previewBytes": sum(item["bytes"] for item in preview_files),
            },
            "sourceFiles": source_files,
            "previews": preview_files,
        }
        atomic_write(
            stage / "SNAPSHOT.json",
            (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
        )

        if destination.exists():
            stamp = dt.datetime.now().strftime("%Y%m%d%H%M%S")
            backup = destination.with_name(f"{destination.name}.backup.{stamp}")
            shutil.move(destination, backup)
            print(f"Backed up: {backup}")
        os.replace(stage, destination)
        print(f"Snapshot: {destination}")
        print(f"Commit: {upstream.commit}")
        print(f"Cards/styles/previews: {manifest['stats']['cardCount']}/{manifest['stats']['styleCount']}/{manifest['stats']['previewCount']}")
        print(f"Files: {manifest['stats']['sourceFileCount']} source + {manifest['stats']['previewCount']} previews")
        return 0
    finally:
        if stage.exists():
            shutil.rmtree(stage)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RouterError as error:
        print(f"shotcraft-snapshot: {error}", file=sys.stderr)
        raise SystemExit(2)
