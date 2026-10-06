import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Video } from "@remotion/media";
import { ACCENT, BoardColor, BoardStep, Scene, msToFrame } from "./plan";

const BOARD_COLORS: Record<BoardColor, string> = {
  white: "#ffffff",
  lime: "#C6FF00",
  yellow: "#FFE10A",
  blue: "#5AC8FF",
  red: "#FF5A4E",
  green: "#7CE84A",
};

/** 黑底暗纹画布：参考片里 demo/概念卡共用的深色点纹背景 */
export const DottedCanvas: React.FC<{ children?: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill
    style={{
      backgroundColor: "#0a0a0d",
      backgroundImage:
        "radial-gradient(rgba(255,255,255,0.07) 1.4px, transparent 1.4px)",
      backgroundSize: "34px 34px",
    }}
  >
    {children}
  </AbsoluteFill>
);

/** 录屏演示：白描边圆角大卡，弹入后微微定住 */
export const DemoScene: React.FC<{ scene: Extract<Scene, { mode: "demo" }> }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200, stiffness: 120 }, durationInFrames: 18 });
  const frameW = width * 0.82;
  const frameH = height * 0.8;
  return (
    <DottedCanvas>
      <div
        style={{
          position: "absolute",
          left: (width - frameW) / 2 + width * 0.03,
          top: (height - frameH) / 2 - height * 0.02,
          width: frameW,
          height: frameH,
          borderRadius: 30,
          background: "#fff",
          border: "6px solid #fff",
          outline: "3px solid #0b0b0e",
          outlineOffset: -9,
          boxShadow: "0 30px 80px rgba(0,0,0,.6)",
          overflow: "hidden",
          opacity: enter,
          transform: `translateY(${interpolate(enter, [0, 1], [40, 0])}px) scale(${interpolate(enter, [0, 1], [0.96, 1])})`,
        }}
      >
        <Video
          muted
          loop
          src={staticFile(`media/${scene.broll}`)}
          trimBefore={msToFrame(scene.broll_offset_ms ?? 0, fps)}
          style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover" }}
        />
      </div>
    </DottedCanvas>
  );
};

/** 概念卡：超大标题 + 荧光副标块，或居中一句话 */
export const ConceptScene: React.FC<{ scene: Extract<Scene, { mode: "concept" }> }> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 200, stiffness: 140 }, durationInFrames: 16 });
  const titleSize = Math.round(Math.min(width * 0.11, height * 0.2));
  return (
    <DottedCanvas>
      <AbsoluteFill style={{ justifyContent: "center", alignItems: "center", gap: height * 0.02 }}>
        {scene.highlight ? (
          <div
            style={{
              background: ACCENT,
              color: "#0b0b0e",
              fontFamily: '"PingFang SC", sans-serif',
              fontWeight: 900,
              fontSize: Math.round(titleSize * 0.34),
              padding: `${Math.round(height * 0.008)}px ${Math.round(width * 0.014)}px`,
              borderRadius: 6,
              transform: `rotate(-1.2deg) scale(${enter})`,
              letterSpacing: 3,
            }}
          >
            {scene.highlight}
          </div>
        ) : null}
        {scene.title ? (
          <div
            style={{
              color: "#fff",
              fontFamily: '"Helvetica Neue", "PingFang SC", sans-serif',
              fontWeight: 900,
              fontSize: titleSize,
              letterSpacing: 2,
              textAlign: "center",
              maxWidth: "90%",
              lineHeight: 1.1,
              opacity: enter,
              transform: `translateY(${interpolate(enter, [0, 1], [30, 0])}px)`,
              textShadow: "0 8px 40px rgba(0,0,0,.6)",
            }}
          >
            {scene.title}
          </div>
        ) : null}
        {scene.note ? (
          <div
            style={{
              color: "#fff",
              fontFamily: '"PingFang SC", sans-serif',
              fontWeight: 700,
              fontSize: Math.round(height * 0.055),
              opacity: enter,
              letterSpacing: 2,
            }}
          >
            {scene.note}
          </div>
        ) : null}
      </AbsoluteFill>
    </DottedCanvas>
  );
};

/** 打字机一行：按帧推进字符数，打字中显示光标块 */
const TypeLine: React.FC<{
  step: BoardStep;
  sceneStart: number;
  fontSize: number;
}> = ({ step, sceneStart, fontSize }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const stepStart = msToFrame(step.start_ms, fps) - sceneStart;
  const parts = step.parts ?? [{ text: step.text ?? "", color: step.color ?? "white" }];
  const fullText = parts.map((p) => p.text).join("");
  const useTyping = step.typewriter !== false;
  const charFrames = 1.15; // ≈38ms/字，跟得上正常语速
  const shown = useTyping
    ? Math.max(0, Math.floor((frame - stepStart) / charFrames))
    : fullText.length;
  const typing = useTyping && shown < fullText.length;
  const pop = spring({
    frame: frame - stepStart,
    fps,
    config: { damping: 200, stiffness: 300 },
    durationInFrames: 6,
  });

  let remaining = shown;
  return (
    <div
      style={{
        fontFamily: '"PingFang SC", sans-serif',
        fontWeight: 800,
        fontSize,
        lineHeight: 1.9,
        letterSpacing: 2,
        opacity: pop,
        whiteSpace: "nowrap",
      }}
    >
      {parts.map((part, index) => {
        const take = Math.max(0, Math.min(part.text.length, remaining));
        remaining -= take;
        return (
          <span key={index} style={{ color: BOARD_COLORS[part.color ?? step.color ?? "white"] }}>
            {part.text.slice(0, take)}
          </span>
        );
      })}
      {typing ? (
        <span style={{ color: "#fff", opacity: Math.floor(frame / 4) % 2 === 0 ? 1 : 0.15 }}>▍</span>
      ) : null}
    </div>
  );
};

/** 白板讲解卡：框架固定，元素渐进（物料贴纸 + 换色标题块 + 打字机正文） */
export const BoardScene: React.FC<{
  scene: Extract<Scene, { mode: "board" }>;
}> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const sceneStart = msToFrame(scene.start_ms, fps);
  const enter = spring({ frame, fps, config: { damping: 200, stiffness: 140 }, durationInFrames: 14 });

  const frameLeft = width * 0.045;
  const frameTop = height * 0.06;
  const frameW = width * 0.91;
  const frameH = height * 0.82;
  const lineSize = Math.round(height * 0.058);

  const titles = scene.steps.filter(
    (s) => s.kind === "title" && frame >= msToFrame(s.start_ms, fps) - sceneStart,
  );
  const title = titles[titles.length - 1];
  const lines = scene.steps.filter(
    (s) => s.kind === "line" && frame >= msToFrame(s.start_ms, fps) - sceneStart,
  );
  const titlePop = title
    ? spring({
        frame: frame - (msToFrame(title.start_ms, fps) - sceneStart),
        fps,
        config: { damping: 13, stiffness: 240, mass: 0.6 },
        durationInFrames: 12,
      })
    : 0;
  const propPop = spring({ frame: frame - 4, fps, config: { damping: 12, stiffness: 160, mass: 0.8 }, durationInFrames: 18 });
  const titleColor = BOARD_COLORS[title?.color ?? "lime"];

  return (
    <DottedCanvas>
      <div
        style={{
          position: "absolute",
          left: frameLeft,
          top: frameTop,
          width: frameW,
          height: frameH,
          border: `${Math.max(3, Math.round(height * 0.006))}px solid rgba(255,255,255,.96)`,
          borderRadius: 28,
          opacity: enter,
          transform: `scale(${interpolate(enter, [0, 1], [0.97, 1])})`,
        }}
      >
        {scene.tag ? (
          <div
            style={{
              position: "absolute",
              left: 24,
              top: -Math.round(height * 0.028),
              background: "#FFE10A",
              color: "#0b0b0e",
              fontFamily: '"PingFang SC", sans-serif',
              fontWeight: 900,
              fontSize: Math.round(height * 0.036),
              padding: `${Math.round(height * 0.006)}px ${Math.round(width * 0.012)}px`,
              borderRadius: 8,
              boxShadow: "4px 4px 0 rgba(0,0,0,.9)",
              transform: "rotate(-1deg)",
            }}
          >
            {scene.tag}
          </div>
        ) : null}

        {scene.prop ? (
          <div
            style={{
              position: "absolute",
              left: "6%",
              top: "16%",
              width: "26%",
              textAlign: "center",
              transform: `scale(${propPop})`,
            }}
          >
            {scene.prop_label ? (
              <div
                style={{
                  color: "#cfc4ff",
                  fontFamily: '"PingFang SC", sans-serif',
                  fontWeight: 900,
                  fontSize: Math.round(height * 0.052),
                  letterSpacing: 4,
                  marginBottom: 8,
                  textShadow: "0 0 24px rgba(160,140,255,.5)",
                }}
              >
                {scene.prop_label}
              </div>
            ) : null}
            <Img
              src={staticFile(`media/${scene.prop}`)}
              style={{
                maxWidth: "88%",
                maxHeight: frameH * 0.5,
                objectFit: "contain",
                filter: "drop-shadow(0 14px 40px rgba(120,120,255,.28))",
                transform: `translateY(${Math.sin(frame / 22) * 6}px)`,
              }}
            />
          </div>
        ) : null}

        {title ? (
          <div
            style={{
              position: "absolute",
              right: "7%",
              top: "9%",
              background: titleColor,
              color: title?.color === "red" ? "#fff" : "#0b0b0e",
              fontFamily: '"PingFang SC", sans-serif',
              fontWeight: 900,
              fontSize: Math.round(height * 0.062),
              padding: `${Math.round(height * 0.008)}px ${Math.round(width * 0.016)}px`,
              borderRadius: 10,
              letterSpacing: 3,
              boxShadow: "5px 5px 0 rgba(0,0,0,.85)",
              transform: `rotate(-1deg) scale(${titlePop})`,
              transformOrigin: "center",
            }}
          >
            {title.text}
          </div>
        ) : null}

        <div
          style={{
            position: "absolute",
            left: "40%",
            top: "30%",
            display: "flex",
            flexDirection: "column",
            gap: Math.round(height * 0.012),
          }}
        >
          {lines.map((line, index) => (
            <TypeLine key={index} step={line} sceneStart={sceneStart} fontSize={lineSize} />
          ))}
        </div>
      </div>
    </DottedCanvas>
  );
};

/** AI 插图：居中完整展示 + 缓慢放大，可叠大字标题 */
export const IllustrationScene: React.FC<{
  scene: Extract<Scene, { mode: "illustration" }>;
}> = ({ scene }) => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const total = msToFrame(scene.end_ms - scene.start_ms, fps);
  const enter = spring({ frame, fps, config: { damping: 200, stiffness: 120 }, durationInFrames: 16 });
  const kenBurns = interpolate(frame, [0, Math.max(total, 1)], [1, 1.06]);
  const cover = scene.fit === "cover";
  return (
    <DottedCanvas>
      <Img
        src={staticFile(`media/${scene.image}`)}
        style={
          cover
            ? {
                position: "absolute",
                inset: 0,
                width: "100%",
                height: "100%",
                objectFit: "cover",
                opacity: enter,
                transform: `scale(${kenBurns})`,
              }
            : {
                position: "absolute",
                left: "50%",
                top: "50%",
                maxWidth: "86%",
                maxHeight: "82%",
                borderRadius: 20,
                boxShadow: "0 30px 90px rgba(0,0,0,.65)",
                opacity: enter,
                transform: `translate(-50%, -50%) scale(${kenBurns})`,
              }
        }
      />
      {scene.title ? (
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: height * 0.07,
            textAlign: "center",
            color: "#fff",
            fontFamily: '"Helvetica Neue", "PingFang SC", sans-serif',
            fontWeight: 900,
            fontSize: Math.round(Math.min(width * 0.075, height * 0.13)),
            letterSpacing: 4,
            textShadow: "0 6px 30px rgba(0,0,0,.85), 0 0 60px rgba(0,0,0,.5)",
            opacity: enter,
            transform: `translateY(${interpolate(enter, [0, 1], [-24, 0])}px)`,
          }}
        >
          {scene.title}
        </div>
      ) : null}
    </DottedCanvas>
  );
};
