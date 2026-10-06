export const ScrollTape: React.FC<{progress: number}> = ({progress}) => {
  const travel = -1260 * progress;
  return (
    <div style={{position: 'absolute', right: 66, top: 90, bottom: 90, width: 72, overflow: 'hidden'}}>
      <div style={{position: 'absolute', inset: 0, background: 'linear-gradient(#111,transparent 18%,transparent 82%,#111)', zIndex: 2}} />
      <div style={{position: 'absolute', left: 34, top: 0, transform: `translateY(${travel % 36}px)`}}>
        {Array.from({length: 48}).map((_, index) => (
          <div key={index} style={{width: index % 4 === 0 ? 25 : 13, height: 1, marginBottom: 35, background: '#d9d4c8', opacity: index % 4 === 0 ? 0.9 : 0.45}} />
        ))}
      </div>
      <div style={{position: 'absolute', zIndex: 3, top: '50%', right: 1, width: 46, height: 2, background: '#ff5a24', boxShadow: '0 0 16px #ff5a24'}} />
    </div>
  );
};
