# EVA 主题

[主题使用与扩展](../README.md) · [返回首页](../../README.md)

`eva` 使用二号机联想的红色、暖色强调与深色正文背景。左上角使用新剧场版的
《Q》的碎片化 NERV 标志，封面保留 Campus Beamer 项目字标。章节起始页保留左侧章节信息，
右侧使用 TV 版标题卡启发的黑底白字日文排版。

```tex
\documentclass[theme=eva]{campusbeamer}
\campusevasectiontitle{1}{方法と\\実験}
\begin{document}
\section{方法与实验}
\sectioncoverpage{本节介绍方法设计与实验结果。}
% 后续章节……
\end{document}
```

用 `\campusevasectiontitle{章节编号}{日文标题}` 为右侧卡片提供日文，可用 `\\` 安排换行。
左侧仍使用原始 `\section` 标题；中文和英文文稿采用同样的日文卡片。未提供日文标题时，
右侧只显示日文章节编号，不会自动翻译正文。

前面的章节轮换四种构图：竖排编号与底部标题、高位标题与低位编号、居中大字、错位横排。
最后一节使用右下方的小型「終。」收尾，保留较大的黑色留白；这是汇报的结束卡设计，
并非对动画某一帧的精确复刻。可在导言区用 `\renewcommand{\campusevaendtext}{終}` 更改文字。
最后一节由 Beamer 导航信息判断，增删章节后使用 latexmk 完成必要的多轮编译。

省略背景参数或使用 `[profile]` 启用标题卡；显式 `[primary]`、`[white]` 或图片路径沿用通用章节页背景。
16:9 与 4:3 都使用实时文字排版，不依赖固定裁剪的标题图片。较长的日文标题应自行安排换行，
并检查编译后的卡片。

## 字体

默认使用 **Harano Aji Mincho Heavy**（原ノ味明朝 Heavy），是粗明朝体的近似选择，
与 TV 原版 **Matisse EB / EVA-マティス-クラシック** 不同。原版字体信息见
[字体厂商说明](https://fontworks.co.jp/products/evamatisse/)及
[标题卡排版案例](https://fontworks.co.jp/column/394/)。本项目不附带商业 Matisse 字体。

完整 TeX Live 和 Overleaf 的完整 TeX Live 环境包含所需字体。精简本地安装需要
[`haranoaji-extra`](https://ctan.org/pkg/haranoaji-extra)：

```bash
# TeX Live 自带包管理器
tlmgr install haranoaji-extra
# Debian / Ubuntu 的系统 TeX Live（二选一）
sudo apt-get install texlive-lang-japanese
```

若已有获授权使用的原版字体，可在导言区设置实际文件路径：

```tex
\renewcommand{\campusevajapanesefont}{materials/fonts/EVA-Matisse-Classic.ttf}
```

文件名以你持有的字体为准；字体文件不随模板或主题素材包分发。

```bash
make pdf MAIN=examples/example-eva
make pdf MAIN=examples/example-eva-43
make overleaf THEME=eva
```

从轻量源码包使用前，可运行 `make theme-assets THEME=eva` 安装本主题独立维护的最新版素材。
`make overleaf` 会在缺失时自动补齐素材。

## 来源与许可

NERV 图形依据用户确认的《Q》版本参考图，用 `emblem.tex` 中的 TikZ 路径手工重建，
版本说明见 [EvaGeeks 的 Nerv Logo 页面](https://wiki.evageeks.org/Nerv_Logo)。
主体采用多边形，左下角四枚细线符号按参考图近似重绘，并非官方矢量母版。
导出的两份 emblem PDF 均为透明背景的矢量图，没有嵌入 JPEG 或 PNG；
图形颜色随深浅背景变体调整，放大时轮廓保持清晰。
图形及相关标识的权利属于相应权利人，
不适用本仓库代码的 GPL 许可；本仓库未获官方授权或单独的再分发许可，不表示官方关联。
如权利人要求移除，请通过仓库 Issue 联系维护者。

`wordmark.tex`、`backdrop.tex`、`section-art.tex` 为本项目制作，采用 GPL-3.0-or-later。
`emblem.tex` 的重建图形及其两份 emblem PDF 保留上述第三方权利说明。
Harano Aji 字体采用 SIL Open Font License；项目字标的字体说明见
[assets/README.md](../../assets/README.md)。主题不包含动画截图或角色原画。
`make eva-assets` 可从本地素材重建 PDF；章节卡在编译文稿时绘制。
