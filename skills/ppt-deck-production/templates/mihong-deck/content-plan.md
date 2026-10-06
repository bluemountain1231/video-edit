# mihong — Holographic "Acid" Business Template

Source: `mihong.pptx` (16 slides, 16:9, "Event Planning / Creator Information" by @SENYAN).
This deck is processed **as a reusable element library** — the HTMLPPT reproduces every
recurring component family with editable placeholder copy, not a specific story.

## Design Tokens (sampled from source pixels)

| Token | Value | Notes |
|-------|-------|-------|
| `--blue` | `#2b46f0` | Primary electric-blue accent (titles, arrows, dots). Sampled (46,82,237). |
| `--blue-deep` | `#0a10c4` | Deep blue for solid circles / emphasis. Sampled (5,9,195). |
| `--ink` | `#141414` | Near-black body text on light slides. |
| `--paper` | `#f1f1f1` | Light-gray content background. Sampled (241,241,241). |
| `--paper-hi` | `#fafafa` | Highlight for crinkle-texture sheen. |
| `--muted` | `#9aa0ad` | De-emphasized justified body copy (gray). |
| `--white` | `#ffffff` | Text on holographic slides. |
| Holographic | violet-blue `#5948b9` → cyan → green `#7dd294` → yellow `#fbeba6` → pink `#f1b6ca` | Iridescent foil gradient, full-spectrum. |

**Type treatment**
- Display / titles: heavy **bold italic** grotesque (Helvetica/Arial Bold Italic). Cover title white with a `--blue` offset shadow (chromatic split). Content titles are `--blue`, centered, italic.
- Microcopy: UPPERCASE, thin weight, wide letter-spacing (~0.35em), small.
- Body: regular sans, generous line-height; secondary blocks justified in `--muted` gray.
- Radii: circles are the signature shape; cards/frames use ~4–8px.

**Signature decorative marks**
- Iridescent **sphere** (rainbow radial/conic fill circle).
- **Blue outline** circle (thin stroke).
- **Solid blue** circle.
- 6-point **sparkle star** (white on holographic).
- Faint **ghost reflection** circles beneath spheres.
- Blue directional **arrows**; dashed circle/square accents.

## Reusable Element Families (→ HTML components)

- `cover/title-system` — holographic full-bleed, sparkle star, bold-italic title w/ blue offset, tracked caps sub + credit.
- `section/divider` — holographic, big italic "Part 0N", bottom "Title Summary", outline circle + star + solid dot.
- `body/contents` — numbered `01. / 02.` list, iridescent spheres + outline circles cluster, big italic section word bottom-right.
- `body/two-column` — light bg, centered blue italic title, two justified gray copy columns.
- `list/persona-rows` — "Name A/B/C" rows each with 3 blue bullets; sphere accent + big italic word.
- `chart/area-wave` — iridescent multi-band area/wave chart with %-labels and a baseline axis.
- `stages/circle-trio` — three circles (iridescent / outline / solid-blue) each w/ heading + 3 bullets, ghost reflections, side arrows.
- `list/icon-row` — row of line icons above a tracked-caps statement + justified copy.
- `chart/big-number` — oversized numerals (25 / 35 / 98) with small image frames and a paragraph.
- `flow/options-timeline` — Options 1–3 with circles + a dotted vertical timeline to Results.
- `chart/swot` — 4 circles S / O / W / T with label + copy in a 2×2 grid.
- `closing/thanks` — holographic, big italic "Thank" + tracked credits + sparkle.
- `chrome/page-number` — small tracked page index bottom corner.

## Slide List (element-library starter deck)

| # | title | template_family | notes |
|---|-------|-----------------|-------|
| 1 | Event Planning (cover) | cover/title-system | holographic + chromatic title |
| 2 | Contents | body/contents | numbered list + spheres |
| 3 | About Us | body/two-column | justified copy |
| 4 | Team | list/persona-rows | name rows + sphere |
| 5 | Part 01 (divider) | section/divider | holographic |
| 6 | Data Analysis | chart/area-wave | iridescent wave |
| 7 | Itemized Display | stages/circle-trio | 3 circle variants |
| 8 | Approach | list/icon-row | icons + statement |
| 9 | Investment Value | chart/big-number | 25 / 35 / 98 |
| 10 | Development | flow/options-timeline | options + results |
| 11 | Integrated Data | chart/swot | S O W T |
| 12 | Thank You | closing/thanks | holographic |

All copy uses `【填入】`-style placeholders where a real deck would supply facts; nothing is invented.
