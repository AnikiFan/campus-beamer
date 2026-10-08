# Changelog / 变更记录

本文件记录 Campus Beamer 的公开版本变化。版本号以 `pyproject.toml` 为准；
发布流程见 [docs/releases.md](docs/releases.md)。
This file tracks public releases. `pyproject.toml` is the version source of truth;
see [the release guide](docs/releases.md).

## [0.4.0](https://github.com/AnikiFan/campus-beamer/compare/v0.3.4...v0.4.0) (2026-10-08)


### Features

* move code captions outside listings and document visual rules ([a24468a](https://github.com/AnikiFan/campus-beamer/commit/a24468a731359141fec5501599b24840e94fc84b))

## [0.3.4](https://github.com/AnikiFan/campus-beamer/compare/v0.3.3...v0.3.4) (2026-10-08)


### Bug Fixes

* remove phantom TOC rows and define editable presentation style ([83bc358](https://github.com/AnikiFan/campus-beamer/commit/83bc358d40a6749c91463884afed743ba8dae8b7))

## [0.3.3](https://github.com/AnikiFan/campus-beamer/compare/v0.3.2...v0.3.3) (2026-10-08)


### Bug Fixes

* require two-line headers for authored body slides ([454312d](https://github.com/AnikiFan/campus-beamer/commit/454312dc5c33d5fbb388a10fdad21208040d0683))

## [0.3.2](https://github.com/AnikiFan/campus-beamer/compare/v0.3.1...v0.3.2) (2026-10-07)


### Bug Fixes

* normalize sample mmlab casing ([084322c](https://github.com/AnikiFan/campus-beamer/commit/084322c611dce6362b6289aeee678903c0dd7f45))

## [0.3.1](https://github.com/AnikiFan/campus-beamer/compare/v0.3.0...v0.3.1) (2026-10-07)


### Documentation

* streamline agent guidance ([2b8185e](https://github.com/AnikiFan/campus-beamer/commit/2b8185e82196ddff6e427c42809c57d7a69f3ae9))

## [0.3.0](https://github.com/AnikiFan/campus-beamer/compare/v0.2.4...v0.3.0) (2026-10-06)


### Features

* align Chinese presenter and advisor names ([97f0870](https://github.com/AnikiFan/campus-beamer/commit/97f0870d0cd0694d951e83bdd4e73a432c427b1e))

## [0.2.4](https://github.com/AnikiFan/campus-beamer/compare/v0.2.3...v0.2.4) (2026-10-06)


### Documentation

* highlight project identity and add README badges ([3433d7c](https://github.com/AnikiFan/campus-beamer/commit/3433d7ca7fac90521e0f787d75caade4e722cd1e))

## [0.2.3](https://github.com/AnikiFan/campus-beamer/compare/v0.2.2...v0.2.3) (2026-10-06)


### Bug Fixes

* enlarge demo video preview area ([fe8854d](https://github.com/AnikiFan/campus-beamer/commit/fe8854d4a12970aade5a5d2e8bf7158b1a6b032b))

## [0.2.2](https://github.com/AnikiFan/campus-beamer/compare/v0.2.1...v0.2.2) (2026-10-06)


### Bug Fixes

* simplify video previews and release source layout ([c945b3d](https://github.com/AnikiFan/campus-beamer/commit/c945b3d8b98678df98cbdaf9f6ed7bc9de59b792))

## [0.2.1](https://github.com/AnikiFan/campus-beamer/compare/v0.2.0...v0.2.1) (2026-10-05)


### Documentation

* add security and accessibility policies ([fd31928](https://github.com/AnikiFan/campus-beamer/commit/fd31928b87afbdf9cf1dfe9061cd38c225d0d5be))
* center README branding and preview grid ([74eef2f](https://github.com/AnikiFan/campus-beamer/commit/74eef2fffe7a9700e0d9bfe1c1458f2b246b3de6))

## [0.2.0](https://github.com/AnikiFan/campus-beamer/compare/v0.1.2...v0.2.0) (2026-10-05)


### Features

* add PDF video poster previews ([c836f71](https://github.com/AnikiFan/campus-beamer/commit/c836f71c0f4b22e0dad3bf8138583b1202b483d6))
* refresh branding and PPTX previews ([f2a5016](https://github.com/AnikiFan/campus-beamer/commit/f2a5016fa0816d922b8e1c2f047699b254929346))


### Bug Fixes

* handle rotated PDF video frames ([c9bed76](https://github.com/AnikiFan/campus-beamer/commit/c9bed76a30d2070476bbc440b6cacd9d59672f04))

## [0.1.2](https://github.com/AnikiFan/campus-beamer/compare/v0.1.1...v0.1.2) (2026-10-05)


### Bug Fixes

* include speaker notes in public demo builds ([085b1c7](https://github.com/AnikiFan/campus-beamer/commit/085b1c79eaebae2446e5878c48414bdcac10c92b))


### Documentation

* explain tracked demo speaker notes ([ff212e0](https://github.com/AnikiFan/campus-beamer/commit/ff212e0d94b4c3a9db55133d7b5f056671dc8b43))

## [0.1.1](https://github.com/AnikiFan/campus-beamer/compare/v0.1.0...v0.1.1) (2026-10-05)


### Documentation

* improve previews and release downloads ([bc5fd26](https://github.com/AnikiFan/campus-beamer/commit/bc5fd26de0b7902142cad8b73a471cc31ccb9359))

## [Unreleased]

Release Please 根据 Conventional Commits 维护后续版本章节；此处可保留待确认的发行说明。
Release Please generates subsequent version sections from Conventional Commits;
use this section for release-note drafts that still need review.

### Bug Fixes

- 视频海报现在填满 PDF 的链接区域，不再保留占位黑框。
  Video posters now fill the PDF link area without retaining a placeholder frame.

### Documentation

- 示例说明页归入第一个 section，避免封面后出现无 section 的页面。
  The example workflow page now belongs to the first section instead of sitting before all sections.
- 源码 ZIP 解压后直接得到项目根目录文件。
  Source ZIPs now unpack directly to the project root.

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
