# Changelog / 变更记录

本文件记录 Campus Beamer 的公开版本变化。版本号以 `pyproject.toml` 为准；
发布流程见 [docs/releases.md](docs/releases.md)。
This file tracks public releases. `pyproject.toml` is the version source of truth;
see [the release guide](docs/releases.md).

## [0.15.1](https://github.com/AnikiFan/campus-beamer/compare/v0.15.0...v0.15.1) (2026-10-22)


### Documentation

* define presentation-ready content and citation layout policies ([761e637](https://github.com/AnikiFan/campus-beamer/commit/761e637772848fcbffa73b64431591071826c89d))

## [0.15.0](https://github.com/AnikiFan/campus-beamer/compare/v0.14.0...v0.15.0) (2026-10-22)


### Features

* add Mermaid diagram skill with shared Campus styling ([d32fd3b](https://github.com/AnikiFan/campus-beamer/commit/d32fd3b3c7cea272aa87c46c840a5d5f2fe15d33))


### Bug Fixes

* cap documentation preview images at one MiB ([175fd3a](https://github.com/AnikiFan/campus-beamer/commit/175fd3a82f5f6cdee610c5bfa2264b8880c1dc93))
* increase emblem padding to 3.5pt ([1975193](https://github.com/AnikiFan/campus-beamer/commit/1975193ce18f7de5b5bcbb4f4bd431e6805ea8bf))
* size emblem block from Large and tiny baselines ([b094d63](https://github.com/AnikiFan/campus-beamer/commit/b094d63a80433c591a067255c859ca734e0f6e06))
* use Huge and tiny baselines for emblem block width ([6cbbf12](https://github.com/AnikiFan/campus-beamer/commit/6cbbf127b8645a2ee2da453505080be991a6ae02))

## [0.14.0](https://github.com/AnikiFan/campus-beamer/compare/v0.13.0...v0.14.0) (2026-10-13)


### Features

* refresh PCL imagery and trim wordmark ([fb0054c](https://github.com/AnikiFan/campus-beamer/commit/fb0054cabf8ff6882c1ac738e2a196306863e33d))


### Bug Fixes

* use updated section preview image mapping ([6500804](https://github.com/AnikiFan/campus-beamer/commit/6500804c39c239cc1ee119fa9dc8d8fb31d53b9d))

## [0.13.0](https://github.com/AnikiFan/campus-beamer/compare/v0.12.1...v0.13.0) (2026-10-13)


### Features

* assign distinct section images to Tsinghua demo ([b306516](https://github.com/AnikiFan/campus-beamer/commit/b306516cfae7436804d4a83b6dd2fc35a5a51db1))


### Bug Fixes

* align paper demo citations with top-right style ([8ae4aec](https://github.com/AnikiFan/campus-beamer/commit/8ae4aecf8e7af014068be0ff78760fcb18407bca))

## [0.12.1](https://github.com/AnikiFan/campus-beamer/compare/v0.12.0...v0.12.1) (2026-10-13)


### Documentation

* show complete examples for every theme ([bc36f83](https://github.com/AnikiFan/campus-beamer/commit/bc36f83d667d67d8484caf7c1a0833af3fcf2c04))

## [0.12.0](https://github.com/AnikiFan/campus-beamer/compare/v0.11.0...v0.12.0) (2026-10-13)


### Features

* unify theme samples and preview order ([8a558db](https://github.com/AnikiFan/campus-beamer/commit/8a558dba136b924eba1cd0c9a08324572573ec49))


### Bug Fixes

* install git in the release build container ([1d4d944](https://github.com/AnikiFan/campus-beamer/commit/1d4d944834ec503fade6cc4c72c49852918f8e9b))

## [0.11.0](https://github.com/AnikiFan/campus-beamer/compare/v0.10.0...v0.11.0) (2026-10-12)


### ⚠ BREAKING CHANGES

* separate public examples from user presentation sources
* the default theme is now general. Select theme=tsinghua explicitly to retain the previous default identity. Release bundles include PDF-only institution samples; local PPTX export remains available.

### Features

* make the black general theme the default ([ef4f72a](https://github.com/AnikiFan/campus-beamer/commit/ef4f72a606922c95a91f6e6d8eb5f6cd54fb0acb))
* publish previews and release samples for every bundled theme ([02dedab](https://github.com/AnikiFan/campus-beamer/commit/02dedab019f3ef569992f80a920130d0053ca608))


### Bug Fixes

* use monochrome branding and transparent PCL lettering ([a89bcd2](https://github.com/AnikiFan/campus-beamer/commit/a89bcd2598b5424b40dff07fb1d415f6c5f7107e))


### Code Refactoring

* separate public examples from user presentation sources ([9e67a38](https://github.com/AnikiFan/campus-beamer/commit/9e67a38df3aa4aa82eebb2d2bd342968c3e4c1b8))

## [0.10.0](https://github.com/AnikiFan/campus-beamer/compare/v0.9.0...v0.10.0) (2026-10-12)


### Features

* add Peng Cheng Laboratory theme ([c6557d6](https://github.com/AnikiFan/campus-beamer/commit/c6557d6bd7b57db653c5f2864c7838bb44f20a78))

## [0.9.0](https://github.com/AnikiFan/campus-beamer/compare/v0.8.0...v0.9.0) (2026-10-12)


### ⚠ BREAKING CHANGES

* school colors and branding move from theme/campuscolor.sty to theme/tsinghua/profile.tex. Direct Tsinghua asset references must move from assets/ to theme/tsinghua/assets/. School branding commands continue to resolve the selected profile automatically.

### Features

* add selectable school theme directories ([1ba1f08](https://github.com/AnikiFan/campus-beamer/commit/1ba1f085976629fc93bd500727285acfd6ea8901))

## [0.8.0](https://github.com/AnikiFan/campus-beamer/compare/v0.7.2...v0.8.0) (2026-10-11)


### Features

* add overview and image-background frame styles ([ee7978c](https://github.com/AnikiFan/campus-beamer/commit/ee7978cdf057ecbf9cba309f24e33c28d81ae1c7))

## [0.7.2](https://github.com/AnikiFan/campus-beamer/compare/v0.7.1...v0.7.2) (2026-10-10)


### Bug Fixes

* refresh public demo for overlays and native notes ([3014248](https://github.com/AnikiFan/campus-beamer/commit/30142483af2aad1f498614b1abf658a0bc0ddc7f))

## [0.7.1](https://github.com/AnikiFan/campus-beamer/compare/v0.7.0...v0.7.1) (2026-10-10)


### Bug Fixes

* unify code and video captions with figure styles ([f7f4c95](https://github.com/AnikiFan/campus-beamer/commit/f7f4c9528dbf6e1b25c855eccde10570e8bdd2e2))

## [0.7.0](https://github.com/AnikiFan/campus-beamer/compare/v0.6.1...v0.7.0) (2026-10-10)


### ⚠ BREAKING CHANGES

* Presentation sources now live in sections/; local talks use sections/talk/. Update source inputs, fixtures, packaging and documentation together. Authoring and validation invoke repository skills without capability fallback routes.

### Code Refactoring

* rename chapters to sections and use skills directly ([327e9c4](https://github.com/AnikiFan/campus-beamer/commit/327e9c4a33fde9443fffde79b723b06169407c11))

## [0.6.1](https://github.com/AnikiFan/campus-beamer/compare/v0.6.0...v0.6.1) (2026-10-10)


### Bug Fixes

* rebuild school wordmarks without raster seams ([b7af9e1](https://github.com/AnikiFan/campus-beamer/commit/b7af9e1a9f2c72a973fd0348d3a64c2e0a2fc25c))

## [0.6.0](https://github.com/AnikiFan/campus-beamer/compare/v0.5.0...v0.6.0) (2026-10-10)


### Features

* author speaker notes in TeX with optional PDF notes ([1a2e0ea](https://github.com/AnikiFan/campus-beamer/commit/1a2e0eae3db6b4d58cce2457f16ddd57890cfcb9))

## [0.5.0](https://github.com/AnikiFan/campus-beamer/compare/v0.4.4...v0.5.0) (2026-10-09)


### Features

* add repository authoring and validation skills ([cd540a4](https://github.com/AnikiFan/campus-beamer/commit/cd540a418b877df61f30418951d3616ea457bd17))
* preserve Beamer overlay transitions in PowerPoint ([3f6488e](https://github.com/AnikiFan/campus-beamer/commit/3f6488ec9bbb76dd2756af6dfb726ca80bbdbc05))
* unify web sources and strengthen authoring validation ([f2f5d75](https://github.com/AnikiFan/campus-beamer/commit/f2f5d751670d7395dd466916c0bda3760bbbd0a1))

## [0.4.4](https://github.com/AnikiFan/campus-beamer/compare/v0.4.3...v0.4.4) (2026-10-09)


### Bug Fixes

* develop section outlines before slide layout ([255399a](https://github.com/AnikiFan/campus-beamer/commit/255399a8d897c01c9bef49bbe698fe9265561e55))

## [0.4.3](https://github.com/AnikiFan/campus-beamer/compare/v0.4.2...v0.4.3) (2026-10-09)


### Bug Fixes

* clarify public documentation and restore outline template ([2244d01](https://github.com/AnikiFan/campus-beamer/commit/2244d019c50053817a9e331ded8bd895477c7bb6))

## [0.4.2](https://github.com/AnikiFan/campus-beamer/compare/v0.4.1...v0.4.2) (2026-10-09)


### Bug Fixes

* make root outline the direct presentation input ([9500b1a](https://github.com/AnikiFan/campus-beamer/commit/9500b1af1a597c9e57c05386d5f6df2f0869ff09))

## [0.4.1](https://github.com/AnikiFan/campus-beamer/compare/v0.4.0...v0.4.1) (2026-10-09)


### Bug Fixes

* restore code headers and require approved talk outlines ([0fcdbd6](https://github.com/AnikiFan/campus-beamer/commit/0fcdbd6252d42f8894ff45ea670298155df00982))

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
清华和鹏城实验室标志、校园／园区图像及派生预览不适用这些许可证，尚未取得明确再分发许可；
来源、权利声明及联系渠道见 [assets/README.md](assets/README.md)。
PPTX 页面为渲染图像，文字不能作为原生 PowerPoint 文本编辑。

Source code uses GPL-3.0-or-later; the procedural demo video separately uses CC0-1.0.
Tsinghua and Peng Cheng Laboratory marks, campus images and derived previews are not covered by these licenses;
explicit redistribution permission has not been obtained. Sources, rights notices and
contact details are in [assets/README.md](assets/README.md).
PPTX slides are rendered images, not editable native PowerPoint text.
