# Final QA Checklist

## Picture

- Correct URL and language are visible.
- No browser tabs, address bar, cookie banner, translation widget, or unrelated overlay.
- First frame is intentional; final frame holds long enough to read.
- Every cut is checked at `cut-1`, `cut`, and `cut+1`.
- No single-frame white or near-white interruption.
- Real page content remains readable at important stops.
- Cursor and click ripple hit the true target.
- Target position stays stable through click zoom.
- Scroll movement has acceleration, deceleration, and section holds.
- Fixed pointer does not drift; tape ticks move consistently.
- No decorative blue focus boxes or generic mock-browser frames.

## Shotcraft Fidelity

- `shotcraft-lock.json` records the repository, exact commit, Gallery revision, selected card/style, source hashes, and preview hashes.
- Every claimed Shotcraft shot uses the selected recipe and a plausible implementation TSX from the lock; no shot is recreated from its name alone.
- The adapted shot is compared with the routed MP4 preview at action start, peak velocity/impact, settle, and final hold.
- Tuned timing, easing, mask boundaries, motion-blur window, and documented pitfall constraints are preserved unless the design spec records a deliberate change.
- Demo fixtures, placeholder copy, colors, coordinates, and screenshots are replaced with real product evidence and measured target coordinates.
- The upstream Apache-2.0 license and attribution material remain with redistributed source.
- Routed package dependencies appear in both the package manifest and its lockfile; a frozen install and TypeScript check pass from the delivered project.

## Audio

- Music and every SFX source are documented in `media-license-manifest.json` with license text/URL, permitted commercial/platform/territory scope, required attribution, proof, and verification timestamp.
- No narration or vocal bleed remains in an extracted BGM bed.
- Strong visual actions land on beats or clear musical subdivisions.
- Mechanical effects are audible but do not mask music.
- No unintended silence longer than 0.8 seconds.
- Encoded peak stays below -1 dBFS; no clipped samples.
- Music fades cleanly and does not end mid-transient.
- Generated music/SFX usage terms are retained; "AI-generated" alone is not a license.

## Technical

- Expected duration, resolution, frame rate, and aspect ratio.
- H.264 video and AAC audio unless another delivery spec is requested.
- 48 kHz stereo audio.
- No corrupt frames or decoder errors.
- File opens in a standard player and seeks correctly.
- Final MP4, editable project, and any optional no-BGM version are delivered from the approved output directory.

Automated freeze detection reports intentional holds too. Treat its output as a review list, not an automatic failure.
