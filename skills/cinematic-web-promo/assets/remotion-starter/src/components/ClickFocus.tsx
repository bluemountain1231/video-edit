import {interpolate, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export const ClickFocus: React.FC<{duration: number; x: number; y: number}> = ({duration, x, y}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const press = spring({frame, fps, config: {damping: 14, stiffness: 260, mass: 0.55}, durationInFrames: 14});
  const ripple = interpolate(frame, [1, 13], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const opacity = interpolate(frame, [0, 2, 13, 18], [0, 1, 0.45, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const cursorOpacity = interpolate(frame, [0, 5, duration - 20, duration], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  return (
    <>
      <div style={{position: 'absolute', left: x - 46, top: y - 46, width: 92, height: 92, borderRadius: '50%', border: '2px solid #ff5a24', opacity, transform: `scale(${0.35 + ripple * 1.25})`}} />
      <div style={{position: 'absolute', left: x, top: y, width: 26, height: 36, opacity: cursorOpacity, transform: `translate(-3px,-3px) scale(${1 - press * 0.13})`, filter: 'drop-shadow(0 4px 8px #0008)'}}>
        <svg viewBox="0 0 26 36" width="26" height="36"><path d="M2 2L22 21H13L18 32L12 35L7 24L2 30Z" fill="#f7f2e8" stroke="#171714" strokeWidth="2" /></svg>
      </div>
    </>
  );
};
