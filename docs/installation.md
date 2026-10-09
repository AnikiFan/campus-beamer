# 安装与故障排查

[返回首页](../README.md) · [完整手册](usage.md) · [编辑器与在线用法](workflows.md)

命令从项目根目录执行。`example.tex` 是功能演示；用户在根目录 `outline.md` 中写草稿并准备素材，
agent 新建 `main.tex` 完成汇报。
本项目需要 XeLaTeX；不支持用 pdfLaTeX 编译中文示例。
如希望免去本机 TeX 和 uv 安装，可使用 [Docker 构建环境](docker.md)。

## 系统依赖

需要 GNU Make、XeLaTeX、latexmk、biber、uv 和 Python 3.10 或更新版本。
推荐完整 TeX Live 或 MacTeX，包含中文字体、`biblatex`、IEEE 样式、TikZ、
`tcolorbox`、`listings`、`fontawesome5`、`xeCJK-listings`、Caladea 和 Carlito。
代码展示不需要 shell escape 或 Pygments。TeX 工具应来自同一套发行版，以免 biber 与 biblatex 版本不匹配。
本地视频的 PDF/PPTX 首帧预览和视频嵌入需要 FFmpeg；无视频的构建不需要它。

Debian / Ubuntu 的 TeX 依赖可用以下命令安装。`texlive-fonts-extra` 体积较大，
但提供本模板所需的 `caladea.sty` 和 `carlito.sty`，仅安装系统同名字体不足以替代它。

```bash
sudo apt-get update
sudo apt-get install make latexmk biber texlive-xetex texlive-latex-extra \
  texlive-bibtex-extra texlive-fonts-recommended texlive-fonts-extra texlive-lang-chinese ffmpeg
```

macOS 安装包含上述工具的 MacTeX 和 GNU Make。Windows 用户可在 WSL 中使用相同命令；
不在 WSL 的用户需自行提供兼容的 GNU Make、XeLaTeX 和 biber。
macOS 可用 `brew install ffmpeg` 安装视频工具；Windows/WSL 需确保 `ffmpeg` 在 PATH 中。

uv 的安装方式见 [uv 官方安装说明](https://docs.astral.sh/uv/getting-started/installation/)。
本项目不把系统 TeX 或 uv 安装器写入构建过程。

## 确认环境

先运行 `make doctor` 一次列出工具版本、关键 TeX 包和默认 Fandol 字体的查找结果。
有缺项时返回非零退出码；不安装软件，不创建 `.venv` 或编译中间文件。
需要可执行的 `python3`（或用 `PYTHON=python` 指定）。这些检查只覆盖默认 PATH 中的工具
与所列 TeX 文件，版本兼容性和完整编译仍需通过实际构建确认。
单独定位问题也可运行：

```bash
make --version
uv --version
xelatex --version
latexmk --version
biber --version
kpsewhich caladea.sty
kpsewhich carlito.sty
kpsewhich xeCJK.sty
```

`kpsewhich` 应输出实际文件路径。缺少命令或空输出时先安装对应组件。
`make` 使用 `uv run --frozen`，自动创建 `.venv` 并安装锁定的 Python 依赖；
不要从另一台机器复制 `.venv`。

仓库中的 `uv.lock` 使用官方 PyPI 索引和 `files.pythonhosted.org` 下载地址，
避免要求所有使用者访问某个地区的镜像。维护公共锁文件时，先排除本机额外索引
环境变量的影响，再运行：

```bash
uv lock --no-config --default-index https://pypi.org/simple
```

检查依赖版本与哈希变化，不要手工替换下载 URL。需要镜像的使用者可在本机配置，
但不要提交由个人镜像重新生成的锁文件。`--frozen` 会保留锁文件，单独配置镜像
不代表已替换其中的下载地址。

## 常见问题

- **`caladea.sty` / `carlito.sty` 找不到**：安装 TeX 的额外字体包，并确认 TeX 文件索引已更新。
- **中文字体提示**：默认示例由 xeCJK 使用 Fandol 字体。检查中文字体包是否齐备；
  `fontspec` 的 Script 提示与可见缺字不是同一问题，应检查实际页面。
- **引用未解析或 biber 报错**：查看 `build/` 中的 `.log` 和 `.blg`，确认条目键、`.bib` 内容及版本兼容。
  先保存诊断，再执行 `make clean` 后重新编译。不要手工修改 `.bbl` / `.bcf`。
- **编译或导出失败**：失败后留下的 PDF/PPTX 不是这次的结果，先检查退出码和日志。
- **备注数量不匹配**：每个最终 PDF 页面都要一条备注，空页用空字符串；包含 overlays 和续页。
- **uv 下载失败**：检查网络和 `uv.lock` 中的源。修改依赖后显式运行 `uv lock`，
  `--frozen` 不会自行更新锁文件。
- **PPTX 很大**：默认 600 DPI；预览时可用 `make DPI=200`，正式导出按需要恢复分辨率。
- **视频预览提取失败**：安装 FFmpeg，并确认 `ffmpeg -version` 可运行、源视频可以解码。
  转换器不会用空白预览替代失败的视频，也不会覆盖已有的 PPTX。
- **页脚或导航太挤**：优先缩短 section/subsection 导航名称；详情见[导航说明](usage.md#section-与小节导航)。

## 检查产物

```bash
make draft MAIN=example
make MAIN=example
make test
make check-theme
```

`make draft` 成功后，检查 `build/draft/example/index.html` 和 `report.txt`。
成功编译仍需逐页检查，不能用无告警替代视觉验证。
