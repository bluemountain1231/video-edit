# Remotion Patterns

## Composition Contract

Use a single source of timeline truth:

```ts
export const SHOTS = {
  open: {from: 0, duration: 210},
  thesis: {from: 210, duration: 60},
  scroll: {from: 270, duration: 180},
  detail: {from: 450, duration: 360},
  outcome: {from: 810, duration: 250},
  outro: {from: 1060, duration: 205},
} as const;
```

Derive SFX frames and transitions from this object. Avoid duplicated magic numbers.

## Camera Transform

Use CSS transforms only on the screenshot layer. Put masks, captions, cursor, and scroll tape in stable screen space.

```ts
const scale = interpolate(frame, [0, duration], [1.02, 1.16], opts);
const y = interpolate(frame, [0, duration], [0, -260], opts);
const bank = interpolate(frame, [0, 14, duration - 10, duration], [0, -0.35, 0.2, 0], opts);
```

For fast pushes, use a short spring or an eased 5-8 frame interpolation. If available, add directional motion blur during those frames. Recoil should be subtle: about 3-6% of the push distance.

## Inertial Multi-Stop Scroll

Define each stop with `from`, `to`, `start`, and `end`. Convert page progress to screenshot translation, then apply a small bank while velocity is high. Hold 4-12 frames at high-value sections so the viewer can read.

The fixed pointer must remain at one screen coordinate. Tape ticks move in the opposite direction of the page. Derive tick velocity from page progress so audio and visuals agree.

## Click Zoom

Keep the target center stable:

```ts
const targetX = 0.68 * width;
const targetY = 0.44 * height;
const zoom = interpolate(local, [0, 6, 11], [1, 1.34, 1.30], opts);
const tx = width / 2 - targetX;
const ty = height / 2 - targetY;
```

Apply the camera transform around the target or compensate translation as scale changes. Put the click ripple above the page, 2-5 frames long. Begin the destination reveal after the press lands.

## Flash Cuts

A flash cut should lift exposure briefly, not create a full white frame. Keep the peak opacity below about 0.72 and composite a warm color over visible source frames on both sides of the cut. Always inspect cut-1, cut, and cut+1.

## Audio Mix

Normalize source music before import. In Remotion, keep a `bgm` prop and a frame-aware volume function:

```tsx
<Audio src={staticFile('audio/music.mp3')} volume={(frame) => bgmGain(frame)} />
```

Use short gain dips around high-energy impacts. Mechanical scroll sounds should form a tactile layer: low tick/spin bed while moving, metallic lock at arrival, and a deeper impact only for the primary feature reveal.

Do not solve clipping by applying a final limiter alone. Reduce source gains, preserve transient hierarchy, then verify the encoded file.
