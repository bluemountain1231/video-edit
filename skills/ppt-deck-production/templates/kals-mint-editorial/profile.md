# kals-mint-editorial Template Profile

Use when the user asks for the extracted `不错的模版`, the Kals mint editorial style, or this template's reusable elements.

## Fixed Files

Keep this template profile lean. Every file must have a direct runtime purpose:

- `profile.md`: concise style rules and component usage guidance.
- `reference-atlas.png`: visual overview of the source template.
- `reference-atlas.json`: slide-position manifest for the atlas.
- `starter.html`: HTMLPPT starter using this template language.

Do not store per-slide PNGs, 4-slide extraction groups, alternate experiments, or multiple exploratory previews inside the skill. Those belong in the project output folder for the active job.

## Extraction Rule

Extract reusable families, not every visible object and not every size variant.

Split a component only when it has a distinct editing job or behavior. Avoid duplicate small/large variants unless the usage is materially different. Prefer a compact set that can compose slides quickly.

## Visual Language

- 16:9 white slide stage with thin warm beige border.
- Warm beige canvas background.
- Mint green accents: circular logo badges, numbered badges, large cropped circles, soft glows.
- Heavy black geometric sans headlines with tight line height.
- Compact editorial copy: bold subheads, short body copy, muted labels.
- Photos are rectangular crops, partial bleeds, collages, or device fills.
- Charts are sparse: mint highlighted series, gray context series, minimal labels.

## Tokens

- `color/bg/canvas`: `#F4F1EA`
- `color/bg/slide`: `#FFFFFF`
- `color/accent/mint`: `#6BE9B3`
- `color/text/primary`: `#111111`
- `color/text/body`: `#333333`
- `color/text/muted`: `#77736B`
- `color/stroke/subtle`: `#DED7C9`
- `color/chart/gray`: `#A7A7A7`
- `color/chart/dark-gray`: `#555555`
- Radius: mostly square or small `8px`; circles use full radius.
- Type: use Inter/system sans if the exact source font is unavailable.

## Component Families

This template has 15 reusable component families, each an editable HTML/CSS component:

- `chrome/logo-badge`: mint circular logo badge.
- `chrome/number-badge`: numbered mint badge.
- `decorative/mint-circle`: editable circle accent.
- `decorative/mint-glow`: soft radial glow.
- `media/image-frame`: replaceable image slot.
- `body/editorial-copy-block`: subhead plus compact body copy.
- `chart/bar-series`: editable mint/gray bar cluster.
- `cover/title-system`: cover or statement slide system.
- `section/divider`: section divider with washed background and mint badge.
- `body/two-column`: large claim plus support copy.
- `body/image-plus-text`: asymmetric image and text layout.
- `card/case-study`: three-card case strip.
- `chart/big-number`: metric/chart proof slide.
- `media/device-frame`: phone/device screenshot frame.
- `chart/map-metric`: map or coverage metric layout.

## HTMLPPT Guidance

- Start from `starter.html` when using this built-in template.
- Keep headings, body copy, charts, badges, circles, and page chrome editable in HTML/CSS.
- Use project-specific images for photos/screenshots. Source images are placeholders only.
- Remove default example text such as `Bring your business to the sky` once real content is available.
- Preserve rhythm and hierarchy; do not copy source slide order mechanically.

## Content Planning Guidance

- Opening claim: `cover/title-system`
- Chapter break: `section/divider`
- Argument/explanation: `body/two-column`
- Evidence image: `body/image-plus-text`
- Three examples: `card/case-study`
- Metric or trend: `chart/big-number`
- Geography or coverage: `chart/map-metric`
- Product or screenshot: `media/device-frame`

Keep one main idea per slide. Avoid dense paragraphs and tiny labels.
