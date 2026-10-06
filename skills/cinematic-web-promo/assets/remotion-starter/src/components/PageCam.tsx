import {Img, interpolate, staticFile, useCurrentFrame} from 'remotion';

export type PageCamProps = {
  src: string;
  duration: number;
  mode?: 'push' | 'scroll';
  pageHeight: number;
  progress: number;
  focusX?: number;
  focusY?: number;
};

const clamp = {extrapolateLeft: 'clamp' as const, extrapolateRight: 'clamp' as const};

export const PageCam: React.FC<PageCamProps> = ({src, duration, mode = 'push', pageHeight, progress, focusX = 1320, focusY = 520}) => {
  const frame = useCurrentFrame();
  const cameraScale = mode === 'scroll'
    ? interpolate(progress, [0, 1], [1.03, 1.08], clamp)
    : interpolate(frame, [0, 7, 12], [1, 1.32, 1.28], clamp);
  const displayHeight = pageHeight * (1808 / 1920);
  const maxTravel = Math.max(0, displayHeight - 968);
  const y = -Math.min(maxTravel, maxTravel * progress);
  const bank = mode === 'scroll'
    ? Math.sin(progress * Math.PI * 8) * 0.24
    : 0;
  const originX = focusX - 56;
  const originY = focusY - 56;

  return (
    <div style={{position: 'absolute', inset: 56, borderRadius: 34, overflow: 'hidden', boxShadow: '0 38px 100px #0008'}}>
      <div
        style={{
          position: 'absolute',
          inset: 0,
          transformOrigin: mode === 'push' ? `${originX}px ${originY}px` : '50% 8%',
          transform: `scale(${cameraScale}) rotateZ(${bank}deg)`,
        }}
      >
        <Img
          src={staticFile(src)}
          style={{
            position: 'absolute',
            left: 0,
            top: 0,
            width: '100%',
            transform: `translateY(${y}px)`,
          }}
        />
      </div>
      <div style={{position: 'absolute', inset: 0, boxShadow: 'inset 0 0 130px #0008', pointerEvents: 'none'}} />
    </div>
  );
};
