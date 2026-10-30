# General 通用主题

[主题使用与扩展](../README.md) · [返回首页](../../README.md)

`general` 是默认主题，与学校或科研机构无关：

```tex
\documentclass{campusbeamer}
% 显式选择：\documentclass[theme=general]{campusbeamer}
```

博士帽替代校徽；封面右下角使用 Campus Beamer 项目字标的文字部分，
保留原有字形、字距和升降关系，去除背景面板。深色底使用白色图形，浅色底使用纯黑色。
主色为 `#000000`，双行正文页眉、章节导航和页脚沿用公共版式。
当前章节目录中的其他条目使用 65% 前景色混合，保持黑底上的可读性。

运行 `make MAIN=examples/example` 构建完整功能演示与讲者备注。全部中文主题示例共用同一份正文与逐页备注，
页面数量和顺序一致，仅配色、标志与配图随主题变化。
Release 为中文 general 提供 PDF/PPTX，为英文 general 与其他所有主题提供 PDF。

根目录 README 会展示 general 主题完整示例的代表性页面；原创素材与字体分别适用下述许可。

## 素材与重建

- `emblem.tex`：本项目用 TikZ 绘制的几何博士帽，无学校标志或第三方图标依赖。
- `wordmark.tex`：沿用项目字标的 Latin Modern 字体排版；透明背景，不绘制底色。
- `backdrop.tex`：本项目用 TikZ 绘制的抽象几何背景，用于图片适配与背景演示。
- `assets/`：对应的矢量 PDF，博士帽和字标各有深浅底版本。

从仓库根目录执行 `make general-assets` 重建。需要 XeLaTeX、TikZ、
`standalone`、Latin Modern 和 PyMuPDF；日常编译直接使用已提供的 PDF。

原创图形与排版源码采用项目的 GPL-3.0-or-later。字标的字体来源及
[GUST Font License](../../assets/Latin-Modern.LICENSE.txt) 见
[项目字标说明](../../assets/README.md#campus-beamer-项目字标)，字体授权保持不变。
这些素材不表示任何学校或科研机构的身份或背书。
