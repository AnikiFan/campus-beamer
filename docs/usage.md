# Campus Beamer 使用手册

这是一个面向组会汇报的 16:9 Beamer 模板，使用 XeLaTeX 排版中文，并使用
`biblatex`/`biber` 管理幻灯片引用。

[返回首页](../README.md) · [English overview](../README.en.md) · [贡献指南](../CONTRIBUTING.md)

所有命令均从项目根目录执行。主要入口是给 agent 的自然语言提示词和本地素材；
`prompt.md` 提供提示词示例，`example.tex` 展示功能，`main.tex` 由 agent 为你的汇报生成。

## 快速开始

用户只需提供两样东西：**想表达的内容**和**已收集的素材**。
在能读写本地文件、运行命令的 agent 中打开本目录，参考 [`prompt.md`](../prompt.md)，
用自然语言说明思路、受众和讲解重点。提示词不是必须逐项填写的表单；已有的大纲、笔记或一段想法都可以。

将素材放到本地 `materials/`，例如：

```text
materials/
├── paper/          从 arXiv 下载并解压的 LaTeX 项目，保留正文、图片和 .bib 的相对路径
├── paper.pdf       可选的论文 PDF
├── figures/        补充图片
└── results/        自己的实验结果
```

只需提供实际用到的文件；不要求具备上面的全部目录。
也可以直接放入下载的论文源码压缩包，由 agent 保留原包并解压工作副本。
告诉 agent 哪个路径对应哪份材料，哪些论点最重要、哪些细节可以放进备注。
例如：“请讲清方法为什么有效、实验是否支撑结论，推导放备注；按 AGENTS.md 完成制作并交付 PDF/PPTX。”

agent 解压并阅读材料、组织叙事、选择原图并核对引用，生成 `main.tex`、`chapters/talk/` 及
需要时的 `bibliography/main.bib`。它会运行 `make draft` 检查实际排版，逐页修正密度和溢出，
按最终页序生成 `build/main.notes.json`，再运行 `make` 导出 PDF 与带备注的 PPTX。
需要补充影响含义的事实、改变核心表达或获取外部材料时先集中确认；常规精简、拆页与排版由 agent 完成。
后续把反馈直接交给 agent，它会修改正文及备注并重新构建。

### 环境与构建入口

首次使用需准备 **GNU Make、uv、XeLaTeX、latexmk、biber** 及模板的 TeX 包和字体，
或使用 [Docker 环境](docker.md)。安装说明见 [installation.md](installation.md)。
Python 依赖由 `uv run --frozen` 按 `uv.lock` 自动安装，无需另行运行 `uv sync`；首次下载需联网。

```bash
make doctor                 # 检查环境
make draft MAIN=example     # 查阅功能示例的实际页面
make MAIN=example           # 构建示例 PDF/PPTX
make                        # 构建 agent 生成的 main.tex；不存在时自动选择 example.tex
make draft                  # 所选入口的排版预览
make DPI=200                # 较低分辨率导出；正式默认 600 DPI
make MAIN=talk              # 构建其他入口 talk.tex
make pdf                    # 编译 PDF，成功后清理 LaTeX 中间文件
make clean                  # 清理所选入口的中间文件，保留产物与备注
make help
```

`MAIN` 是不含 `.tex` 后缀的入口名；显式设置会覆盖自动选择。含空格时用 `MAIN="my talk"`。
`make` 编译已有源码，不会调用模型；从提示词到内容的工作由遵循 `AGENTS.md` 的 agent 完成。
`example.tex` 及其章节用于查阅版式，agent 另行编写自己的汇报内容。

`latexmk` 自动处理多轮编译与 biber，跟踪正文、文献和素材；PPTX 转换每次都运行以应用最新备注与 DPI。
PDF/PPTX、备注和临时文件统一在 `build/`：

```text
main.tex                      agent 生成的汇报入口
chapters/talk/                agent 生成的元信息和章节
bibliography/main.bib         核实后的汇报文献
build/
├── main.pdf / main.pptx       最终交付
├── main.notes.json           逐页备注，清理时保留
├── main.aux / main.log / ...  临时文件，成功后清理、失败时保留
├── draft/main/               页面预览与排版报告
├── theme-check/              主题检查结果
├── literature/               文献检索结果
└── dist/                     源码包
```

构建示例时对应 `build/example.pdf`、`build/example.pptx` 和 `build/draft/example/`。
`make`、`make pdf` 和 `make draft` 成功后自动清理所选入口的 LaTeX 中间文件，失败时保留诊断。
转换失败会保留原 PPTX，不能把留存的文件当作本次结果；先查看退出码和日志，再运行 `make clean`。
不要并行运行清理与构建，例如 `make -j clean all`。

`materials/.gitkeep` 随仓库和源码包提供，克隆或解压后素材目录已经存在。
放进 `materials/` 的文件、`main.tex`、`chapters/talk/`、`bibliography/main.bib` 和 `build/` 中的其他构建产物只留在本地：Git 会忽略它们，源码包也不包含它们；公开示例备注 `build/example.notes.json` 是版本控制例外。
自己的图片和论文放在 `materials/`，不要放进 `assets/`；`assets/` 是模板自带的标志、校园图片和示例视频。
`prompt.md` 是随仓库提供的通用示例，把自己的思路直接发给 agent。

样式文件在 `theme/`，`.latexmkrc` 自动配置 TeX 搜索路径；始终从项目根目录构建。
正文与图像路径相对于项目根目录，PDF 内的本地附件链接相对于 `build/`。
复制这个文件夹时保留源码、`prompt.md`、`AGENTS.md`、Makefile、`.latexmkrc`、`theme/`、
`tools/`、`chapters/`、`bibliography/`、`assets/`、`docs/`、`pyproject.toml` 和 `uv.lock`；
无需复制 `.venv` 或已有构建产物。直接调用 XeLaTeX 时须自行设置主题搜索路径、创建输出目录并处理 biber，推荐交由 Make 完成。

## 更换学校

文档类为 `campusbeamer`，自动加载名为 `campus` 的主题。清华只是默认学校配置；
更换学校的品牌配色和标志时编辑 **`theme/campuscolor.sty`**，无需修改主题实现。

该文件集中定义：

- `maincolor`：封面、章节页、标题、导航和页脚的主题主色；
- `tipcolor` / `notecolor` / `alertcolor`：提示、备注、警告框的基准色；
- `examplecolor` / `definitioncolor`：示例、定义框的基准色；
- `\schoolemblemondark` / `\schoolemblemonlight`：深色／浅色底上的透明校徽；
- `\schoolwordmarkondark` / `\schoolwordmarkonlight`：深色／浅色底上的透明校名标志。

颜色按功能命名，可以改变提示框的颜色而无需修改主题代码。默认 `notecolor`
通过 `\colorlet{notecolor}{maincolor}` 跟随主色；需要独立配色时可改为
`\definecolor{notecolor}{HTML}{所需色值}`。主题根据各框的基准色派生底色、标题色和边线。
默认定义框使用琥珀色 `definitioncolor`（`B36B16`），与紫色注释框区分。
需要其他颜色时，在汇报中自行定义。

页脚固定使用 `maincolor` 背景和白色文字，无需在正文中设置颜色。
要更换页脚颜色，修改学校配置中的 `maincolor`，其他主色元素也随之变化。

把新的校徽和校名标志放到 `assets/`，再修改配置中的路径；支持写扩展名。
校徽保持透明、等比例缩放，建议使用与默认素材一致的方形画布；校名标志可使用
不同宽高比，主题按固定宽度等比例缩放。无需覆盖默认素材文件。
个人姓名、导师、日期、课题组和汇报标题属于演示文稿内容，完整示例在
`chapters/metadata.tex` 中编辑，正文在对应的章节文件中编辑；
标题与课题组直接填写文字，不通过学校配置命令间接定义。

校园照片、章节背景和普通插图属于汇报内容，直接在章节或示例文件中
传入素材路径，不在学校配置里定义编号图片或演示图片别名。例如：

```tex
\sectioncoverpage[assets/sigs_building]{本节导读}
\fitgraphic[width=.58,height=.45]{assets/sigs_wordmark.png}
```

更换学校不会自动更换演示照片。按汇报需要替换路径；不使用照片时写
`\sectioncoverpage[primary]{本节导读}`，需要白色右侧面板时用 `[white]`。

封面固定为主色斜边版式，只支持 `\titlebackground{primary}`；省略该命令也使用同一封面。
右侧色块跟随 `maincolor`，不提供整页主色、白色或图片封面选项。
`\sectioncoverpage[primary]{导读}` 表示整页主色章节页。
省略章节背景时使用主色。白色右侧面板使用 `white`。版式、字体、边距和斜边几何留在
`theme/beamerthemecampus.sty`，不属于学校配置。

## 快速排版迭代（draft）

```bash
make draft                      # 默认 96 DPI，预览所有最终 PDF 页面
make draft PAGES=3,8-10          # 只渲染第 3、8–10 页（PDF 页码，从 1 开始）
make draft DRAFT_DPI=144         # 需要看清文字细节时提高预览分辨率
make draft MAIN=talk            # 预览另一个入口文件
```

输出位于 `build/draft/<入口名>/`：自己的汇报通常为 `build/draft/main/`，功能示例为 `build/draft/example/`。

- `index.html`：本地浏览器可直接打开的逐页预览，点击图片查看原图。
- `page-0001.png` 等：agent 可直接查看的页面图像。
- `contact-001.png` 等：每组最多 12 页的缩略图，便于快速检查整体密度。
- `report.txt` / `report.json`：PDF 页数、实际预览页码、生成时间、文件哈希，以及
  LaTeX 的 Overfull/Underfull 告警与其日志行号。

draft 使用正式版相同的排版与全部图片，由 `latexmk` 增量编译；成功生成报告后会自动
清理 `build/` 中的 LaTeX 中间文件。加速来自低分辨率
渲染和跳过 PPTX 导出，不会启用隐藏图片的 TeX draft 模式。它不要求备注已经写完，
也不改写正式 PPTX。只选部分页面时仍会编译完整 PDF；告警也来自完整日志，不能按
日志行号推断 PDF 页码。每次成功预览会去掉上一轮多出来的预览图片，避免把上一轮页面当成这次的结果。
构建失败则必须先修复错误；失败时留下的报告不能作为这次的结果。

推荐循环：**写内容 → `make draft` → 看图和报告 → 精简／移入备注／拆页 → 再预览**。
每页应有合理留白、可读字号，正文不能侵入页眉、页脚或引用区。不要靠缩小到难以阅读的
字体、负间距或隐藏内容来解决溢出。精简时必须保留关键论点及必要限定条件，拆页后同步
调整备注顺序。Overfull 提醒需要检查，但不等同于可见溢出；无告警也不代表页面一定合理。
正式交付前运行不带 `PAGES` 筛选的 `make draft`，逐页检查后再运行 `make`。

## 作为 PPT 生成 harness 使用

复制这个文件夹后，向 agent 提供思路及 `materials/` 中的素材路径即可。
模型先阅读唯一的项目指令文件 `AGENTS.md`，再查阅 `example.tex` 中的布局用法和本地材料，
新建 `main.tex`，将元信息及正文写入 `chapters/talk/`，按需建立 `bibliography/main.bib`。默认采用 16:9、原文语言、简洁的讲演式页面，每个 section 的起始页使用整页主色；默认清华配置下为紫色。模型会把解释、过渡、数字含义和讲解提醒写入 `build/main.notes.json`，而不是
把所有文字堆到页面上。

当受众、用途、时长、语言、关键事实、引用、外部素材或隐私内容会改变最终叙事时，
模型必须先向你集中确认，再生成依赖这些决定的页面。普通的排版、分节、页面数量和
本地素材选择可以按模板默认值直接完成。生成后模型应编译 PDF、校对页面顺序和备注，
再导出带有 PowerPoint speaker notes 的 PPTX。

备注文件按最终 PDF 页码排列，包含 section 起始页、目录页、参考文献续页和致谢页：

```json
{
  "slides": [
    {"notes": "开场说明本页目标。"},
    {"notes": "解释图中趋势，并强调右侧结论。"},
    {"notes": ""}
  ]
}
```

[`docs/notes.example.json`](notes.example.json) 是格式示例，不能直接作为任意演示文稿的完整备注。
实际备注是 agent 生成的产物，写入 `build/<入口名>.notes.json`，不纳入版本控制或源码包。
新复制的源码不带生成的备注；按当前内容和最终页序重新生成。
公开功能演示的逐页讲解保存在 `build/example.notes.json`；它与 PDF 同目录，转换器会按默认规则自动读取，
因此 GitHub Release 中的示例 PPTX 也带有备注。
默认 `make` 在备注文件存在时严格要求条目数与 PDF 页数相同；无备注的页用 `""` 占位。
没有备注文件时会提示并生成空备注，方便直接构建模板示例。agent 生成新演示文稿时必须
提供完整备注。页数相同仍可能出现顺序错位，调整页面后需要人工或 agent 核对。
直接调用转换器时，只有加上 `--strict-notes` 才会拒绝少于 PDF 页数的备注条目。
Make 和直接调用都默认从 PDF 同目录读取同名的 `.notes.json`，无需额外参数。
`--notes-dir 路径` 可改用其他备注目录，`--notes` 可指定任意文件，`--no-notes` 禁用自动读取。

## 转换为 PowerPoint（保留跳转链接）

`tools/images_to_ppt.py` 将 PDF 的每一页渲染为一张幻灯片，并叠加近乎透明的
可点击区域，保留目录、章节导航、交叉引用、网址、邮箱及本地文件链接。
同时自动写入 PowerPoint 原生分节和文档属性；运行 `make` 即可完成，无需额外参数或元信息文件。
使用 Python 3.10+ 和 `uv`，在模板根目录执行：

```bash
uv sync --frozen
uv run --frozen tools/images_to_ppt.py build/main.pdf build/main.pptx

# 显式指定备注文件；Make 默认自动读取 build/main.notes.json
uv run --frozen tools/images_to_ppt.py build/main.pdf build/main.pptx --notes build/main.notes.json
```

`pyproject.toml` 是依赖清单，`uv.lock` 固定完整依赖版本。
Make 使用 `--frozen` 按锁文件安装，不重新解析依赖；修改依赖清单后需先运行 `uv lock`，
再执行 `make`。现有锁文件中的下载地址需要能够访问。
只有两个直接依赖：`pymupdf`（渲染 PDF、读取链接）和 `python-pptx`（写入 PPTX）；
其间接依赖由 `uv` 自动安装。转换已有 PDF 时无需安装 LaTeX、Poppler 或 LibreOffice。
只有嵌入本地视频时需要系统命令 `ffmpeg`；普通链接和没有视频的 PDF 不需要它。

原生分节从 PDF 的一级章节书签读取，与 Beamer 的 `\section` 对应；`subsection`
仍属于所在章节。每个 overlay 都归入对应分节。第一章之前的封面、导读等页面单独归入
“封面与导读”（英文模板为 `Introduction`）。同页开始且没有独立页面的空章节会跳过并报告；
没有章节书签的 PDF 不会凭空生成分节。转换器使用
[Microsoft 定义的 PowerPoint section XML](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-pptx/5bd8a237-8753-4d05-b757-c5e84e5d1ba6)，
分节是可在 PowerPoint 中折叠和重命名的原生结构。

`campusbeamer` 自动把封面字段以 Unicode 元信息嵌入 PDF，再传给 PPTX：

- `\title`、`\author` 写入标准标题、作者属性；PDF 的 subject、keywords 也会保留。
- `\subtitle`、`\course`、`\advisor`、`\date`、`\IDnumber` 分别写入自定义属性
  `Subtitle`、`Group`、`Advisor`、`PresentationDate`、`Contact`；未填写的字段不生成。
- 汇报日期来自 `\date`，与文件创建、修改时间分别保存。文件创建时间优先采用有时区的 PDF 创建时间，
  修改时间是本次导出的时间，不使用空白模板里的作者或日期。
- 文件的扩展属性记录实际幻灯片数、备注页数、嵌入视频数和页面比例，生成程序标记为 `Campus Beamer`。
- 标准文本属性超过 Office 的 255 字符限制时，会报告截断，并在 `FullTitle`、
  `FullAuthor` 等自定义属性中保留完整值。

这些属性保存在文件中，可通过 PowerPoint 的文档属性查看；分节和文档属性可编辑。
转换其他来源的 PDF 时，仅使用其中已有的书签和属性，不从画面猜测封面字段。

```bash
# 省略输出文件名：默认生成同目录、同名的 .pptx
uv run --frozen tools/images_to_ppt.py build/main.pdf

# 提高分辨率，并显示每个链接的去向
uv run --frozen tools/images_to_ppt.py build/main.pdf build/exports/main.pptx --dpi 600 --verbose

# 任何链接无法保留时返回非零退出码，不写入或覆盖输出文件
uv run --frozen tools/images_to_ppt.py build/main.pdf build/main.pptx --strict-links

# 运行回归测试（使用标准库 unittest，无额外测试依赖）
uv run --frozen python -m unittest discover -s tools/tests -v
```

默认分辨率为 600 DPI。混合尺寸页面等比例居中；PDF 每一页（包括 Beamer 的每个
overlay）都会变成独立幻灯片。输出保留视觉外观，文字、公式和图形仍是图像，
不能作为 PowerPoint 原生对象编辑。内部跳转定位到目标幻灯片，不保留 PDF 页内缩放位置；
请在 PowerPoint 放映模式下点击测试。

指向已存在本地文件的 MP4、M4V、MOV、AVI、WMV、MPEG、WebM 或 MKV 视频会作为
PowerPoint movie 对象嵌入 PPTX；视频文件随 PPTX 一起打包，文件体积会增加。远程视频、
缺失的本地视频和其他附件仍保留为文件链接。相对文件路径会按输出目录重新计算，
因此可以将输出放到子目录；分享未嵌入的附件时也需保留相应素材及相对目录结构。
完整示例使用 `assets/presentation_demo.mp4`：约 17 KB 的 6 秒原创 CC0 几何动画，
展示“大纲 → 幻灯片 → 备注”。来源、授权和重建命令见 [素材说明](../assets/README.md#原创演示视频)。
文件链接的起点是 PDF 所在目录。模板 PDF 在 `build/` 中时，正文写
`\href{run:../assets/video.mp4}{点击播放}`，图片插入仍写 `assets/图片.png`。
这使 PDF 的本地视频链接和 PPTX 的视频嵌入都指向根目录的 `assets/`。

转换器通过 FFmpeg 提取视频首帧作为预览，按画面的实际宽高比等比例缩放，居中内切于
PDF 的视频框，空余部分保留页面背景。PPT 背景图中的原边框和占位文字会被清除，
源 PDF 保持不变。如果链接只包住框内文字，转换器会尝试识别包围文字的最小矩形边框；
没有边框时使用链接区域本身。建议让整个框成为链接，示例写法为：

```tex
\href{run:../assets/video.mp4}{%
  \XeTeXLinkBox{\fbox{\parbox[c][.30\textheight][c]{.65\textwidth}{%
    \centering 点击播放视频}}}%
}
```

缺少 FFmpeg、视频损坏或无法解码时，导出失败并保留上一次 PPTX，不会生成没有预览的
视频对象。首帧如果本身是黑屏，预览也会是黑屏。实际播放仍取决于 PowerPoint 对视频编码
的支持；转换器嵌入原视频，不重新编码。
跨 PDF 的页码/命名目标使用 URI 片段，是否定位到对应位置取决于打开文件的应用。
PDF 专有动作（如 JavaScript）不转换；无法解析或无有效热区的链接会被计数并警告，
可用 `--verbose` 查看细节或用 `--strict-links` 阻止保存。

## 重构时校验 PDF

修改主题前先保存一次成功编译的 PDF；修改后用逐页比较工具检查：

```bash
uv run --frozen python tools/compare_pdf.py before.pdf build/example.pdf
```

工具默认以 600 DPI 比较所有页面的完整像素、文字及位置、尺寸、链接动作、
PDF 目录和文档信息；任一变化返回非零退出码。创建时间和修改时间单独报告，
不计入内容差异，同时报告文件是否逐字节相同。加 `--strict-bytes` 时，
任何字节差异也会导致校验失败。LaTeX 的重新编译通常会改变
创建时间、字体子集标识和 PDF trailer ID，因此内容一致与文件哈希一致应分开判断。
需要检查逐字节一致时，在前后两次完整编译中使用同一个 `SOURCE_DATE_EPOCH`，例如：

```bash
SOURCE_DATE_EPOCH=1790911667 make pdf MAIN=example LATEXMK="latexmk -g"
uv run --frozen python tools/compare_pdf.py before.pdf build/example.pdf --strict-bytes
```

固定时间必须在保存基线前和重构后同时使用；只对其中一次编译设置时间无法消除差异。
`\today` 的日期随实际编译环境变化，跨日期比较时还应固定演示文稿日期或设置
`FORCE_SOURCE_DATE=1`。

## 文件说明

- `AGENTS.md`：唯一的模型指令文件，包含工作流、确认门槛和质量检查。
- `Makefile`：供人和 agent 共用的一键编译、转换、测试及清理入口。
- `tools/draft_preview.py`：draft 页面图像、缩略图及排版告警报告，不增加依赖。
- `tools/compare_pdf.py`：重构前后 PDF 的完整逐页像素与链接回归比较。
- `prompt.md`：交给 agent 的自然语言请求示例。
- `materials/`：用户提供的论文源码、PDF、图片和数据，本地目录。
- `example.tex`：完整功能演示入口与配置参考。
- `main.tex`：agent 生成的汇报入口、文献资源及章节顺序。
- `chapters/talk/`：agent 生成的汇报元信息及正文。
- `chapters/metadata.tex`：完整示例的标题、课题组、汇报人、导师和日期。
- `chapters/01_*.tex` 至 `05_*.tex`：完整示例的五节正文，每个文件包含本节起始页和 frames。
- `theme/campusbeamer.cls`：文档类选项、中文支持、字体与文献宏包的统一入口。
- `build/main.notes.json`：agent 生成的逐页 speaker notes；转换器会自动读取它并写入 PPTX 备注。
- `build/example.notes.json`：公开功能演示的逐页备注，转换器按 PDF 同名路径自动读取。
- `docs/notes.example.json`：备注文件格式示例，不会被自动加载。
- `theme/beamerthemecampus.sty`：标题页、页眉、页脚、致谢页和引用命令等主题实现。
- `theme/campuscolor.sty`：加载 xcolor 并定义学校的功能配色与品牌标志；演示元信息和汇报插图路径在正文中维护。
- `bibliography/refs.bib`：示例的文献数据库；`bibliography/main.bib` 是 agent 为汇报建立的本地文献库。
- `docker/`：容器环境定义、Dockerfile 专用构建上下文清单与入口脚本。
- `.latexmkrc`：将 PDF 和编译临时文件统一写入 `build/`，并设置中间文件清理规则。
- `assets/`：随模板分发的标志、校园图片和原创示例视频；自己的素材放在 `materials/`。

## 常用命令

封面只支持 `\titlebackground{primary}`，也是无需额外设置的默认样式：右侧斜边主色区域由主题代码绘制，
右下角叠加配置中的 `\schoolwordmarkondark`。
左侧为白底，标题和个人信息使用封面版式。修改 `theme/campuscolor.sty` 中的 `maincolor` 即可更换主色。
除 `primary` 以外的封面参数会报错。
右侧斜边的中点位于页面半高、页面宽度的 61.8% 处；与水平线的夹角为 72°，
保持上端偏右、下端偏左。从中点水平向右的射线转向斜边右上端，逆时针测量这个角度。
上下端点由中点和角度自动推导：16:9 页面上分别位于页面宽度约 70.94% 和 52.66% 处。
封面主色色块、章节图片分栏和白色章节分栏共用这套斜边几何；默认章节页是整页主色。
主题中的 `\campussplitmidfraction`、`\campussplitangle` 定义这两个参数。
红线版本会标出斜边、中点所在竖线以及角度的测量方向。
标志通过等比缩放，使左边缘与斜边中点所在的竖线对齐，即页面宽度的 61.8% 处；
右边缘停在固定的右边距上，右、下边距均为一个 `\large` 的 `\baselineskip`
（当前为 14 pt，约 4.92 mm）。宽度按 `页面宽度 - 左边距 - 右边距` 自动推导，
高度由素材比例自动确定；当前白色标志约为 56.20 mm × 18.86 mm。
左边距由 `\campussplitmidfraction` 推导，右、下边距分别由
`\campuswordmarkrightskip`、`\campuswordmarkbottomskip` 定义。
启用红线开关时，会标注标志外接矩形、实际宽高、左边缘的 61.8% 对齐线，
以及右、下边距所用的 `\large` 行距基准和实际长度。

公式示例位于 `chapters/math-examples.tex`，展示行内数学、多行对齐、梯度、
矩阵和分段函数；`chapters/bibliography-guide.tex` 展示文献字段、角落引用和文末列表的对应关系。
两个文件分别由基础页面章节和论文讲解章节引入，通过 `example.tex` 编译查看。

### 分文件组织完整示例

`example.tex` 存放演示配置与章节入口，标题信息和正文分开放：

```text
chapters/
├── metadata.tex       标题与个人信息
├── harness-guide.tex  用户提供思路与素材、agent 制作与交付的说明
├── 01_basics.tex      基础页面、公式与图像
├── 02_papers.tex      论文讲解与引用
├── 03_callouts.tex    提示框、定义与示例
├── 04_navigation.tex  四小节导航布局
├── 05_media.tex       视频、参考文献与致谢
├── layout-guide.tex   页面对齐参考线
├── font-guide.tex     字号与用途
├── math-examples.tex  公式示例
├── code-guide.tex     代码展示
├── bibliography-guide.tex 文献用法
└── code/normalize.py  演示中读取的代码源文件
```

正文用 `\input{chapters/01_basics.tex}` 等命令按入口中的顺序组合，
章节文件只包含内容，不重复写 `\documentclass` 或 `\begin{document}`。
要给示例增加章节时，在 `example.tex` 中添加一条 `\input`；重排这些语句即可调整章节顺序。
资源和嵌套 `\input` 路径相对于项目根目录，例如章节中使用
`assets/sigs_building` 和 `chapters/math-examples.tex`。
查看示例时从根目录运行 `make MAIN=example` 或 `make draft MAIN=example`，不单独编译章节；
`latexmk` 会追踪这些文件的变化。调整顺序后同步核对逐页备注。
演示片段与所属章节同放在 `chapters/`，由章节中的 `\input` 引入。
自己的汇报由 agent 组织在 `main.tex` 与 `chapters/talk/` 中，提示词示例见 `prompt.md`。

`example.tex` 在封面后先介绍推荐使用方式，再按“基础页面与图像、论文讲解与引用、提示框、导航布局、媒体与收尾”组织示例，
五节分别包含 1、2、3、4、5 个 subsection，覆盖单列、两列及奇数项最后一行的排列。
每节均显式调用 `\sectioncoverpage`，展示本节标题、全部小节和一句导读；第二节起始页前另有一次内容总览。
五节分别使用 `assets/sigs_building`、`assets/tsinghua_door`、`assets/sigs_dom`、
`assets/tsinghua_door1` 和 `assets/sigs_night`，
展示左侧紫底文字、右侧斜边图片的样式；原图右边缘贴齐页面右边缘，
可直接修改原图来调整显示区域。新演示文稿的章节起始页默认使用整页主色背景；
需要图片样式时，把图片路径传给 `\sectioncoverpage`。
每节内先展示效果，再介绍对应命令，便于复制使用。新增 section 时可沿用该结构，起始页可以按需增删。

微调封面、章节起始页或致谢页时，在所选入口（`main.tex` 或 `example.tex`）的文档类选项中加入
`layoutguides=true`，再运行 `make draft`：

```tex
\documentclass[language=chinese,layoutguides=true]{campusbeamer}
```

主题会在这些页面叠加红色边界、对齐线，
并标出各区域字号、字号点数和实际 `\baselineskip` 数值；封面与致谢页还会逐行标出元信息的字号和行距。
章节页会标出编号、标题、小节清单/导读的字号，以及页顶→编号、编号→标题、标题→列表、
列表→导读和导读→页底的实际竖直间距。各箭头给出 `baselineskip` 倍数和所依据的字号；
编号到标题的间距基于 `\Large`；标题到列表、列表到导读的间距基于 `\normalsize`。
完成检查后删除 `layoutguides=true` 或改为 `layoutguides=false`，再运行 `make`
生成无标注的最终 PDF/PPTX。开关默认关闭，不提供命令形式的开关。

主题自带的标签可以统一切换语言。在文档类中设置
`language=chinese`（默认）或 `language=english`；该选项会切换目录标题、
section 起始页的编号标签、指导教师标签、参考文献页标题、致谢文字、图表标签和提示框的默认标题。
用户自己写入的 section、subsection、导读、正文和自定义提示框标题不会被翻译。
文档类也随语言选择是否加载 xeCJK；英文标签配中文正文使用 `cjk=true`。
`\campussetlayout{template language=...}` 只切换标签，不加载或卸载宏包。

中英文共用字号、行距和对齐位置。封面及致谢页的汇报人／指导教师标签
（英文为 Speaker／Advisor）以当前字体下两者自然宽度的最大值作为共同宽度；
较长标签保持自然字距，较短标签按字符两端对齐。冒号另占 `1em`，
使两行冒号和姓名起点一致。致谢文字与日期的底部按实际字形边界对齐，
英文中 `y`、`g` 等字母的下伸部分也计入其中。

- `\fitgraphic[width=.8,height=.6]{file}`：把图片或 PDF 等比例放入页面宽度
  80%、页面高度 60% 的方框中。
- `\fitgraphic[width=.8,height=.6,page=2]{file.pdf}`：插入多页 PDF 的第 2 页。
- `\fitfigure[width=.8,height=.6]{file}{图注}`：生成包含自动适配素材和图注的
  完整 `figure`；图注写成空参数 `{}` 时不显示图注。
- `\begin{paperframe}{论文标题}{key1,key2} ... \end{paperframe}`：生成论文
  讲解页，并在右上角自动插入一篇或多篇引用；页眉自动显示当前 subsection。
  在文献键之后添加 `[bottom-left]` 或 `[bottom-right]` 可选择左下或右下位置。
  条目中的 `userb`、`userc`、`usere`、`userf` 可自动追加机构、发表 venue（预印本写 `arXiv`）、引用量和统计日期，
  样式与当前角落引用保持一致。
- `\begin{rightimageframe}[image width=.40]{标题}{图片} ... \end{rightimageframe}`：
  生成右侧图片页，图片不覆盖导航和页脚，左侧保留正文空间。
- `\sectioncoverpage[图片]{导读文字}`：按需生成当前 section 的起始页；主标题和编号自动取当前
  `\section`，副标题区域自动列出该 section 下的全部 `subsection`，调用者只需提供图片和导读文字。
  可选参数也可填 `white`（左侧保持主色、右侧纯白）或 `primary`（整页主色、白色标题）：
  `\sectioncoverpage[white]{导读文字}`、`\sectioncoverpage[primary]{导读文字}`。
  省略可选参数或写 `[]` 时使用纯紫色背景；也可以直接填写图片路径。
  图片默认不裁边。先等比例缩放覆盖右侧面板，再读取缩放后图片的实际宽度，按“左边位置 = 页面宽度 − 缩放后宽度”放置，使图片右边缘与页面右边缘重合；竖直方向居中，最后按斜边区域裁切。可直接调整原图来改变显示区域，图片自带白边也按原图显示。
  需要手动改变取景时，可在导读之后附加 `[trim right=.112,align=center]`：`trim right` 按原图宽度比例裁去右边缘，`align=center` 将照片在右侧面板的外接矩形中居中取景。示例不启用这些选项。
  没有 subsection 时自动隐藏列表。每个 subsection 前显示数字编号（如 `1.1`、`1.2`）。
  section 编号使用 `\Large`，subsection 清单和自定义导读语句使用 `\normalsize`。
  1–3 个小节采用单列，4 个及以上自动采用两列，按从左到右、再从上到下的顺序排列；奇数个小节的最后一项位于左列。
  封面、section 起始页和致谢页主标题统一使用 `\Huge` 字号。
  封面和 section 起始页以主标题自身的垂直中心对齐页面中心；多行标题按整个标题文本盒居中。
  其余信息跟随标题排布，作者信息和小节数量不会改变标题的居中位置。
  section 起始页中，section 编号与主标题之间留一个 `\Large` 的 `\baselineskip`；
  主标题与 subsection 清单之间、subsection 清单与自定义导读语句之间各留一个
  `\normalsize` 的 `\baselineskip`。
  封面副标题、课程/课题组、汇报人、指导教师（若有）和日期各占当前字体的一个 `\baselineskip`，
  信息行之间没有额外的段落间距。
  封面与致谢页的副标题使用 `\Large`；课程/课题组、汇报人、指导教师和日期使用 `\normalsize`，
  封面中课程/课题组与汇报人、指导教师同为黑色；致谢页全部正文文字为白色。
  主标题下方紧接信息区，不额外留白。
- `\sectiontocpage`：无参数，按需生成列出全部 section 的目录页；标题自动显示为“目录”或“Table of Contents”。
  `\sectioncoverpage` 和 `\sectiontocpage` 都不会由 `\section` 自动调用，二者可以单独使用、同时使用，
  也可以按任意顺序排列。
- 目录、参考文献（含续页）等单行页眉使用 `\LARGE`，文字框底部位于校徽色块底边上方一个 `\tiny` 的 `\baselineskip`（当前为 7 pt）。间隔由主题的 `\campusheaderemptybaseline` 从实际字号读取。没有小节页眉的普通内容页也使用此样式；标题左边缘和正文起始位置与双行页眉相同。
- `\cornercite{key}`：在右上角插入一篇默认格式的引用。
- `\cornercite{key1,key2}`：用逗号分隔文献键，每篇引用独立成行。
- `\cornercite[bottom-left]{key}`：将引用放在左下角；也可使用
  `bottom-right`，默认位置为 `top-right`。
- `\referencespage[shrink][\normalsize]`：汇总正文中已引用文献，内容过多时缩小字号并保持一页。
- `\referencespage[break][\small]`：汇总正文中已引用文献，内容过多时按页续排，并使用指定字号。
- `\referencespage[shrink][\small][twocolumn]`：使用双栏排版；第三个参数省略或写 `onecolumn` 时使用单栏。
- `\backmatter`：生成致谢页，并同步显示封面的标题、副标题、课程/课题组、作者、指导教师和日期信息；主标题沿用封面的页面垂直中心锚点。
  信息行分别占用当前字体的一个 `\baselineskip`，不叠加段落间距。右侧两行感谢语句使用 `\LARGE` 并保持右对齐，
  两行基线相距一个 `\LARGE` 的 `\baselineskip`，末行文字下边缘与左侧日期对齐；加入 `[notitle]` 可隐藏主标题。

封面可以用 `\advisor{姓名}` 增加指导教师信息。该命令是可选的；省略时不增加这一行，填写后会在汇报人
下方显示 `指导教师：姓名`。

## 代码与终端窗口

`campuscode` 提供深灰代码区、窄标题栏和语言图标。标题栏直接显示图标与文件名或
Terminal 标题，不添加窗口控制圆点。窗口没有阴影，
宽度跟随当前正文或 column；代码使用等宽字体与语法高亮。Python 显示 Python 图标，
`bash` / `text` 显示终端图标，Java 显示 Java 图标，其他语言使用通用代码图标。
图标来自 TeX 自带的 Font Awesome 5 包，无需下载图片。

```tex
\begin{frame}[fragile]{归一化函数}
\begin{campuscode}[language=Python,numbers]{normalize.py}
def normalize(values):
    total = sum(values)
    return [value / total for value in values]
\end{campuscode}
\end{frame}
```

直接输入代码时，外层必须是 `frame[fragile]`，`\end{campuscode}` 和
`\end{frame}` 分别独占一行。文件名参数按字面显示，下划线无需转义。
默认语言为 `Python`，默认不显示行号；示例中的 `numbers` 等同于 `numbers=true`。
每个窗口独立恢复默认设置。

```tex
\begin{frame}[fragile]{运行示例}
\begin{campuscode}[language=bash]{Terminal}
$ python normalize.py
[0.2, 0.3, 0.5]
\end{campuscode}
\end{frame}
```

命令与输出是静态文本，编译不会执行代码，不需要 shell escape、Pygments 或新增 Python 依赖。
终端转录用 `bash`，无需语法高亮的日志用 `language=text`。其他语言采用 listings 的名称，
例如 `C++`、`Java` 或 `{[LaTeX]TeX}`；当前图标匹配使用上述大小写。

已有代码文件使用 `\campusinputcode[选项]{窗口标题}{文件路径}`，路径相对于项目根目录。
这种用法不含逐字输入，外层普通 frame 即可：

```tex
\begin{frame}{关键实现}
\campusinputcode[language=Python,numbers,firstline=2,lastline=5,firstnumber=2]
  {normalize.py}{chapters/code/normalize.py}
\end{frame}
```

- `firstline` / `lastline`：读取的首尾行号，包含两端；默认显示全部。
- `firstnumber`：显示的第一个行号，默认 `1`；摘录文件时可手动设为源文件行号。
- `numbers=false`：隐藏行号。
- `label=...`：覆盖标题栏右侧语言文字。
- `icon=\faCode`：覆盖标题栏图标，也可使用已加载 Font Awesome 5 的其他图标。
  自定义 `label`、`icon` 应写在 `language` 之后。

中文注释在启用 xeCJK 的汇报中受支持；英文汇报含中文代码时设置 `cjk=true`。
长行会在词元之间自动换行，单个超长标识符仍需手动改写；窗口不会自动跨幻灯片拆分。
建议一页只展示一个短函数，内容较长时
用文件行范围拆成多页；不要缩小字号来隐藏拥挤。窗口标题应简短，完整路径放在备注中。
实现位于 `theme/campuscode.sty`，由主题自动加载。普通 `verbatim` 环境也可以使用。
完整演示见 `chapters/code-guide.tex`。

## Section 与小节导航

普通页页脚包含两行紧凑文字导航：上方列出当前 section 下所有 subsection，下方列出当前
`part` 内所有 section 名。当前 section 和 subsection 使用主题强调色，其余项目使用较浅的颜色；
导航栏中的 section 保留序号，subsection 使用 `section.subsection` 层级序号；section 起始页中的
subsection 列表显示 `section.subsection` 编号与名称。
点击名称可以跳到对应页面。同一行的项目按页面宽度均匀分布。两行导航使用页脚的字号、
行高和下沉深度。三行共用页脚 `\scriptsize` 字体的 `\baselineskip` 作为固定网格基准，
每行总高度为 `1` 个基准（盒高 `0.80`、下沉深度 `0.20`），不随页内字号切换而变化。
这些尺寸由主题内部统一推导，图片下边界及底部引用位置随页脚总高度同步。
居中位置根据网格行高和实际文字的高度、下沉深度计算，不使用硬编码的偏移量或额外支撑盒留白，
使文字上下边界的中点与色带中点重合；最底部页脚文字采用相同规则。背景色从下方
section 行到上方 subsection 行逐渐变淡。
导航位于页码和作者标题色条之上，
不改变标题和副标题的位置。
标题页、section 起始页、目录页和致谢页不显示导航。
使用 `plain` 样式，不显示导航。`\sectiontocpage` 只列 section 标题，不展开 subsection，避免小节过多挤满页面。

`\section` 不会自动插入起始页。需要时，在 `\section` 后显式调用下面的命令；两种页面可以同时使用，顺序完全由正文决定：

```tex
\section{研究方法与系统设计}
\sectiontocpage                    % 全部 section 的目录页（标题自动生成）
\sectioncoverpage[assets/section.jpg]{本节的导读文字。}
```

导航自动读取 Beamer 的结构，直接使用 `\section` 和 `\subsection` 即可。
示例 `example.tex` 包含多个小节，可观察翻页时的高亮变化：

```tex
\section[方法]{研究方法与系统设计}
\subsection[建模]{问题建模与基本假设}
\begin{frame}{方法概览}
  ...
\end{frame}
\subsection[训练]{训练流程与实现细节}
```

方括号中的短名称用于导航，完整名称用于 section 目录等位置。section 较多或名称较长时，
优先提供短名称；横向导航保持单行，不自动换行。没有小节时，上方 subsection 行自动留空，导航高度
保持一致。导航名称和链接需要至少两轮 XeLaTeX，`latexmk` 会自动完成。

```tex
\documentclass[language=chinese,navigation=true,cornerwidth=4.8cm]{campusbeamer}
```

`\campussetlayout{section navigation=on/off,corner width=...}` 可以覆盖这些配置。

导航两行和底部页脚的字号由主题统一固定，以保持各行高度和垂直对齐一致。
导航不会增加正文上方的高度，也不会改变标题和副标题的位置。版式参考了 Beamer 官方的
[miniframes 外部主题](https://github.com/josephwright/beamer/blob/main/base/themes/outer/beamerouterthememiniframes.sty)
及[用户手册的导航接口](https://texdoc.org/serve/beameruserguide/0)，
保留原生导航链接，同时将每个 section 和 subsection 放入等宽单元格。

## 图像与引用版式

`\fitgraphic` 的 `width` 和 `height` 是相对于整张幻灯片 `\paperwidth`、
`\paperheight` 的无量纲比例，默认值分别为 `.85` 和 `.60`。命令会创建固定大小
的隐形方框，再将图片或 PDF 页面保持纵横比地水平、垂直居中；内容不会被拉伸或
裁切。方框比例应为正数，通常不超过 `1`。

论文讲解页可以把标题、图片、图注和角落引用写在一起：

```tex
\begin{paperframe}{Paper Title}{paper-key}
  \fitfigure[width=.9,height=.58]{figures/method.pdf}{Method overview.}
\end{paperframe}
```

`paperframe` 自动使用当前 subsection 作为页眉上方的主题名称；文献键参数
同样接受逗号分隔的多个文献键。引用位置可通过末尾的可选参数指定：

```tex
\begin{paperframe}{Paper Title}{key1,key2}[bottom-left][6cm]
  % 正文
\end{paperframe}
```

支持 `top-right`（默认）、`bottom-left` 和 `bottom-right`，与 `\cornercite` 一致。
位置之后的可选参数用于设置本页引用宽度，例如 `[6cm]` 或
`[0.35\paperwidth]`；省略时使用全局 `corner width`。正文中仍可使用
`\setcornercitewidth{...}` 临时调整宽度。
如果引用条目的 `userb`、`userc`、`usere`、`userf` 字段非空，`paperframe` 会在同一引用样式下
依次追加机构、发表 venue 或 `arXiv`、引用量和统计日期；不填写的字段会自动隐藏。
以下为字段填写示意，尖括号内容需要替换为核实后的信息：

```bibtex
userb = {<论文署名机构>},
userc = {<会议或期刊简称，发表年月；预印本填写 arXiv>},
usere = {<引用次数>},
userf = {<统计来源，截至 YYYY-MM-DD>},
```

完整标题仍来自 `title`，年份沿用 `year`；发表 venue、发表年月或 `arXiv` 统一填写在 `userc`。
这些信息逐篇追加在原引用之后，保持灰色、小字号和紧凑行距。
`userf` 随 `usere` 显示；不填写引用量时不单独显示统计日期。
可使用 `make literature QUERY="论文标题"` 搜索 DBLP，再用
`make bibtex DBLP_KEY=conf/... CITE_KEY=MyPaper` 获取 BibTeX 与引用次数快照；
已有条目使用 `make citations DOI=10.../...` 查询。默认引用数来源为 OpenAlex，
可切换 Semantic Scholar；来源与日期写入 `userf`。详见[文献获取流程](literature.md)。
这些字段只用于 `paperframe` 的自动引用，普通 `\cornercite` 和文末参考文献不使用它们。
页眉也可以写在最前面，例如 `\begin{paperframe}[Method]{Title}{key}[bottom-right]`。
需要代码或 verbatim 内容的页面使用普通的
`\begin{frame}[fragile] ... \end{frame}`。

右侧图片页使用普通页面的标题、副标题、页眉和页脚：

```tex
\begin{rightimageframe}[image width=.40,page=2]{Experiment}{figures/result.pdf}
  \begin{itemize}
    \item 左侧可以放置文字、公式或提示框。
    \item 图片保持纵横比，右边缘与幻灯片右边缘重合。
  \end{itemize}
\end{rightimageframe}
```

`image width` 是右侧图片区域占 `\paperwidth` 的比例，默认值为 `.40`；图片会
按可用高度缩放，并在过宽时仅裁去左侧超出图片区域的部分，因此不会侵入左侧正文。
对于多页 PDF，可以使用 `page=...` 选择页面。图片可见区域从页面顶端延伸至页脚
导航上边缘，导航和页脚本身不会被覆盖。若页面包含 verbatim 或代码块，请改用普通的
`frame[fragile]`，并手动安排图文布局。

`main.tex` 的文档类选项中，`navigation=true/false` 控制两层导航，
`cornerwidth=4.8cm` 设置角落引用的默认宽度（默认占页面宽度的 30%）。其余版式由主题固定。
`language=chinese/english` 控制主题自动生成的文字语言和默认中文支持，默认中文。
`\campussetlayout` 的 `section navigation`、`corner width` 和
`template language` 可以做局部覆盖，但不会改变宏包加载。
普通页正文的左右边界采用相同页边距，并与左上角校徽色块的左边缘对齐；普通页标题和副标题从校徽色块右侧
再留一个 `\normalsize` 的 `\baselineskip`，避免与校徽重叠。上方使用 frametitle 字号显示 subsection，下方的页眉副标题行使用 `\normalsize` 显示 frametitle；尚未设置 subsection 时只显示主标题。
页眉纵向采用三行基线网格：最上方空行占一个 `\tiny` 字体的 `\baselineskip`，中间标题行占一个 `frametitle` 字体的 `\baselineskip`，副标题行占一个 `framesubtitle` 字体的 `\baselineskip`。
该网格从幻灯片上边缘开始，校徽色块作为左上角独立元素覆盖在网格旁边。
校徽色块底边与副标题行的底部对齐；色块左边距以及正文左右边距均采用普通页眉标题字号的一个
`\baselineskip`，色块右边到页眉标题和副标题的间距为一个 `\normalsize` 的
`\baselineskip`，由 `\campusheadertextgap` 控制（当前为 13.6 pt，约 4.78 mm）。
校徽使用配置中的 `\schoolemblemondark`（默认白色图案）和
`\schoolemblemonlight`（默认紫色图案），背景色块由主题绘制：白色页面上为紫色，
紫色章节页上为白色。色块宽度为一个 `\Huge` 的 `\baselineskip`（当前为 30 pt），高度采用页眉三行网格。
透明校徽等比缩放并水平居中，其外接矩形到色块左、右和下边各留 `3 pt`。
因此当前校徽宽度为 `30 - 2 × 3 = 24 pt`；
上方留白由色块高度与校徽高度自动确定。图片尺寸和留白分别由主题中的
`\campuslogoimagewidth`、`\campuslogopadding` 推导，色块本身的几何尺寸保持独立。
description 标签按同一环境内的最长标签右对齐；最长标签的左边缘与正文左边界对齐。使用
`\begin{description}[最长标签]` 指定该环境的最长标签，说明文字会保持统一的起始位置。
右侧图片页会依据相同的正文区域自动调整左侧内容宽度。

单页需要不同宽度时，在 frame 内、引用命令之前使用 `\setcornercitewidth`：

```tex
\begin{frame}{实验结果}
  \setcornercitewidth{6cm}
  % 本页正文
  \cornercite{Zadeh2017TensorFN}
\end{frame}
```

此设置仅影响当前 frame 中之后生成的角落引用，下一页自动恢复全局宽度。
也可以写成 `\setcornercitewidth{0.35\paperwidth}`。三个引用位置共用此宽度；
在 `paperframe` 的正文中使用同一命令，也会作用于该页自动生成的引用。
该设置不改变引用的字号、边缘位置或文末参考文献页。

参考文献字号作为 `\referencespage` 的第二个可选参数设置，例如
`\referencespage[shrink][\small]` 或 `\referencespage[break][\footnotesize]`。
第三个可选参数控制栏数：默认是 `onecolumn`，也可以写成
`\referencespage[shrink][\small][twocolumn]` 使用双栏排版。

参考文献汇总页固定使用数字标签；配合 `sorting=none` 时，标签按照文献首次被
引用的顺序排列。角落引用需要自定义短文本时，在 `bibliography/refs.bib` 条目中使用
`usera = {...}`，该字段不会替换汇总页的数字标签。条目中的 `shorthand`
会按 `usera` 处理。

`.bib` 字段的显示规则（当前 `biblatex` / IEEE 配置）：

- 文献键是 `\cornercite{...}` 的查找标识，本身不作为论文标题输出。
- 无 `usera` 时，角落引用使用 `author`、`year` 和 `title`；作者姓名的缩写和省略由样式控制。
- 有 `usera` 时，角落引用使用 `usera` 和 `title`，不追加作者或年份。
  因此自定义文本中需要的会议简称、年份应自行写入 `usera`。
- `shorttitle` 仅在缺少 `title` 时作为角落标题的备选；它不会覆盖已有的完整标题。
- 文末列表使用标准文献字段；本例 `@inproceedings` 的 `booktitle` 是会议论文集名称，
  与 `author`、`title`、`year` 一起组成完整出处。其他类型可使用 `journaltitle`、
  `volume`、`number`、`pages`、`doi` 等字段，具体输出由条目类型、样式与选项决定。
- 角落引用不自动打印 `booktitle`、页码或 DOI；`usera` 不替换文末列表的数字标签。
  未引用的数据库条目默认不会列入汇总页。


普通页面推荐按 `section → subsection → frametitle` 组织，不需要逐页填写 `\framesubtitle`：

```tex
\section{实验结果}
\sectioncoverpage{本节介绍实验设置与结果分析。}
\subsection{性能对比}
\begin{frame}{主要结果}
  % 页眉上方自动显示“性能对比”，下方显示“主要结果”。
\end{frame}
\begin{frame}{消融实验}
  % 沿用相同 subsection，只更换本页标题。
\end{frame}
```

`\begin{frame}{标题}` 的标题参数等价于在 frame 内使用 `\frametitle{标题}`。
封面的 `\subtitle` 是整场报告的副标题，仍可按需填写。

示例文件还专门包含了分别拥有 1、2、3、4、5 个 subsection 的 section，便于检查单列、偶数项两列和奇数项两列的显示效果。
其中“版式对齐检查”页会用贯穿页面的红色参考线标出校徽、正文、普通页标题、页脚色带和页面中轴，方便直接比较不同页面的几何位置。
