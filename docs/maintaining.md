# 维护者指南

[贡献主题](../CONTRIBUTING.md) · [主题配置](../theme/README.md) · [发布流程](releases.md)

本页用于接入已审阅的主题、修改通用代码和维护发布流程。主题贡献者先按[贡献指南](../CONTRIBUTING.md)准备主题目录与预览即可。

## 接入新主题

以下步骤由维护者完成，也欢迎熟悉仓库的贡献者协助。保留显式文件清单，不自动公开扫描到的文件。

1. 审阅 `theme/<名称>/` 的配色、素材、来源说明、字体依赖和 16:9 / 4:3 预览；确认新的公共文件适合分发。
2. 在 `tools/package_source.py` 的 `FILES` 中逐项登记配置、说明、可编辑素材源码及 `demo-images.tex`（如果提供）。非默认主题的 `assets/` 保持在独立素材包中；在 `tools/theme_assets.py` 的 `THEMES` / `ASSET_FILES` 登记素材，在 `.github/workflows/theme-assets.yml` 中添加路径触发条件与主题矩阵项。
3. 添加 `examples/example-<名称>.tex`、4:3 入口与 `theme/<名称>/sample.tex`，共用公开示例正文。配图优先留在主题的 `demo-images.tex`。将示例接入 Make 的 `examples`、`examples-43`、`theme-previews` 和 `tools/package_release.py` 的 `DEMO_FORMATS`。
4. 在 `tools/render_theme_previews.py` 的 `THEMES` 注册图库项，并将预览图加入源码清单。运行 `make theme-previews` 更新中英文图库，补充两份 README 的主题入口、素材说明和实际设计参考。
5. 为新增视觉行为添加 `tools/fixtures/` 检查例并接入 `tools/check_theme.py`；运行 `make test`、`make check-theme`、`make dist`。验证独立素材包、Overleaf 导入包和完整发行构建，操作见下文与[发布指南](releases.md)。

仅修改已有主题时，复用现有注册项；配色和素材变化不需要增加通用类选项。

## 修改代码

1. 先运行 `make test` 确认 Python 环境。
2. 修改通用逻辑时保留 `campus` 命名；学校品牌标志与功能配色放在 `theme/<名称>/profile.tex`，素材及来源声明保存在同目录，汇报图片直接在正文选择。
3. 对照 [AGENTS.md](../AGENTS.md) 保留固定版式、默认学校配置与页面可读性。
4. 转换器改动应增加能复现问题的测试；文档改动应检查命令与相对链接。
5. 公开文档面向首次使用项目的读者，说明当前功能、操作步骤和限制。修改过程、对话背景
   和临时排查记录放在提交说明或 Issue 中；中英文 README 保持一致。
   README 的核心读者是使用模板的人：保留帮助下载、安装、选择主题、制作或导出汇报的信息。
   预览图体积预算、渲染参数、文件白名单、内部实现约束、测试和发行维护步骤放在本维护指南
   或对应维护文档中，首页提供链接。审阅每段时检查它是否帮助读者理解功能、选择用法或完成操作。

```bash
make test
make check-theme
make draft MAIN=examples/example
make MAIN=examples/example
```

`make check-theme` 编译 `tools/fixtures/` 中的主题与文档类检查例，报告保存在 `build/theme-check/`。
它检查编译、预期页数、语言与字体锚点、可选宏包以及错误选项的诊断，不能代替肉眼检查。
修改主题后应检查全部演示页面、引用、PPTX 跳转和备注，参见[完整 draft 流程](usage.md#快速排版迭代draft)。

文档预览图每张不超过 **0.25 MiB（256 KiB）**，中英文图库合计不超过 **3 MiB**。
README 每个主题一行，用四列比较封面、章节页、正文页和致谢页，再用 general 展示六种公共功能。
英文 README 使用英文 general 图片，机构主题图片在中英文文档间共用。
生成器按屏幕显示尺寸直接从 PDF 渲染 PNG：普通缩略图宽 **640 px**，复用为 README 顶图的
中英文 general 封面宽 **1200 px**。超限时先无损优化，再降低分辨率，最低 **480 px**；
达到下限仍超限时尝试 256 色调色板，否则报错。检查照片色阶、文字边缘与点击放大的效果。
这项限制只用于 `docs/images/`，不改变主题原图或 PDF/PPTX 导出质量。
`make test` 检查图片体积、图库总预算、README 引用与源码打包清单。
`make theme-previews` 重建六套中文完整演示及英文 general 示例，更新全部预览和两个 README，
并移除已知的废弃预览文件；不再单独保存与 general 缩略图重复的顶图和引用示例图。
六套中文 PDF 的页数、章节和元信息必须一致；英文版保持同等功能覆盖与页序，并单独核对英文文本锚点。
预览页码、用途和中英文锚点维护在 `tools/render_theme_previews.py` 的 `MATRIX_PAGES` 与
`FEATURE_PAGES`。调整选页时同步维护显式源码打包清单；新增主题只需生成四种对比页。

纯重构需要比较前后 PDF。先保存基线，再使用
`uv run --frozen python tools/compare_pdf.py before.pdf build/example.pdf`；
需要逐字节一致时两次编译都固定 `SOURCE_DATE_EPOCH` 并加 `--strict-bytes`。
详情见[PDF 比较](usage.md#重构时校验-pdf)。

## 组织与提交

- 草稿入口 `outline.md` 保留在根目录，全部功能示例入口集中在 `examples/`；用户汇报由 agent 生成在 `main.tex` 与 `sections/`，文档类、主题、配色和学校配置统一放在 `theme/`，通过 `.latexmkrc` 配置搜索路径。
- 中文演示元信息、章节正文与可复用演示片段放在 `examples/sections/`，英文版放在 `examples/english/`；两者共用的示例代码源文件放在 `examples/sections/code/`。
- 用户文献数据库放在 `bibliography/`，中文公开演示文献放在 `examples/bibliography/`，英文版使用 `examples/english/refs.bib`；Dockerfile、构建上下文清单与容器入口放在 `docker/`。
- 手册与少量精选预览放在 `docs/`；测试源码放在 `tools/fixtures/`。
- 仓库级 skill 入口放在 `.agents/skills/`，描述明确触发任务，详细流程引用 `docs/agent-*.md`。
  风格偏好保留在可编辑的 `STYLE.md`；新增 skill 文件也须登记源码打包清单。
- 讲者备注与对应页面一起写在 TeX 的 `\note` 中；编译日志、PDF/PPTX、临时备注 PDF
  和图片保存在忽略的 `build/` 中。`docs/notes.example.json` 仅用于旧 JSON 导入接口示例。
- 新素材同时注明作者、来源和再分发许可；未知内容不要声明为 GPL。
- PR 描述应说明问题、变化、验证结果及剩余限制。实际借鉴的项目写入
  [README 最后一节的致谢](../README.md#致谢)，说明具体借鉴点，并同步英文 README。

源码贡献按现有 GPL-3.0-or-later 许可证提供；素材授权单独说明。

## CI 与发布资料

`.github/workflows/ci.yml` 在仓库根目录运行 Python 测试与源码打包检查。
涉及主题、工具、示例或构建配置时，还在 Docker 中运行 `make check-theme` 和公开示例的 PDF/PPTX 导出。
纯文档变更跳过该较慢的任务；手动触发时执行全部检查。本地通过不等于远程 CI 已通过。

`make dist` 生成 `build/dist/campus-beamer.zip`，只包含清单内的源码、文档、配置和示例素材。
除 general 外，所有 `theme/<名称>/assets/` 素材不进入该 ZIP，按主题分别维护最新版包；
general 素材、全部主题配置、可编辑素材源码、来源说明和文档预览图保留。
从源码包使用其他主题前运行 `make theme-assets THEME=undefined`，或将 `undefined` 换成所选主题名。
这份 ZIP 可以作为独立仓库的根目录；GitHub 只从仓库根目录读取 workflows。
不包含 `.venv`、生成的备注、构建产物，或未列入清单的根目录汇报；新增源码时同步更新打包清单。
`materials/`、`sections/` 和 `bibliography/` 仅打包各自的 `.gitkeep` 以保留写作目录；其中的用户内容及生成的 `main.tex` 不会被打包。
源码包公开文件逐一登记在 `tools/package_source.py` 的 `FILES` 白名单中，不递归收录目录中的新文件；
根目录 `outline.md` 是唯一的生成入口，由已登记的 `tools/templates/outline.md` 提供。
独立主题素材包使用 `tools/theme_assets.py` 的 `ASSET_FILES` 白名单，详见[素材发布流程](releases.md#每个主题独立维护最新版素材)。
新增文件默认不打包；审核其内容可公开后，再将路径加入白名单并运行 `make test`、`make dist`。
清单文件及其父目录不能是符号链接。已登记文件的内容仍需审核，白名单不代替隐私检查。
`outline.md` 是被 Git 忽略的用户草稿入口，克隆仓库后用 `make init` 创建，已有内容不会被覆盖。
源码包从 `tools/templates/outline.md` 提供起始模板，本地草稿保持原样；修改公共模板只需编辑该模板文件。
旧版本曾跟踪根目录大纲，升级前应先在仓库外备份已填写的内容，更新后恢复为本地文件。
agent 扩充后的详细大纲保存在忽略的 `build/outline-normalized.md`。公共提交应排除已填写的
私人大纲；其余白名单文件同样需要审核内容是否适合公开。
各机构素材的来源、使用范围和权利人联系方式见对应主题说明：
[清华](../theme/tsinghua/README.md)、[鹏城实验室](../theme/pcl/README.md)。
打包这些素材不表示已经取得授权。如有权利或署名问题，按该说明中的邮箱或本仓库 Issue 联系维护者。

## Overleaf 导入包维护

`make overleaf` 使用 `tools/package_overleaf.py` 从源码 `FILES` 白名单中选择公开演示依赖，
只收录所选语言、通用主题与所选主题的配置、素材和许可声明。生成根目录 `main.tex`，
使用 `tools/templates/overleaf-latexmkrc` 与 `overleaf-README.md`，不携带本地输出目录配置、
测试工具或私人汇报。视频链接在包内改为相对于根目录 PDF，仓库源文件保持原样。
缺失素材时通过现有下载器校验并暂存整份主题包，不混入本地不完整素材；该命令不上传任何文件。

修改后运行 `make test`、`make dist`，并从独立目录解压生成的 Overleaf ZIP，用
`latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex` 检查入口、文献及素材完整性。
本地验证不代表 Overleaf 在线编译或免费套餐时限已验证；发布说明应分别记录。

## 版本维护

版本号统一取自 `pyproject.toml`，使用 `make version` 查询；`uv.lock` 与版本保持同步。
提交和 squash 合并标题使用 Conventional Commits：`feat:` 为新功能，`fix:` 为修复，
`feat!:` 或正文中的 `BREAKING CHANGE:` 表示不兼容变化。
Release Please 根据这些提交维护版本、锁文件和 [CHANGELOG.md](../CHANGELOG.md)；
合并发行 PR 前检查版本变化、迁移说明及完整演示的视觉效果。
`make release` 运行测试、编译功能演示与全部内置主题样例，并生成包含源码 ZIP、中文 general PDF/PPTX、英文 general PDF、general 4:3 PDF、Tokyo Night、undefined、EVA PDF 和机构主题 PDF、
发行说明与校验和的版本化发行包。发行 PR 合并后，GitHub 工作流会自动构建并上传附件。
详细配置、令牌与手动重试入口见
[版本维护与发布](releases.md)。
