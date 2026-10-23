<div align="center">
  <h1>
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/campus-beamer-logo-white.svg">
      <img src="assets/campus-beamer-logo.svg" alt="Campus Beamer" width="480">
    </picture>
  </h1>
  <h2>简洁、优雅，面向 Agent 的学术 Beamer 模板</h2>
  <p>
    <a href="https://github.com/AnikiFan/campus-beamer/releases/latest"><img src="https://img.shields.io/github/v/release/AnikiFan/campus-beamer?color=000000&amp;label=release" alt="最新发布版本"></a>
    <a href="https://github.com/AnikiFan/campus-beamer/actions/workflows/ci.yml"><img src="https://github.com/AnikiFan/campus-beamer/actions/workflows/ci.yml/badge.svg?branch=main" alt="源码检查状态"></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/code-GPL--3.0%2B-blue" alt="代码许可：GPL-3.0-or-later"></a>
    <a href="https://github.com/AnikiFan/campus-beamer/releases"><img src="https://img.shields.io/badge/export-PDF%20%2B%20PPTX-000000" alt="导出 PDF 与 PowerPoint"></a>
  </p>
  <p>把思路和备好的素材交给 agent，生成排版完整、带讲解备注的 PDF 与 PowerPoint。</p>
  <p>
    <a href="README.en.md">English</a> ·
    <a href="docs/usage.md">使用手册</a> ·
    <a href="CONTRIBUTING.md">贡献指南</a> ·
    <a href="docs/releases.md">版本与发布</a>
    <br>
    <a href="SECURITY.md">安全政策</a> ·
    <a href="ACCESSIBILITY.md">无障碍说明</a> ·
    <a href="#致谢">致谢</a>
  </p>
</div>

![默认 general 主题的封面预览](docs/images/cover.png)

## 示例页面

`example.tex` 是版式与功能演示；general 主题完整功能演示的 PDF/PPTX，以及清华和鹏城实验室主题的 PDF 样例请前往
[GitHub Releases](https://github.com/AnikiFan/campus-beamer/releases) 下载。
general 另提供完整英文版 [`example-en.tex`](example-en.tex)，可用 `make pdf MAIN=example-en` 编译。
Release 中的 `campus-beamer-X.Y.Z-example-en.pdf` 为英文 PDF；英文版不附带 PPTX。
Release 中的示例 PPTX 已写入逐页 PowerPoint 备注，可直接在演讲者视图查看。
渐进显示页包含实际 overlays：在 PDF/PPTX 中按页推进，可看到要点累积与内容替换，并查看各阶段备注。
三个主题使用相同的页面内容、页数和页序，下面分别展示各主题的完整代表性页面：

<!-- demo-gallery:start -->

### General 通用主题

<div align="center">
  <p>
    <img src="docs/images/preview-general-cover.png" alt="封面" width="200">
    <img src="docs/images/preview-general-toc.png" alt="目录页" width="200">
    <img src="docs/images/preview-general-focus.png" alt="简洁页面" width="200">
    <img src="docs/images/preview-general-background.png" alt="居中图片背景" width="200">
  </p>
  <p>
    <img src="docs/images/preview-general-flow.png" alt="对齐流程图" width="200">
    <img src="docs/images/preview-general-layout.png" alt="公式页" width="200">
    <img src="docs/images/preview-general-code.png" alt="代码窗口页" width="200">
    <img src="docs/images/preview-general-fullheight.png" alt="右侧满高图片页" width="200">
  </p>
  <p>
    <img src="docs/images/preview-general-paper.png" alt="论文讲解章节页" width="200">
    <img src="docs/images/preview-general-callouts.png" alt="提示框页" width="200">
    <img src="docs/images/preview-general-overlays.png" alt="逐步显示" width="200">
    <img src="docs/images/preview-general-media.png" alt="视频链接页" width="200">
  </p>
  <p>
    <img src="docs/images/preview-general-notes.png" alt="TeX 讲者备注" width="200">
    <img src="docs/images/preview-general-references.png" alt="参考文献页" width="200">
    <img src="docs/images/preview-general-closing.png" alt="致谢页" width="200">
  </p>
</div>

### 清华大学（tsinghua）

<div align="center">
  <p>
    <img src="docs/images/preview-tsinghua-cover.png" alt="封面" width="200">
    <img src="docs/images/preview-tsinghua-toc.png" alt="目录页" width="200">
    <img src="docs/images/preview-tsinghua-focus.png" alt="简洁页面" width="200">
    <img src="docs/images/preview-tsinghua-background.png" alt="居中图片背景" width="200">
  </p>
  <p>
    <img src="docs/images/preview-tsinghua-flow.png" alt="对齐流程图" width="200">
    <img src="docs/images/preview-tsinghua-layout.png" alt="公式页" width="200">
    <img src="docs/images/preview-tsinghua-code.png" alt="代码窗口页" width="200">
    <img src="docs/images/preview-tsinghua-fullheight.png" alt="右侧满高图片页" width="200">
  </p>
  <p>
    <img src="docs/images/preview-tsinghua-paper.png" alt="论文讲解章节页" width="200">
    <img src="docs/images/preview-tsinghua-callouts.png" alt="提示框页" width="200">
    <img src="docs/images/preview-tsinghua-overlays.png" alt="逐步显示" width="200">
    <img src="docs/images/preview-tsinghua-media.png" alt="视频链接页" width="200">
  </p>
  <p>
    <img src="docs/images/preview-tsinghua-notes.png" alt="TeX 讲者备注" width="200">
    <img src="docs/images/preview-tsinghua-references.png" alt="参考文献页" width="200">
    <img src="docs/images/preview-tsinghua-closing.png" alt="致谢页" width="200">
  </p>
</div>

### 鹏城实验室（pcl）

<div align="center">
  <p>
    <img src="docs/images/preview-pcl-cover.png" alt="封面" width="200">
    <img src="docs/images/preview-pcl-toc.png" alt="目录页" width="200">
    <img src="docs/images/preview-pcl-focus.png" alt="简洁页面" width="200">
    <img src="docs/images/preview-pcl-background.png" alt="居中图片背景" width="200">
  </p>
  <p>
    <img src="docs/images/preview-pcl-flow.png" alt="对齐流程图" width="200">
    <img src="docs/images/preview-pcl-layout.png" alt="公式页" width="200">
    <img src="docs/images/preview-pcl-code.png" alt="代码窗口页" width="200">
    <img src="docs/images/preview-pcl-fullheight.png" alt="右侧满高图片页" width="200">
  </p>
  <p>
    <img src="docs/images/preview-pcl-paper.png" alt="论文讲解章节页" width="200">
    <img src="docs/images/preview-pcl-callouts.png" alt="提示框页" width="200">
    <img src="docs/images/preview-pcl-overlays.png" alt="逐步显示" width="200">
    <img src="docs/images/preview-pcl-media.png" alt="视频链接页" width="200">
  </p>
  <p>
    <img src="docs/images/preview-pcl-notes.png" alt="TeX 讲者备注" width="200">
    <img src="docs/images/preview-pcl-references.png" alt="参考文献页" width="200">
    <img src="docs/images/preview-pcl-closing.png" alt="致谢页" width="200">
  </p>
</div>

<!-- demo-gallery:end -->

各主题示例页由对应样例 PDF 从 600 DPI 开始渲染，每张不超过 0.5 MiB，保持相同页序；其中的校徽、校名和校园图像适用
[素材来源与使用声明](assets/README.md)。

默认主题为与机构无关的 `general`；可用 `\documentclass[theme=general]{campusbeamer}` 显式选择。
博士帽、透明项目字标、配色和可编辑素材集中在 [`theme/general/`](theme/general/README.md)。主题实现沿用通用的 `campus` 命名。
`example.tex` 展示模板的版式与功能；自己的汇报由 agent 根据你的需求生成。
本项目不是学校官方发布的模板。

## 下载主题素材

从 Release 下载并解压所选版本的 `campus-beamer-*-source.zip` 后，默认 general 主题可直接使用。
清华与鹏城实验室素材分别维护一份最新版，不随每次模板发布重复打包；按需在项目根目录执行：

```bash
make theme-assets THEME=tsinghua
# 使用鹏城实验室主题时：
make theme-assets THEME=pcl
```

命令只需 Python 3.10+，会下载对应主题、校验 SHA-256 并安装到 `theme/<主题>/assets/`。
已有完整素材时不联网；Git 克隆通常已包含素材，无需另行下载。预览图仍随源码包提供。
[清华素材](https://github.com/AnikiFan/campus-beamer/releases/tag/theme-assets-tsinghua)与
[鹏城实验室素材](https://github.com/AnikiFan/campus-beamer/releases/tag/theme-assets-pcl)独立更新。
显式更新和手动下载方法见[安装说明](docs/installation.md#机构主题素材)。

## 推荐使用方式：提供思路与素材

1. 克隆仓库或解压源码包，在支持本地文件读写和命令执行的 agent 中打开项目。
2. 提前把素材放进 `materials/`：例如从 arXiv 下载的论文 LaTeX 源码包、论文 PDF、图片或自己的实验结果。
3. 在根目录的 [`outline.md`](outline.md) 中填写基本信息，并在草稿区写下演讲思路。草稿可使用自然语言、笔记或章节列表，也可注明目标、素材路径和讲解偏好。
4. 向 agent 发出制作请求：

> 根据大纲制作 PPT。

agent 按 [`AGENTS.md`](AGENTS.md) 读取草稿和素材，先扩充成按章节（`section`）与小节（`subsection`）组织的详细大纲，
展开要点、解释、证据和讲述顺序，供你审阅。内容补充与重组在这个阶段完成。
确认后，它会按详细大纲编排页面、分配正文与备注、检查排版，并导出 `build/main.pdf` 和 `build/main.pptx`。

制作、验证与 Mermaid 图形流程由仓库内置的 [Agent Skills](docs/usage.md#内置-agent-skills) 提供，agent 按任务调用对应入口。

[`STYLE.md`](STYLE.md) 定义默认汇报风格，**可按你的需求修改**：
包括每页内容密度、正文与备注的分工、备注详细程度、引用位置及日期格式。
agent 在制作和修订时应用这些偏好；当前大纲中的明确要求优先。
论文源码包的解压，以及正文、图注、图片和文献的阅读与整理，也由 agent 完成。
大纲扩充以演讲目标和已提供材料为依据；需要外部检索、新素材或修改事实时，agent 会集中列出待确认事项。

内容修订回到详细大纲，确认后再同步页面与备注。制作阶段中的拆页、精简措辞和版式调整，
由 agent 在已确认内容和时长范围内完成。

讲者备注直接写在 TeX 的 `\note` 中。默认 `shownotes=false` 的 PDF 只含幻灯片；
设置 `shownotes=true` 可生成右侧带备注的 PDF，PPTX 在两种设置下都会保留讲者备注。
详见[原生讲者备注](docs/usage.md#原生讲者备注)。

PPTX 自动保留原生章节分节、标题与作者，以及副标题、课题组、指导教师、汇报日期等文档属性。

**PPTX 每页是一张渲染图像，文字不能作为 PowerPoint 原生文本编辑。**
请把修改意见交给 agent，或直接编辑生成的 `.tex` 源码。
`make` 负责已有源码的编译与转换；从思路到内容的写作由 agent 完成。

## 环境与功能示例

制作环境需要 **GNU Make、uv、XeLaTeX、latexmk、biber** 及模板的 TeX 包／字体。
可以使用本机的 TeX Live / MacTeX，或使用 [Docker 环境](docs/docker.md)；
详细安装步骤见[安装说明](docs/installation.md)。使用 `make doctor` 检查本地环境。
`uv run --frozen` 按 `uv.lock` 自动建立 `.venv`，首次下载 Python 依赖需要联网。

```bash
make doctor              # 检查环境
make draft MAIN=example  # 查看示例的逐页预览与排版报告
make MAIN=example        # 构建 build/example.pdf 和 build/example.pptx
make examples            # 构建清华和鹏城实验室主题 PDF 样例
make theme-previews      # 更新 README 预览图（从 600 DPI 开始，每张不超过 0.5 MiB）
make                     # 有 main.tex 时构建自己的汇报，否则构建 example.tex
```

[`example.tex`](example.tex) 是供人和 agent 查阅的功能演示，正文在 `examples/sections/`，
包含章节页、图像、公式、统一题注、引用、代码窗口、逐步显示、导航、视频与 TeX 备注。要直接查看完整 PDF/PPTX，请使用
[GitHub Releases](https://github.com/AnikiFan/campus-beamer/releases) 中的附件；agent 根据汇报目标挑选适合的版式，
另行生成你的内容。全部文档类选项及默认值也列在示例入口中，见[选项说明](docs/class-options.md)。

- 固定 16:9 布局，支持中英文；默认全主色章节页：general 为纯黑，清华为紫色，PCL 为蓝色。
- 完整目录可用 `\sectiontocpage[overview]` 统一展示章节；[简洁页面](docs/usage.md#简洁页面与图片背景)支持单行页眉、底行页脚及居中等比铺满的可调透明度图片背景。
- 自动适配图片、公式、论文讲解页及[终端风格代码窗口](docs/usage.md#代码与终端窗口)。
- `biblatex` / `biber` 文献管理，角落引用与已引用文献汇总；[网页来源引用](docs/usage.md#网页来源引用)同时显示来源名与实际 URL。可按需使用 [DBLP 与引用数工具](docs/literature.md)。
- PDF → PPTX 保留跳转、外部链接、本地视频与逐页备注；PDF 和 PPTX 的视频首帧预览需要 FFmpeg。
- [逐步显示与换页效果](docs/usage.md#逐步显示与换页效果)：按讲解顺序使用 overlays，PPTX 保留各阶段及明确设置的淡入／溶解切换。
- `make draft` 提供逐页预览和排版诊断，帮助 agent 精简、拆页并检查溢出。

<details>
<summary>查看引用与导航示例</summary>

![完整演示中的角落引用与章节导航](docs/images/citations.png)

</details>

`materials/` 用于个人素材，`build/` 保存构建产物。个人汇报源码、素材和备注默认仅保存在本地；
目录和分发规则见[使用手册](docs/usage.md#快速开始)。
VS Code、Overleaf 和命令行用法见[环境说明](docs/workflows.md)。

## 更换学校

内置 `general`（通用，默认）、`tsinghua`（清华）和 `pcl`（鹏城实验室）主题。
使用 `\documentclass[theme=pcl]{campusbeamer}` 切换，素材说明见[鹏城实验室主题](theme/pcl/README.md)。

复制 `theme/general/` 为 `theme/myschool/`，修改其中的 `profile.tex` 与素材，
然后使用 `\documentclass[theme=myschool]{campusbeamer}`。本地添加主题无需修改通用代码或登记名称。
详见[主题使用与扩展](theme/README.md)。

- 修改按功能命名的 `maincolor`、`tipcolor`、`notecolor`、`alertcolor`、`examplecolor`、`definitioncolor`。
- 页脚使用 `maincolor` 背景和白色文字。
- 封面采用主色斜边版式，颜色跟随 `maincolor`；显式设置为 `\titlebackground{primary}`。
- 将深色／浅色底上的校徽、校名标志路径指向自己的透明素材。

示例个人信息在 `examples/sections/metadata.tex`；自己的汇报信息由 agent 根据大纲写入 `sections/metadata.tex`。
照片和插图由各自的章节文件直接引用。
章节页默认用 `primary`，也可在正文中指定图片或 `white`。布局几何留在主题实现内；
配置字段和素材尺寸要求见[学校配置说明](docs/usage.md#更换学校)。

## 常用命令

```bash
make pdf                       # 编译 PDF，成功后自动清理 LaTeX 中间文件
make DPI=200                   # 较小的 PPTX，适合预览
make draft PAGES=3,8-10         # 局部页面排版检查
make test                      # Python 回归测试
make literature QUERY="论文标题" # 搜索 DBLP 候选
make bibtex DBLP_KEY=conf/...    # 下载单条 BibTeX 和引用次数到 build/literature/
make citations DOI=10.../...    # 查询引用次数、来源与日期
make check-theme               # 在隔离目录编译主题测试例
make dist                      # 生成可作为独立仓库使用的源码 ZIP
make version                   # 查看 pyproject.toml 中的项目版本
make release                   # 测试、构建演示并生成带校验和的版本化发行包
make clean                     # 手动清理失败构建留下的中间文件
make help                      # 查看全部入口
```

## 项目结构

```text
.
├── outline.md                  基本信息与自由草稿
├── example.tex                 版式与功能演示
├── main.tex                    agent 生成的汇报入口（本地文件）
├── materials/                  预置素材目录，放入的文件仅本地保留
├── sections/                   agent 生成的元信息与章节（本地文件）
├── examples/                   公共功能演示源码
│   ├── sections/               演示章节、片段与代码
│   └── bibliography/           演示文献数据库
├── theme/                      样式与学校配置
│   ├── campusbeamer.cls        文档类：语言、文献及通用配置入口
│   ├── beamerthemecampus.sty    主题版式与命令
│   ├── campuscode.sty          代码与终端窗口
│   ├── campuscolor.sty          学校主题加载器
│   ├── general/                 默认通用配色、博士帽和透明项目字标
│   ├── tsinghua/                清华配色、标志、素材及来源说明
│   └── pcl/                     鹏城实验室配色、标志、素材及来源说明
├── bibliography/               汇报文献数据库（本地文件）
├── assets/                     项目字标与原创示例视频
├── docs/                       详细手册、安装说明、环境用法与预览
├── docker/                     Dockerfile、构建上下文清单与容器入口
├── tools/                      转换、预览、校验与打包工具
│   ├── tests/                  Python 回归测试
│   └── fixtures/               主题测试源码
├── .github/                    CI、Issue 和 PR 模板
└── build/                      PDF、PPTX、备注渲染等构建产物
```

演示入口留在根目录，样式集中在 `theme/`；`.latexmkrc` 自动配置 TeX 搜索路径，
正文使用 `\documentclass{campusbeamer}`，从项目根目录运行 `make` 即可构建。
复制模板时保留 `theme/` 和 `.latexmkrc`。
GitHub Actions 读取仓库根目录下的 `.github/workflows/`。

## 参与改进

欢迎报告可复现的排版、转换和导航问题，也欢迎贡献文档及学校配置示例。
提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，附最小示例与必要日志；
不要把自己的完整汇报、私人备注或编译中间文件提交到源码仓库。

版本变化记录在 [CHANGELOG.md](CHANGELOG.md)。`make dist` 只收录
`tools/package_source.py` 中逐一登记的公开文件，新增文件默认不进入源码包。
`make release` 生成本地校验用的 `build/releases/campus-beamer-v<版本>-release.zip`。
GitHub Release 会将源码 ZIP、general 完整演示的 PDF/PPTX、清华与鹏城实验室主题的 PDF 样例、发行说明和 SHA-256 校验文件分别作为附件，
方便单独下载；始终构建 `example.tex`。GitHub 的 **Release Please** 工作流维护发行 PR，合并后创建 Release 并上传发行包，也保留手动构建入口；配置与发布步骤见
[发布指南](docs/releases.md)。

## 许可与素材

项目源码采用 **GPL-3.0-or-later**，见 [LICENSE](LICENSE)。各主题素材分别说明：

- **General**：原创博士帽、几何背景及项目字标排版源码采用 GPL-3.0-or-later；
  字标使用的 Latin Modern 字体保留 GUST Font License。见 [general 素材说明](theme/general/README.md)
  和[项目字标说明](assets/README.md#campus-beamer-项目字标)。
- **清华大学**：校徽、校名、组合标志及校园图像来自清华大学视觉形象识别系统和
  深圳国际研究生院官方图库，部分经过裁剪。来源、文件清单及使用声明见
  [清华主题说明](theme/tsinghua/README.md)。
- **鹏城实验室**：徽章来自深圳政府河套合作区网站；横向标志及园区图片来自鹏城实验室官网、
  美丽园区页面和人才招聘网站。派生素材包含裁切、格式转换及深色背景字标适配，见
  [PCL 主题说明](theme/pcl/README.md)。

清华及鹏城实验室的标志和图片涉及各自权利人的商标、著作权及其他权利，
仅供本模板的演示文稿用途，不适用项目 GPL 许可证；本项目不代表相关机构的授权或背书。
目前尚未取得这些机构素材的明确许可或核实逐张摄影者署名。
如有侵权、署名遗漏或来源标注问题，请通过 [xiaofan140@gmail.com](mailto:xiaofan140@gmail.com)
或本仓库 Issue 联系维护者；我们会核实并补充署名、更正说明、替换或移除相关素材。
联系声明不替代权利人许可；PDF、PPTX 及 README 预览中的素材适用各自同一声明。

原创演示视频 `assets/presentation_demo.mp4` 单独采用 **CC0-1.0**；
生成源码与授权说明见[素材清单](assets/README.md#原创演示视频)。

## 致谢

感谢以下项目的作者与贡献者：

- **构建环境**：[xu-cheng/latex-docker](https://github.com/xu-cheng/latex-docker)。
  本项目的 Docker 环境基于其预装 TeX Live 的 Debian 镜像，补充模板字体和 PDF/PPTX 工具。
- **工程实践**：[TongjiThesis 同济论文模板](https://github.com/TJ-CSCCG/TongjiThesis)。
  本项目参考了其文档类选项、文献配置入口、章节文件组织，以及 Make 构建、环境检查和
  命令行、VS Code、Overleaf、GitHub Actions 的使用说明，结合 Beamer 汇报流程独立实现。
- **视觉风格**：[THU-beamer-template](https://github.com/FangWHao/THU-beamer-template)
  和 [TongjiBeamer](https://github.com/Kian-Chen/TongjiBeamer)。本模板的风格在这两个项目的
  基础上改进，并根据本项目的排版与功能需求进一步调整。
- **早期模板来源**：[college-beamer](https://github.com/liu-qilong/college-beamer)
  和 Federico Zenith 创建的 [SINTEF Presentation](https://www.overleaf.com/latex/templates/sintef-presentation/jhbhdffczpnx)。
  本模板的早期基础可追溯到这两个项目；college-beamer 也明确注明其源自 SINTEF Presentation。
