# st-workflow — 圣韬同学的好用 Agent Skill 工作流合集

由 **圣韬同学**（[@loushengtao](https://github.com/loushengtao)）维护的 **Claude Code / Agent Skill 工作流分享仓库**。

## 这是什么

Skill 是给 AI Agent（如 Claude Code）用的"工作流说明书"：一个文件夹里装着一份 `SKILL.md`（告诉 Agent 该怎么一步步干活）加上配套的脚本和模板。装好之后，你对 Agent 说一句话（比如"帮我剪一下这条口播"），它就会按照 skill 里沉淀好的完整流程自动执行——而不是每次都从零发挥。

这个仓库收录我在实际业务中打磨出来、验证过的 skill，每一个都做到**开箱即用**：依赖交代清楚、流程写成步骤、坑都提前标好。

## 有什么用

- **拿来即用**：复制一个文件夹就获得一条完整的自动化工作流，不用自己摸索提示词和流程编排
- **可复现**：同一个 skill 在任何机器、任何项目目录下行为一致，依赖自动解决
- **可进化**：skill 是纯文本 + 脚本，用得不顺手直接改，改完全局生效

## 支持的产品

Skill 是通用格式，**WorkBuddy、Codex、Claude Code 都支持**，同一份 skill 三边通用，装法一致。

## 安装方式（二选一）

**方式一：拖进 skill 文件夹**

克隆或下载本仓库，把想用的 skill 文件夹整个拖（复制）进对应产品的 skill 目录：

| 产品 | skill 目录 |
|---|---|
| Claude Code | `~/.claude/skills/` |
| Codex | `~/.codex/skills/` |
| WorkBuddy | 应用内技能目录（技能面板可直接导入） |

```bash
git clone https://github.com/loushengtao/st-workflow.git
cp -R st-workflow/skills/koubo-edit ~/.claude/skills/   # 以 Claude Code 为例
```

**方式二：自然语言安装（最省事）**

直接把仓库链接发给你的 Agent，说一句：

> 帮我安装 https://github.com/loushengtao/st-workflow 里的 koubo-edit skill

它会自己 clone 仓库并把 skill 放进正确的目录。

**装好之后**：直接说需求（如"剪一下这条口播"），或用斜杠命令 `/koubo-edit` 显式调用。

> 前置要求各 skill 不同，均写在各自 `SKILL.md` 的环境说明里，Agent 会照着自检，无需手动配置。

## Skill 目录

| Skill | 一句话说明 | 主要依赖 |
|---|---|---|
| [koubo-edit](skills/koubo-edit/) | 中文口播视频自动剪辑：本机转写 → 语义规划与 Talkcraft 候选 → AI 导演做视觉设计（胶囊字幕、侧方大字、白板讲解卡、AI 配图物料）→ Remotion 渲染成片，附带 Shotcraft 动效、镜头卡和音效素材库 | uv、Node.js ≥ 18（macOS / Windows / Linux 全平台） |
| [ppt-deck-production](skills/ppt-deck-production/) | 双模式 PPT 生产：模式 A 按需求从内置模板库选型，走内容规划 → 配图生成 → 浏览器校验的 HTMLPPT 出成品（可迁移 PPTX）；模式 B 把参考 PPTX 沉淀为可复用模板档案（页面图集 + 设计 token + 组件族）。自带 11 款免费商用中文字体和多套模板 | 浏览器渲染环境（skill 内置字体与模板库，开箱即用） |
| [cinematic-web-promo](skills/cinematic-web-promo/) | 把真实网站或前端项目制作成电影感 Remotion 宣传片：内置并自动路由 152 个 Shotcraft Recipe、209 个动态样片、准确 Demo TSX、公共组件与 Ink Press；支持惯性下滑、固定指针滚轮、点击急推、节拍剪辑、机械音效和最终 QA，默认离线可复现 | Node.js ≥ 20、pnpm、Python ≥ 3.10、ffmpeg/ffprobe、浏览器采集能力 |

*持续更新中，后续会陆续放入更多经过实战验证的 skill。*

## 仓库结构

```
st-workflow/
├── README.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md        # 工作流主文档（Agent 读这个干活）
        ├── scripts/        # 配套脚本（PEP 723 内联依赖，uv run 直接跑）
        └── assets/         # 模板等静态资源
```

## 反馈与交流

用得不顺、发现 bug、想要新的工作流，欢迎提 Issue。
