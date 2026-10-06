#!/usr/bin/env python3
"""Rank video-talkcraft card candidates against a koubo semantic plan.

Only the imported metadata catalog is read.  The script never imports or
executes upstream demo code; a chosen card is a reviewable reference for the
director, not an automatic runtime dependency.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


INPUT_FAMILY = {"人", "V", "图", "截图", "文", "界", "场"}


def score(card: dict, semantic: str, inputs: set[str]) -> tuple[float, list[str]]:
    if semantic not in card.get("semantics", []):
        return (-999.0, [])
    value = 3.0
    why = ["语义匹配"]
    card_inputs = {item.get("type") for item in card.get("inputs", [])}
    families = card_inputs & INPUT_FAMILY
    if not families or families & inputs:
        value += 2
        why.append("输入形态可用")
    else:
        value -= 3
        why.append("需要额外素材")
    if card.get("priority") == "P0":
        value += 0.5
        why.append("P0")
    if card.get("hardcoded"):
        value -= 0.25
        why.append("需改源码")
    return value, why


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("semantics", type=Path)
    ap.add_argument("--catalog", type=Path, default=None)
    ap.add_argument("--inputs", default="人,文", help="available input families, comma separated")
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    catalog = args.catalog or Path(
        os.environ.get("VIDEO_TALKCRAFT_CATALOG", "assets/talkcraft-bridge/cards-index.json")
    )
    data = json.loads(catalog.read_text(encoding="utf-8"))
    cards = data.get("cards", [])
    inputs = {item.strip() for item in args.inputs.split(",") if item.strip()}
    plan = json.loads(args.semantics.read_text(encoding="utf-8"))
    rows = []
    for sentence in plan.get("sentences", []):
        candidates = []
        for semantic in sentence.get("sem", []):
            ranked = []
            for card in cards:
                value, why = score(card, semantic, inputs)
                if value > -100:
                    ranked.append((value, card, why))
            ranked.sort(key=lambda item: (-item[0], item[1].get("slug", "")))
            candidates.append({
                "semantic": semantic,
                "cards": [
                    {
                        "slug": card.get("slug"),
                        "title": card.get("title"),
                        "category": card.get("category"),
                        "energy": card.get("energy"),
                        "code": card.get("code"),
                        "score": value,
                        "why": why,
                    }
                    for value, card, why in ranked[: args.top]
                ],
            })
        rows.append({
            "sentence_index": sentence.get("i"),
            "start_ms": sentence.get("start_ms"),
            "end_ms": sentence.get("end_ms"),
            "text": sentence.get("text"),
            "candidates": candidates,
        })
    payload = {
        "version": 1,
        "source": {"semanticPlan": str(args.semantics), "catalog": str(catalog)},
        "availableInputs": sorted(inputs),
        "sentences": rows,
        "policy": "Review candidates, then copy/adapt a card only under the upstream license terms.",
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"talkcraft candidates: {len(rows)} sentences -> {args.out}")


if __name__ == "__main__":
    main()
