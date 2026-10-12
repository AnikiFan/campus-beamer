# 清华主题

[主题使用与扩展](../README.md) · [返回首页](../../README.md)

使用 `\documentclass[theme=tsinghua]{campusbeamer}` 选择此主题；省略 `theme` 时默认启用。
`profile.tex` 定义配色和品牌标志，`assets/` 保存校徽、校名及校园示例素材。

## 清华素材来源与使用声明

本项目分发的清华大学校徽、校名及组合标志图形，以及校园图像，来自
[清华大学视觉形象识别系统](https://vi.tsinghua.edu.cn/)和
[清华大学深圳国际研究生院官方图库](https://www.sigs.tsinghua.edu.cn/en/7453/list.htm)。
这些素材用于本模板的封面、页眉、致谢页、校园背景及版式演示。
上述来源由项目维护者确认；部分图像经过裁剪，以适应演示文稿的版式。
主题使用的校徽与校名标志以透明 PNG 保存，呈现时的背景色块由主题绘制。

两套 `wordmark_on_*.png` 由 [`wordmark.svg`](assets/wordmark.svg) 的完整复合路径渲染，
避免分段栅格化在笔画内部产生透明接缝。矢量路径提取自
[官方中文版手册](https://vi.tsinghua.edu.cn/download/VisualIdentity-cn.pdf)
第 30 页（A-3-10「校徽与横式中英文标准字左右组合」），保留官方字形与组合比例；
浅色版使用主题紫色 `#552174`，深色版使用白色。
执行 `uv run --frozen python tools/render_wordmarks.py` 可重建透明 PNG。
SVG 及其派生 PNG 均适用下述清华标志权利声明，不采用脚本的 GPL 许可证。

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

校徽与校名标志由 `theme/tsinghua/profile.tex` 中的主题命令引用，文件名只表示功能，不写学校名。
`emblem` 为校徽，`wordmark` 为校名标志；
`on_dark` 是深色底上的白色图案，`on_light` 是浅色底上的彩色图案。
演示文稿直接引用的插图则按内容命名。

- [`emblem_on_dark.png`](assets/emblem_on_dark.png)：深色底上的透明校徽，对应 `\schoolemblemondark`。
- [`emblem_on_light.png`](assets/emblem_on_light.png)：浅色底上的透明校徽，对应 `\schoolemblemonlight`。
- [`wordmark_on_dark.png`](assets/wordmark_on_dark.png)：深色底上的透明校名标志，对应 `\schoolwordmarkondark`。
- [`wordmark_on_light.png`](assets/wordmark_on_light.png)：浅色底上的透明校名标志，对应 `\schoolwordmarkonlight`。
- [`wordmark.svg`](assets/wordmark.svg)：上述两套校名标志的官方矢量路径源。
- [`sigs_wordmark.png`](assets/sigs_wordmark.png)：完整演示中的清华大学深圳国际研究生院组合标志。

校园图像，官方来源为上述视觉形象识别系统及深圳国际研究生院图库：

- [`sigs_building.jpg`](assets/sigs_building.jpg)：校园建筑照片。
- [`sigs_dom.jpg`](assets/sigs_dom.jpg)：校园建筑照片。
- [`sigs_night.jpg`](assets/sigs_night.jpg)：校园夜景照片。
- [`tsinghua_door.png`](assets/tsinghua_door.png)：校门图像。
- [`tsinghua_door1.png`](assets/tsinghua_door1.png)：校门图像。
  PNG 经无损重新编码，保留 2205×2476 尺寸、RGBA 像素及 ICC 颜色配置，约 3.08 MB。
- [`tsinghua_temple.png`](assets/tsinghua_temple.png)：校园建筑图像。

[`docs/images/cover.png`](../../docs/images/cover.png)、
[`docs/images/citations.png`](../../docs/images/citations.png) 和
`docs/images/preview-*.png` 来自当前示例 PPTX 转换后的幻灯片图像；视频预览页还合成了 PPTX 内嵌视频的首帧，
其中的清华素材适用上述声明；缩略图用于 README 页面预览。

随仓库分发的 PNG 已进行无损编码优化，保留原尺寸、像素、透明度、ICC 颜色配置、
DPI 和已有元数据；其中 `tsinghua_door.png` 从约 11.12 MB 缩至 3.27 MB。
JPEG 仅优化无损熵编码并保留已有元数据，未重新量化图像；夜景图减少约 1.3 KB，
另外两张 JPEG 没有进一步缩小，保留原文件。

## 素材核查与权利人联系

随仓库分发的项目字标、清华标志矢量源与图像、派生预览图和原创演示视频都有来源说明。
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
