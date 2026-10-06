#!/usr/bin/env python3
"""Sync the reusable, offline Shotcraft assets into koubo-edit.

The upstream repository is intentionally treated as a source tree.  This
script copies the source files, audio, recipes, demos, and gallery index into
the skill and writes a small manifest so an installed skill can inspect what
is available without importing the full gallery application.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


COPY_DIRS = ("assets/lib", "assets/audio", "demos", "references/shots")


def git_revision(source: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def copy_tree(source: Path, destination: Path) -> None:
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination)


def relative_files(root: Path, suffix: str | None = None) -> list[str]:
    paths = [p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()]
    if suffix:
        paths = [p for p in paths if p.endswith(suffix)]
    return sorted(paths)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True, help="video-shotcraft checkout")
    parser.add_argument("--destination", type=Path, required=True, help="remotion-library directory")
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.resolve()
    if not (source / "assets/lib").is_dir():
        raise SystemExit(f"not a video-shotcraft checkout: {source}")

    for rel in COPY_DIRS:
        copy_tree(source / rel, destination / Path(rel).name)
    gallery = source / "gallery/api/library.json"
    if gallery.is_file():
        destination.joinpath("gallery").mkdir(parents=True, exist_ok=True)
        shutil.copy2(gallery, destination / "gallery/library.json")
    license_file = source / "LICENSE"
    if license_file.is_file():
        shutil.copy2(license_file, destination / "THIRD_PARTY_LICENSE")

    audio_root = destination / "audio"
    sfx = relative_files(audio_root / "sfx", ".mp3") if (audio_root / "sfx").exists() else []
    bgm = relative_files(audio_root / "bgm", ".mp3") if (audio_root / "bgm").exists() else []
    demos = relative_files(destination / "demos", ".tsx") if (destination / "demos").exists() else []
    demo_cards = [p for p in demos if not p.startswith("_fixtures/")]
    recipes = relative_files(destination / "shots", ".md") if (destination / "shots").exists() else []
    recipe_cards = [p for p in recipes if p != "ATTRIBUTION.md"]
    components = relative_files(destination / "lib", ".tsx") if (destination / "lib").exists() else []

    gallery_cards = []
    gallery_path = destination / "gallery/library.json"
    if gallery_path.is_file():
        try:
            gallery_cards = json.loads(gallery_path.read_text(encoding="utf-8")).get("cards", [])
        except (OSError, json.JSONDecodeError):
            gallery_cards = []

    manifest = {
        "schemaVersion": 1,
        "source": {
            "repository": "https://github.com/Vincentwei1021/video-shotcraft",
            "commit": git_revision(source),
        },
        "counts": {
            "components": len(components),
            "demos": len(demo_cards),
            "demoSourceFiles": len(demos),
            "recipes": len(recipe_cards),
            "galleryCards": len(gallery_cards),
            "sfx": len(sfx),
            "bgm": len(bgm),
        },
        "components": components,
        "audio": {"sfx": sfx, "bgm": bgm},
        "demos": demo_cards,
        "recipes": recipe_cards,
        "license": "See THIRD_PARTY_LICENSE and audio/ATTRIBUTION.md before redistribution.",
    }
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
