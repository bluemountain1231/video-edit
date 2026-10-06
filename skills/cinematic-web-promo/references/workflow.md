# End-to-End Website Film Workflow

## Preflight

Confirm the URL, desired language, target duration, aspect ratio, preferred template, CTA, and music rights. If the user does not specify them, use English, 30-45 seconds, 1920x1080, and 30fps. Derive the visual direction from the product and routed Shotcraft recipes; use Ink Press only when the user names it or the product genuinely supports its editorial paper language.

Audit the page before capturing:

- hero claim and CTA;
- product screenshots or live UI;
- sections worth stopping on;
- dark/light visual contrast;
- interactions that communicate value;
- footer or CTA suitable for the sign-off;
- overlays that must be dismissed.

## Page Sufficiency Gate

Measure the document height after lazy loading and count meaningful sections and real interactions. A requested long scroll or click tour is unsupported when the page is shorter than roughly 1.6 viewports, has fewer than three useful sections, or offers no value-bearing interaction.

Choose one path explicitly:

1. ask for a richer product URL or authenticated app route;
2. obtain permission to insert clearly authored editorial cards, diagrams, or supplied product assets;
3. downgrade to a short hero/brand film without pretending that extra product proof exists.

Never stretch a sparse page off-canvas or invent features to satisfy a shot count.

## Capture Matrix

Capture:

| Asset | Purpose | Default |
|---|---|---|
| Hero viewport | Establish the product | 1920x1080 PNG |
| Full page | Authored vertical scroll | Full-page PNG |
| Product interaction | Click/zoom proof | Before and after PNG |
| Dark/high-contrast section | Rhythmic contrast | 1920x1080 PNG |
| CTA/footer | Closing proof | 1920x1080 PNG |

Wait for fonts, images, and animations to settle. Scroll through the page once to trigger lazy loading, return to the top, then capture. Set the browser locale before page load when the page localizes automatically.

Store the measured document height in capture metadata and pass it to the Remotion camera. This prevents hardcoded scroll travel from revealing empty canvas.

## Story and Shot Recipe

Before locking the timeline, route the intended motion through `scripts/shotcraft_router.py`. Use exact Gallery names when supplied; otherwise search with a concrete description of the product function, motion, material, and energy. Read the selected recipe, ranked demo source, MP4 preview, and `shotcraft-lock.json` before assigning frames.

Write one sentence that the film must prove. Example: "Leva is a living agent community where agents discover each other, collaborate, and retain shared memory."

Assign every shot one job. A useful 42-second rhythm at 30fps is:

| Frames | Job |
|---:|---|
| 0-210 | Brand premise and visual hook |
| 210-270 | Editorial thesis card |
| 270-450 | Full-page inertial scroll |
| 450-650 | Click/feature proof |
| 650-800 | Detail montage |
| 800-1060 | Outcome proof and contrast |
| 1060-1265 | Sign-off and CTA |

Use this only as a starting point. Move cuts to nearby beats once the music grid is known.

## Capture-to-Camera Mapping

For a screenshot with dimensions `imageWidth × imageHeight`, calculate the cover scale first. Apply camera scale and translation on top of that base. Clamp vertical translation so no empty canvas appears at maximum zoom.

For a full-page scroll, define semantic stops as normalized page positions (0 to 1) and interpolate between them with separate easing curves. Avoid one continuous linear motion. A good four-stage structure is hero → product proof → contrast section → CTA.

## Editorial Direction

Use the page's existing colors as evidence. Surround it with a neutral paper field, warm black, one accent sampled from the product, restrained grain, and short technical labels. Serif display type can carry the emotional statement; compact sans/mono type carries metadata.

Masks should guide attention, not announce the effect. Use feathered rounded rectangles, radial reveals, edge vignettes, paper windows, or gradient scrims. Avoid thick borders and glowing blue rectangles.

## Iteration Order

1. Validate the capture and language.
2. Route and preview exact Shotcraft implementations.
3. Lock the shot recipe and duration.
4. Lock camera movement without sound.
5. Add music and align key cuts.
6. Add foreground SFX.
7. Add captions and micro-overlays.
8. Run cut-frame and audio QA.

Do not polish typography before the page proof and camera timing are correct.
