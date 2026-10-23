# 鹏城实验室主题

[主题使用与扩展](../README.md) · [返回首页](../../README.md)

从 Release 源码包使用此主题前，在项目根目录运行 `make theme-assets THEME=pcl`，
下载该主题独立维护的最新版素材。已有素材时不联网；详见[安装说明](../../docs/installation.md#机构主题素材)。

```tex
\documentclass[theme=pcl]{campusbeamer}
```

`profile.tex` 定义鹏城实验室主题的功能配色与标志路径。主色 `#1A569E`
取自下述徽章图像的蓝色外环；其余功能色为本模板的配套选择，不是官方 VI 色值规范。
版式沿用 Campus Beamer 的双行正文页眉、章节导航和固定页脚。

徽章在深浅背景上均保留原色。横向标志在浅色背景上使用透明 PNG，
深色封面使用透明 PDF：左侧徽章保留原色，右侧中英文文字改为纯白，不加底色。
文字轮廓、尺寸、间距与原始透明度保持不变；该深色适配版本由本项目制作，不代表官方 VI 版本。
园区图片由正文显式选用，例如：

```tex
\sectioncoverpage[theme/pcl/assets/lakeside-aerial.jpg]{本节导读}
```

运行 `make pdf MAIN=example-pcl` 查看完整功能演示。三个主题共用同一份正文与逐页备注，
页面数量和顺序一致，仅配色、标志与配图随主题变化；Release 仅为 general 额外提供 PPTX。

根目录 README 会展示 PCL 主题完整示例的代表性页面；其中的机构素材适用下述声明。

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

本项目分发的横向标志与园区图片来自[鹏城实验室官网](https://www.pcl.ac.cn/index.html)、
[美丽园区](https://www.pcl.ac.cn/html/1018/)和
[人才招聘网站](https://hr.pcl.ac.cn/SU62b979a5bef57c0f6fb046d7/pb/index.html#/)；
上述来源由项目维护者确认。原始 WebP 文件保留不变；字标另提供供 XeLaTeX 使用的派生素材。
这些素材用于本模板的封面、页眉、园区背景及版式演示。

- [`wordmark-source.webp`](assets/wordmark-source.webp)：横向中英文组合标志，保留 WebP 原始编码。
- [`campus-aerial.jpg`](assets/campus-aerial.jpg)：园区整体鸟瞰效果图。
- [`lakeside-aerial.jpg`](assets/lakeside-aerial.jpg)：湖畔建筑鸟瞰效果图。
- [`lakeside-building.jpg`](assets/lakeside-building.jpg)：湖畔建筑效果图。
- [`campus-buildings-aerial.jpg`](assets/campus-buildings-aerial.jpg)：园区建筑群鸟瞰效果图。
- [`campus-courtyard.png`](assets/campus-courtyard.png)：当前示例使用的园区庭院图片。
- [`campus-courtyard-source.webp`](assets/campus-courtyard-source.webp)：另存的庭院 WebP 素材，保留原始编码。

当前 JPEG 已去除 EXIF/XMP 元数据但保留 ICC 色彩配置和原始 JPEG 图像数据；庭院 PNG
重新压缩了无损 IDAT 数据并保留 RGBA 像素、ICC 配置和分辨率信息。压缩前后逐像素核对一致，
因此不会改变示例页面的图像内容。

为兼容 XeLaTeX，字标另提供 [`wordmark.png`](assets/wordmark.png)。
它裁去原图左侧 94 像素、右侧 128 像素的透明留边，画布由 1108×224 变为 886×224，
保留图案像素与透明度，不重采样。封面沿用与清华主题相同的字标宽度和右下角锚点，保持纵横比。
当前园区图片由维护者更新；`campus-courtyard.png` 不再由早期 WebP 转码生成。
[`wordmark_on_dark.png`](assets/wordmark_on_dark.png) 由
[`recolor_pcl_wordmark.py`](../../tools/recolor_pcl_wordmark.py) 从 `wordmark.png` 精确改色：
先规范化左右透明边界，再以徽章与文字之间的透明间隔分区，只将右侧文字设为白色，
左侧徽章及整图 alpha 保持不变。
[`wordmark_on_dark.pdf`](assets/wordmark_on_dark.pdf) 由 [`wordmark.tex`](wordmark.tex)
直接嵌入此透明图像，不添加底色或留白框。

## 重建派生素材

从仓库根目录运行。PNG 转码需要 ImageMagick；PDF 排版需要 XeLaTeX、
`standalone`、`tikz`、`graphicx` 和 `xcolor`。精确改色脚本使用项目 Python 环境中的 Pillow。平时编译文稿直接使用随主题分发的文件。

```bash
mkdir -p build/pcl-assets
convert 'theme/pcl/assets/wordmark-source.webp' theme/pcl/assets/wordmark.png
xelatex -output-directory=build/pcl-assets theme/pcl/emblem.tex
uv run --frozen python tools/recolor_pcl_wordmark.py
xelatex -output-directory=build/pcl-assets theme/pcl/wordmark.tex
cp build/pcl-assets/emblem.pdf theme/pcl/assets/emblem.pdf
cp build/pcl-assets/wordmark.pdf theme/pcl/assets/wordmark_on_dark.pdf
```

## 素材使用声明

**鹏城实验室名称、徽章及组合标志的相关权利归鹏城实验室及相应权利人所有。
除本模板的演示文稿用途外，请勿将这些标志用于其他用途；本声明不构成实验室授权，
也不表示本项目获得鹏城实验室的认可或背书。**
使用标志时应遵循相关视觉形象规范，不得用于商业宣传或造成机构背书的误解。

园区图像的著作权归相应权利人所有，公开展示不等于开放许可。
本项目仅将其作为模板的园区背景及插图示例，不将其纳入 GPL 或 CC0 授权，
也不授予使用者独立提取、修改、商业使用或再分发这些图像的权利。
上述用途说明不能替代权利人的许可；需要许可的使用应另行取得许可。
派生 PDF/PNG、README 预览及 Release 样例中的鹏城素材适用相同声明。

## 素材核查与权利人联系

目前暂时无法联系到相关权利人或摄影者，尚未取得适用于本仓库分发的明确修改与再分发许可，
也未能核实园区照片的逐张摄影者署名。来源说明和下面的联系渠道用于处理权利与署名问题。

**如您认为本项目使用的素材侵犯了您的著作权、商标权或其他合法权益，或存在署名遗漏、
来源标注错误，请随时联系维护者。我们会及时核实，并根据具体情况补充署名、更正说明、
替换或移除相关素材及其派生预览。**

- 邮箱：[xiaofan140@gmail.com](mailto:xiaofan140@gmail.com)。
- 也可在本仓库提交 Issue；涉及个人信息或不宜公开的材料时请使用邮件。
- 请尽可能提供相关文件名、原始作品或来源链接、权利情况及希望采取的处理方式，方便定位和核实。

本联系与处理声明不替代权利人的许可，也不赋予使用者新的授权。
确认来源或生成源码 ZIP 不表示已取得素材许可；如后续收到许可或准确的作者信息，将在此更新。
