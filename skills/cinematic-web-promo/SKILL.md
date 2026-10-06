---
name: cinematic-web-promo
description: "Create cinematic Remotion product videos from real websites or frontend projects using an offline bundled video-shotcraft snapshot, automatic recipe routing, exact demo TSX imports, shared components, Gallery previews, Ink Press, page capture, inertial scrolling, click zooms, beat-synced cuts, mechanical SFX, and final QA. Use for website promos, landing-page films, product tours, video-shotcraft/Ink Press/Gallery recipe requests, and reusable website-to-video workflows. Do not use for ordinary footage-only edits with no website or product capture."
---

# Cinematic Web Promo

Turn a real website into a 16:9 product film that proves the product exists while giving it editorial, cinematic rhythm. Use actual page captures for evidence and Remotion for authored camera movement, typography, overlays, and sound.

## Select the Host Adapter

Identify the active host once, then read only its adapter:

- Codex: read `references/platform-codex.md`.
- Claude Code: read `references/platform-claude-code.md`.
- WorkBuddy Desktop or CodeBuddy workspace: read `references/platform-workbuddy.md`.

Use the shared workflow below after applying that host's path, invocation, and browser rules. Do not assume one host's skill directory on another host.

## Operating Contract

- Treat the supplied website or frontend as the source of truth. Do not redraw the whole product as generic UI.
- Separate evidence shots (real page capture) from authored title cards and overlays.
- Match the requested language in both the page capture and on-screen copy.
- Never bundle or publish unlicensed music. A user-provided reference track is draft-only until rights are confirmed.
- Keep click targets fixed during a zoom; move the camera around the target, not the target around the frame.
- Prefer masks, soft vignettes, editorial labels, parallax, and light sweeps. Avoid decorative blue focus boxes unless the product itself uses them.
- Make scrolling feel physical: eased velocity, visible section arrivals, a fixed pointer, and synchronized mechanical ticks or locks.
- Render a music version and a no-music version from the same timeline when music rights are uncertain.
- Route named or requested Shotcraft motion through the bundled, commit-locked upstream index and exact demo source. Never recreate a named recipe from its title alone.
- Use the embedded Shotcraft snapshot by default. Access GitHub only when the user explicitly asks to refresh or select another upstream version.

## Workflow

### 0. Resolve the Skill Root and Run Preflight

Set `CWP_SKILL_DIR` to the absolute directory containing this `SKILL.md`. Claude Code can map `${CLAUDE_SKILL_DIR}` to it. Codex exposes the skill path in its skill catalog. WorkBuddy Desktop should use the imported package resources or its authorized local copy.

```bash
export CWP_SKILL_DIR="/absolute/path/to/cinematic-web-promo"
"$CWP_SKILL_DIR/scripts/preflight.sh" --browser auto --beats auto
```

On Windows PowerShell, run `& "$env:CWP_SKILL_DIR/scripts/preflight.ps1" -Browser auto -Beats auto`. The preflight reports missing Node, browser automation, Python beat-analysis packages, ffmpeg/ffprobe, and starter files. `auto` warns about optional capabilities; use `playwright` or `required` to make them blocking. Do not assume dependencies are globally installed.

### 1. Inspect and Capture

1. Open the URL and identify the value proposition, product proof, dark/light sections, interaction targets, and final CTA.
2. Capture desktop 1920x1080 viewport frames plus one full-page image. Prefer the active browser tool when it preserves authenticated state.
3. If a scriptable browser is available, run `"$CWP_SKILL_DIR/scripts/capture_page.mjs"`. Trigger lazy-loaded sections by scrolling before the final full-page capture.
4. Hide browser chrome, cookie banners, floating translation widgets, and unrelated tab bars. Never hide product content.
5. Record the capture URL, timestamp, viewport, locale, and any authentication assumptions.
6. Gate the concept against the page: if the document is shorter than about 1.6 viewports, has fewer than three meaningful sections, or lacks a real click target, do not fabricate product proof. Ask for a richer URL, request permission to add clearly authored editorial interludes, or downgrade the scroll/click beats.

Read `references/workflow.md` for the detailed capture and shot-planning procedure.

### 2. Route Shotcraft Motion

Run the router before locking the storyboard whenever the user names video-shotcraft, Ink Press, a Gallery card/style, or asks the agent to select polished upstream motion:

```bash
python3 "$CWP_SKILL_DIR/scripts/shotcraft_router.py" \
  --query "product function, desired motion, material, and energy" \
  --top 5 \
  --out-dir "/absolute/promo-project/shotcraft"
```

Use repeatable `--recipe` arguments for exact Gallery names. By default the router reads the Skill's embedded Shotcraft snapshot without network access, validates card/style names, imports the exact recipe and ranked demo TSX plus required shared assets, copies the matching preview, and writes `shotcraft-lock.json` with hashes and the fixed upstream commit. Read `references/shotcraft-router.md`, every selected recipe, the plausible implementation TSX, and the preview before adaptation.

Do not execute imported source blindly. Review imports, static assets, licenses, and dependency hints first. Preserve tuned timing, easing, mask boundaries, holds, and documented pitfalls; replace screenshots, copy, brand tokens, measured coordinates, and necessary framing. If the embedded snapshot fails integrity checks, stop and report it; do not silently approximate a named Shotcraft recipe.

### 3. Write a Shot Recipe

Create 6-10 shots. Each shot must have:

- duration in frames;
- source asset or page region;
- camera start/end scale and translation;
- one clear story beat;
- transition type;
- SFX and music beat target;
- proof text, if any.

Use this default arc:

1. brand premise;
2. hero page proof;
3. inertial landing-page scroll;
4. click or feature zoom;
5. two product-detail proofs;
6. outcome statement;
7. CTA or brand sign-off.

Keep title cards short. Copy should describe outcomes, not narrate every UI element.

### 4. Build the Remotion Composition

Copy `assets/remotion-starter` into a new working directory, then replace its placeholder page asset, dimensions, and copy. For routed shots, copy the locked upstream implementation into the working project and adapt it locally; never runtime-import remote code. Merge every routed `packageDependencies` entry into `package.json`, update the project's package-manager lockfile, install from that lock, and run TypeScript checks. Do not call the editable source reproducible or ready while the manifest and lock disagree or typechecking fails. Also copy any helpers you will invoke, or continue calling them through the absolute `CWP_SKILL_DIR`. Use 1920x1080, 30fps, H.264/AAC unless the user specifies otherwise.

Core patterns live in `references/remotion-patterns.md`:

- `PageCam`: transform a real screenshot with scale, translation, bank, blur, and mask;
- `ScrollTape`: a fixed pointer with moving ticks to externalize scroll velocity;
- `ClickFocus`: a target-stable cursor press, ripple, and camera push;
- `FlashCut`: a short warm exposure lift that never becomes a full white frame;
- title cards: high-contrast serif + compact technical metadata;
- audio mix: BGM bed with foreground mechanical SFX and short ducks at impact frames.

Keep props for `bgm`, `locale`, and content paths so the same timeline can produce variants.

### 5. Make Scrolling and Clicking Feel Physical

For page scrolls:

- divide the full page into meaningful section stops;
- use four or more eased segments instead of one linear translate;
- accelerate through low-information space and decelerate into proof sections;
- add a subtle 0.2-0.6 degree bank during acceleration and settle to zero at stops;
- move tape ticks under a fixed pointer; play a tick bed while moving and a metallic lock on arrival;
- add a soft mask or vignette so the page feels framed, not boxed.

For clicks:

- place the cursor and click ripple on the actual target;
- use 5-8 frames for the main push, optional 4-6 frame micro-recoil, and motion blur;
- keep the target at a stable screen coordinate through the move;
- reveal the destination with a soft radial or rounded mask over 12-20 frames;
- pair the first push frame with a metallic/camera click, not a visual border.

### 6. Align Music and Sound

1. Accept only licensed, generated, public-domain, or explicitly user-provided music. Record source, rights scope, attribution, proof URL/file, and verification timestamp in `media-license-manifest.json`; apply the same standard to SFX.
2. Analyze the clean music file with `"$CWP_SKILL_DIR/scripts/analyze_beats.py"`.
3. Start the edit on a strong beat or downbeat. Move important cuts within ±3 frames when possible.
4. Put mechanical clicks, locks, and whooshes on visual action frames.
5. Normalize the music source before Remotion, then mix it as a bed. Duck 1-3 dB for 8-14 frames around major impacts.
6. Check peaks after the final encode. Target true/encoded peak below -1 dBFS; -3 to -5 dBFS is a safe promo master.

Do not use a tutorial's full audio as BGM. Separate narration first, review for vocal bleed, and treat the result as a private draft unless publication rights are verified.

### 7. Render and Verify

Run TypeScript checks before rendering. Render the BGM version and, when applicable, the no-BGM version. Then run:

```bash
"$CWP_SKILL_DIR/scripts/qa_video.sh" path/to/final.mp4
```

Review at least these frames manually: first frame, every cut ±1 frame, each click frame, each section arrival, and final frame. Reject single-frame white flashes, unreadable text, wrong-language page content, cursor drift, blue focus boxes, clipped audio, silent gaps, or accidental browser chrome.

Read `references/qa-checklist.md` before delivery.

## Deliverables

Return:

- final MP4;
- optional no-BGM MP4;
- editable Remotion project;
- shot recipe/timeline notes;
- `shotcraft-lock.json`, selected recipe cards, demo source paths, and preview provenance;
- capture provenance;
- music and SFX license notes;
- QA summary with resolution, duration, codecs, peak level, and any intentional freeze/hold segments.

## Portability

This folder follows the Agent Skills layout and keeps host-specific behavior in references and installers. Read `references/compatibility.md`. Install with `scripts/install_skill.sh` on macOS/Linux or `scripts/install_skill.ps1` on Windows. Generate all three distributable packages with `scripts/package_three_targets.sh <output-directory>`.
