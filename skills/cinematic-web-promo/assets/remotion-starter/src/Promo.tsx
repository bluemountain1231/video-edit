import {AbsoluteFill, Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {ClickFocus} from './components/ClickFocus';
import {FlashCut} from './components/FlashCut';
import {PageCam} from './components/PageCam';
import {ScrollTape} from './components/ScrollTape';

export type PromoProps = {
  bgm?: boolean;
  sfx?: boolean;
  brand: string;
  locale: string;
  screenshot: string;
  pageHeight: number;
  clickX: number;
  clickY: number;
};

export const SHOTS = {
  open: {from: 0, duration: 150},
  scroll: {from: 150, duration: 510},
  click: {from: 660, duration: 210},
  outro: {from: 870, duration: 180},
} as const;

export const PROMO_FRAMES = 1050; // 35 seconds at 30fps

const title: React.CSSProperties = {
  color: '#181714',
  fontFamily: 'Georgia, Times New Roman, serif',
  fontSize: 118,
  fontWeight: 700,
  letterSpacing: -5,
  lineHeight: 0.92,
  textAlign: 'center',
};

const smooth = (value: number) => value * value * (3 - 2 * value);

export const scrollProgressAt = (frame: number) => {
  const stops = [
    {from: 0, to: 0.22, start: 0, end: 105},
    {from: 0.22, to: 0.54, start: 126, end: 255},
    {from: 0.54, to: 0.78, start: 279, end: 389},
    {from: 0.78, to: 1, start: 414, end: 510},
  ];
  for (const stop of stops) {
    if (frame <= stop.start) return stop.from;
    if (frame <= stop.end) {
      const t = interpolate(frame, [stop.start, stop.end], [0, 1], {
        extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
      });
      return stop.from + (stop.to - stop.from) * smooth(t);
    }
  }
  return 1;
};

const bgmGain = (frame: number) => {
  const distance = Math.abs(frame - SHOTS.click.from);
  const duck = interpolate(distance, [0, 14], [0.72, 1], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return 0.3 * duck;
};

const scrollTickGain = (frame: number) => {
  const velocity = Math.abs(scrollProgressAt(frame) - scrollProgressAt(Math.max(0, frame - 1)));
  return interpolate(velocity, [0, 0.0015, 0.004], [0, 0.18, 0.38], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
};

export const Promo: React.FC<PromoProps> = ({
  bgm = false,
  sfx = true,
  brand,
  locale,
  screenshot,
  pageHeight,
  clickX,
  clickY,
}) => (
  <AbsoluteFill style={{background: '#f1eee5'}} data-locale={locale}>
    {bgm ? <Audio src={staticFile('audio/music.mp3')} volume={(frame) => bgmGain(frame)} /> : null}
    {sfx ? (
      <>
        <Sequence from={SHOTS.scroll.from} durationInFrames={SHOTS.scroll.duration}>
          <Audio src={staticFile('audio/scroll-ticks.wav')} volume={(frame) => scrollTickGain(frame)} />
        </Sequence>
        <Sequence from={SHOTS.click.from} durationInFrames={30}>
          <Audio src={staticFile('audio/click-metal.wav')} volume={0.65} />
        </Sequence>
      </>
    ) : null}

    <Sequence from={SHOTS.open.from} durationInFrames={SHOTS.open.duration}>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        <div style={{...title, maxWidth: 1300}}>{brand}<br />deserves a film.</div>
        <div style={{position: 'absolute', bottom: 110, fontFamily: 'Arial, sans-serif', fontSize: 17, letterSpacing: 6}}>
          REAL PRODUCT · AUTHORED MOTION
        </div>
      </AbsoluteFill>
    </Sequence>

    <Sequence from={SHOTS.scroll.from} durationInFrames={SHOTS.scroll.duration}>
      <ScrollScene screenshot={screenshot} pageHeight={pageHeight} />
    </Sequence>

    <Sequence from={SHOTS.click.from} durationInFrames={SHOTS.click.duration}>
      <AbsoluteFill style={{background: '#11110f'}}>
        <PageCam
          src={screenshot}
          duration={SHOTS.click.duration}
          mode="push"
          pageHeight={pageHeight}
          progress={0.52}
          focusX={clickX}
          focusY={clickY}
        />
        <ClickFocus duration={SHOTS.click.duration} x={clickX} y={clickY} />
      </AbsoluteFill>
    </Sequence>

    <Sequence from={SHOTS.click.from - 4} durationInFrames={10}>
      <FlashCut duration={10} />
    </Sequence>

    <Sequence from={SHOTS.outro.from} durationInFrames={SHOTS.outro.duration}>
      <AbsoluteFill style={{alignItems: 'center', justifyContent: 'center'}}>
        <div style={{...title, color: '#181714'}}>{brand}</div>
        <div style={{position: 'absolute', bottom: 130, fontFamily: 'Arial, sans-serif', fontSize: 18, letterSpacing: 7}}>
          BUILT TO BE REMEMBERED
        </div>
      </AbsoluteFill>
    </Sequence>
  </AbsoluteFill>
);

const ScrollScene: React.FC<{screenshot: string; pageHeight: number}> = ({screenshot, pageHeight}) => {
  const frame = useCurrentFrame();
  const progress = scrollProgressAt(frame);
  return (
    <AbsoluteFill style={{background: '#11110f'}}>
      <PageCam src={screenshot} duration={SHOTS.scroll.duration} mode="scroll" pageHeight={pageHeight} progress={progress} />
      <ScrollTape progress={progress} />
    </AbsoluteFill>
  );
};
