# senyan — "Senyan / Morimoto" Editorial Branding Template

A reusable 16:9 template built from the source PPTX. Minimalist fashion/branding
editorial language: cream canvas, one giant grotesque display word per slide,
a signature soft peach gradient circle, and tiny corner microcopy chrome.

## Design tokens

| Token | Value | Use |
|-------|-------|-----|
| `--cream` | `#F7EEE7` | default canvas |
| `--navy` | `#293377` | display titles, dark full-bleed mood |
| `--coral` | `#EB6856` | statement titles, accent labels |
| `--gold` | `#F6C88F` | side panel / warm mood block |
| `--char` | `#444F4D` | charcoal-green dark mood |
| `--ink` | `#111318` | body microcopy on cream |
| peach circle | radial `#F6D3B0 → #F7EEE7` | signature decorative mark |

Type: heavy grotesque display (`Archivo`/`Helvetica Neue`), 11px uppercase
letter-spaced microcopy for all chrome.

## Chrome (every slide)

- Top-left: `Senyan —` wordmark (◆ glyph + label)
- Top-right: `Los Angeles — Hongkong — Australia` locations
- Right edge (vertical): section label — `Manifesto` / `The Service` / `Pricing` / `Founders` / `Timeline` / `Contact`
- Bottom-left: `www.domain.com`
- Bottom-right: `@minimalisimoofficial`

## Template element families (one showcase slide each)

| # | family | job | headline sample | notes |
|---|--------|-----|-----------------|-------|
| 01 | `cover/title-system` | brand cover | Morimoto | navy word + peach circle |
| 02 | `statement/big-quote` | manifesto line | Speak your mind through emotions infinitely. | coral centered statement |
| 03 | `mood/navy-intro` | full-bleed intro | Journey & History of International Corporation | navy bg, coral title |
| 04 | `body/image-plus-text` | copy beside photos | Senyan empowers millions… | 2 portrait crops |
| 05 | `body/manifesto` | right-aligned copy block | Turns a well trained eye… | vertical section label |
| 06 | `mood/gold-panel` | warm side-panel copy | 10-Years vision manifesto | gold left column + photo |
| 07 | `statement/image-quote` | statement on photo | Senyan isn't just a brand, it's a brain. | dark full-bleed photo |
| 08 | `section/divider` | chapter opener | Architecture | giant word + circle |
| 09 | `people/founders-list` | named leaders | Founders — | portrait + name/handle rows |
| 10 | `people/members-grid` | team row | Members | 4 portrait cards + handles |
| 11 | `pricing/big-number` | priced service | Architecture Concept · $25k | portrait + price card |
| 12 | `offer/highlight` | promo line | 50% Offer for all services @Senyan | coral+muted split text |
| 13 | `process/week-block` | timeline stage | Week 01. | coral heading + copy panel |
| 14 | `gallery/image-grid` | lookbook collage | — | 4–5 image mosaic |
| 15 | `contact/collaborate` | CTA | Let's collaborate! | email, charcoal mood |
| 16 | `closing/thanks` | sign-off | Thanks | circle + address block |

## Usage

Duplicate any `.slide` block, keep the `chrome` frame, swap the family's inner
markup and copy. All text, shapes, price cards, and labels stay editable HTML.
Replace `assets/*.jpg` portrait/lookbook crops with project photos (raster only
for photography). Never bake copy into images.
