# 鹏城实验室主题

[主题使用与扩展](../README.md) · [返回首页](../../README.md)

```tex
\documentclass[theme=pcl]{campusbeamer}
```

`profile.tex` 定义鹏城实验室主题的功能配色与标志路径。主色 `#1A569E`
取自下述徽章图像的蓝色外环；其余功能色为本模板的配套选择，不是官方 VI 色值规范。
版式沿用 Campus Beamer 的双行正文页眉、章节导航和固定页脚。

徽章在深浅背景上均保留原色。横向标志在浅色背景上使用透明 PNG，
深色封面使用带白色衬底的 PDF，保持原有蓝色文字可读，不重绘或重新着色标志。
园区图片由正文显式选用，例如：

```tex
\sectioncoverpage[theme/pcl/assets/20230726202103815.jpg]{本节导读}
```

## 素材与来源

### 徽章

- [`assets/emblem-source.png`](assets/emblem-source.png)：来自深圳政府
  [河套深港科技创新合作区「科创朋友圈」](https://htcz.sz.gov.cn/cxsj/kcpyq/)
  的鹏城实验室条目；[原图地址](http://htcz.sz.gov.cn/img/4/4252/4252313/11777001.png)。
  原始尺寸 1890×949，保留下载文件，核查日期为 2026-10-12。
- [`assets/emblem.pdf`](assets/emblem.pdf)：由 [`emblem.tex`](emblem.tex)
  将原图置于圆形裁切区域中，去除版面留边，内部图案和颜色保持原样。
  圆形外为透明区域，供深浅两种页眉背景共用。

### 横向标志与园区图片

下列六个原始文件由主题贡献者提供，保留原文件名及内容；未附逐项原始来源、
摄影者或再分发许可，不将其标记为本项目原创或 GPL 素材：

- [`c572737a-7108-43f0-930a-22a2c911464f.png`](assets/c572737a-7108-43f0-930a-22a2c911464f.png)：横向中英文组合标志；文件实际为 WebP。
- [`20221118002045758.jpg`](assets/20221118002045758.jpg)：园区整体鸟瞰效果图。
- [`20230726202103815.jpg`](assets/20230726202103815.jpg)：湖畔建筑鸟瞰效果图。
- [`20230726202115013.jpg`](assets/20230726202115013.jpg)：湖畔建筑效果图。
- [`c1cd6dd82a723a23.jpg`](assets/c1cd6dd82a723a23.jpg)：园区建筑群鸟瞰效果图。
- [`640+(4).jpg`](assets/640+(4).jpg)：园区庭院图片；文件实际为 WebP。

为兼容 XeLaTeX，两个 WebP 文件另提供无损 PNG 编码副本：
[`wordmark.png`](assets/wordmark.png) 和 [`campus-courtyard.png`](assets/campus-courtyard.png)。
它们保持解码后的像素、尺寸与透明度，不放大或重采样。
[`wordmark_on_dark.pdf`](assets/wordmark_on_dark.pdf) 由 [`wordmark.tex`](wordmark.tex)
为横向标志排版白色衬底。

## 重建派生素材

从仓库根目录运行。PNG 转码需要 ImageMagick；PDF 排版需要 XeLaTeX、
`standalone`、`tikz`、`graphicx` 和 `xcolor`。平时编译文稿直接使用随主题分发的文件。

```bash
mkdir -p build/pcl-assets
convert 'theme/pcl/assets/c572737a-7108-43f0-930a-22a2c911464f.png' theme/pcl/assets/wordmark.png
convert 'theme/pcl/assets/640+(4).jpg' theme/pcl/assets/campus-courtyard.png
xelatex -output-directory=build/pcl-assets theme/pcl/emblem.tex
xelatex -output-directory=build/pcl-assets theme/pcl/wordmark.tex
cp build/pcl-assets/emblem.pdf theme/pcl/assets/emblem.pdf
cp build/pcl-assets/wordmark.pdf theme/pcl/assets/wordmark_on_dark.pdf
```

## 权利说明

鹏城实验室名称、徽章与组合标志的相关权利归相应权利人所有；本主题不是官方模板，
不代表实验室认可或背书。园区图片的权利归原作者或相关权利人所有。
公开网页上的展示不等于授予修改或再分发许可，来源记录也不替代许可。
本仓库尚未核实上述素材的完整授权链；其原图和派生 PDF/PNG 不适用主题代码的 GPL 许可证。

如需更正来源、补充署名或处理权利问题，请联系
[xiaofan140@gmail.com](mailto:xiaofan140@gmail.com) 或在仓库提交 Issue，说明涉及的文件及原始来源。
