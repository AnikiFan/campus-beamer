# 参与贡献

[首页](README.md) · [English overview](README.en.md) · [使用手册](docs/usage.md)

欢迎修复可复现的问题、改善文档和增加有来源说明的学校配置示例。
项目目录可单独作为仓库根目录使用；所有命令从包含 `Makefile` 的目录运行。
编辑器和在线 PDF 编辑的配置方式见[环境用法](docs/workflows.md)。

## 报告问题

请提供操作系统、TeX 发行版、XeLaTeX / biber / uv 版本、执行命令和最小可复现的源码。
版式问题请附相关页面截图与日志片段；备注或链接问题请说明 PDF 页码、预期目标和实际行为。
本地依赖问题可附 `make doctor` 的相关输出；它能集中报告缺失工具、包和默认字体。
使用容器时附 Docker 版本、镜像构建命令与日志；用法见 [Docker 构建环境](docs/docker.md)。
不要附带整份私人汇报、账号凭据或与问题无关的个人资料。

## 修改代码

1. 先运行 `make test` 确认 Python 环境。
2. 修改通用逻辑时保留 `campus` 命名；学校品牌标志与功能配色放在 `theme/campuscolor.sty`，汇报图片直接在正文选择。
3. 对照 [AGENTS.md](AGENTS.md) 保留固定版式、默认学校配置与页面可读性。
4. 转换器改动应增加能复现问题的测试；文档改动应检查命令与相对链接。

```bash
make test
make check-theme
make draft MAIN=example
make MAIN=example
```

`make check-theme` 编译 `tools/fixtures/` 中的主题与文档类检查例，报告保存在 `build/theme-check/`。
它检查编译、预期页数、语言与字体锚点、可选宏包以及错误选项的诊断，不能代替肉眼检查。
修改主题后应检查全部演示页面、引用、PPTX 跳转和备注，参见[完整 draft 流程](docs/usage.md#快速排版迭代draft)。

README 的封面与引用截图从当前 `build/example.pdf` 以至少 **600 DPI** 直接渲染为 PNG，
并保留 DPI 元信息；更新后检查文字、角落引用和页脚的清晰度。

纯重构需要比较前后 PDF。先保存基线，再使用
`uv run --frozen python tools/compare_pdf.py before.pdf build/example.pdf`；
需要逐字节一致时两次编译都固定 `SOURCE_DATE_EPOCH` 并加 `--strict-bytes`。
详情见[PDF 比较](docs/usage.md#重构时校验-pdf)。

## 组织与提交

- 提示词 `prompt.md` 和功能示例 `example.tex` 保留在根目录；用户汇报由 agent 生成在 `main.tex` 与 `chapters/talk/`，文档类、主题、配色和学校配置统一放在 `theme/`，通过 `.latexmkrc` 配置搜索路径。
- 演示元信息、章节正文与可复用演示片段统一放在 `chapters/`；示例代码源文件放在 `chapters/code/`。
- 文献数据库放在 `bibliography/`，Dockerfile、构建上下文清单与容器入口放在 `docker/`。
- 手册与少量精选预览放在 `docs/`；测试源码放在 `tools/fixtures/`。
- 编译日志、PDF/PPTX、agent 生成的 `*.notes.json` 和临时图片保存在忽略的 `build/` 中；
  备注格式示例作为文档保留在 `docs/notes.example.json`。
- 新素材同时注明作者、来源和再分发许可；未知内容不要声明为 GPL。
- PR 描述应说明问题、变化、验证结果及剩余限制。实际借鉴的项目写入
  [README 最后一节的致谢](README.md#致谢)，说明具体借鉴点，并同步英文 README。

源码贡献按现有 GPL-3.0-or-later 许可证提供；素材授权单独说明。

## CI 与发布资料

`.github/workflows/ci.yml` 在仓库根目录运行 Python 测试与源码打包检查。
本地通过不等于远程 CI 已通过。主题编译验证需要 TeX 环境，使用 `make check-theme`。

`make dist` 生成 `build/dist/campus-beamer.zip`，只包含清单内的源码、文档、配置和示例素材。
这份 ZIP 可以作为独立仓库的根目录；GitHub 只从仓库根目录读取 workflows。
不包含 `.venv`、生成的备注、构建产物，或未列入清单的根目录汇报；新增源码时同步更新打包清单。
`materials/` 仅打包 `.gitkeep` 以保留目录；用户素材、生成的 `main.tex`、`chapters/talk/` 和 `bibliography/main.bib` 不会被打包。
所有公开文件逐一登记在 `tools/package_source.py` 的 `FILES` 白名单中，不递归收录目录中的新文件。
新增文件默认不打包；审核其内容可公开后，再将路径加入白名单并运行 `make test`、`make dist`。
清单文件及其父目录不能是符号链接。已登记文件的内容仍需审核，白名单不代替隐私检查。
`prompt.md` 与 `outline.md` 也随源码分发，发布前请保留通用流程和空白大纲。
填写后的私人大纲放入 `materials/outline.md`，规范化大纲放入 `build/outline-normalized.md`；
这两个目录中的私人文件不提交、不打包。白名单内的模板不要写入私人需求。
清华素材的来源、使用范围和权利人联系方式见 [assets/README.md](assets/README.md)。
打包这些素材不表示已经取得授权。如有权利或署名问题，按该说明中的邮箱或本仓库 Issue 联系维护者。

## 版本维护

版本号统一取自 `pyproject.toml`，使用 `make version` 查询；`uv.lock` 与版本保持同步。
提交和 squash 合并标题使用 Conventional Commits：`feat:` 为新功能，`fix:` 为修复，
`feat!:` 或正文中的 `BREAKING CHANGE:` 表示不兼容变化。
Release Please 根据这些提交维护版本、锁文件和 [CHANGELOG.md](CHANGELOG.md)；
合并发行 PR 前检查版本变化、迁移说明及完整演示的视觉效果。
`make release` 运行测试、编译公开演示，并生成包含源码 ZIP、演示 PDF/PPTX、
发行说明与校验和的版本化发行包。发行 PR 合并后，GitHub 工作流会自动构建并上传附件。
详细配置、令牌与手动重试入口见
[版本维护与发布](docs/releases.md)。
