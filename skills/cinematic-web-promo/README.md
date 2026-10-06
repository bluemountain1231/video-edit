# Cinematic Web Promo

An offline-first Agent Skill for turning real websites and frontend projects into cinematic Remotion product films.

It bundles a version-locked snapshot of [video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft), automatically routes a motion request to exact recipe cards and Demo TSX implementations, imports the required shared components and assets, and preserves the matching Gallery preview for visual acceptance testing.

## What is included

- 152 indexed Shotcraft recipe cards
- 209 motion styles and 209 MP4 Gallery previews
- 202 Demo TSX files
- shared helpers from `assets/lib`
- the complete Ink Press template
- Remotion starter composition and website-capture tools
- inertial scrolling, fixed-pointer tape, click zoom, beat analysis, SFX, and final-video QA workflows
- Codex, Claude Code, WorkBuddy, and CodeBuddy adapters/installers

The embedded upstream is locked to:

- video-shotcraft commit: `41ee360d82f4c491ba9d88a24a4add7d8ff1cf8b`
- Gallery revision: `bdd94be16d60fa8f`

Every embedded source file and preview is recorded with a SHA-256 digest in `assets/shotcraft-snapshot/SNAPSHOT.json`.

## Why bundle Shotcraft?

Named effects should not be recreated from their titles. The router reads the exact Gallery index, recipe, Demo TSX, shared dependencies, and preview from the embedded snapshot. Normal routing therefore works without GitHub or Gallery access and remains reproducible after upstream changes.

Network access is used only when the caller explicitly requests a different upstream version or refreshes the snapshot.

## Install

Clone over SSH:

```bash
git clone git@github.com:bluemountain1231/cinematic-web-promo.git
cd cinematic-web-promo
```

Codex user install:

```bash
./scripts/install_skill.sh codex-user
```

Claude Code user install:

```bash
./scripts/install_skill.sh claude-user
```

CodeBuddy workspace install:

```bash
./scripts/install_skill.sh codebuddy-project /absolute/workspace
```

Build the three distributable ZIP packages:

```bash
./scripts/package_three_targets.sh /absolute/output-directory
```

Windows users can use `scripts/install_skill.ps1` and `scripts/preflight.ps1`.

## Route exact Shotcraft motion

Set the absolute Skill path:

```bash
export CWP_SKILL_DIR="$PWD"
```

Route by intent:

```bash
python3 "$CWP_SKILL_DIR/scripts/shotcraft_router.py" \
  --query "landing-page scroll with a fixed metal tape pointer, cursor click, fast target zoom, and Ink Press editorial tone" \
  --top 5 \
  --out-dir "/absolute/promo-project/shotcraft"
```

Route exact Gallery styles:

```bash
python3 "$CWP_SKILL_DIR/scripts/shotcraft_router.py" \
  --recipe tape-scroll-fixed-pointer \
  --recipe crash-zoom-punch \
  --out-dir "/absolute/promo-project/shotcraft"
```

The router writes `shotcraft-lock.json` containing the fixed upstream commit, Gallery revision, selected recipes, Demo TSX paths, imported file hashes, preview hashes, dependencies, and static-file mappings.

## Default source policy

`--source auto` is the default and prefers the embedded snapshot. It does not silently fall back to a network approximation when the snapshot is corrupt.

Use a one-off remote import only when explicitly needed:

```bash
python3 "$CWP_SKILL_DIR/scripts/shotcraft_router.py" \
  --source remote \
  --ref BRANCH_TAG_OR_COMMIT \
  --recipe crash-zoom-punch \
  --out-dir "/absolute/promo-project/shotcraft"
```

Refresh the embedded snapshot intentionally:

```bash
python3 "$CWP_SKILL_DIR/scripts/sync_shotcraft_snapshot.py" \
  --ref main \
  --force
```

Re-run validation and packaging after any refresh.

## Validate

```bash
./scripts/preflight.sh --browser auto --beats auto
```

For an offline router smoke test:

```bash
python3 scripts/shotcraft_router.py \
  --source embedded \
  --recipe tape-scroll-fixed-pointer \
  --json
```

The release snapshot was independently blind-tested without network access: all 445 embedded source records and 209 preview records matched their manifest hashes.

## Project layout

```text
SKILL.md                              Main Agent Skill workflow
agents/openai.yaml                    Codex Skill metadata
assets/remotion-starter/              Editable Remotion starter
assets/shotcraft-snapshot/            Commit-locked offline Shotcraft library
references/                           Host adapters and production guidance
scripts/shotcraft_router.py           Recipe search, import, and lock generation
scripts/sync_shotcraft_snapshot.py    Atomic upstream snapshot refresh
scripts/capture_page.mjs              Website capture helper
scripts/analyze_beats.py              Music beat analysis
scripts/qa_video.sh                   Final MP4 QA
```

## Licensing and attribution

This repository is licensed under Apache-2.0. The embedded video-shotcraft snapshot is also distributed under its upstream Apache-2.0 license. The original upstream license and motion-study attribution are preserved inside the snapshot.

See [NOTICE](NOTICE), [LICENSE](LICENSE), and `assets/shotcraft-snapshot/repo/references/shots/ATTRIBUTION.md` before redistributing derived source or publishing a film that incorporates third-party reference material.

Music and SFX rights remain project-specific. Do not publish unlicensed reference tracks.
