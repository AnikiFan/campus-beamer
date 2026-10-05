# 项目标志与示例素材

[返回首页](../README.md)

本目录保存项目字标和演示文稿的本地素材。校徽和校名标志路径在 `theme/campuscolor.sty` 配置；
照片、章节背景和普通插图直接在演示文稿中传入素材路径。
清华素材的官方来源与使用声明见下文，原创演示视频单独采用 CC0-1.0。
主题代码的 GPL 许可证不适用于清华校徽、校名标志和校园图像。

## Campus Beamer 项目字标

- [`campus-beamer-logo.svg`](campus-beamer-logo.svg)：透明背景的紫色字标，颜色为 `#552174`。
- [`campus-beamer-logo-white.svg`](campus-beamer-logo-white.svg)：透明背景的白色反白版，用于深色背景。
- [`campus-beamer-logo.tex`](campus-beamer-logo.tex)：可编辑的 LaTeX 排版源码，包含字号、升降量和字距。

字标使用 `Campus Beamer` 的完整文字，以 Latin Modern Roman 衬线字形排版。
`Campus` 的 A 缩小并上提，顶端与大写字母对齐；`Beamer` 的第一个 E 下沉，
呼应 TeX 字标的排版方式。两份 SVG 已将字形转为路径，缩放时保持清晰，显示时无需安装字体。
README 根据浅色／深色模式选择版本；项目字标不替代幻灯片中的学校校徽或校名标志。

在项目根目录执行 `make logo` 可重建两份 SVG，并在 `build/logo/` 中生成透明 PNG、
PDF 和双色背景预览 `preview.png`。生成使用 XeLaTeX、`standalone`、`fontspec`、
`xcolor`、Latin Modern 字体及已有的 PyMuPDF，无需新增 Python 依赖。

字体来源为 TeX 发行版中的 Latin Modern，作者为 Bogusław Jackowski 与 Janusz M. Nowacki，
基于 Donald E. Knuth 的 Computer Modern；字体版权为 © 2003–2021 B. Jackowski 和 J. M. Nowacki
（代表 TeX 用户组），采用 [GUST Font License](Latin-Modern.LICENSE.txt)。
字标的定制排版源码与 [`tools/generate_logo.py`](../tools/generate_logo.py) 采用项目的
GPL-3.0-or-later；字体自身的授权保持不变，不归入演示视频的 CC0 许可。

## 原创演示视频

- [`presentation_demo.mp4`](presentation_demo.mp4)：为本项目程序生成的“大纲 → 幻灯片 → 备注”动画。
  6 秒、640×360、24 fps、H.264 / yuv420p，无音轨，约 17 KB。
- 来源：仓库内的 [`tools/generate_demo_video.py`](../tools/generate_demo_video.py)。
  所有图形和字母均由脚本中的几何图元绘制，不使用第三方画面、图片、音乐、字体或校徽。
- 授权：**CC0-1.0**，具体声明见 [`presentation_demo.LICENSE.txt`](presentation_demo.LICENSE.txt)。
  [CC0 官方说明](https://creativecommons.org/publicdomain/zero/1.0/)允许复制、修改及再分发，包含商业用途。
  生成脚本本身仍采用项目的 GPL-3.0-or-later，不改变其他素材的授权。

在项目根目录重建视频（使用已有 PyMuPDF 与 FFmpeg，不增加依赖）：

```bash
uv run --frozen python tools/generate_demo_video.py
```

## 清华素材来源与使用声明

本项目分发的清华大学校徽、校名及组合标志图形，以及校园图像，来自
[清华大学视觉形象识别系统](https://vi.tsinghua.edu.cn/)和
[清华大学深圳国际研究生院官方图库](https://www.sigs.tsinghua.edu.cn/en/7453/list.htm)。
这些素材用于本模板的封面、页眉、致谢页、校园背景及版式演示。
上述来源由项目维护者确认；部分图像经过裁剪，以适应演示文稿的版式。
主题使用的校徽与校名标志以透明 PNG 保存，呈现时的背景色块由主题绘制。

**请注意：清华大学校徽、校名及相关标志涉及清华大学的注册商标与其他权利，
相关权利归清华大学及相应权利人所有。除本模板的演示文稿用途外，请勿将这些标志用于其他用途；
本声明不构成校方授权，也不表示本项目获得清华大学的认可或背书。**
使用标志时应遵循官方视觉形象规范；不得用于商业宣传或造成校方背书的误解。
商标背景可参阅清华大学校史馆的[校徽介绍](https://xsg.tsinghua.edu.cn/info/1003/1166.htm)
和[校名介绍](https://xsg.tsinghua.edu.cn/info/1003/2288.htm)。

校园图像的著作权归相应权利人所有，公开展示不等于开放许可。
本项目仅将其作为模板的校园背景及插图示例，不将其纳入 GPL 或 CC0 授权，
也不授予使用者独立提取、修改、商业使用或再分发这些图像的权利。
上述用途说明不能替代权利人的许可；需要许可的使用应另行取得许可。

### 文件清单

校徽与校名标志由 `theme/campuscolor.sty` 中的主题命令引用，文件名只表示功能，不写学校名。
`emblem` 为校徽，`wordmark` 为校名标志；
`on_dark` 是深色底上的白色图案，`on_light` 是浅色底上的彩色图案。
演示文稿直接引用的插图则按内容命名。

- [`emblem_on_dark.png`](emblem_on_dark.png)：深色底上的透明校徽，对应 `\schoolemblemondark`。
- [`emblem_on_light.png`](emblem_on_light.png)：浅色底上的透明校徽，对应 `\schoolemblemonlight`。
- [`wordmark_on_dark.png`](wordmark_on_dark.png)：深色底上的透明校名标志，对应 `\schoolwordmarkondark`。
- [`wordmark_on_light.png`](wordmark_on_light.png)：浅色底上的透明校名标志，对应 `\schoolwordmarkonlight`。
- [`sigs_wordmark.png`](sigs_wordmark.png)：完整演示中的清华大学深圳国际研究生院组合标志。

校园图像，官方来源为上述视觉形象识别系统及深圳国际研究生院图库：

- [`sigs_building.jpg`](sigs_building.jpg)：校园建筑照片。
- [`sigs_dom.jpg`](sigs_dom.jpg)：校园建筑照片。
- [`sigs_night.jpg`](sigs_night.jpg)：校园夜景照片。
- [`tsinghua_door.png`](tsinghua_door.png)：校门图像。
- [`tsinghua_door1.png`](tsinghua_door1.png)：校门图像。
  PNG 经无损重新编码，保留 2205×2476 尺寸、RGBA 像素及 ICC 颜色配置，约 3.08 MB。
- [`tsinghua_temple.png`](tsinghua_temple.png)：校园建筑图像。

[`docs/images/cover.png`](../docs/images/cover.png)、
[`docs/images/citations.png`](../docs/images/citations.png) 和
`docs/images/preview-*.png` 从本项目 PDF 渲染而来，
其中的清华素材适用上述声明；缩略图用于 README 页面预览。

随仓库分发的 PNG 已进行无损编码优化，保留原尺寸、像素、透明度、ICC 颜色配置、
DPI 和已有元数据；其中 `tsinghua_door.png` 从约 11.12 MB 缩至 3.27 MB。
JPEG 仅优化无损熵编码并保留已有元数据，未重新量化图像；夜景图减少约 1.3 KB，
另外两张 JPEG 没有进一步缩小，保留原文件。

## 素材核查与权利人联系

截至 2026-10-05，随仓库分发的两份项目字标 SVG、11 个清华图像文件、10 张派生预览图和原创演示视频都有来源说明。
此外没有来源不明的图片、音视频或字体文件。源码采用 GPL-3.0-or-later；
主题文件中的作者声明和 README 致谢说明模板来源。

目前暂时无法联系到相关权利人或摄影者，尚未取得适用于本仓库分发的明确修改与再分发许可，
也未能核实校园照片的逐张摄影者署名。来源说明和下面的联系渠道用于处理权利与署名问题。

**如您认为本项目使用的素材侵犯了您的著作权、商标权或其他合法权益，或存在署名遗漏、
来源标注错误，请随时联系维护者。我们会及时核实，并根据具体情况补充署名、更正说明、
替换或移除相关素材及其派生预览。**

- 邮箱：[xiaofan140@gmail.com](mailto:xiaofan140@gmail.com)。
- 也可在本仓库提交 Issue；涉及个人信息或不宜公开的材料时请使用邮件。
- 请尽可能提供相关文件名、原始作品或来源链接、权利情况及希望采取的处理方式，方便定位和核实。

本联系与处理声明不替代权利人的许可，也不赋予使用者新的授权。
确认来源或生成源码 ZIP 不表示已取得素材许可；如后续收到许可或准确的作者信息，将在此更新。

新增素材时请同时提供原始作者、来源页面、许可证或书面许可、允许的修改与再分发范围及署名要求。
不要猜测作者或把学校公开展示误认为允许再分发。
