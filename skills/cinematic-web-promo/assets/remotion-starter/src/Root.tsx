import {Composition} from 'remotion';
import {Promo, PROMO_FRAMES} from './Promo';

export const Root: React.FC = () => (
  <Composition
    id="WebPromo"
    component={Promo}
    durationInFrames={PROMO_FRAMES}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={{
      bgm: false,
      sfx: true,
      brand: 'Your Product',
      locale: 'en-US',
      screenshot: 'site-placeholder.svg',
      pageHeight: 3000,
      clickX: 1320,
      clickY: 520,
    }}
  />
);
