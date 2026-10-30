# @THEME@

使用 `\documentclass[theme=@THEME@]{campusbeamer}` 选择此主题。

此目录从 general 起步。提交前将这一段改为主题的视觉特点、适用场景与设计参考。
从仓库根目录运行 `make theme-preview THEME=@THEME@` 查看完整公开示例的 16:9 和 4:3 预览。

## 配色与素材

- `profile.tex`：主题色、正文色、提示框颜色与标志路径。
- `assets/`：深浅底标志、字标和示例背景；保留透明背景与原始纵横比。
- `demo-images.tex`：公开示例的配图；不改变用户汇报的正文图片。
- `emblem.tex`、`wordmark.tex`、`backdrop.tex`：起始素材的可编辑源码。

## 来源与使用范围

初始文件复用本项目 general 的原创图形与字标，原始声明保存在同目录的 `BASE_ASSETS.md`。
图形与排版源码采用 GPL-3.0-or-later，Latin Modern 字体保留 [GUST Font License](../../assets/Latin-Modern.LICENSE.txt)。
保留复用素材的来源；替换素材时同步更新本节，并移除不再使用的起始素材及源码。

为新增素材逐项写明文件名、作者或来源链接、修改方式、许可或授权状态。
尚未确认的部分请如实注明，不能把来源网址或联系声明当作已获授权。
涉及新字体时补充字体名称、获取方式与许可；代码许可不自动覆盖素材。
