# Changelog / 变更记录

本文件记录 Campus Beamer 的公开版本变化。版本号以 `pyproject.toml` 为准；
发布流程见 [docs/releases.md](docs/releases.md)。
This file tracks public releases. `pyproject.toml` is the version source of truth;
see [the release guide](docs/releases.md).

## [0.1.1](https://github.com/AnikiFan/campus-beamer/compare/v0.1.0...v0.1.1) (2026-10-05)


### Documentation

* improve previews and release downloads ([bc5fd26](https://github.com/AnikiFan/campus-beamer/commit/bc5fd26de0b7902142cad8b73a471cc31ccb9359))

## [Unreleased]

Release Please 根据 Conventional Commits 维护后续版本章节；此处可保留待确认的发行说明。
Release Please generates subsequent version sections from Conventional Commits;
use this section for release-note drafts that still need review.

## [0.1.0] - 2026-10-05

- 面向 agent 的 Beamer 汇报流程：本地素材、独立用户正文、逐页预览与讲解备注。
  Agent-oriented Beamer workflow with local materials, separate user sources,
  page previews and speaker notes.
- 中英文文档类、校园主题、角落引用、代码窗口、章节导航与媒体演示。
  Chinese/English document class, campus theme, corner citations, code windows,
  section navigation and media examples.
- PDF → 图像型 PPTX，保留链接、备注、原生分节、文档属性与本地视频。
  Image-based PDF-to-PPTX conversion preserving links, notes, native sections,
  document properties and embedded local video.
- 源码包采用逐文件白名单，排除未登记文件及符号链接路径。
  Explicit source-file allowlist; unlisted files and symlinked source paths are excluded.
- 示例图片与文档预览进行无损编码优化，保留尺寸、像素、透明度、颜色配置、DPI 和已有元数据。
  Lossless encoding optimization of demo images and documentation previews preserves
  dimensions, pixels, transparency, color profiles, DPI and existing metadata.
- 版本查询、带校验和的发行包、手动发行构建工作流，以及固定版本的 CI uv。
  Version query, checksummed release bundle, manual release-build workflow and pinned CI uv.
- Release Please 维护版本与变更记录；合并发行 PR 后自动构建并上传 GitHub Release 附件。
  Release Please maintains versions and changelogs; merging its release PR builds
  and uploads the GitHub Release bundle automatically.

## 许可与使用范围 / License and scope

源码采用 GPL-3.0-or-later；原创演示视频单独采用 CC0-1.0。
清华标志、校园图像及派生预览不适用这些许可证，尚未取得明确再分发许可；
来源、权利声明及联系渠道见 [assets/README.md](assets/README.md)。
PPTX 页面为渲染图像，文字不能作为原生 PowerPoint 文本编辑。

Source code uses GPL-3.0-or-later; the procedural demo video separately uses CC0-1.0.
Tsinghua marks, campus images and derived previews are not covered by these licenses;
explicit redistribution permission has not been obtained. Sources, rights notices and
contact details are in [assets/README.md](assets/README.md).
PPTX slides are rendered images, not editable native PowerPoint text.
