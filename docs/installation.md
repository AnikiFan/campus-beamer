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

## Mermaid 绘图（可选）

**仅在需要新建或修改 Mermaid 图时安装。** 编译已有图片、构建 PDF/PPTX 和 GitHub
发布不需要这组依赖；默认 `make` 不安装或调用 Mermaid。下面的命令适用于
Linux、macOS 或 WSL，并从仓库根目录执行。

### 准备 Node、浏览器与字体

通过 [Node.js 官方下载页](https://nodejs.org/en/download) 选择 **Node.js 24 LTS**
及对应平台的安装方式，安装包含 npm 的发行包，然后确认命令可用：

```bash
node --version
npm --version
```

复用本机已有的 Chrome/Chromium；若尚未安装，可从
[Chrome 官网](https://www.google.com/chrome/) 安装适合本机的版本，或使用系统软件包中的
Chromium。WSL 中请使用 Linux 浏览器及 Linux 版 Node/TeX。Linux 可先查找浏览器：

```bash
command -v google-chrome || command -v chromium || command -v chromium-browser
```

将实际可执行文件路径存入变量；下面是常见示例，按本机情况选择一行：

```bash
# Linux 示例；Chromium 的路径以 command -v 输出为准。
MERMAID_BROWSER=/usr/bin/google-chrome
# macOS 示例（使用此行替换上面的 Linux 路径）。
# MERMAID_BROWSER='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
"$MERMAID_BROWSER" --version
```

默认绘图字体复用前述 TeX 安装中的 Carlito 和 FandolHei；以下命令均应返回文件路径：

```bash
kpsewhich Carlito-Regular.ttf
kpsewhich Carlito-Bold.ttf
kpsewhich FandolHei-Regular.otf
kpsewhich FandolHei-Bold.otf
```

### 安装本地绘图运行时

将已测试的 CLI 与 Mermaid 引擎版本安装到被 Git 忽略的 `build/mermaid-runtime/`，
无需全局安装或 `sudo npm`。安装会联网下载 npm 包；通过
[`PUPPETEER_SKIP_DOWNLOAD`](https://pptr.dev/api/puppeteer.configuration)
跳过 Puppeteer 的浏览器下载，使用上一步准备的浏览器：

```bash
mkdir -p build/mermaid-runtime
PUPPETEER_SKIP_DOWNLOAD=true npm install --prefix build/mermaid-runtime --save-exact \
  @mermaid-js/mermaid-cli@11.12.0 mermaid@11.17.2
npm ls --prefix build/mermaid-runtime --depth=0
```

npm 会同时安装 CLI 所需的 Puppeteer。这组固定版本依赖 Puppeteer 23，安装时会出现
其已停止支持的弃用提示；这里保留已验证的兼容组合，升级时需一起验证 CLI、引擎与浏览器。
保留该目录中的 `package.json` 和
`package-lock.json`；它们与 `node_modules/` 都属于本地环境，不提交到公共模板。
需要按同一锁文件重建时运行：

```bash
PUPPETEER_SKIP_DOWNLOAD=true npm ci --prefix build/mermaid-runtime
```

手动删除整个 `build/` 时也会移除上述运行时。若希望独立保留，可将运行时放到
仓库外的固定目录，并同步修改安装命令的 `--prefix` 和渲染命令的 `--runtime`。

### 验证一次中文绘图

保持在设置 `MERMAID_BROWSER` 的同一终端中，创建测试图并调用仓库渲染脚本：

```bash
mkdir -p build/mermaid-check
cat > build/mermaid-check/check.mmd <<'EOF'
flowchart LR
  A[输入材料] --> B[处理模块]
  B --> C[结果检查]
EOF
node .agents/skills/campus-mermaid/scripts/render.mjs \
  --input build/mermaid-check/check.mmd \
  --output build/mermaid-check/check \
  --profile general \
  --runtime build/mermaid-runtime \
  --browser "$MERMAID_BROWSER"
```

成功后应生成 `check.pdf`、`check.svg`、`check.png` 和 `check.render.json`。
打开 PNG 确认中文、箭头和边界正常，并检查 JSON 中的 `actualFonts`、`warnings`
与文字 `clipped` 字段；命令成功仍需视觉检查。`make doctor` 不检查这组可选依赖。
渲染脚本使用本地资源，不下载包或访问在线绘图服务。

若提示找不到 `puppeteer` 或 Mermaid，检查 `--runtime` 是否指向包含 `node_modules/`
的目录；字体缺失时补齐 TeX 字体或使用脚本的 `--latin-font` / `--cjk-font` 参数。
浏览器启动失败时先核对路径和系统依赖，参见
[Puppeteer 故障排查](https://pptr.dev/troubleshooting)。默认保留浏览器沙箱，
`--no-sandbox` 仅供确实需要该选项的受控环境显式使用。
更多配色、字体覆盖与生成参数见
[Mermaid 渲染说明](../.agents/skills/campus-mermaid/references/rendering.md)。

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
