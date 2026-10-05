# 文档类与前言区

[返回首页](../README.md) · [使用手册](usage.md) · [安装说明](installation.md)

新汇报使用 `theme/campusbeamer.cls`。它继承 Beamer，自动加载 `campus` 主题、
中文支持、默认数学字体和文献配置；不必重复写 `\usetheme`、
`\usepackage{xeCJK}`、`\usefonttheme` 或 `\usepackage{biblatex}`。
使用 XeLaTeX 和本项目的 Make 工作流，学校信息由 `theme/campuscolor.sty` 管理。
封面默认就是主色斜边版式，无需额外设置。若显式填写，只使用 `\titlebackground{primary}`；
封面颜色通过学校配置中的 `maincolor` 修改。

封面元信息使用 `\title`、`\subtitle`、`\author`、`\course`、`\advisor`、`\date` 和
`\IDnumber`。类会自动将这些字段嵌入 PDF，供 PPTX 导出写入文档属性；无需另外设置导出元信息。
`\section` 的 PDF 书签自动成为 PowerPoint 原生分节，见[转换说明](usage.md#转换为-powerpoint保留跳转链接)。

```tex
\documentclass[language=chinese]{campusbeamer}
\campusbibresource{bibliography/refs.bib}
\title{我的研究汇报}
\author{汇报人}
\date{\today}

\begin{document}
\maketitle
\section{研究问题}
\sectioncoverpage[primary]{本节说明要解决的问题。}
\subsection{问题定义}
\begin{frame}{本页的主要结论}
  用简短内容说明论点，并给出必要证据。
\end{frame}
\backmatter
\end{document}
```

所有选项都有默认值，直接写 `\documentclass{campusbeamer}` 即可使用中文版本。
文献文件属于具体汇报，类不会自动指定 `bibliography/refs.bib`；需要引用时用
`\campusbibresource{bibliography/自己的文献文件.bib}`，有多份数据库可调用多次。
原生 `\addbibresource` 也保持可用。
文献支持始终启用，自动配置 `backend=biber,style=ieee,giveninits=true,sorting=none`，
无需设置启用开关。

## 文档类选项

选项由 agent 写在生成入口的 `\documentclass[...]` 中，不必提前填写。功能示例 `example.tex` 列出全部模板选项、
默认值与可选值注释，方便直接修改；实际汇报也可以省略使用默认值的项：

- `language=chinese`（默认）或 `english`：选择主题自动生成的目录、章节标签、
  图表标签、提示框标题、日期和致谢文字。中文版本自动加载 xeCJK；英文版本默认不加载。
  不会翻译用户撰写的正文。
- `cjk=auto`（默认）、`true` 或 `false`：控制中文排版支持。默认随语言选择；
  使用英文主题文字、中文正文时设置 `language=english,cjk=true`。
  `cjk=false` 是供自行安排中文支持的高级选项；它不会删除中文文本。
- `bibstyle=ieee`（默认）：选择 biblatex 样式，例如 `authoryear`。
  改变此项会改变引用或文末参考文献的格式；需要安装相应样式。
- `bibsorting=none`（默认）：按首次引用顺序排列。可用其他 biblatex 排序方案，
  例如 `nyt`；排序与参考文献样式各自生效。
- `mathfont=serif`（默认）或 `sans`：使用衬线数学字体，或使用 Beamer 的
  默认无衬线数学字体。正文使用主题的 Caladea／Carlito 配置。
- `navigation=true`（默认）或 `false`：显示或隐藏页脚的章节／小节导航。
- `cornerwidth=4.8cm`（默认）：角落引用的默认宽度。单页仍可用
  `\setcornercitewidth{6cm}` 局部调整。
- `layoutguides=false`（默认）或 `true`：在封面、章节页与致谢页显示红线诊断。
  只能通过此文档类选项开关，最终导出前关闭。
  普通页面的“版式对齐检查”示例固定显示参考线，不受此选项控制。

Beamer 自身的选项会传递给底层文档类，例如 `handout` 可将 overlays 合并为讲义页。
默认 16:9 几何由主题固定。通用字体与版式在主题中，学校配色和素材路径在配置文件中。

## 常见用法

英文汇报，有引用：

```tex
\documentclass[language=english]{campusbeamer}
\campusbibresource{bibliography/refs.bib}
```

英文主题文字、中文正文：

```tex
\documentclass[language=english,cjk=true]{campusbeamer}
```

完全不使用文献的汇报：

```tex
\documentclass{campusbeamer}
```

无需指定文献文件或添加 `\referencespage`。文献支持由类自动加载。
若需要正文引用但不需要文末列表，保留文献资源和引用，仅省略 `\referencespage`。

定制默认引用宽度、关闭导航，以及生成讲义：

```tex
\documentclass[language=chinese,cornerwidth=6cm,navigation=false,handout]{campusbeamer}
\campusbibresource{bibliography/refs.bib}
```

`\campusbibresource[...]{...}` 接受原生 `\addbibresource` 的可选参数。
需要其他可运行时调整的 biblatex 设置时，仍可使用 `\ExecuteBibliographyOptions{...}`；
不要再次加载已由类启用的包，以免出现选项冲突。
自定义中文字体时，在启用中文支持后直接使用 `\setCJKmainfont`／`\setCJKsansfont`。

## 改用本文档类

已有的 Beamer 文稿可以改用 `campusbeamer`。把前言里单独加载的主题、xeCJK、数学字体和 biblatex 换成：

```tex
\documentclass[language=chinese]{campusbeamer}
\campusbibresource{bibliography/refs.bib}
```

标题、正文、引用和插图可以保留。文献支持由文档类启用。封面默认是主色斜边版式，一般不必写 `\titlebackground`。
语言在文档类里设置：该选项会同时安排中文支持，`\campussetlayout{template language=...}` 只切换主题标签，不会加载或卸载 xeCJK。
导航和引用宽度写在文档类选项里；需要时也可以用 `\campussetlayout` 做局部覆盖。
版式红线使用 `layoutguides=true/false`。

也可以不换文档类，写 `\documentclass{beamer}` 和 `\usetheme{campus}`。
文档类、主题和学校配置都在 `theme/`。复制模板时保留整个 `theme/` 和根目录的 `.latexmkrc`；
`make dist` 的源码包已经包含它们。通过 `make` 或 `latexmk` 编译时会自动配置搜索路径，文档类名称不用加目录前缀。
