import React from "react";
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { CAPTION_ACCENT, plan, msToFrame, Caption } from "./plan";

/** 把 text 按 keywords 切开，关键词内联变色（参考片的黑底条内彩字风格） */
const renderText = (caption: Caption): React.ReactNode => {
  const keywords = (caption.keywords ?? []).filter(
    (k) => k && caption.text.includes(k),
  );
  if (keywords.length === 0) return caption.text;
  const pattern = keywords
    .map((k) => k.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"))
    .join("|");
  return caption.text.split(new RegExp(`(${pattern})`)).map((part, index) =>
    keywords.includes(part) ? (
      <span key={index} style={{ color: CAPTION_ACCENT }}>
        {part}
      </span>
    ) : (
      <React.Fragment key={index}>{part}</React.Fragment>
    ),
  );
};

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const active = plan.captions.find(
    (c) => frame >= msToFrame(c.start_ms, fps) && frame < msToFrame(c.end_ms, fps),
  );
  if (!active) return null;

  const start = msToFrame(active.start_ms, fps);
  const pop = spring({
    frame: frame - start,
    fps,
    config: { damping: 200, stiffness: 300 },
    durationInFrames: 7,
  });
  const fontSize = Math.round(Math.min(width * 0.036, height * 0.052));

  return (
    <div
      style={{
        position: "absolute",
        left: 0,
        right: 0,
        bottom: height * 0.038,
        display: "flex",
        justifyContent: "center",
        opacity: interpolate(pop, [0, 1], [0, 1]),
        transform: `translateY(${interpolate(pop, [0, 1], [10, 0])}px)`,
        zIndex: 50,
      }}
    >
      <div
        style={{
          maxWidth: "84%",
          textAlign: "center",
          fontFamily: '"PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif',
          fontWeight: 700,
          fontSize,
          lineHeight: 1.45,
          letterSpacing: 1.5,
          color: "#fff",
          background: "rgba(8,8,10,.68)",
          padding: `${Math.round(fontSize * 0.22)}px ${Math.round(fontSize * 0.75)}px`,
          borderRadius: 10,
        }}
      >
        {renderText(active)}
      </div>
    </div>
  );
};
