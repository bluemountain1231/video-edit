# Shotcraft Recipe Router

Use this reference whenever the user names video-shotcraft, Ink Press, a Gallery card/style, or asks the agent to choose polished upstream motion.

## Contract

Treat the embedded Gallery index, previews, recipes, demo source, shared components, and Ink Press template as one version-locked upstream snapshot. Never recreate a named effect from its title alone. The online Gallery and GitHub repository are refresh sources, not runtime dependencies.

For every routed shot:

1. use the embedded snapshot's exact upstream commit unless the user explicitly requests a refresh;
2. validate the card/style against `gallery/api/library.json`;
3. read the complete recipe card;
4. inspect the ranked demo TSX and the selected MP4 preview;
5. preserve tuned timing, easing, mask boundaries, holds, and documented pitfalls;
6. replace product imagery, copy, brand tokens, measured coordinates, and necessary composition framing;
7. retain `shotcraft-lock.json` with the editable Remotion project.

The router imports source but never executes it. Review imports, dependencies, static assets, and license notes before adding it to a composition.

## Automatic Route

Use a concrete intent containing product function, motion, material, and energy:

```bash
python3 "$CWP_SKILL_DIR/scripts/shotcraft_router.py" \
  --query "landing-page downward scroll, fixed metal tape pointer, cursor click and fast target zoom, Ink Press editorial tone" \
  --top 5 \
  --out-dir "/absolute/promo-project/shotcraft"
```

The default `--source auto` route is fully offline and contains:

- the exact upstream commit and Gallery revision;
- distinct selected cards and concrete style keys;
- ranked demo TSX candidates;
- imported recipe cards, demos, fixtures, reusable helpers, and public assets;
- selected embedded MP4 previews, with their original Gallery URLs retained only as provenance;
- package/static-file integration hints;
- SHA-256 hashes for imported source and previews.

Windows PowerShell can invoke the same router with `py -3`:

```powershell
py -3 "$env:CWP_SKILL_DIR\scripts\shotcraft_router.py" `
  --recipe tape-scroll-fixed-pointer `
  --out-dir "C:\absolute\promo-project\shotcraft"
```

Open `shotcraft-lock.json`, then read each selected recipe and its first plausible implementation candidate. If the first candidate does not express the selected style, inspect the remaining ranked candidates instead of guessing.

## Exact Route

When the user supplies a Gallery name, prefer exact lookup:

```bash
python3 "$CWP_SKILL_DIR/scripts/shotcraft_router.py" \
  --recipe tape-scroll-fixed-pointer \
  --recipe cursor-performance \
  --recipe crash-zoom-punch \
  --out-dir "/absolute/promo-project/shotcraft"
```

Use `--recipe ink-press` to import the complete upstream template. A card name selects its indexed default style; a style key selects that exact variant. Unknown names must fail with real nearest matches.

## Embedded Snapshot and Reproducibility

The Skill bundles `assets/shotcraft-snapshot/` with:

- all recipe cards under `references/shots`;
- all demo TSX, fixtures, and textures under `demos`;
- reusable upstream helpers under `assets/lib`;
- the complete Ink Press `template`;
- `gallery/api/library.json` and every indexed MP4 preview;
- the upstream Apache-2.0 license, attribution, and `SNAPSHOT.json` hashes.

The default route uses that snapshot and its fixed 40-character commit. It does not resolve `main` online. Re-run with either `--source embedded` or the commit from the lock:

```bash
python3 "$CWP_SKILL_DIR/scripts/shotcraft_router.py" \
  --source embedded \
  --ref COMMIT_FROM_LOCK \
  --recipe tape-scroll-fixed-pointer \
  --out-dir "/absolute/promo-project/shotcraft-rebuild"
```

For an authorized local checkout or extracted archive:

```bash
python3 "$CWP_SKILL_DIR/scripts/shotcraft_router.py" \
  --offline-root "/absolute/video-shotcraft" \
  --ref EXACT_40_CHARACTER_COMMIT \
  --query "physical scroll and click zoom" \
  --no-previews \
  --out-dir "/absolute/promo-project/shotcraft"
```

An extracted archive without `.git` requires the exact commit. `--offline-root` always takes precedence over the embedded and remote modes.

## Explicit Upstream Refresh

Do not refresh during normal video work. When the user explicitly requests a newer Shotcraft version, review the upstream license/change scope, then rebuild the snapshot atomically:

```bash
python3 "$CWP_SKILL_DIR/scripts/sync_shotcraft_snapshot.py" \
  --ref main \
  --force
```

For a one-off network import that must not modify the Skill snapshot, pass `--source remote --ref BRANCH_TAG_OR_COMMIT`. Both refresh paths resolve and lock an exact commit. Re-run preflight, integrity tests, and three-host packaging after any snapshot update.

## Adaptation Rules

- Route before finalizing the storyboard so exact recipe durations and holds inform the timeline.
- Preview the embedded MP4 before adapting the TSX. Source parameters are the implementation truth; the preview is the perceptual acceptance target.
- Copy selected code into the working Remotion project; do not runtime-import from the Skill or a remote URL.
- Add every `integration.packageDependencies` entry to the working project's package manifest, regenerate the matching npm/pnpm lockfile, install from that lock, and run TypeScript checks before declaring source preparation complete.
- Treat a manifest/lock mismatch, missing routed dependency, or failed typecheck as blocking even when recipe import and preview download succeeded.
- Keep a click target at a stable screen coordinate during the push.
- Keep fixed-pointer tape mechanics separate from page translation: the tape visualizes velocity while the page remains the product evidence.
- Re-measure coordinates from the target page. Do not retain demo fixture coordinates.
- Do not copy upstream placeholder branding, screenshots, or copy into the final film.
- Do not import upstream music by default. Apply the project's existing media-rights rules independently.
- Preserve the upstream Apache-2.0 license and attribution files for redistributed source. Recipe cards derived from third-party motion studies may include additional provenance warnings; read `references/shots/ATTRIBUTION.md` before publication.

## Ink Press Boundary

Ink Press is a complete upstream template, while recipe cards are modular motion grammar. When Ink Press is selected, choose one of these explicitly in the design spec:

- template mode: retain its sequence structure and replace product content;
- recipe mode: use only selected Ink Press-compatible ideas while composing a new sequence.

Do not combine both silently or claim a custom sequence is the unchanged Ink Press template.
