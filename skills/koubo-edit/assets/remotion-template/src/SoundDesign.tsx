import React from "react";
import { Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import { AudioCue, msToFrame, plan } from "./plan";

const clamp = (value: number, min: number, max: number) =>
  Math.max(min, Math.min(max, value));

const cueVolume = (cue: AudioCue, frame: number, fps: number, duration: number) => {
  const base = clamp(cue.volume ?? 1, 0, 1);
  const fadeIn = Math.max(0, msToFrame(cue.fade_in_ms ?? 0, fps));
  const fadeOut = Math.max(0, msToFrame(cue.fade_out_ms ?? 0, fps));
  const fadeInGain = fadeIn > 0 ? clamp(frame / fadeIn, 0, 1) : 1;
  const fadeOutStart = Math.max(0, duration - fadeOut);
  const fadeOutGain = fadeOut > 0 ? clamp((duration - frame) / fadeOut, 0, 1) : 1;
  return base * Math.min(fadeInGain, fadeOutStart <= frame ? fadeOutGain : 1);
};

/**
 * Frame-aware audio mixer for edit-plan.json.  Each cue is isolated in a
 * Sequence so plans can place a large SFX library on exact spoken-word or
 * transition frames without changing the video scene code.
 */
export const SoundDesign: React.FC = () => {
  const { fps, durationInFrames } = useVideoConfig();
  return (
    <>
      {(plan.audio ?? []).map((cue, index) => {
        const from = msToFrame(cue.start_ms, fps);
        const requestedDuration = cue.end_ms
          ? msToFrame(cue.end_ms, fps) - from
          : durationInFrames - from;
        const duration = Math.max(1, Math.min(durationInFrames - from, requestedDuration));
        if (from >= durationInFrames || duration <= 0) return null;
        return (
          <Sequence key={`${cue.src}-${index}`} from={from} durationInFrames={duration}>
            <Audio
              src={staticFile(`audio/${cue.src}`)}
              loop={cue.loop}
              volume={(frame) => cueVolume(cue, frame, fps, duration)}
            />
          </Sequence>
        );
      })}
    </>
  );
};
