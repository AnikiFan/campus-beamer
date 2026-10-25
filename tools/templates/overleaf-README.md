# Campus Beamer in Overleaf

## 中文

1. 在 Overleaf 选择 **New Project → Upload Project**，上传此 ZIP。
2. 在项目设置中选择 **Main document: main.tex**、**Compiler: XeLaTeX**。
3. 编译后修改 `main.tex` 中的选项，以及 `examples/sections/`（中文）或
   `examples/english/`（英文）中的标题、作者和正文。文献也放在 `examples/` 中。

包内已包含所选主题素材。比例可在 `main.tex` 中将 `169` 改为 `43`；
主题插图仍按 16:9 裁剪，未针对 4:3 单独优化。
完整示例较长，遇到编译超时可先在 `main.tex` 中注释暂不需要的章节。

此项目生成 PDF。视频保留为本地文件链接，不会在 Overleaf 预览器中播放，
也不会自动添加视频首帧。PPTX、视频嵌入和讲者备注导出使用完整仓库的本地工具。
需要导出时下载项目源码，并参照
[在线编辑与本地导出说明](https://github.com/AnikiFan/campus-beamer/blob/main/docs/workflows.md)。

源码许可见 `LICENSE`，素材来源与使用范围见 `theme/<主题>/README.md` 和 `assets/README.md`。

## English

1. Choose **New Project → Upload Project** in Overleaf and upload this ZIP.
2. Set **Main document: main.tex** and **Compiler: XeLaTeX** in project settings.
3. Compile, then edit the options in `main.tex` and the metadata and chapters in
   `examples/english/` (English) or `examples/sections/` (Chinese). Bibliographies
   also live under `examples/`.

The selected theme's assets are included. Change `169` to `43` in `main.tex` for
4:3 slides; illustrations are cropped for 16:9 and have no dedicated 4:3 crops.
If the complete demo exceeds your compile time limit, comment out unused chapter
inputs in `main.tex` while editing.

This project produces a PDF. Videos remain local file links; Overleaf's viewer
does not play them or automatically generate video posters. Download the edited
source and use the full repository's local tools for PPTX, embedded videos and
speaker notes; see the
[workflow guide](https://github.com/AnikiFan/campus-beamer/blob/main/docs/workflows.md).

See `LICENSE` for source licensing, and `theme/<theme>/README.md` and
`assets/README.md` for asset provenance and usage terms.
