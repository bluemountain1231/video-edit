# Shotcraft Remotion 素材库

这是 `koubo-edit` 随附的离线剪辑素材库，来源于
[video-shotcraft](https://github.com/Vincentwei1021/video-shotcraft)。同步脚本会把
可复用的 Remotion 组件、镜头 Demo、镜头卡、音效和图库索引冻结在 skill 内，
安装后不依赖网络即可查找素材。

当前快照见 [`manifest.json`](manifest.json)：

- 8 个通用组件（PageCam、ClipCard、DigitRoll、FlashCut、VerticalTicker 等）
- 221 个 Remotion Demo 实现，覆盖开场、字卡、界面、数据、交互、转场、节奏、光效和收尾
- 158 张镜头卡和 `gallery/library.json` 索引
- 149 个按场景分类的 SFX、5 首 BGM

## 在口播模板中使用

模板已经直接暴露不依赖 Three.js 的组件：

```tsx
import { ClipCard, FlashCut, PageCam } from "./shotcraft";
```

完整 Demo 与镜头卡只作为可复制的参考实现保存于本目录；它们依赖的 fixture 和
纹理也一并保留。需要 Three.js 的 `FlatPanel` 与 `helpers/camera` 请按各自 Demo
说明安装依赖后再复制，不会自动进入基础口播渲染器。

## 音效

`edit-plan.json` 可以用 `audio` 数组精确放置音效：

```json
{
  "audio": [
    {
      "src": "shotcraft/impact-cine-big.mp3",
      "start_ms": 12800,
      "volume": 0.75,
      "fade_in_ms": 20,
      "fade_out_ms": 120
    }
  ]
}
```

模板中预置了一小组常用 SFX；完整 149 个文件在 `audio/sfx/`，复制到项目的
`public/audio/` 后即可按相对路径引用。来源、授权和仍需复核的文件见
[`audio/ATTRIBUTION.md`](audio/ATTRIBUTION.md)。BGM 同样随库提供，但发布前请
按清单复核授权范围。

## 更新快照

在包含 `video-shotcraft` checkout 的机器上运行：

```bash
python3 skills/koubo-edit/scripts/sync-shotcraft-library.py \
  --source /path/to/video-shotcraft \
  --destination skills/koubo-edit/assets/remotion-library
```

脚本会重建库目录并更新 `manifest.json`，同时记录上游 commit，便于回溯素材版本。

## 许可

Remotion 组件、Demo 和镜头卡遵循上游 Apache-2.0 许可，副本见
[`THIRD_PARTY_LICENSE`](THIRD_PARTY_LICENSE)。音频有单独的来源与授权记录，不能仅
因为代码仓库采用 Apache-2.0 就跳过音频清单检查。
