# Tokyo Night 深色主题

[主题使用与扩展](../README.md) · [返回首页](../../README.md)

从 Release 源码包使用此主题前，在项目根目录运行 `make theme-assets THEME=tokyo-night`，
下载该主题独立维护的最新版素材。Git 克隆通常已包含素材。

`tokyo-night` 是与机构无关的深色主题，采用 Tokyo Night 的夜间配色，沿用 Campus Beamer
的默认 16:9（可选 4:3）版式、双行正文页眉、章节导航和固定页脚。

```tex
\documentclass[theme=tokyo-night]{campusbeamer}
```

```bash
make pdf MAIN=examples/example-tokyo-night
make draft MAIN=examples/example-tokyo-night
# 如需本地导出 PPTX：
make MAIN=examples/example-tokyo-night
```

完整功能演示在 `build/example-tokyo-night.pdf`，内容与中文 general 示例对应，共 51 页。
Release 仅包含 Tokyo Night 的 PDF。主题素材通过独立的最新版素材包提供。

## 配色

| 用途 | 色值 |
|---|---|
| 正文底色 | `#1A1B26` |
| 封面右侧、章节页与页脚 | `#24283B` |
| 正文与元信息 | `#C0CAF5` |
| 标题、链接和强调 | `#7AA2F7` |
| 引用与次要文字 | `#9AA5CE` |
| 代码关键字 | `#BB9AF7` |
| 提示 / 警告 / 示例 / 定义 | `#7DCFFF` / `#F7768E` / `#9ECE6A` / `#E0AF68` |

为适应投影阅读，正文、引用、代码注释和导航使用较亮的前景色；不照搬编辑器中刻意低对比度的 UI 文字。
普通页面和提示框使用深色底。封面保留对角分区，右侧为较亮的深蓝灰；默认章节页仍使用主题主色。
示例章节页右侧采用较亮的蓝紫色夜空、月亮与分层城市剪影，拉开与左侧深蓝灰背景的明暗差异，
保留清晰的斜切边界。左上角使用月牙与一颗星组成的简洁原创标志。
显式 `\sectioncoverpage[white]` 继续提供白色右侧区域。插入图片保留原始颜色，不自动反色。

## 素材与来源

- 配色参考 [Tokyo Night](https://github.com/tokyo-night/tokyo-night-vscode-theme)（Enkia），
  核验版本 [`7c0f11e`](https://github.com/tokyo-night/tokyo-night-vscode-theme/tree/7c0f11eaef322f293621ca7befe462214b7ea468)。
  原项目采用 MIT 许可，完整通知保存在 [Tokyo-Night.LICENSE.txt](Tokyo-Night.LICENSE.txt)。
- `emblem.tex`：本项目原创月牙与单颗星光标志，深色区域使用白色，正文底色区域使用蓝色。
  图形保留透明背景，按左上角实际显示尺寸简化细节。
- `backdrop.tex`：本项目用 TikZ 绘制的月夜城市插画，含月亮、远近城市剪影和水岸灯光；
  使用蓝紫色夜空与较亮的底部水岸强化章节页斜切边界。建筑为抽象几何造型，没有描摹具体地标。
- `wordmark.tex`：从 general 主题适配的项目字标。本目录独立保存上述源码和矢量 PDF，
  不含机构标志、城市照片或其他外部图片。
- 原创图形和 Beamer 适配代码遵循项目 GPL-3.0-or-later；字标使用 Latin Modern，字体许可见
  [GUST Font License](../../assets/Latin-Modern.LICENSE.txt)。本主题不是 Tokyo Night 上游官方发布的 Beamer 版本。

运行 `make tokyo-night-assets` 重建 `assets/` 中的五个 PDF。日常编译直接使用已提供的素材。
