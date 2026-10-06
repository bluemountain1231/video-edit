# red-halo-minimal — 红晕极简编辑部

Source: 小夕素材(2).pptx · 31 slides · 16:9. White minimal editorial deck ("Morimoto/Kasama"):
vast white canvas, ONE signature soft red radial halo blob per page, black grotesque titles,
desaturated B&W interior/lifestyle photography, red-and-gray charts. 高级感来自留白 + 单一视觉锚点。

## Design tokens

| Token | Value | Use |
|---|---|---|
| `--paper` | `#FFFFFF` | canvas, always white |
| `--ink` | `#111111` | titles, body, chart gray-black |
| `--halo-core` | `#E73222` | halo blob center, chart accent, key numbers |
| `--halo-mid` | `#F3ADAB` | halo blob mid ring |
| `--halo-edge` | `#F7DCDC` | halo blob outer fade (radial gradient to white) |
| `--gray-chart` | `#9E9E9E` | secondary chart series |
| photo treatment | desaturated / B&W interior & lifestyle shots | all image frames |

Type: neutral grotesque (Helvetica 类), titles sentence-case ~28-36pt, tiny logo chrome + thin rule.
Signature mark: soft-edged red radial halo (one per page, varied size/position; CSS radial-gradient 即可实现).

## 推荐三级字体方案（fonts/ 库）

- 封面: 优设标题黑 · 标题: 阿里巴巴普惠体 Bold · 正文: 阿里巴巴普惠体
- 备选文艺向: 封面 思源宋体 Heavy

## Element families

- `cover/title-system` — big black wordmark top-left + large halo blob right + tiny sub-line
- `section/divider` — 1-2 line statement (black, left or centered) + halo blob, nothing else
- `body/image-plus-text` — B&W photo frame one side, title + 2-col micro body other side
- `body/two-column` — title left, dual text columns right, tiny dot row divider
- `media/image-grid` — 2x2 / 4-up B&W photo grid with thin gaps, small side captions
- `card/price-panel` — white panel floated over full-bleed photo, big number ($470,00)
- `chart/donut` — red arc on light-gray track, % centered (73%)
- `chart/bars` `chart/lines` — gray + red series only, hairline axes
- `card/device-mockup` — phone/laptop raster + numbered feature list
- `chrome/page` — tiny logo + thin underline top-left or top-center
- `decorative/halo-blob` — THE signature; never more than one focal halo per slide

## Triggers

"红晕" / "红色光晕" / "小夕素材(2)" / red halo minimal / Morimoto 白底红点风 / 极简留白 + 一点红。
