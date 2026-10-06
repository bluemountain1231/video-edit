import React from "react";
import { Composition } from "remotion";
import { Main } from "./Main";
import { plan, msToFrame } from "./plan";

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Main"
      component={Main}
      durationInFrames={Math.max(1, msToFrame(plan.duration_ms, plan.fps))}
      fps={plan.fps}
      width={plan.width}
      height={plan.height}
    />
  );
};
