#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render the shared feature-tour pages for every public theme sample."""
from __future__ import annotations

import argparse
from io import BytesIO
import math
import re
from pathlib import Path

import pymupdf
from PIL import Image


MAX_PREVIEW_BYTES = 512 * 1024
MIN_PREVIEW_DPI = 150


# Physical PDF pages, in presentation order. Closing remains the final page.
GALLERY = (
    ('cover', 1, '封面', 'Cover', 'Campus Beamer 模板'),
    ('toc', 2, '目录页', 'Contents', '目录'),
    ('focus', 4, '简洁页面', 'Focus page', '简洁页面'),
    ('background', 5, '居中图片背景', 'Centered image background', '居中图片背景'),
    ('flow', 6, '对齐流程图', 'Aligned flowchart', '流程图布局'),
    ('layout', 11, '公式页', 'Equations', '行内公式与多行推导'),
    ('code', 13, '代码窗口页', 'Code window', '代码展示'),
    ('fullheight', 18, '右侧满高图片页', 'Full-height image', '右侧满高图片'),
    ('paper', 21, '论文讲解章节页', 'Paper section', '论文讲解与引用'),
    ('callouts', 33, '提示框页', 'Callouts', '提示、备注与警告'),
    ('overlays', 40, '逐步显示', 'Progressive reveal', '按讲述顺序呈现要点'),
    ('media', 46, '视频链接页', 'Video', '视频链接示例'),
    ('notes', 48, 'TeX 讲者备注', 'TeX speaker notes', '正文与备注分工'),
    ('references', 49, '参考文献页', 'References', '参考文献'),
    ('closing', 50, '致谢页', 'Closing', 'Campus Beamer 模板'),
)

THEMES = (
    ('general', 'General 通用主题', 'General (default)'),
    ('tsinghua', '清华大学（tsinghua）', 'Tsinghua (tsinghua)'),
    ('pcl', '鹏城实验室（pcl）', 'Peng Cheng Laboratory (pcl)'),
)

LEGACY_PREVIEWS = tuple(
    [f'preview-{name}.png' for name, *_ in GALLERY]
    + [f'theme-{theme}-{label}.png' for theme, *_ in THEMES for label in ('cover', 'section', 'body')]
)


def validate_samples(paths: list[Path]) -> None:
    """Reject mismatched pagination, navigation or preview anchors before rendering."""
    reference = None
    for path in paths:
        with pymupdf.open(path) as document:
            signature = (len(document), document.get_toc(),
                         document.metadata.get('title'), document.metadata.get('author'))
            if reference is not None and signature != reference:
                raise ValueError(f'{path}: theme samples must share page count, sections and metadata')
            reference = signature
            if len(document) != GALLERY[-1][1]:
                raise ValueError(f'{path}: update gallery page numbers for the new demo length')
            for _, number, _, _, anchor in GALLERY:
                if anchor not in document[number - 1].get_text():
                    raise ValueError(f'{path}: gallery anchor {anchor!r} is not on page {number}')


def gallery_markup(english: bool = False) -> str:
    lines = ['<!-- demo-gallery:start -->', '']
    for theme, chinese_theme, english_theme in THEMES:
        lines.append(f'### {english_theme if english else chinese_theme}')
        lines.append('')
        lines.append('<div align="center">')
        for start in range(0, len(GALLERY), 4):
            lines.append('  <p>')
            for name, _, chinese, english_label, _ in GALLERY[start:start + 4]:
                label = english_label if english else chinese
                lines.append(f'    <img src="docs/images/preview-{theme}-{name}.png" alt="{label}" width="200">')
            lines.append('  </p>')
        lines.append('</div>')
        lines.append('')
    lines.append('<!-- demo-gallery:end -->')
    return '\n'.join(lines)


def save_preview(page: pymupdf.Page, destination: Path, dpi: int,
                 max_bytes: int = MAX_PREVIEW_BYTES) -> None:
    """Keep small PNGs intact; rerender large pages within a byte budget."""
    if dpi < MIN_PREVIEW_DPI or max_bytes <= 0:
        raise ValueError('Preview DPI must be at least 150 and byte limit must be positive.')
    render_dpi = dpi
    while True:
        data = page.get_pixmap(dpi=render_dpi, alpha=False).tobytes('png')
        if len(data) > max_bytes and render_dpi == MIN_PREVIEW_DPI:
            # Preserve the minimum readable resolution. First optimize PNG
            # losslessly; use a palette only for photos still above the budget.
            with Image.open(BytesIO(data)) as image:
                optimized = BytesIO()
                image.save(optimized, format='PNG', optimize=True, dpi=(render_dpi, render_dpi))
                data = optimized.getvalue()
                if len(data) > max_bytes:
                    optimized = BytesIO()
                    image.quantize(colors=256).save(optimized, format='PNG', optimize=True,
                                                    dpi=(render_dpi, render_dpi))
                    data = optimized.getvalue()
                    print(f'{destination.name}: using a 256-color preview at {render_dpi} DPI')
        if len(data) <= max_bytes:
            destination.write_bytes(data)
            if render_dpi != dpi:
                print(f'{destination.name}: {len(data) / 1024:.0f} KiB at {render_dpi} DPI')
            return
        if render_dpi == MIN_PREVIEW_DPI:
            raise ValueError(f'{destination.name}: cannot fit {max_bytes} bytes at '
                             f'{MIN_PREVIEW_DPI} DPI; simplify the preview image.')
        # Pixel count scales quadratically. Leave room for PNG compression
        # variability and always make progress, without sacrificing readability.
        scale = min(0.9, 0.9 * math.sqrt(max_bytes / len(data)))
        render_dpi = max(MIN_PREVIEW_DPI, int(render_dpi * scale))


def render_gallery(pdf: Path, theme: str, output: Path, dpi: int) -> None:
    with pymupdf.open(pdf) as document:
        for name, number, _, _, _ in GALLERY:
            save_preview(document[number - 1], output / f'preview-{theme}-{name}.png', dpi)
        if theme == 'general':
            save_preview(document[0], output / 'cover.png', dpi)
            save_preview(document[23], output / 'citations.png', dpi)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='append', required=True)
    parser.add_argument('--theme', action='append', required=True)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--update-readme', action='store_true')
    parser.add_argument('--english-pdf', type=Path,
                        help='Also render the English general cover for README.en.md')
    parser.add_argument('--output', type=Path, default=Path('docs/images'))
    parser.add_argument('--dpi', type=int, default=600,
                        help='Initial DPI (at least 600); large PNGs adapt down to 150 DPI to fit 0.5 MiB')
    args = parser.parse_args()
    if args.dpi < 600:
        raise ValueError('Preview DPI must be at least 600.')
    if len(args.pdf) != len(args.theme):
        parser.error('--pdf and --theme must be supplied in matching pairs')
    validate_samples([Path(pdf) for pdf in args.pdf])
    if args.check_only:
        print('Theme samples: shared page count, sections, metadata and preview order verified.')
        return
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    for name in LEGACY_PREVIEWS:
        (output / name).unlink(missing_ok=True)
    for pdf, theme in zip(args.pdf, args.theme):
        if not Path(pdf).is_file():
            raise FileNotFoundError(pdf)
        render_gallery(Path(pdf), theme, output, args.dpi)
    if args.english_pdf:
        with pymupdf.open(args.english_pdf) as document:
            save_preview(document[0], output / 'preview-general-en-cover.png', args.dpi)
    if args.update_readme:
        root = Path(__file__).resolve().parents[1]
        for name, english in (('README.md', False), ('README.en.md', True)):
            path = root / name
            updated, count = re.subn(r'<!-- demo-gallery:start -->.*?<!-- demo-gallery:end -->',
                                     lambda _: gallery_markup(english), path.read_text(), flags=re.S)
            if count != 1:
                raise ValueError(f'{name}: expected exactly one demo gallery')
            path.write_text(updated)


if __name__ == '__main__':
    main()
