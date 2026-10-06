---
name: koubo-edit
description: 中文口播视频自动剪辑：输入一段口播视频（真人或数字人），可选配录屏素材，自动完成本机 Whisper 转写 → Remotion 成片。剪辑语言对标高级知识区/带货视频：黑底胶囊字幕+关键词变色、人物侧方荧光大字块、黄色章节角标、白板讲解卡（框架固定元素渐进+打字机）、物料工厂（gpt-image 一图多物料批量抠图+浮动物料）、概念大字卡、录屏白框演示卡+人物缩小窗。流程为三阶段：分析+物料确认 → 渲染 → 微调。当用户说「剪一下这条口播」「给视频加字幕」「把录屏配进去」「画中画」「配图」「做物料」「剪辑成片」「auto edit」，或提供口播视频/录屏想要成片时，使用本 skill。只要交付物是"剪辑好的口播成片"，即使用户没提到剪辑二字，也应触发。
---

# 口播自动剪辑（koubo-edit）

把一段口播剪成可直接发布的成片。本机 Whisper 拿到逐句/逐词时间戳，你（Claude）担任导演——不只是配字幕，而是**给整条片做视觉设计**：什么时候上大字、什么时候切演示、什么时候插一张生成的配图。写成 `edit-plan.json` 交给 Remotion 渲染，全程本机。

## 视觉语言（对标高级知识区成片）

一共 5 种画面场景 + 5 种叠加层，全部由 plan 驱动：

**场景（scenes，互不重叠，空档默认全屏口播）**

| mode | 画面 | 用途 |
|---|---|---|
| （无） | 口播全屏 | 默认底座 |
| `demo` | 黑底暗纹 + 白描边圆角大卡装录屏，人物缩到左下圆角方卡 | 实操演示、界面展示 |
| `concept` | 黑底暗纹 + 超大标题/荧光色块副标/居中金句 | 章节开场、转场、观点定格 |
| `illustration` | 黑底暗纹 + AI 生成配图（缓慢放大）+ 可叠大字 | 比喻、场景化、产品/概念可视化 |
| `board` | 白描边外框**固定**，元素**渐进**：左侧物料贴纸 + 右上换色标题块 + 正文逐行打字机 | 结构化讲解——规则、对比、分条论述（最高级的手法，讲解段优先用它） |

**叠加层（可与任何场景同时出现）**

- `captions`：底部黑底半透明胶囊白字，关键词内联变色（黄）。字号中等，不抢画面
- `side_notes`：人物侧方 2-4 个荧光绿/黄大字块，叠放依次弹入、交替微旋转——**枚举、并列卖点、痛点清单必用**
- `chapter_tags`：左上角黄底黑字角标（「实操演示」「成分爆料」），一个段落内常驻
- `stickers`：白底彩描边小贴纸（「需要密钥 🔑」「限时价💥」），点缀用
- `props`：物料工厂抠出的透明物料浮动出现（弹入+轻浮动），跟着口播语义对位——说到价格上价签、说到安全上盾牌。**抠出来的物料尽量全部用上**，每个都在讲对应内容时登场

## 工作流（三阶段）

**阶段一 · 分析与物料确认**（步骤 1-5）：转写分析 → 设计 → 生产物料 → **把设计概要和全部物料 showcase 给用户确认**。
**阶段二 · 剪辑渲染**（步骤 6-7）：用户点头后才渲染，自检后交付。
**阶段三 · 微调**（步骤 8）：按反馈改 plan 秒级重渲。

物料确认是必经关卡——生图有随机性，渲染要几分钟，先把物料和设计给用户过目，比渲完再返工便宜得多。用户明确说"直接剪、不用确认"才可跳过阶段一的确认步。

约定：`SKILL_DIR = ~/.claude/skills/koubo-edit`（用户级安装，任意项目可用），渲染器常驻 `$SKILL_DIR/renderer/`（一次搭好全局复用，含 npm 依赖和无头浏览器），每单活的产物放**当前项目**的 `output/koubo-edit/jobs/<名字>/`。脚本带 PEP 723 内联依赖声明，`uv run` 在任何目录都能直接跑（首次自动建隔离环境）。

### 0. 环境与依赖（先读；除下面两样外，禁止自行安装任何东西）

**唯一需要预装的两样**：`uv`（`brew install uv`）和 Node.js ≥ 18（渲染器用）。开工前自检：

```bash
which uv node npm
```

**Python 依赖零手动安装**：`transcribe.py` / `cutout.py` 头部都有 PEP 723 内联声明，依赖**按平台自动选择**——Apple Silicon Mac 装 `mlx-whisper`（MLX，最快），Windows / Linux / Intel Mac 装 `faster-whisper`（CTranslate2，CPU 可跑），`uv run` 首次运行自动建好隔离环境。**严禁**自己 `pip install` 任何转写方案——尤其不要装 `openai-whisper` / `torch` / `whisperx`：两个后端都**不依赖 PyTorch**。如果发现自己正在下载 torch（100MB+）、llvmlite 这类包，说明已经走错路，立刻停下改用上面的 `uv run` 命令。

**平台**：macOS / Windows / Linux 全平台可用，同一条命令，转写后端自动切换（也可 `--backend mlx|faster` 强制指定）。Windows 注意两点：① 文档里的示例命令是 bash 风格，PowerShell 下把 `~` 换成 `$env:USERPROFILE`、`cp -R` 换成 `Copy-Item -Recurse` 即可，`uv run` 与 Node/Remotion 渲染流程完全一致；② 首次转写会从 Hugging Face 下载模型（small 约 460MB），网络慢时先 `set HF_ENDPOINT=https://hf-mirror.com` 再跑。

**ffmpeg 不是前置条件**：系统没有 ffmpeg 也能转写（脚本内置 static-ffmpeg 兜底）。文档里的 ffmpeg 质检/拼图命令若报 command not found，二选一：`brew install ffmpeg`，或直接用兜底二进制——

```bash
uv run --with static-ffmpeg python -c "from static_ffmpeg import run; print(run.get_or_fetch_platform_executables_else_raise()[0])"
```

**无外网 / 网络慢（国内环境）**：全链路都有国内通道，无需任何翻墙——

- Python 包：`export UV_DEFAULT_INDEX=https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple`
- npm 与无头浏览器：npmmirror，见「故障排查」
- Whisper 模型三级兜底，按顺序自动生效：① skill 目录下存在 `models/faster-whisper-small/`（百度网盘分发的完整离线版自带）时**直接用本地模型，零联网**；② 否则从 **hf-mirror.com 国内镜像**自动下载（脚本默认，设过 `HF_ENDPOINT` 则尊重用户配置，small 约 460MB）；③ 也可显式 `--model <任意本地模型目录>`
- GitHub 版仓库不含模型（超出 GitHub 文件大小限制），从 GitHub 装的用户走镜像自动下载即可；完全无网环境用网盘完整版

### 1. 收集输入

必需：口播视频。可选：录屏素材、口播原文文稿、手动编排指令。没有录屏/配图需求也能剪，但**不要只做字幕**——侧方大字、概念卡、生成配图都不依赖外部素材。

### 2. 本机转写

```bash
uv run ~/.claude/skills/koubo-edit/scripts/transcribe.py <口播视频> -o output/koubo-edit/jobs/<名字>/transcript.json
```

产出逐句 `segments` + 词级 `words` + 画幅元数据。识别不准加 `--model large-v3-turbo`（通用模型名，MLX / faster-whisper 两个后端自动映射）。Apple Silicon 走 MLX，Windows / Linux / Intel Mac 自动降级 faster-whisper，无需关心。

`metadata` 里的 `width/height` **已按显示方向换算**（手机竖拍视频常按横向存储 + 旋转元数据 `rotation`，播放端才转正；脚本读了 stream 的 side_data 做了换算）——plan 直接用这两个值，竖屏进就竖屏出，别再自己去 ffprobe 裸取 stream 宽高（那是存储方向，会把竖屏做成横屏）。

### 3. 当导演：通读文稿做视觉设计

读 transcript.json，先在心里把整条片**分成 2-5 个内容段**（钩子/痛点/方案/演示/行动号召……），再逐段决定视觉：哪里全屏讲、哪里切演示、哪里上概念卡、哪里需要一张图、哪几句配侧方大字。目标密度：**每 5-10 秒画面上要有一次新的视觉事件**（一页字幕不算事件）。写出 plan（字段定义见 [src/plan.ts](assets/remotion-template/src/plan.ts)）：

```json
{
  "fps": 30, "width": 1280, "height": 704, "duration_ms": 35000,
  "source": "koubo.mp4", "accent": "#C6FF00",
  "captions": [{ "text": "≤16字一页", "start_ms": 0, "end_ms": 2100, "keywords": ["关键词"] }],
  "chapter_tags": [{ "text": "成分爆料", "start_ms": 13000, "end_ms": 19800 }],
  "side_notes": [{ "items": ["烟酰胺 5%", "玻色因", "二裂酵母"], "start_ms": 13980, "end_ms": 18520, "side": "right", "color": "lime" }],
  "stickers": [{ "text": "限时价 💥", "start_ms": 22300, "end_ms": 25100, "x_pct": 62, "y_pct": 12, "color": "red" }],
  "props": [{ "image": "prop_4.png", "start_ms": 19820, "end_ms": 22300, "x_pct": 69, "y_pct": 18, "w_pct": 14, "rotate": 8 }],
  "scenes": [
    { "mode": "demo", "start_ms": 10000, "end_ms": 17000, "broll": "screen1.mp4" },
    { "mode": "concept", "start_ms": 19820, "end_ms": 22300, "highlight": "直播间专属", "title": "拍1发2" },
    { "mode": "illustration", "start_ms": 5000, "end_ms": 8000, "image": "ill_serum.png", "title": "28天实测" },
    { "mode": "board", "start_ms": 13080, "end_ms": 19820, "tag": "成分爆料", "prop": "prop_1.png", "prop_label": "王炸精华",
      "steps": [
        { "start_ms": 13080, "kind": "title", "text": "成分直接爆", "color": "lime" },
        { "start_ms": 13980, "kind": "line", "parts": [{ "text": "5% ", "color": "yellow" }, { "text": "烟酰胺" }] },
        { "start_ms": 18520, "kind": "title", "text": "打到骨折", "color": "red" }
      ] }
  ]
}
```

`width/height` 用源画幅（奇数减 1），`duration_ms` 用源时长。

### 4. 物料工厂：一次生成、批量抠图、全片复用

配图分两类，都用 gpt-image MCP（`mcp__gpt-image__generate_image`）生成：

**① 透明物料（board/贴纸用）——一张图生成一批**：把整条片要用的物件（产品、图标、道具）写进一条 prompt，要求「pure white background, evenly spaced 2x2 grid, one object per cell, consistent style」，生成一张 1536x1024，然后抠图切开：

```bash
uv run ~/.claude/skills/koubo-edit/scripts/cutout.py sheet.png --grid 2x2 \
  -o ~/.claude/skills/koubo-edit/renderer/public/media --prefix prop
```

得到 prop_1.png…（透明 PNG，已按内容裁边）。好处：一次生成省时省费、**全片物料同一画风**、同一物料在多个场景反复出现形成视觉锚点（参考片的吉祥物贴法）。风格推荐「soft 3D glassy gradient icon, blue-purple palette」或「flat bold sticker illustration with thick white outline」。

**② 全屏配图（illustration 场景用）**：单张生成，写明 dark/black background 才能和暗纹画布融为一体；横屏片 1536x1024、竖屏片 1024x1536。

两类都**不要让模型画文字**（文字由模板叠加，AI 生成的字会出错）。生成后必须用 Read 看一遍图，废图（元素粘连、风格跑偏）就重新生成。

**抠图质检（必做）**：Read 预览会把透明渲染成白色，看不出问题；把抠好的物料合到深色底上看真实效果——

```bash
ffmpeg -f lavfi -i "color=c=0x14141b:size=700x560" -i prop_1.png \
  -filter_complex "[0][1]overlay=20:20:format=auto" -frames:v 1 check.png
```

背景有雾状纹理残留说明生成图的白底不纯，调 `cutout.py --pad` 不行就加大 `white_to_alpha` 的 `floor`（默认 12）。裁边框如果顶满整个格子，基本就是噪点没除干净。

### 5. 物料确认：showcase 给用户过目

把**全部物料**（用户提供的 + 生成的，含备用）拼一张总览图发给用户：

```bash
# ffmpeg 深色底平铺（不加文字，标注写在消息里；drawtext 中文字体易出错）
ffmpeg -f lavfi -i "color=c=0x0f0f13:size=1680x860" -i ill_1.png -i prop_1.png ... \
  -filter_complex "[1]scale=780:-1[a];[0][a]overlay=40:170[x];..." -frames:v 1 showcase.png
```

随图在消息里给两样东西，然后**停下来等用户确认**：

1. **物料清单**：编号 · 文件名 · 来源（用户提供/AI生成）· 拟用于哪段（时间 + 场景）· 备用标注
2. **剪辑设计概要**：按时间轴列分段表——每段的时间区间、场景模式、叠加元素、一句话说明

用户提出换图/改设计就改完重新 showcase；确认后进阶段二。

### 6. 搭渲染器（首次一次）+ 放素材 + 渲染

```bash
R=~/.claude/skills/koubo-edit/renderer
[ -d "$R" ] || { cp -R ~/.claude/skills/koubo-edit/assets/remotion-template "$R" && cd "$R" && npm install; }  # 首次
```

```bash
R=~/.claude/skills/koubo-edit/renderer
mkdir -p "$R/public/media" output/koubo-edit/jobs/<名字>
cp <口播视频> "$R/public/media/koubo.mp4"
cp <录屏/配图> "$R/public/media/"
cp <plan> "$R/public/edit-plan.json"
# 需要音效时，把素材库中的文件复制进 public/audio/，并在 plan.audio 中钉帧
cp -R "$SKILL_DIR/assets/remotion-template/public/audio/shotcraft" "$R/public/audio/"
cd "$R" && npx tsc --noEmit && npx remotion render Main "<当前项目绝对路径>/output/koubo-edit/jobs/<名字>/final.mp4"
```

`tsc --noEmit` 先跑：plan JSON 字段拼错会在 3 秒内报出来，不用等渲染半途失败。模板更新后记得同步 `cp $SKILL_DIR/assets/remotion-template/src/* $R/src/`。

### Shotcraft 素材库（可选增强）

`assets/remotion-library/` 已冻结一份来自 video-shotcraft 的离线素材库：
149 个按类别整理的 SFX、5 首 BGM、221 个 Remotion Demo、158 张镜头卡和图库索引。
需要查找镜头时先读 `manifest.json` 与 `shots/`，再复制对应 Demo 及其 `_fixtures/`、
`_textures/` 依赖；不要凭卡名重新手写已经调好的动效。模板直接暴露的轻量组件在
`assets/remotion-template/src/shotcraft/index.ts`，包括 `ClipCard`、`PageCam`、
`DigitRoll`、`FlashCut` 和 `VerticalTicker`，无需额外安装 Three.js。

`edit-plan.json` 新增可选 `audio` 数组，支持 `src`、`start_ms`、`end_ms`、`volume`、
`fade_in_ms`、`fade_out_ms` 与 `loop`。`src` 相对于 `public/audio/`；常用音效已预置在
`public/audio/shotcraft/`，完整音效和授权记录见素材库的 `audio/`。发布前必须按
`audio/ATTRIBUTION.md` 复核来源和授权，BGM 不会因为被复制进仓库就自动获得商用许可。

更新上游快照时使用 `scripts/sync-shotcraft-library.py`，它会重建素材目录并在
`manifest.json` 中记录上游 commit，避免素材和说明脱节：

```bash
python3 "$SKILL_DIR/scripts/sync-shotcraft-library.py" \
  --source /path/to/video-shotcraft \
  --destination "$SKILL_DIR/assets/remotion-library"
```

### 7. 自检后交付

渲染完抽 3-4 帧亲眼确认（每种用到的场景各一帧 + 一帧侧方大字），用 Read 查看：字幕不越界、大字块不压脸、演示卡完整、配图清晰、角标位置正确、**横竖方向与源视频在手机里看到的一致（竖屏进必须竖屏出，人是正的）**。ffprobe 核对时长。有问题改 plan 重渲；没问题交付（有 SendUserFile 直接发送）。

### 8. 微调迭代

用户看片后的反馈（改字、换时间、换色、换物料）都只动 `edit-plan.json` 或单张物料，重渲一次约一两分钟。主动告诉用户"哪里不满意直接说"。

## 导演准则

**分段与节奏**：先分内容段再排视觉，同一段内视觉手法保持一致，切段时换手法。开头 3 秒保持全屏口播抓脸；结尾行动号召可以上 concept 卡或贴纸强化。**避免整条片只有字幕在动**——那是最低级的剪法。

**字幕**：一页一个语义单元 ≤16 字，用词级时间戳对齐切点，页间不留空隙，每页 ≥500ms。有文稿以文稿纠错；没文稿只修明显同音错字，拿不准不改。全片挑 4-8 页标 1-2 个关键词变色。

**side_notes**：口播里出现枚举（三种成分/三个功能/几步操作）就上侧方大字块，一块 2-6 字，随口播说到的节奏出现。人物在画面哪侧，大字放另一侧。同屏最多一组。

**chapter_tags**：内容段的标题，一段常驻（5-20 秒），全片 2-4 个。演示段固定用「实操演示」这类动作词。

**concept**：金句/转折/大数字值得定格 2-4 秒。`highlight` 放荧光小块（分类词），`title` 放大字（≤8 字或英文短语）。人物默认隐藏（音频不断），超过 4 秒建议 `"pip": "square"` 保留人物。

**board（框架不变、元素渐进）**：口播在**成段讲解**（一个东西的几条规则、几种模式、优缺点对比）时的首选，一段 board 通常 8-30 秒。要点：

- 元素出现时间**逐词对齐口播**——说到哪行哪行才出现，用 transcript 的 `words` 时间戳定 `start_ms`，这是"跟着讲"的灵魂
- 正文行默认打字机（约 38ms/字），行文案是口播的**压缩改写**（≤12 字），不是逐字字幕
- 讲到新小节就上一个 `title` step 换色块：中性 lime、正面 green/blue、风险/爆点 red，颜色本身就是信息
- 行内语义配色用 `parts`：`[{"text":"危险操作","color":"red"},{"text":" → 前来询问"}]`；行尾可加 emoji 当小图标
- `prop` 放物料工厂的透明贴纸（讲什么放什么），整段固定不动形成锚点，`prop_label` 给它命名
- 同一条片多个 board 段共用同一批物料，观众会记住这个"角色"

**illustration**：口播说到抽象比喻（"像个藏经阁"）、场景（"早晚各一次"）、产品特写时插图 2.5-5 秒。生图要提前想好整条片的统一画风。人物默认左下方卡。

**demo**：用户给了录屏才用。规则同前：≥3 秒、相邻合并、开头结尾保留全屏、录屏比段落短会自动循环。配上「实操演示」chapter_tag。

**画中画形状**：demo/illustration 默认左下圆角方卡（`square`），用户点名要圆形就 `"pip": "circle"`（右下）。

## 模板进化

调参数预览可起 `npx remotion studio`。模板级改动（新动画/新布局）改 `renderer/src/` 后同步回 `SKILL_DIR/assets/remotion-template/src/`，让 skill 持续进化。

## 故障排查

- 转写环节在下载 torch / llvmlite 等大包：装错方案了，本 skill 不用 PyTorch。停掉，改用 `uv run $SKILL_DIR/scripts/transcribe.py`（依赖见「0. 环境与依赖」）
- **竖屏源被剪成了横屏**：plan 的画幅没用 transcribe 输出的 `metadata.width/height`（它已按旋转元数据换算显示方向），而是裸拿了 ffprobe 的存储宽高。重写 plan 画幅重渲即可。若个别文件方向仍不对（旋转标记异常），重编码把方向烘焙进画面再喂：`ffmpeg -i in.mp4 -c:v libx264 -crf 18 -preset fast -c:a copy out.mp4`（Remotion 渲染本身会正确应用旋转元数据，通常无需烘焙）
- `npm install` 卡住/失败：`npm install --registry=https://registry.npmmirror.com`
- 首次渲染卡在下载无头浏览器（Google CDN 国内极慢）：从 npmmirror 手动装。版本号看 `node_modules/@remotion/renderer/dist` 里的 `TESTED_VERSION`（`grep -rho "TESTED_VERSION = '[^']*'" ...`）：

  ```bash
  D=~/.claude/skills/koubo-edit/renderer/node_modules/.remotion/chrome-headless-shell
  V=149.0.7790.0   # 换成实际 TESTED_VERSION
  mkdir -p $D/mac-arm64 && curl -sL -o $D/shell.zip \
    "https://registry.npmmirror.com/-/binary/chrome-for-testing/$V/mac-arm64/chrome-headless-shell-mac-arm64.zip"
  cd $D/mac-arm64 && unzip -qo ../shell.zip && rm ../shell.zip
  echo -n "$V" > ../VERSION; chmod +x chrome-headless-shell-mac-arm64/chrome-headless-shell
  ```

- 渲染报编解码错：先 `ffmpeg -i in.mov -c:v libx264 -crf 18 -c:a aac out.mp4` 转码再喂
- 成片黑屏/时长为 0：核对 `edit-plan.json` 的 `duration_ms`、文件名与 `public/media/` 实际文件
