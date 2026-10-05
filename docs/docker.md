# Docker 构建环境

[首页](../README.md) · [安装说明](installation.md) · [使用手册](usage.md)

`docker/Dockerfile` 构建一个专用于本项目的环境镜像，包含 GNU Make、
XeLaTeX、latexmk、biber、中文与模板字体、Python、uv 和用于视频预览的 FFmpeg。
只安装项目使用的 TeX 软件包集合，不安装整个 `texlive-full`。
额外字体包较大，首次构建需要下载系统和 Python 依赖。
宿主机只需安装并运行 Docker，无需另外安装 TeX 或 uv。

镜像内不包含汇报源码、学校图片或视频。运行时挂载项目，输出仍在项目的 `build/`。

## 构建镜像

在包含 `Makefile` 的项目根目录运行，以整个项目根目录为构建上下文：

```bash
docker build -f docker/Dockerfile -t campus-beamer:local .
```

构建时使用 Ubuntu 24.04 和固定版本的 uv，按照 `uv.lock` 安装 Python 依赖，
并运行项目的环境检查和 Python 导入检查；缺少必要工具、TeX 包或字体时构建失败。
`docker/Dockerfile.dockerignore` 使用 Dockerfile 专用命名，只允许构建所需的依赖文件和
辅助工具进入上下文，排除私人汇报、素材、`.venv` 和已有产物；无需在顶层放 `.dockerignore`。
`docker/entrypoint.sh` 是容器入口。`COPY` 的源路径相对于项目根目录，
因此不要用 `docker build docker/` 替代上述命令。

## 编译与导出

Linux、macOS 或 WSL 中运行以下命令：

```bash
docker run --rm \
  --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$(pwd),dst=/workspace" \
  campus-beamer:local
```

默认命令就是 `make`：有 agent 生成的 `main.tex` 时输出 `build/main.pdf` 和 `build/main.pptx`，
否则输出功能示例的 `build/example.pdf` 和 `build/example.pptx`。保留链接、视频和备注。
思路与素材交给 agent 完成写作，容器负责编译和转换，不调用模型。
agent 生成的备注放在挂载项目的 `build/main.notes.json`，构建会自动读取；
镜像和源码包不包含这些生成产物，首次制作新汇报时按最终页序生成备注。
使用宿主机 UID/GID，避免 Linux 下产生属于 root 的文件；挂载目录必须对当前用户可写。
Windows 建议在 WSL 中执行这些命令。
镜像默认使用 UTC。如果汇报中的 `\today` 需要本地日期，在 `docker run` 中加入
`-e TZ=Asia/Singapore` 等时区设置。

把命令追加在镜像名后面，即可运行其他构建目标：

```bash
docker run --rm --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$(pwd),dst=/workspace" \
  campus-beamer:local make draft

docker run --rm --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$(pwd),dst=/workspace" \
  campus-beamer:local make MAIN=example DPI=200

docker run --rm --user "$(id -u):$(id -g)" \
  --mount "type=bind,src=$(pwd),dst=/workspace" \
  campus-beamer:local make doctor
```

也可使用 `make test`、`make check-theme`、`make clean` 或文献检索目标。
预览位于宿主机的 `build/draft/<入口名>/index.html`，直接用浏览器打开。
编译和 PDF/PPTX 转换使用镜像内预装依赖，可在镜像构建后离线运行；
DBLP 和引用次数检索仍需要网络。

## 依赖与字体

容器的 Python 环境在 `/opt/campus-venv`，不使用或修改宿主机的 `.venv`。
入口会检查挂载项目的 `pyproject.toml` 和 `uv.lock` 是否与镜像一致；
修改依赖后，先更新锁文件，再重新运行 `docker build`。
日常修改 `.tex`、学校配置、素材或备注后无需重建镜像。

容器预装默认 Fandol、Caladea 和 Carlito 字体。自定义系统字体需要在 `docker/Dockerfile` 中
安装对应字体包，或将字体文件作为本地素材提供，并在汇报中按文件路径加载。
不指定 CPU 架构时，Docker 默认为当前主机选择镜像；不需要强制模拟 amd64。

实现方式参考 [uv 官方 Docker 指南](https://docs.astral.sh/uv/guides/integration/docker/)
和 [Docker 容器运行文档](https://docs.docker.com/engine/containers/run/)。
Dockerfile 专用忽略文件的命名与上下文规则见 [Docker 构建上下文文档](https://docs.docker.com/build/concepts/context/#dockerignore-files)。
