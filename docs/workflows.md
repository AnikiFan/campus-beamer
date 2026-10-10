# 命令行、VS Code 与在线编辑

[首页](../README.md) · [安装说明](installation.md) · [完整手册](usage.md)

## 本地命令行

打开包含 `Makefile` 的项目目录，先运行 `make doctor`。它检查 PATH 中的默认工具、
关键 TeX 包和默认 Fandol 字体；无需先建立 `.venv`，不会下载或编译文件。
若系统只有 `python` 命令，可用 `make doctor PYTHON=python`，解释器需要 Python 3.10 或更新版本。
检查通过后可运行 `make MAIN=example` 验证编译与导出。
日常使用时，直接在根目录的 [`outline.md`](../outline.md) 写草稿，再对 agent 说
“根据大纲制作 PPT”。它会按 `AGENTS.md` 执行两阶段流程：

1. agent 读取 `AGENTS.md`、`STYLE.md`、用户草稿及提供的材料，扩充为按 section/subsection
   组织的详细内容，保存在 `build/outline-normalized.md`。在这一阶段审阅内容、解释、证据、
   来源、时间分配和待确认事项。
2. 确认后按详细大纲制作页面与备注，主要处理排版、页面划分和输出检查，再编译 PDF 并导出 PPTX。
   拆页和精简措辞可在已确认内容内直接完成；新增论点、例子或实质性解释回到大纲阶段。

原始草稿保留在根目录 `outline.md`，审阅副本和确认记录保存在 `build/`；不要用审阅副本覆盖原稿。
源码 ZIP 提供起始大纲模板；个人草稿、素材和确认记录仅保存在本地。
agent 在大纲阶段按演讲目标和提供的材料扩充内容；外部资料、新素材和事实修改集中确认。
页面与备注采用已确认的大纲内容。确认步骤由 agent 组织，命令行和编辑器负责编译。
检查不判断 biber / biblatex 的版本兼容，也不检查自定义系统字体和学校素材。
设置 `UV`、`LATEXMK` 等覆盖值时，应另外检查所指定的工具。

agent 生成 `main.tex` 后，使用 `make draft` 检查排版，再用 `make` 输出 PDF 和 PPTX。
没有用户入口时这两个命令选择 `example.tex`；显式 `MAIN=talk` 可构建其他入口。
PDF/PPTX 和编译临时文件统一写入 `build/`；成功后清理临时文件，失败时保留日志供诊断。
命令参数及备注要求见[完整手册](usage.md)。
样式位于 `theme/`，搜索路径由根目录的 `.latexmkrc` 自动配置；复制项目时保留两者。

## VS Code / LaTeX Workshop

用 **Open Folder** 打开包含 `Makefile` 的目录，确保 `.vscode/` 和 `Makefile` 在工作区根目录。
打开上一级目录不会自动加载这里的 VS Code 设置。安装推荐的 LaTeX Workshop 扩展，
并在 VS Code 终端中确认系统工具可用；Windows 推荐通过 WSL 打开项目。

- **快速查看 PDF**：打开 `example.tex`、agent 生成的 `main.tex` 或其他入口，在 TeX 面板中选择
  `Recipe: latexmk (xelatex)`。这个 recipe 将 PDF 和临时文件写入根目录下的 `build/`，成功后清理中间文件。
- **导出 PDF + PPTX**：使用 **Tasks: Run Build Task**，选择 `Campus: PDF + PPTX`，
  自动选择 `main.tex`（存在时）或 `example.tex`，执行同一 Make 工作流。
- **逐页预览**：使用 **Tasks: Run Task → Campus: draft preview**；成功后打开
  `build/draft/<入口名>/index.html`，检查全部页面和诊断报告。
- **功能演示**：使用 **Tasks: Run Task → Campus: reference example**，始终构建 `example.tex`。
- **环境排查**：使用 **Tasks: Run Task → Campus: environment check**。

模板命令补全由 `.vscode/settings.json` 提供。在 `.tex` 中输入 `@campus-` 查看代码片段。
上述 latexmk recipe 同样读取 `.latexmkrc`，无需在文档中额外添加主题路径。
编辑 `sections/` 中的章节或演示片段时，应编译引用它的入口；也可回到入口执行上述任务。
演示章节的 `% !TeX root = ../example.tex` 指向功能示例；agent 生成的章节应指向其汇报入口。
任务输出在终端中查看；编辑器按钮本身不会验证页面可读性或备注顺序。
任务格式依据 [VS Code 官方文档](https://code.visualstudio.com/docs/debugtest/tasks)，
recipe 机制见 [LaTeX Workshop 文档](https://github.com/James-Yu/LaTeX-Workshop/wiki/Compile)。

## Overleaf 中编辑 PDF

上传源码项目到 Overleaf 后，将需要编译的 `example.tex`、agent 生成的 `main.tex` 或其他入口
设为 **Main document**，编译器选 **XeLaTeX**。保持主题、配置、`assets/` 和汇报所用 `materials/` 的相对目录结构。
Overleaf 使用其自己的 TeX 环境，需要具备[安装说明](installation.md)中的包和字体。
本项目尚未在 Overleaf 实测；此处说明配置方式，不能视为在线兼容性保证。

在线编辑产生 PDF；本地构建会把视频首帧写入 PDF，PPTX、视频嵌入和备注写入由本项目的 Python 转换器完成。
导出 PPTX 时下载最新源码，保留 TeX 中的 `\note`、素材及文献相对路径，在具备本项目
构建环境的本地根目录运行：

```bash
make MAIN=talk
```

本地 Make 从 TeX 构建 PDF、渲染原生备注并导出 PPTX；默认 600 DPI，本地视频需要 FFmpeg。
仅下载普通 PDF 无法恢复未写入其中的隐藏备注。已有 JSON 备注可通过直接转换器的
`--notes` 参数导入。详细用法见[原生讲者备注](usage.md#原生讲者备注)。

## GitHub Actions

当前工作流检查 Python 测试和源码打包，不生成 PDF 或 PPTX。
工作流文件是仓库根目录下的 `.github/workflows/ci.yml`，在 push、pull request 或手动触发时运行。
应在仓库的 Actions 页面核实执行结果。
完整 TeX 编译与逐页检查使用本地 `make draft`、`make check-theme` 和 `make`。
