---
name: ppt-deck-production
description: Two-mode PPT skill with a built-in Chinese font library and an asset-factory pipeline. Mode A (deck development) runs 需求梳理 → 方案三件套（模版 + 三级字体方案 + 生成素材/抠图物料）→ showcase 方案确认 → content plan → browser-validated HTMLPPT → editable PPTX delivery. Mode B (template accumulation) turns an input reference PPTX into a reusable template profile — atlas, design tokens, named HTML/CSS component families — saved under templates/ and registered for future Mode A use. Use for any request to build slides/decks/presentations, or to add/extract/accumulate a PPT template from a PPTX file.
---

# PPT Deck Production

## Two Modes — Decide First

This skill has exactly two modes. Before doing anything else, decide which mode the request is:

| | Mode A: Deck Development (开发PPT) | Mode B: Template Accumulation (积累模版) |
|---|---|---|
| **Goal** | Deliver a finished, still-editable deck | Grow the template library |
| **Input** | User's topic/material | One or more reference PPTX files |
| **Output** | Project folder: HTMLPPT + **editable PPTX** | A profile under **this skill's** `templates/<profile-name>/`, registered in this file |
| **Uses** | Template profile + font library + asset factory + Shared Rules | Page export → atlas → token/component extraction |

Mode selection:

- User provides content/topic and wants slides → **Mode A**.
- User provides a PPTX and asks to make it a template, extract its style, add it to the library, or "积累模版" → **Mode B**. The deliverable is the profile itself; do not build a deck.
- User provides a *new* reference PPTX **and** wants a deck in its style → run **Mode B first** to create the profile, then run **Mode A** using that new profile.

The HTMLPPT is the single source of truth during development; the editable PPTX is the final deliverable.

## Built-in Resources

- `templates/<profile>/` — template profiles; selectable list lives in the **Template Profile Registry** below.
- `fonts/` — 免费商用中文字体库, three tiers: `cover/` 封面艺术字, `title/` 标题字, `body/` 正文字. Font names, vibes, pairings, and @font-face / PPTX usage: read [fonts/FONTS.md](fonts/FONTS.md).
- `scripts/cutout.py` — 物料工厂抠图: slices a white-background multi-object sheet into transparent PNGs (`uv run` 自动解决依赖, 无需安装).

---

## Mode A: Deck Development (开发PPT)

Pipeline: **A1 需求梳理 → A2 方案三件套（模版 + 字体 + 素材工厂）→ A3 方案确认 showcase → A4 content plan → A5 HTMLPPT + 浏览器验证 → A6 可编辑 PPTX 交付**.

A3 是必经关卡：生图有随机性、建 deck 要很久，先把模版、字体、素材给用户过目，比做完再返工便宜得多。用户明确说"直接做、不用确认"才可跳过。

### A1. 需求梳理

Establish before generating anything:

- 主题、受众、场合（融资路演 / 内部汇报 / 产品发布 / 课程 …）、预估页数。
- Deck 气质关键词（商务稳重 / 潮流 / 高级编辑部 / 国风 / 电商促销 / 可爱 …）——这个词同时驱动模版、字体、素材风格三个选择。
- 粗分段大纲：章节级（封面 / 问题 / 方案 / 案例 / 数据 / 行动号召 …），不用逐页。

### A2. 方案三件套

**① 选模版**：从 Registry 选一个匹配气质的 profile。只读该 profile 的 `profile.md`（或其登记的 spec 文件）。atlas 是组件参考，never final slides。没有合适的且用户给了参考 PPTX → 先走 Mode B；没参考 → 提议最接近的 profile。

**② 定字体方案**：读 [fonts/FONTS.md](fonts/FONTS.md)，按气质选出三级方案——**封面字体**（艺术感，只用于封面/章节页大字）、**标题字体**（每页标题）、**正文字体**（正文与说明文字）。FONTS.md 底部有按气质的推荐搭配，可直接起手再微调。封面与标题可以是同一款加大加粗，但必须显式写成三级方案。

**③ 素材工厂**（参考口播剪辑的物料工厂，全部用 `mcp__gpt-image__generate_image`）：

- **透明物料（一图一批）**：把整个 deck 会反复用的物件（产品、图标、道具、吉祥物）写进一条 prompt，要求 "pure white background, evenly spaced 2x2 grid, one object per cell, consistent style"，生成一张 1536x1024，然后抠图：

  ```bash
  uv run ~/.claude/skills/ppt-deck-production/scripts/cutout.py sheet.png --grid 2x2 -o htmlppt/assets --prefix prop
  ```

  得到 `prop_1.png…`（透明 PNG，已裁边）。用途：卡片配图标、页面浮动贴纸、章节锚点装饰。一次生成保证全 deck 物料同一画风；同一物料多页复用形成视觉锚点。
- **全幅/半幅插图**：概念、流程、场景、人群类页面单张生成。整个 deck 只定义一种插图风格，从模版色板推导（例：kals = "isometric 3D clay render, white background, mint green #6BE9B3 and light gray palette, soft shadows"），每条 prompt 复用。横版 1536x1024 最适配 16:9 版位。纯数据页、表格页、文字页不配插图。
- **铁律**：任何生成图里不允许出现文字——prompt 末尾必加 "no text, no letters, no labels"。所有标注后面用 HTML/PPTX 文本叠加，保持可编辑。
- **质检（必做）**：每张图用 Read 亲眼看一遍，废图（元素粘连、风格跑偏）重新生成。透明物料要合到模版底色上看真实效果（Read 预览会把透明渲染成白色，看不出白边/雾状残留）：

  ```bash
  ffmpeg -f lavfi -i "color=c=0xF7EEE7:size=700x560" -i prop_1.png -filter_complex "[0][1]overlay=20:20:format=auto" -frames:v 1 check.png
  ```

  底色残留调 `cutout.py --pad` 或加大 `white_to_alpha` 的 `floor`。

### A3. 方案确认 showcase（必经关卡）

把三件套拼成一页 showcase 给用户过目。做法：写一个临时 `showcase.html`（headless Chrome 截图发给用户），包含三个区块：

1. **模版**：所选 profile 的 reference-atlas 缩略 + 一句话说明选它的理由。
2. **字体**：三级方案各用**真实字体**渲染一行示例——封面字体渲一个大字号候选主标题、标题字体渲一条章节标题、正文字体渲两行正文样句（@font-face 指向 `fonts/` 里的文件），标注字体名。
3. **素材**：全部生成素材平铺（含备用），编号。

随图附清单，然后**停下来等用户确认**：

- 素材清单：编号 · 文件名 · 拟用于哪个章节/页。
- 模版 + 字体三级方案（写清中文族名）。
- 粗分段大纲（A1 的章节级）。

用户要求换模版/换字体/换图 → 改完重新 showcase；确认后才进 A4。

### A4. Content Planning

Create `content-plan.md` with one entry per slide:

- `slide`: page number and short title.
- `job`: what this page must make the audience understand or believe.
- `headline`: the main claim, not just a topic label.
- `supporting_copy`: concise copy, usually 1-3 short lines.
- `evidence`: facts, examples, workflow steps, screenshots, or source status.
- `template_family`: component family to use (e.g. `cover/title-system`, `section/divider`, `body/two-column`, `card/case-study`, `chart/big-number`, `chart/timeline`).
- `visual_notes`: 引用 A2 已确认的素材文件名（`assets/prop_1.png`）。规划中发现缺素材 → 按 A2 同风格补造，重要新增需向用户展示。

Planning rules:

- One main idea per slide.
- **Text is a hard budget.** Any single text block (headline, body, panel copy, caption) must render in at most 3 lines, with no orphan line (a final line holding only 1-2 characters/words). Headlines are one claim; body copy 1-2 short sentences; everything else becomes a chip, label, or visual.
- When copy exceeds the budget, cut words or split the idea across slides/panels. Never shrink the font to make text fit.
- Prefer showing over telling: lists of actors, entry points, or stages usually work better as an illustration plus overlaid chips than as sentences.
- Match content to the template's component library; do not force every idea into a source-page layout, and do not copy the template's page order mechanically.
- Mark unknown facts with explicit placeholders (e.g. `【填入】`) and a visible pre-send reminder note on the slide, instead of inventing numbers.

### A5. HTMLPPT Development + Browser Validation

Build `htmlppt/index.html` as the first real draft:

- 16:9 slides with stable dimensions. Proven pattern: a fixed 1280x720 `.stage` inside each slide, absolutely positioned elements on the stage, and a JS `transform: scale()` fit to the viewport.
- **字体接入**：把选中的三款字体文件复制进项目 `htmlppt/fonts/`，在 `index.html` 里 @font-face（相对路径，保证换机可看），按三级方案落到组件上——封面/章节页用封面字体，页标题用标题字体，其余全部正文字体。不要引入方案外的第四种字体。
- Implement the profile's style with its named HTML/CSS components. Keep text, shapes, bars, cards, labels, and page chrome editable.
- Raster images only for photos, complex crops, textures, and generated illustrations/物料.
- With absolute positioning, later DOM elements paint on top of earlier ones — a full-bleed image placed after a headline silently clips text. When text and images share space, give the text an explicit `z-index`.
- Keyboard navigation is fine, but no instructional text inside the deck.

Validate per slide, not just once:

- Start a local static server and screenshot EVERY slide (headless Chrome works well). Save revised slides as `slideNN-preview.png` and one overview as `htmlppt-preview.png`（项目产物，放项目目录，不进 skill）.
- On each screenshot check: 16:9 ratio, broken image paths, cropping, visual density, chip/label alignment against generated images, 字体是否真的加载（fallback 成系统字会一眼看出）, and the text budget — every block ≤3 rendered lines, no orphan line, nothing clipped by an overlapping image.
- Line count is only knowable from a rendered screenshot, never from source. Re-screenshot after every copy or layout change.
- Fix overflow by rewording or widening the text box; never by shrinking the font.

### A6. 可编辑 PPTX 交付（默认交付物）

HTMLPPT 草稿过目后，迁移成人可以继续编辑的 PPTX（用户明确只要网页版才可省略）：

- 用 python-pptx（或已安装的 pptx 技能）逐页重建：文本框、形状、色块、图表全部用原生可编辑对象；raster 仅照片、生成插图、透明物料。
- 文本一律使用三级方案的**中文族名**（见 FONTS.md 清单，如「得意黑」「优设标题黑」「阿里巴巴普惠体」）。本机预览前先安装字体：`cp <字体文件> ~/Library/Fonts/`。
- 交付包 = `deck.pptx` + `fonts/` 内用到的字体文件 + 一句安装提示（对方没装字体 PPTX 会 fallback）。
- 逐页与 HTMLPPT 截图对照验证（转 PDF 或截图比对），错位/字体 fallback / 文字被图压住都要修掉。

### Mode A Outputs

Project folder with stable names:

- `content-plan.md` — slide-by-slide plan, tokens, component-family list.
- `showcase.png` — A3 方案确认图。
- `htmlppt/index.html` + `htmlppt/fonts/` + `htmlppt/assets/`（素材按内容命名, e.g. `service-model.png`, `prop_1.png`）。
- `htmlppt-preview.png` / `slideNN-preview.png` — validation proof。
- `deck.pptx` + 随附字体文件 — 最终交付。

---

## Mode B: Template Accumulation (积累模版)

Input: one or more reference PPTX files. Output: a reusable profile plus a registry entry in this SKILL.md. No deck is produced in this mode.

**Where profiles live:** always inside this skill's own directory — `<skill base directory>/templates/<profile-name>/`. Never write the profile into the user's project folder; the project/working folder is only for intermediate files (raw page exports, experiments). This is what makes the template reusable across future projects.

### B1. Export Every Slide to PNG

- Prefer Keynote or PowerPoint automation on macOS. Use LibreOffice only if it renders correctly.
- Do not rely on Quick Look unless verified; it may export only a cover thumbnail.
- Do not parse PPTX internals unless page-image export fails or exact original assets are required.
- Keep the raw exports in a working/project folder (`template/page-images/`), **NOT inside the skill**.

### B2. Verify Export Quality

- PNG count matches slide count; all slides are 16:9.
- Visual style, type scale, and image treatment are readable.

### B3. Stitch the Reference Atlas

- One long contact sheet, 4-5 columns depending on page count, with clear labels (`SLIDE 01`, `SLIDE 02`, …) and enough spacing for inspection.
- This becomes the profile's `reference-atlas.png` (optionally with a `reference-atlas.json` slide-position manifest). 存入 skill 前压缩：最长边 ≤4000px、量化 256 色（Pillow quantize 即可），控制在 ~2MB 内。

### B4. Derive Design Tokens

- Sample exact colors from the source pixels (background, accents, dark/mood variants) — never guess.
- Record type treatment (display face/weight, microcopy size and tracking), radii, and any signature decorative mark. 若源字体不可用，从 `fonts/` 库里指定气质最接近的替代并写进 profile。

### B5. Extract the Reusable Element Library

- Read the atlas and list recurring **families**, not every source slide or object: title systems, section dividers, text boxes, image frames, cards, charts, page chrome, decorative marks, masks, recurring layout patterns.
- Each family becomes one editable HTML/CSS component keyed off the tokens. Photos and complex texture stay as raster fills inside editable frames.
- Extraction is lean: capture reusable families, not every size or positional duplicate. Split only when a component has a distinct editing job or behavior.
- Name families with the shared naming scheme (see Shared Rules) so Mode A can reference them directly.

### B6. Write the Profile

Create `<skill base directory>/templates/<profile-name>/` containing ONLY:

- `profile.md` — visual language, token table, element families with usage guidance, 推荐三级字体方案（从 fonts/ 库选）, and trigger phrases (what user wording should select this profile).
- `starter.html` — optional HTMLPPT starter implementing the template language with the named components.
- `reference-atlas.png` / `reference-atlas.json` — visual reference (compressed per B3).

Do NOT store per-slide exports, page-images, project photos, grouped extraction images, alternate experiments, or exploratory previews inside the skill — those stay in the working folder. (This is what once bloated the skill to 45MB.)

### B7. Register the Profile

Add one entry to the **Template Profile Registry** below: profile name, one-line visual description, and the trigger phrases/keywords that should select it in Mode A. A profile that isn't registered here is invisible to Mode A.

---

## Template Profile Registry

Profiles live under this skill's `templates/<profile-name>/`. Mode A selects from this list; Mode B appends to it.

- `kals-mint-editorial`: white 16:9 editorial deck with mint green circular accents, bold black title systems, image-plus-text layouts, device frames, simple charts, map overlays, and compact business copy modules. Triggers: user asks for this template, "不错的模版", the mint-circle Kals style, or reusing the built-in template elements.
- `senyan-template`: cream minimalist fashion/branding editorial — one giant grotesque display word per slide, signature peach gradient circle, navy/coral/gold mood blocks, tiny uppercase corner microcopy chrome. Spec lives in the profile's `content-plan.md`; starter deck at `htmlppt/index.html` (image frames reference project photos — replace with project assets). Triggers: "senyan", "森言", 品牌手册 / 时尚 / 极简编辑部 style requests.
- `mihong-deck`: holographic "acid" business deck — iridescent full-bleed foil covers/dividers, light crinkle-paper content slides, electric-blue bold-italic titles with chromatic offset shadows, iridescent spheres / outline circles / solid dots, sparkle stars, wave charts, circle-trio stages, options-timelines, SWOT circles. Spec lives in the profile's `content-plan.md`; starter deck at `htmlppt/index.html`. Triggers: "mihong", "米红模版", holographic/acid/iridescent style requests.
- `red-halo-minimal`: white minimal editorial — one soft red radial halo blob per page, black grotesque titles, B&W interior photography, red/gray charts. Triggers: "红晕", "小夕素材(2)", 极简留白 + 一点红.
- `olive-botanical`: cream-greige canvas + olive green blocks + botanical photography, giant olive display words overlapping photos, 温柔自然. Triggers: "橄榄绿", "植物系", "小夕素材(13)", Cloverie.
- `crimson-grain-acid`: 中文商务 — crimson grainy diffuse-gradient covers with black four-point sparkles + hairline grid chrome, white content pages with black outline boxes and red infographics, metallic silver flower photos. Triggers: "绯红", "弥散渐变", "酸性", "小夕素材(21)".
- `y2k-marquee-white`: 中文活动策划 — white canvas framed by marquee ticker text borders, black outline cards, holographic chrome 3D props (cat/mannequin), aqua gradient accents, B&W infographics. Triggers: "跑马灯", "Y2K", "铬猫", "小夕素材(29)".
- `splash-annual-report`: business annual report — dark charcoal covers/dividers with blue-water × molten-gold splash photography, white content pages with blue-violet gradient UI cards/buttons/progress, full data & team page set. Triggers: "水花", "年报", "小夕素材(31)", SaaS 汇报风.

---

## Shared Rules (Both Modes)

Component family naming — use these names consistently in `profile.md`, `content-plan.md`, and HTML class/comment structure, so the flow continues cleanly from atlas to HTMLPPT to PPTX:

- `cover/title-system`
- `section/divider`
- `body/two-column`
- `body/image-plus-text`
- `body/editorial-copy`
- `media/image-frame`
- `card/case-study`
- `chart/big-number`
- `chart/timeline`
- `chrome/page-number`
- `decorative/shape-system`

Universal decision rules:

- When copy and layout conflict, cut copy. The 3-line budget wins over completeness; move detail to speaker notes or an appendix slide.
- Never bake text into a generated image; labels are always editable HTML chips (later editable PPTX text).
- 一个 deck 只有一套三级字体方案（封面/标题/正文），从 `fonts/` 库选定并贯穿 HTMLPPT 与 PPTX；不要中途混入第四种字体。
- The reference atlas is never final output — it is only the source for element extraction.
- Preserve style, hierarchy, and component language; never preserve tiny unreadable source text.
- Keep final important text editable in HTML and in any migrated PPTX.
