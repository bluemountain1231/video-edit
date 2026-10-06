import planJson from "../public/edit-plan.json";

export type Caption = {
  text: string;
  start_ms: number;
  end_ms: number;
  /** 本页里要变色强调的关键词（必须是 text 的子串），0-2 个为宜 */
  keywords?: string[];
};

/** 黄色章节角标（左上角，如「实操演示」「成分爆料」），一段时间内常驻 */
export type ChapterTag = {
  text: string;
  start_ms: number;
  end_ms: number;
};

/** 口播人物侧方的荧光大字块，2-4 个叠放，依次弹入 */
export type SideNote = {
  items: string[];
  start_ms: number;
  end_ms: number;
  /** 出现在人物哪一侧，默认 right */
  side?: "left" | "right";
  /** lime 荧光绿 / yellow 黄 / white 白底黑字，默认 lime */
  color?: "lime" | "yellow" | "white";
};

/** 浮动物料：物料工厂抠出的透明 PNG，弹入后轻微浮动，跟着口播语义出现 */
export type PropOverlay = {
  /** public/media/ 下的透明物料文件名 */
  image: string;
  start_ms: number;
  end_ms: number;
  /** 左上角位置百分比 */
  x_pct?: number;
  y_pct?: number;
  /** 宽度占画面宽的百分比，默认 14 */
  w_pct?: number;
  rotate?: number;
};

/** 小贴纸标注（如「需要密钥 🔑」），白底描边微旋转 */
export type Sticker = {
  text: string;
  start_ms: number;
  end_ms: number;
  /** 位置百分比（相对画面），默认右上区域 */
  x_pct?: number;
  y_pct?: number;
  color?: "red" | "black" | "lime";
  rotate?: number;
};

/**
 * Optional sound cue.  Files are resolved from public/audio/, so a plan can
 * use the bundled Shotcraft SFX by referring to e.g.
 * `shotcraft/transition-swoosh.mp3`.
 */
export type AudioCue = {
  src: string;
  start_ms: number;
  end_ms?: number;
  volume?: number;
  fade_in_ms?: number;
  fade_out_ms?: number;
  loop?: boolean;
};

/** A traceable planning reference selected from the optional talkcraft bridge. */
export type TalkcraftCardRef = {
  slug: string;
  start_ms: number;
  end_ms: number;
  reason?: string;
  variant?: string;
};

export type BoardColor = "white" | "lime" | "yellow" | "blue" | "red" | "green";

/** 白板卡的一个渐进步骤：换右上标题块，或追加一行正文（打字机） */
export type BoardStep = {
  /** 绝对时间（相对整条片），到点出现并保留 */
  start_ms: number;
  kind: "title" | "line";
  /** 单色文本（title 的文案 / line 的整行） */
  text?: string;
  /** 行内多色（line 用），如 [{"text":"危险操作","color":"red"},{"text":" → 前来询问"}] */
  parts?: { text: string; color?: BoardColor }[];
  /** title=色块底色（默认 lime）；line=整行文字色（默认 white） */
  color?: BoardColor;
  /** line 默认开启打字机；false 则整行直接弹出 */
  typewriter?: boolean;
};

export type Scene =
  | {
      /** 白板讲解卡：白描边外框固定，元素渐进——左侧物料贴纸 + 右上换色标题块 + 正文逐行打字机 */
      mode: "board";
      start_ms: number;
      end_ms: number;
      /** 框角黄色小标签（如「新对话」「成分爆料」） */
      tag?: string;
      /** public/media/ 下的透明物料 PNG（物料工厂抠图产物） */
      prop?: string;
      /** 物料上方的标题文字 */
      prop_label?: string;
      steps: BoardStep[];
      pip?: "square" | "circle" | "none";
    }
  | {
      /** 录屏演示：白描边圆角大卡装录屏，人物缩成左下圆角方卡 */
      mode: "demo";
      start_ms: number;
      end_ms: number;
      broll: string;
      broll_offset_ms?: number;
      /** square 左下方卡（默认）/ circle 右下圆窗 / none 隐藏人物 */
      pip?: "square" | "circle" | "none";
    }
  | {
      /** 概念卡：黑底暗纹 + 超大标题/荧光副标，用于转场、金句、章节开场 */
      mode: "concept";
      start_ms: number;
      end_ms: number;
      /** 超大主标题（英文用无衬线粗体、中文用超粗黑体） */
      title?: string;
      /** 荧光色块副标题（贴在主标题上方） */
      highlight?: string;
      /** 居中的一句话（没有 title 时单独使用） */
      note?: string;
      pip?: "square" | "circle" | "none";
    }
  | {
      /** AI 生成插图：黑底暗纹上居中展示，缓慢放大（Ken Burns） */
      mode: "illustration";
      start_ms: number;
      end_ms: number;
      /** public/media/ 下的图片文件名 */
      image: string;
      /** 叠在图上方的大字标题（可选） */
      title?: string;
      /** contain 完整展示（默认）/ cover 铺满 */
      fit?: "contain" | "cover";
      pip?: "square" | "circle" | "none";
    };

export type EditPlan = {
  fps: number;
  width: number;
  height: number;
  duration_ms: number;
  /** public/media/ 下的口播源视频文件名 */
  source: string;
  /** 荧光强调色，默认 #C6FF00（参考片的荧光绿） */
  accent?: string;
  /** 字幕关键词的内联强调色，默认 #FFD24A */
  caption_accent?: string;
  pip?: {
    /** 方卡宽度占画面宽的比例，默认 0.16；圆窗直径占短边比例，默认 0.3 */
    size_ratio?: number;
    /** 方形裁切时人脸纵向对位，默认 "28%" */
    focus_y?: string;
  };
  captions: Caption[];
  chapter_tags?: ChapterTag[];
  side_notes?: SideNote[];
  stickers?: Sticker[];
  props?: PropOverlay[];
  /** Optional BGM/SFX tracks mixed on top of the source video. */
  audio?: AudioCue[];
  /** Optional semantic-planning trace; the renderer ignores this metadata. */
  card_refs?: TalkcraftCardRef[];
  scenes: Scene[];
};

export const plan = planJson as unknown as EditPlan;

export const ACCENT = plan.accent ?? "#C6FF00";
export const CAPTION_ACCENT = plan.caption_accent ?? "#FFD24A";

export const msToFrame = (ms: number, fps: number): number =>
  Math.round((ms / 1000) * fps);
