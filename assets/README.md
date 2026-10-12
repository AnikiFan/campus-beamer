# 项目标志与示例素材

[返回首页](../README.md)

本目录保存 Campus Beamer 项目字标和原创演示视频。学校配色、校徽、校名及校园素材
按学校集中存放在 `theme/<名称>/`；清华素材及完整的来源、权利和联系声明见
[清华主题](../theme/tsinghua/README.md)。原创演示视频单独采用 CC0-1.0。
主题代码的 GPL 许可证不适用于学校标志和校园图像。

## Campus Beamer 项目字标

- [`campus-beamer-logo.svg`](campus-beamer-logo.svg)：仿封面白左紫右的 16:9 项目标志，紫色为 `#552174`。
- [`campus-beamer-logo-white.svg`](campus-beamer-logo-white.svg)：深色 README 背景使用的同款分割标志，保留白左紫右面板。
- [`campus-beamer-logo.tex`](campus-beamer-logo.tex)：可编辑的 LaTeX 排版源码，包含封面斜线、字号、升降量和字距。

标志沿用封面的 61.8% 中点和 72° 斜线。画布由两个单词的可见字形外接矩形加四边相等的
12 pt padding 自动生成。`Campus` 保持自然字形；`Beamer` 放在紫色区域，第一个 E 和 M
采用等比例缩小并配合紧字距，同时把 M 向左上方微移。两份 SVG 已将字形转为路径，缩放时保持清晰，
显示时无需安装字体。项目字标不替代幻灯片中的学校校徽或校名标志。

在项目根目录执行 `make logo` 可重建两份 SVG，并在 `build/logo/` 中生成 PNG、
PDF 和双色背景预览 `preview.png`。生成依赖 XeLaTeX、`standalone`、`fontspec`、
`xcolor`、Latin Modern 字体及 PyMuPDF。

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

在项目根目录重建视频（需要 PyMuPDF 与 FFmpeg）：

```bash
uv run --frozen python tools/generate_demo_video.py
```
