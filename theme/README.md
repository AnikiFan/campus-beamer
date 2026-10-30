# 通用与机构主题

[返回首页](../README.md) · [文档类选项](../docs/class-options.md)

每个主题的配色、图标、字标和相关素材放在各自的目录中。通用版式由
`beamerthemecampus.sty` 实现，`campuscolor.sty` 按名称加载主题配置。

```tex
\documentclass[theme=general]{campusbeamer}
```

`theme` 默认为 `general`。名称对应 `theme/<名称>/profile.tex`，区分大小写，
使用英文字母、数字、连字符或下划线，首字符为字母或数字。
内置主题：`general`（[通用](general/README.md)，默认）、`tsinghua`（[清华](tsinghua/README.md)）、`pcl`（[鹏城实验室](pcl/README.md)）、`tokyo-night`（[深色](tokyo-night/README.md)）、`undefined`（[奶蛙名画](undefined/README.md)）和 `eva`（[EVA 标题卡](eva/README.md)）。
例如 `\documentclass[theme=pcl]{campusbeamer}` 选择鹏城实验室主题。
在仓库根目录运行 `make examples` 可导出清华、PCL、Tokyo Night、undefined 和 EVA 的 PDF 样例；`make MAIN=examples/example` 导出 general 完整演示；单独构建使用
`make pdf MAIN=examples/example-tsinghua`、`make pdf MAIN=examples/example-pcl`、`make pdf MAIN=examples/example-tokyo-night`、`make pdf MAIN=examples/example-undefined` 或 `make pdf MAIN=examples/example-eva`。六个中文主题示例共用 `examples/example.tex` 与 `examples/sections/` 的完整演示，页数、内容和顺序一致；
主题目录中的 `sample.tex` 只选择主题，`examples/theme-images.tex` 选择背景和各 section 起始页配图。
每个 section 都有独立的图片配置位；清华示例已为五个 section 分别配置校园素材。
未知名称或不完整的配置会给出编译错误。
已有 Beamer 文稿也可使用 `\usetheme[theme=general]{campus}`。

<a id="添加学校"></a>

## 添加主题

学校主题和独立视觉主题都可从同一入口开始：

```bash
make theme-new THEME=myschool
# 编辑 theme/myschool/ 中的配色、素材与说明后：
make theme-preview THEME=myschool
```

创建命令提供可编译的 general 起点，不覆盖已有目录；预览命令构建完整公开示例的
16:9 和 4:3 页面。纯配色主题可以保留通用标志，也可替换为自己的素材。
在文档类中设置 `theme=myschool` 即可使用，无需登记名称。
向项目贡献主题的步骤见[贡献指南](../CONTRIBUTING.md)，公共图库与发行接入由维护者按
[接入清单](../docs/maintaining.md#接入新主题)完成。

目录约定：

```text
theme/myschool/
├── profile.tex
├── README.md
├── demo-images.tex        # 可选，公开示例配图
└── assets/
    ├── emblem_on_dark.pdf
    ├── emblem_on_light.pdf
    ├── wordmark_on_dark.pdf
    ├── wordmark_on_light.pdf
    └── backdrop.pdf
```

`profile.tex` 定义 `maincolor`、`tipcolor`、`notecolor`、`alertcolor`、
`examplecolor`、`definitioncolor`。页脚使用主色与 `campusonprimary` 文字（默认白色）；general 的主色为纯黑 `#000000`。
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

公开功能示例会在默认配图配置后读取 `theme/<名称>/demo-images.tex`（存在时）。
可在其中用 `\renewcommand` 设置 `\campusexampleimage` 与
`\campusexamplesectiononeimage` 至 `\campusexamplesectionfiveimage`；前者必须是图片路径，
后五项也可用 `primary`、`white` 或 `profile`。工具生成的文件已包含起始配置。
此入口仅用于公开示例与主题预览，不会改写用户汇报。

## 主题的可选前景与背景颜色

现有六种功能色和四个素材路径仍是必填字段。以下颜色可以在 `profile.tex` 中覆盖；
省略时保持原有浅色主题效果，不需要在文稿中修改通用主题。

| 可选颜色 | 默认值 | 用途 |
|---|---|---|
| `campusonprimary` | `white` | 主色背景上的文字：章节页、目录、致谢页和底部页脚；明亮主色可设为深色 |
| `campusbackground` | `white` | 正文、封面左侧与提示框的基底 |
| `campustext` / `campusheading` | `darkgray` | 正文 / 页眉文字 |
| `campusaccent` | `maincolor` | 标题、结构标记、图注标签和正文导航 |
| `campusmetadatatext` | `black` | 封面作者、导师、日期 |
| `campuscitation` | `black!50` | 角落引用 |
| `campusnavigationmuted` | `black!55` | 正文中非当前导航条目 |
| `campusnavigationsection` | `maincolor!18!white` | 章节导航底色 |
| `campusnavigationsubsection` | `maincolor!7!white` | 小节导航底色 |
| `campuscallouttitlebase` / `campuscallouttext` | `black` | 提示框标题混色基准 / 正文 |

`maincolor` 继续控制封面右侧、默认章节页和页脚底色；深色主题应配合明亮的 `campusaccent`。
黄色等明亮主色应配合深色 `campusonprimary`，如 [`undefined/profile.tex`](undefined/profile.tex)。
封面字标是独立素材，应同时提供与主色背景对比清楚的版本。
`campuscodebackground`、`campuscodebar`、`campuscodetext`、`campuscodemuted`、`campuscodekeyword`、
`campuscodestring` 和 `campuscodeaccent` 也可以在 profile 中定义；省略时保留原有代码窗口配色。
参考 [`tokyo-night/profile.tex`](tokyo-night/profile.tex)。自绘图表可使用 `campusaccent` 与
`campusbackground` 配色，使文字和节点同时适应深浅背景。

## 默认主题与旧路径迁移

默认主题已从 `tsinghua` 改为 `general`。原有文稿需要保持清华样式时，
显式设置 `\documentclass[theme=tsinghua]{campusbeamer}` 或 `\usetheme[theme=tsinghua]{campus}`。
Release 仅提供 general 的 PPTX；机构主题可在本地用 `make MAIN=examples/example-tsinghua`
或 `make MAIN=examples/example-pcl` 额外导出 PPTX。

原 `theme/campuscolor.sty` 中的清华配置已移至 `theme/tsinghua/profile.tex`；
前者现在是通用加载器。清华素材从 `assets/` 移至 `theme/tsinghua/assets/`。
已有文稿若直接引用 `assets/sigs_*`、`assets/tsinghua_*`、`assets/emblem_*`
或 `assets/wordmark*`，请更新为新路径。使用学校标志命令的页面会自动使用所选主题的路径。

## 动态章节配图

主题可在 `profile.tex` 中定义 `\campussectionart` 绘制章节背景，并从同目录加载其实现。
`\sectioncoverpage{导读}` 或 `\sectioncoverpage[profile]{导读}` 使用该绘图；未定义时保持原有主色背景。
显式的 `[primary]`、`[white]` 或图片路径仍优先于主题绘图。
EVA 使用此接口生成右侧标题卡，左侧章节信息与通用几何保持不变；见 [EVA 说明](eva/README.md)。
