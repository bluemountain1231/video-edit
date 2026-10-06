# video-talkcraft bridge

`koubo-edit` can use video-talkcraft as a planning reference without importing
its renderer or its runtime dependencies. The bridge keeps only the upstream
machine-readable card catalog and required notices in
`assets/talkcraft-bridge/`.

The upstream project currently provides 108 cards and a 26-word semantic
vocabulary. Its toolkit is licensed under PolyForm Noncommercial 1.0.0. Read
the copied `LICENSE` and `THIRD_PARTY_NOTICES.md` before copying any upstream
card source or demo into a production project. The bridge itself does not
bundle those TSX files, so the base koubo renderer remains independent.

## Workflow

After transcription, generate a reviewable semantic first pass:

```bash
python3 "$SKILL_DIR/scripts/semantic-plan.py" \
  output/koubo-edit/jobs/<name>/transcript.json \
  -o output/koubo-edit/jobs/<name>/semantics.json
```

Then rank cards against the semantic labels and the assets actually available
for this edit:

```bash
python3 "$SKILL_DIR/scripts/talkcraft-match.py" \
  output/koubo-edit/jobs/<name>/semantics.json \
  --catalog "$SKILL_DIR/assets/talkcraft-bridge/cards-index.json" \
  --inputs 人,文 \
  --out output/koubo-edit/jobs/<name>/talkcraft-candidates.json
```

The result is a candidate list, not an automatic implementation. Select at
most one primary motion per semantic beat, preserve the card's timing and
easing constraints, and adapt only colors, copy, dimensions, and media. Record
selected cards in `edit-plan.json` under `card_refs` so later revisions can
trace why a motion was chosen.

```json
{
  "card_refs": [
    {
      "slug": "chapter-title-card",
      "start_ms": 10000,
      "end_ms": 11920,
      "reason": "转折句：保证金陷阱"
    }
  ]
}
```

If a selected card needs its upstream TSX, clone or point to the exact
`video-talkcraft` checkout and copy it into a separate, clearly marked project
area only after checking its license and `THIRD_PARTY_NOTICES.md`. Do not add
remote imports to a render, and do not silently replace a card with a hand-made
approximation when the selected card's tuned timing is material to the shot.
