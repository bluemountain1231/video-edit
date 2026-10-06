import React from "react";
import { Img, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { ACCENT, plan, msToFrame } from "./plan";

const FONT = '"PingFang SC", "Hiragino Sans GB", sans-serif';

const NOTE_COLORS: Record<string, { bg: string; fg: string }> = {
  lime: { bg: "#C6FF00", fg: "#0b0b0e" },
  yellow: { bg: "#FFE10A", fg: "#0b0b0e" },
  white: { bg: "#ffffff", fg: "#0b0b0e" },
};

/** 左上角黄色章节角标：黑色错位投影 + 微旋转，参考片的「实操演示」样式 */
export const ChapterTags: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const active = (plan.chapter_tags ?? []).find(
    (t) => frame >= msToFrame(t.start_ms, fps) && frame < msToFrame(t.end_ms, fps),
  );
  if (!active) return null;
  const enter = spring({
    frame: frame - msToFrame(active.start_ms, fps),
    fps,
    config: { damping: 14, stiffness: 220, mass: 0.6 },
    durationInFrames: 14,
  });
  return (
    <div
      style={{
        position: "absolute",
        left: width * 0.045,
        top: height * 0.055,
        background: "#FFE10A",
        color: "#0b0b0e",
        fontFamily: FONT,
        fontWeight: 900,
        fontSize: Math.round(height * 0.052),
        padding: `${Math.round(height * 0.012)}px ${Math.round(width * 0.016)}px`,
        borderRadius: 10,
        boxShadow: "7px 7px 0 rgba(0,0,0,.92)",
        transform: `rotate(-1.5deg) scale(${enter})`,
        transformOrigin: "left top",
        letterSpacing: 2,
        zIndex: 40,
      }}
    >
      {active.text}
    </div>
  );
};

/** 人物侧方荧光大字块：叠放 + 依次弹入 + 交替微旋转 */
export const SideNotes: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const active = (plan.side_notes ?? []).find(
    (n) => frame >= msToFrame(n.start_ms, fps) && frame < msToFrame(n.end_ms, fps),
  );
  if (!active) return null;
  const start = msToFrame(active.start_ms, fps);
  const side = active.side ?? "right";
  const { bg, fg } = NOTE_COLORS[active.color ?? "lime"];
  const fontSize = Math.round(height * 0.078);
  const itemH = fontSize * 1.72;
  const stackH = active.items.length * itemH + (active.items.length - 1) * height * 0.028;
  const top0 = Math.max(height * 0.1, height * 0.42 - stackH / 2);
  return (
    <>
      {active.items.map((item, index) => {
        const enter = spring({
          frame: frame - start - index * 6,
          fps,
          config: { damping: 13, stiffness: 200, mass: 0.7 },
          durationInFrames: 15,
        });
        const slide = interpolate(enter, [0, 1], [side === "right" ? 120 : -120, 0]);
        return (
          <div
            key={index}
            style={{
              position: "absolute",
              [side]: width * 0.045,
              top: top0 + index * (itemH + height * 0.028),
              background: bg,
              color: fg,
              fontFamily: FONT,
              fontWeight: 900,
              fontSize,
              lineHeight: 1.55,
              padding: `${Math.round(fontSize * 0.08)}px ${Math.round(fontSize * 0.45)}px`,
              borderRadius: 10,
              outline: `${Math.max(3, Math.round(fontSize * 0.07))}px solid rgba(255,255,255,.95)`,
              boxShadow: "0 14px 40px rgba(0,0,0,.45)",
              transform: `translateX(${slide}px) rotate(${(index % 2 === 0 ? -1 : 1) * 1.4}deg) scale(${Math.min(enter, 1)})`,
              opacity: Math.min(enter * 1.4, 1),
              letterSpacing: 3,
              zIndex: 30,
            }}
          >
            {item}
          </div>
        );
      })}
    </>
  );
};

/** 浮动物料：透明 PNG 弹入 + 轻微上下浮动，跟着口播语义出现 */
export const PropImages: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width } = useVideoConfig();
  const active = (plan.props ?? []).filter(
    (p) => frame >= msToFrame(p.start_ms, fps) && frame < msToFrame(p.end_ms, fps),
  );
  return (
    <>
      {active.map((prop, index) => {
        const enter = spring({
          frame: frame - msToFrame(prop.start_ms, fps),
          fps,
          config: { damping: 13, stiffness: 180, mass: 0.7 },
          durationInFrames: 15,
        });
        return (
          <Img
            key={index}
            src={staticFile(`media/${prop.image}`)}
            style={{
              position: "absolute",
              left: `${prop.x_pct ?? 70}%`,
              top: `${prop.y_pct ?? 20}%`,
              width: width * ((prop.w_pct ?? 14) / 100),
              filter: "drop-shadow(0 12px 34px rgba(120,120,255,.3))",
              transform: `rotate(${prop.rotate ?? 0}deg) scale(${enter}) translateY(${Math.sin((frame + index * 40) / 20) * 6}px)`,
              zIndex: 28,
            }}
          />
        );
      })}
    </>
  );
};

/** 小贴纸标注：白底彩色描边微旋转（如「需要密钥 🔑」） */
export const Stickers: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const stickers = (plan.stickers ?? []).filter(
    (s) => frame >= msToFrame(s.start_ms, fps) && frame < msToFrame(s.end_ms, fps),
  );
  const colors: Record<string, string> = { red: "#FF3B30", black: "#0b0b0e", lime: ACCENT };
  return (
    <>
      {stickers.map((sticker, index) => {
        const enter = spring({
          frame: frame - msToFrame(sticker.start_ms, fps),
          fps,
          config: { damping: 12, stiffness: 260, mass: 0.5 },
          durationInFrames: 12,
        });
        const edge = colors[sticker.color ?? "red"];
        return (
          <div
            key={index}
            style={{
              position: "absolute",
              left: `${sticker.x_pct ?? 66}%`,
              top: `${sticker.y_pct ?? 14}%`,
              background: "#fff",
              color: edge,
              border: `4px solid ${edge}`,
              fontFamily: FONT,
              fontWeight: 900,
              fontSize: Math.round(height * 0.045),
              padding: `${Math.round(height * 0.008)}px ${Math.round(width * 0.013)}px`,
              borderRadius: 999,
              boxShadow: "0 10px 30px rgba(0,0,0,.4)",
              transform: `rotate(${sticker.rotate ?? -4}deg) scale(${enter})`,
              zIndex: 35,
            }}
          >
            {sticker.text}
          </div>
        );
      })}
    </>
  );
};
