import {interpolate, useCurrentFrame} from 'remotion';

export const FlashCut: React.FC<{duration: number}> = ({duration}) => {
  const frame = useCurrentFrame();
  const opacity = interpolate(frame, [0, duration * 0.45, duration], [0, 0.62, 0], {
    extrapolateLeft: 'clamp', extrapolateRight: 'clamp',
  });
  return <div style={{position: 'absolute', inset: 0, background: '#fff1d5', opacity, mixBlendMode: 'screen'}} />;
};
