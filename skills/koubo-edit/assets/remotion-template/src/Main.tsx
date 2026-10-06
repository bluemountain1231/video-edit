import React from "react";
import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from "remotion";
import { Video } from "@remotion/media";
import { Captions } from "./Captions";
import { ChapterTags, PropImages, SideNotes, Stickers } from "./Overlays";
import { BoardScene, DemoScene, ConceptScene, IllustrationScene } from "./Scenes";
import { plan, msToFrame, Scene } from "./plan";
import { SoundDesign } from "./SoundDesign";

const TRANSITION_FRAMES = 14;

type PipStyle = "square" | "circle" | "none";

const defaultPip = (scene: Scene): PipStyle => {
  if (scene.pip) return scene.pip;
  if (scene.mode === "concept") return "none";
  return "square";
};

/** 当前帧所处的非口播场景及其进入/退出进度（0 全屏口播 → 1 完全进入场景） */
const sceneStateAt = (
  frame: number,
  fps: number,
): { scene: Scene | null; progress: number; pip: PipStyle } => {
  for (const scene of plan.scenes) {
    const start = msToFrame(scene.start_ms, fps);
    const end = msToFrame(scene.end_ms, fps);
    if (frame < start || frame > end) continue;
    const enter = interpolate(frame, [start, start + TRANSITION_FRAMES], [0, 1], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    });
    const exit = interpolate(frame, [end - TRANSITION_FRAMES, end], [1, 0], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.inOut(Easing.cubic),
    });
    return { scene, progress: Math.min(enter, exit), pip: defaultPip(scene) };
  }
  return { scene: null, progress: 0, pip: "square" };
};

export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps, width, height } = useVideoConfig();
  const { progress, pip } = sceneStateAt(frame, fps);

  const conf = plan.pip ?? {};

  // 三种缩小目标：左下圆角方卡 / 右下圆窗 / 隐藏（缩小淡出）
  let targetW: number, targetH: number, targetLeft: number, targetTop: number, targetRadius: number;
  if (pip === "circle") {
    const d = (conf.size_ratio ?? 0.3) * Math.min(width, height);
    targetW = d;
    targetH = d;
    targetLeft = width - d - width * 0.035;
    targetTop = height - d - height * 0.13;
    targetRadius = d / 2;
  } else if (pip === "square") {
    const w = (conf.size_ratio ?? 0.16) * width;
    targetW = w;
    targetH = w * 1.12;
    targetLeft = width * 0.035;
    targetTop = height - w * 1.12 - height * 0.05;
    targetRadius = w * 0.14;
  } else {
    targetW = width * 0.3;
    targetH = height * 0.3;
    targetLeft = width * 0.35;
    targetTop = height * 0.35;
    targetRadius = 24;
  }

  const boxW = interpolate(progress, [0, 1], [width, targetW]);
  const boxH = interpolate(progress, [0, 1], [height, targetH]);
  const boxLeft = interpolate(progress, [0, 1], [0, targetLeft]);
  const boxTop = interpolate(progress, [0, 1], [0, targetTop]);
  const radius = interpolate(progress, [0, 1], [0, targetRadius]);
  const speakerOpacity = pip === "none" ? interpolate(progress, [0, 0.85], [1, 0], { extrapolateRight: "clamp" }) : 1;

  // <Video> 画布不响应 objectFit，手动算 cover 几何并按 focus_y 对准人脸
  const coverScale = Math.max(boxW / width, boxH / height);
  const innerW = width * coverScale;
  const innerH = height * coverScale;
  const focusY = parseFloat(conf.focus_y ?? "28%") / 100;
  const innerLeft = (boxW - innerW) / 2;
  const innerTop = -(innerH - boxH) * focusY;

  const borderPx = Math.max(4, Math.round(Math.min(width, height) * 0.008));

  return (
    <AbsoluteFill style={{ backgroundColor: "#000" }}>
      {plan.scenes.map((scene, index) => {
        const start = msToFrame(scene.start_ms, fps);
        const end = msToFrame(scene.end_ms, fps);
        return (
          <Sequence key={index} from={start} durationInFrames={Math.max(1, end - start)}>
            {scene.mode === "demo" ? (
              <DemoScene scene={scene} />
            ) : scene.mode === "concept" ? (
              <ConceptScene scene={scene} />
            ) : scene.mode === "board" ? (
              <BoardScene scene={scene} />
            ) : (
              <IllustrationScene scene={scene} />
            )}
          </Sequence>
        );
      })}
      <div
        style={{
          position: "absolute",
          left: boxLeft,
          top: boxTop,
          width: boxW,
          height: boxH,
          borderRadius: radius,
          overflow: "hidden",
          opacity: speakerOpacity,
          border: `${borderPx}px solid rgba(255,255,255,${progress * 0.95})`,
          boxShadow:
            progress > 0.01
              ? `0 ${targetW * 0.08}px ${targetW * 0.25}px rgba(0,0,0,${progress * 0.55})`
              : "none",
          zIndex: 20,
        }}
      >
        <Video
          src={staticFile(`media/${plan.source}`)}
          style={{
            position: "absolute",
            left: innerLeft,
            top: innerTop,
            width: innerW,
            height: innerH,
          }}
        />
      </div>
      <PropImages />
      <SideNotes />
      <Stickers />
      <ChapterTags />
      <Captions />
      <SoundDesign />
    </AbsoluteFill>
  );
};
