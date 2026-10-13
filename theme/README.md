# 通用与机构主题

[返回首页](../README.md) · [文档类选项](../docs/class-options.md)

每个主题的配色、图标、字标和相关素材放在各自的目录中。通用版式由
`beamerthemecampus.sty` 实现，`campuscolor.sty` 按名称加载主题配置。

```tex
\documentclass[theme=general]{campusbeamer}
```

`theme` 默认为 `general`。名称对应 `theme/<名称>/profile.tex`，区分大小写，
使用英文字母、数字、连字符或下划线，首字符为字母或数字。
内置主题：`general`（[通用](general/README.md)，默认）、`tsinghua`（[清华](tsinghua/README.md)）和 `pcl`（[鹏城实验室](pcl/README.md)）。
例如 `\documentclass[theme=pcl]{campusbeamer}` 选择鹏城实验室主题。
在仓库根目录运行 `make examples` 可导出清华和 PCL 的 PDF 样例；`make MAIN=example` 导出 general 完整演示；单独构建使用
`make pdf MAIN=example-tsinghua` 或 `make pdf MAIN=example-pcl`。三个主题共用 `example.tex` 与 `examples/sections/` 的完整演示，页数、内容和顺序一致；
机构目录中的 `sample.tex` 只选择主题，`examples/theme-images.tex` 选择背景和各 section 起始页配图。
每个 section 都有独立的图片配置位；清华示例已为五个 section 分别配置校园素材。
未知名称或不完整的配置会给出编译错误。
已有 Beamer 文稿也可使用 `\usetheme[theme=general]{campus}`。

## 添加学校

1. 从仓库根目录复制一个主题目录，例如 `cp -R theme/general theme/myschool`。
2. 修改 `theme/myschool/profile.tex` 中的六种功能色，并替换 `assets/` 中的四个标志文件。
   删除不需要的原学校照片和标志，更新同目录的 `README.md`，记录自己的素材来源、作者和许可。
3. 在文档类中设置 `theme=myschool`。无需修改通用主题、文档类或登记主题名称。
4. 编译并检查封面、目录、普通页、提示框与结束页；公开分发新增主题时，
   将审核后的文件逐一加入 `tools/package_source.py` 的 `FILES`，再运行 `make dist`。
   同时提供 `theme/<名称>/sample.tex` 与根目录编译入口，将样例加入 Make 的 `examples`、
   `theme-previews` 以及 `tools/package_release.py` 的 `DEMO_FORMATS`，更新中英文 README 预览。
   本地使用主题不需要修改打包清单。

目录约定：

```text
theme/myschool/
├── profile.tex
├── README.md
└── assets/
    ├── emblem_on_dark.png
    ├── emblem_on_light.png
    ├── wordmark_on_dark.png
    └── wordmark_on_light.png
```

`profile.tex` 定义 `maincolor`、`tipcolor`、`notecolor`、`alertcolor`、
`examplecolor`、`definitioncolor`。页脚使用主色与白色文字；general 的主色为纯黑 `#000000`。
目录中非当前章节统一使用 65% 前景色混合，保持各主题的可读性。
四个品牌命令分别是 `\schoolemblemondark`、`\schoolemblemonlight`、
`\schoolwordmarkondark`、`\schoolwordmarkonlight`。使用加载器提供的
`\campusthemedir` 引用本主题的素材，复制目录后无需改写目录前缀：

```tex
\definecolor{maincolor}{HTML}{245C80}
\colorlet{notecolor}{maincolor}
\newcommand{\schoolemblemondark}{\campusthemedir/assets/emblem_on_dark.png}
```

上面仅展示部分字段；完整配置可参照 [`general/profile.tex`](general/profile.tex)。
标志应有透明背景。校徽建议采用方形画布，校名标志保持原纵横比；版式会等比缩放。
主题配置在前言区加载一次，选择作用于整份文稿。

个人信息和演讲内容写在文稿中；学校照片可与主题一起保存，但由具体页面显式引用，
切换主题不会自动替换正文照片。布局、字体与几何参数继续使用通用主题。

## 默认主题与旧路径迁移

默认主题已从 `tsinghua` 改为 `general`。原有文稿需要保持清华样式时，
显式设置 `\documentclass[theme=tsinghua]{campusbeamer}` 或 `\usetheme[theme=tsinghua]{campus}`。
Release 仅提供 general 的 PPTX；机构主题可在本地用 `make MAIN=example-tsinghua`
或 `make MAIN=example-pcl` 额外导出 PPTX。

原 `theme/campuscolor.sty` 中的清华配置已移至 `theme/tsinghua/profile.tex`；
前者现在是通用加载器。清华素材从 `assets/` 移至 `theme/tsinghua/assets/`。
已有文稿若直接引用 `assets/sigs_*`、`assets/tsinghua_*`、`assets/emblem_*`
或 `assets/wordmark*`，请更新为新路径。使用学校标志命令的页面会自动使用所选主题的路径。
