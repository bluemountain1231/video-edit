# 内置中文字体库

全部为可免费商用字体。按三级用途分目录：`cover/`（封面艺术字）、`title/`（标题字）、`body/`（正文字）。
方案确认环节（Mode A 的 A3）从这里各选一款组成「封面/标题/正文」三级字体方案，showcase 给用户确认。

## 使用方式

**HTMLPPT（@font-face 直接引本地文件）**：

```css
@font-face { font-family: "得意黑"; src: url("file:///Users/<user>/.claude/skills/ppt-deck-production/fonts/cover/SmileySans-Oblique.ttf"); }
```

生成 HTMLPPT 时把选中的三款字体的 @font-face 写进 `index.html`（用绝对 file:// 路径或复制进项目 `htmlppt/fonts/` 再用相对路径——**交付给别人看时必须用后者**）。

**PPTX（用「字体族名」而非文件名）**：PPTX 里字体按族名引用，对方机器需装有该字体。交付 PPTX 时：

1. 把用到的字体文件随包一起交付，并提示用户双击安装（或 `cp *.ttf ~/Library/Fonts/`）；
2. 本机预览前先安装：`cp <选中的字体> ~/Library/Fonts/`。

## 字体清单

| 文件 | 族名(zh / PPTX 用这个) | 族名(en) | 级别 | 气质 & 适用 |
|---|---|---|---|---|
| cover/SmileySans-Oblique.ttf | 得意黑 | Smiley Sans Oblique | 封面 | 窄斜体、运动潮流感；科技/年轻/发布会封面 |
| cover/ZCOOLKuHei.ttf | 站酷酷黑 | ZCOOL_KuHei | 封面 | 厚重硬朗大黑；电商/促销/力量感封面 |
| cover/SlideXiaXingKai.ttf | 演示夏行楷 | Slidexiaxing | 封面 | 毛笔行楷；国风/文化/品牌故事封面 |
| cover/SourceHanSerifSC-Heavy.otf | 思源宋体 Heavy | Source Han Serif SC Heavy | 封面 | 特粗衬线；高级编辑部/杂志/奢侈感封面 |
| cover/LianMengQiYi-RuiHei.ttf | 联盟起艺卢帅正锐黑体 | lianmengqiyilushuaizhengruiheiti | 封面 | 锐利切角黑；游戏/竞技/热血封面 |
| title/YouSheBiaoTiHei.ttf | 优设标题黑 | YouSheBiaoTiHei | 标题 | 微斜紧凑标题黑，万金油；商务/互联网风标题 |
| title/PangMenZhengDao-BiaoTi.ttf | 庞门正道标题体 | PangMenZhengDao | 标题 | 经典电商标题体，重心高、张力强 |
| title/SheTuModengXiaoFang.ttf | 摄图摩登小方体 | shetumodengxiaofangti | 标题 | 圆润方块体；可爱/消费品/轻松场合标题 |
| title/Alibaba-PuHuiTi-Bold.ttf | 阿里巴巴普惠体 (Bold) | Alibaba PuHuiTi | 标题 | 中性现代黑 Bold；稳重商务标题 |
| body/Alibaba-PuHuiTi-Regular.ttf | 阿里巴巴普惠体 | Alibaba PuHuiTi | 正文 | 中性现代黑；默认正文首选 |
| body/LXGWWenKai-Regular.ttf | 霞鹜文楷 | LXGW WenKai | 正文 | 温润楷体；文艺/人文/教育类正文 |

## 推荐搭配（按 deck 气质起手，可再调）

- **商务报告**：优设标题黑（封面兼标题加大）+ 阿里巴巴普惠体
- **潮流发布**：得意黑 封面 + 优设标题黑 标题 + 普惠体 正文
- **高级编辑部**（kals-mint-editorial 类）：思源宋体 Heavy 封面 + 普惠体 Bold 标题 + 普惠体 正文
- **国风/文化**：演示夏行楷 封面 + 庞门正道标题体 标题 + 霞鹜文楷 正文
- **电商/促销**（mihong 类）：站酷酷黑 封面 + 庞门正道标题体 标题 + 普惠体 正文
- **可爱/消费品**：摄图摩登小方体 封面兼标题 + 普惠体 正文

## 许可

得意黑/霞鹜文楷/思源宋体 = SIL OFL；站酷系列、庞门正道、优设标题黑、联盟起艺、摄图摩登小方体、演示系列、阿里巴巴普惠体 = 官方声明免费商用。均可用于商业 PPT 交付。新增字体时：确认可免费商用 → 放入对应级别目录 → 在上表登记族名与气质。
