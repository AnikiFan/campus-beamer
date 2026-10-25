# undefined：奶蛙名画主题

[主题使用与扩展](../README.md) · [返回首页](../../README.md)

从 Release 源码包使用此主题前，在项目根目录运行 `make theme-assets THEME=undefined`，
下载该主题独立维护的最新版素材。Git 克隆通常已包含素材。

`undefined` 是奶蛙恶搞主题：经典黄色的封面分区、章节页和页脚，配奶油色正文与深色文字。
左上角是一只圆形眼睛：黄色外圈、绿色虹膜，黑色瞳孔偏向右下方，注视页面中央，四周保留绿色间隙。
封面右下角使用 Campus Beamer 字标，五个章节各有一幅不同的奶蛙名画配图。

```tex
\documentclass[theme=undefined]{campusbeamer}
```

```bash
make pdf MAIN=examples/example-undefined
make draft MAIN=examples/example-undefined
# 本地导出 PowerPoint：
make MAIN=examples/example-undefined
```

完整示例沿用 general 的内容和页序。发行包包含本主题的 PDF；素材通过独立的最新版素材包提供。
自己的汇报可选择章节配图，建议使用居中裁切，让角色的脸保留在画面内：

```tex
\sectioncoverpage[theme/undefined/assets/pearl-earring.png]{本章导语}[align=center]
```

| 示例章节 | 配图 | 构图参考 |
|---|---|---|
| 基础页面与图像 | `pearl-earring.png` | 维米尔《戴珍珠耳环的少女》 |
| 论文讲解与引用 | `mona-lisa.png` | 达·芬奇《蒙娜丽莎》 |
| 提示框 | `scream.png` | 蒙克《呐喊》 |
| 导航与渐进显示 | `napoleon.png` | 大卫《拿破仑越过阿尔卑斯山》 |
| 媒体与收尾 | `starry-night.png` | 梵高《星月夜》 |

这些图片位于本主题的 `assets/` 中，可按内容自由选择。主题配置本身不自动插入章节页。

## 素材与来源

- `profile.tex`：本项目编写的主题配色。主色 `#FFD52A`，正文底色 `#FFFCF0`，
  主色背景上的文字为 `#34311C`；标题、目录和页脚使用深色前景以保持黄色背景上的可读性。
- `emblem.tex`：单眼矢量图，使用圆形外圈、虹膜和偏向右下方的圆形瞳孔。深浅背景保留相同的角色颜色。
- `wordmark.tex`：从 general 适配的 Campus Beamer 项目字标，使用 Latin Modern Roman。两个字标文件都使用深色文字，
  适配黄色封面与奶油色正文；文件名沿用主题素材接口。字体许可见
  [GUST Font License](../../assets/Latin-Modern.LICENSE.txt)。
- 五张绘画于 2026-10-24 使用 OpenAI 内置图像生成工具制作；均为奶蛙恶搞画。
  角色外形参考 [naiwa-universe 的 thinkerSuit.jpg](https://github.com/Marshall-Jimmy/naiwa-universe/blob/master/public/images/thinkerSuit.jpg)；
  下载的参考图片仅用于本地制作，未纳入主题或源码包。生成提示词见 [GENERATION.md](GENERATION.md)。
- 构图参考原作的馆藏说明：[《戴珍珠耳环的少女》](https://www.mauritshuis.nl/en/our-collection/artworks/670-girl-with-a-pearl-earring)、
  [《蒙娜丽莎》](https://www.louvre.fr/en/explore/the-palace/from-the-mona-lisa-to-the-wedding-feast-at-cana)、
  [《呐喊》](https://www.munch.no/en/The-Scream)、
  [《拿破仑越过阿尔卑斯山》](https://musees-nationaux-malmaison.fr/chateau-malmaison/collection/objet/le-premier-consul-franchissant-les-alpes-au-col-du-grand-saint-bernard)、
  [《星月夜》](https://www.moma.org/collection/works/79802)。馆藏图片未下载或纳入素材包。

主题适配代码遵循项目 GPL-3.0-or-later。奶蛙为网络二创形象；本项目不宣称拥有原角色权利，
也不将图像生成或参考网站的代码许可视为角色再分发授权。角色衍生图案与生成配图的第三方权利
不由仓库代码许可证覆盖。本主题为非官方恶搞作品。

`make undefined-assets` 可从 TeX 重建单眼与字标 PDF；绘画 PNG 直接使用随附文件。
