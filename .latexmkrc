# Campus Beamer: XeLaTeX build settings and theme search path.
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# xeCJK 仅支持 XeTeX；无论从何处调用 latexmk 都固定使用 xelatex。
$pdf_mode = 5;

# 文档类、主题与学校配置位于 theme/；保留已有搜索路径和 TeX 默认路径。
# 使用绝对路径，避免编译器切换到 build/ 后找不到主题。
use File::Spec;
ensure_path('TEXINPUTS', File::Spec->rel2abs('theme') . '//');

# PDF 与编译临时文件统一写入 build/；输入与素材仍相对于项目根目录。
$out_dir = 'build';

# Biber 生成的 .bbl 可由 bibliography/refs.bib 重建，因此允许 clean 阶段删除。
$bibtex_use = 2;

# 补充 latexmk 默认未覆盖的 Beamer、SyncTeX 和 biblatex 中间文件。
$clean_ext = 'nav snm vrb listing synctex synctex.gz %R-blx.bib';
