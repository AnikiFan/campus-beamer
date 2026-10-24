#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render a compact theme matrix and shared feature previews for both READMEs."""
from __future__ import annotations

import argparse
from io import BytesIO
import math
import re
from pathlib import Path

import pymupdf
from PIL import Image


MAX_PREVIEW_BYTES = 256 * 1024
MAX_GALLERY_BYTES = 3 * 1024 * 1024
PREVIEW_WIDTH = 640
COVER_WIDTH = 1200
MIN_PREVIEW_WIDTH = 480

# Key, physical PDF page, Chinese/English labels, Chinese/English text anchors.
MATRIX_PAGES = (
    ('cover', 1, '封面', 'Cover', 'Campus Beamer 模板', 'Complete feature tour'),
    ('section', 21, '章节页', 'Section', '论文讲解与引用', 'Papers and citations'),
    ('body', 10, '正文页', 'Body', '三级内容结构', 'Three levels of structure'),
    ('closing', 50, '致谢页', 'Closing', '感谢倾听', 'Thank you for listening'),
)
FEATURE_PAGES = (
    ('flow', 6, '流程图', 'Flowcharts', '流程图布局', 'Aligned flowchart'),
    ('layout', 11, '公式', 'Equations', '行内公式与多行推导', 'Inline math and derivations'),
    ('code', 13, '代码', 'Code', '代码展示', 'Python code'),
    ('fullheight', 18, '图文混排', 'Text and images', '右侧满高图片', 'Full-height image'),
    ('citations', 24, '论文引用', 'Citations', '角落引用位置', 'Corner citation positions'),
    ('callouts', 33, '提示框', 'Callouts', '提示、备注与警告', 'Tips, notes and alerts'),
)
GALLERY = tuple(sorted(MATRIX_PAGES + FEATURE_PAGES, key=lambda item: item[1]))
THEMES = (
    ('general', '通用', 'General'),
    ('undefined', 'undefined', 'undefined'),
    ('tokyo-night', 'Tokyo Night', 'Tokyo Night'),
    ('tsinghua', '清华大学', 'Tsinghua'),
    ('pcl', '鹏城实验室', 'PCL'),
)

# Remove only known generated files retired by the compact gallery.
_OLD_KEYS = ('cover', 'toc', 'focus', 'background', 'flow', 'layout', 'code',
             'fullheight', 'paper', 'callouts', 'overlays', 'media', 'notes',
             'references', 'closing')
LEGACY_PREVIEWS = (
    'cover.png', 'citations.png',
    *(f'preview-{key}.png' for key in _OLD_KEYS),
    *(f'preview-{theme}-{key}.png' for theme, *_ in THEMES for key in _OLD_KEYS),
    *(f'theme-{theme}-{key}.png' for theme, *_ in THEMES
      for key in ('cover', 'section', 'body')),
)


def preview_names(theme: str) -> set[str]:
    pages = GALLERY if theme in ('general', 'general-en') else MATRIX_PAGES
    return {f'preview-{theme}-{key}.png' for key, *_ in pages}


def validate_samples(paths: list[Path], english_pdf: Path | None = None) -> None:
    """Check Chinese theme parity and localized gallery anchors before rendering."""
    reference = None
    for path in [*paths, *([english_pdf] if english_pdf else [])]:
        english = path == english_pdf
        with pymupdf.open(path) as document:
            signature = (len(document), document.get_toc(),
                         document.metadata.get('title'), document.metadata.get('author'))
            if not english:
                if reference is not None and signature != reference:
                    raise ValueError(f'{path}: theme samples must share page count, sections and metadata')
                reference = signature
            if len(document) != GALLERY[-1][1]:
                raise ValueError(f'{path}: update gallery page numbers for the new demo length')
            for _, number, _, _, chinese_anchor, english_anchor in GALLERY:
                anchor = english_anchor if english else chinese_anchor
                if anchor not in document[number - 1].get_text():
                    raise ValueError(f'{path}: gallery anchor {anchor!r} is not on page {number}')


def thumbnail(theme: str, key: str, label: str, width: int) -> str:
    path = f'docs/images/preview-{theme}-{key}.png'
    return f'<a href="{path}"><img src="{path}" alt="{label}" width="{width}"></a>'


def gallery_markup(english: bool = False) -> str:
    lines = ['<!-- demo-gallery:start -->', '', '<table>', '  <thead>', '    <tr>']
    lines.append(f'      <th nowrap>{"Theme" if english else "主题"}</th>')
    for _, _, chinese, translated, *_ in MATRIX_PAGES:
        lines.append(f'      <th nowrap>{translated if english else chinese}</th>')
    lines.extend(['    </tr>', '  </thead>', '  <tbody>'])
    for theme, chinese_theme, english_theme in THEMES:
        label = english_theme if english else chinese_theme
        image_theme = 'general-en' if english and theme == 'general' else theme
        lines.extend(['    <tr>',
                      f'      <th scope="row" nowrap><a href="theme/{theme}/README.md">{label}</a></th>'])
        for key, _, chinese, translated, *_ in MATRIX_PAGES:
            caption = translated if english else chinese
            lines.append(f'      <td nowrap>{thumbnail(image_theme, key, label + ": " + caption, 170)}</td>')
        lines.append('    </tr>')
    lines.extend(['  </tbody>', '</table>', '',
                  '### Shared features' if english else '### 公共功能精选', '',
                  'All themes share these features; the examples below use General.' if english
                  else '以下功能适用于全部主题，统一用 general 展示。', '', '<table>'])
    image_theme = 'general-en' if english else 'general'
    for start in range(0, len(FEATURE_PAGES), 3):
        row = FEATURE_PAGES[start:start + 3]
        lines.append('  <tr>')
        for _, _, chinese, translated, *_ in row:
            lines.append(f'    <th nowrap>{translated if english else chinese}</th>')
        lines.extend(['  </tr>', '  <tr>'])
        for key, _, chinese, translated, *_ in row:
            label = translated if english else chinese
            lines.append(f'    <td>{thumbnail(image_theme, key, label, 240)}</td>')
        lines.append('  </tr>')
    lines.extend(['</table>', '', '<!-- demo-gallery:end -->'])
    return '\n'.join(lines)


def save_preview(page: pymupdf.Page, destination: Path, width: int = PREVIEW_WIDTH,
                 max_bytes: int = MAX_PREVIEW_BYTES) -> None:
    """Render for screen display, preserving a pixel-width floor and a byte cap."""
    if width < MIN_PREVIEW_WIDTH or max_bytes <= 0:
        raise ValueError(f'Preview width must be at least {MIN_PREVIEW_WIDTH} pixels; budget must be positive.')
    render_width = width
    while True:
        scale = render_width / page.rect.width
        pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
        data = pixmap.tobytes('png')
        if len(data) > max_bytes:
            with Image.open(BytesIO(data)) as image:
                optimized = BytesIO()
                image.save(optimized, format='PNG', optimize=True)
                data = optimized.getvalue()
                if len(data) > max_bytes and render_width == MIN_PREVIEW_WIDTH:
                    optimized = BytesIO()
                    image.quantize(colors=256).save(optimized, format='PNG', optimize=True)
                    data = optimized.getvalue()
                    print(f'{destination.name}: using a 256-color preview at {render_width}px')
        if len(data) <= max_bytes:
            destination.write_bytes(data)
            return
        if render_width == MIN_PREVIEW_WIDTH:
            raise ValueError(f'{destination.name}: cannot fit {max_bytes} bytes at '
                             f'{MIN_PREVIEW_WIDTH}px; simplify the preview image.')
        scale = min(0.9, 0.9 * math.sqrt(max_bytes / len(data)))
        render_width = max(MIN_PREVIEW_WIDTH, int(render_width * scale))


def render_gallery(pdf: Path, theme: str, output: Path, width: int = PREVIEW_WIDTH) -> None:
    pages = GALLERY if theme in ('general', 'general-en') else MATRIX_PAGES
    with pymupdf.open(pdf) as document:
        for key, number, *_ in pages:
            # The general covers are reused as the README hero images.
            pixels = max(width, COVER_WIDTH) if key == 'cover' and theme in ('general', 'general-en') else width
            save_preview(document[number - 1], output / f'preview-{theme}-{key}.png', pixels)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='append', required=True, type=Path)
    parser.add_argument('--theme', action='append', required=True, choices=[item[0] for item in THEMES])
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--update-readme', action='store_true')
    parser.add_argument('--english-pdf', type=Path, help='English general PDF for README.en.md')
    parser.add_argument('--output', type=Path, default=Path('docs/images'))
    parser.add_argument('--width', type=int, default=PREVIEW_WIDTH,
                        help='Starting thumbnail width in pixels (default: 640; minimum: 480)')
    args = parser.parse_args()
    if args.width < MIN_PREVIEW_WIDTH:
        parser.error(f'--width must be at least {MIN_PREVIEW_WIDTH}')
    if len(args.pdf) != len(args.theme) or len(set(args.theme)) != len(args.theme):
        parser.error('--pdf and --theme must be supplied in unique matching pairs')
    if args.update_readme and (set(args.theme) != {item[0] for item in THEMES} or not args.english_pdf):
        parser.error('--update-readme requires all built-in themes and --english-pdf')
    validate_samples(args.pdf, args.english_pdf)
    if args.check_only:
        print('Theme samples: shared Chinese metadata and localized preview anchors verified.')
        return
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    for pdf, theme in zip(args.pdf, args.theme):
        render_gallery(pdf, theme, output, args.width)
    if args.english_pdf:
        render_gallery(args.english_pdf, 'general-en', output, args.width)
    current = set().union(*(preview_names(theme) for theme in [*(item[0] for item in THEMES), 'general-en']))
    for name in set(LEGACY_PREVIEWS) - current:
        (output / name).unlink(missing_ok=True)
    total = sum((output / name).stat().st_size for name in current if (output / name).is_file())
    if total > MAX_GALLERY_BYTES:
        raise ValueError('Combined preview gallery exceeds 3 MiB; reduce thumbnail widths or page count.')
    print(f'Preview gallery: {total / 1024**2:.2f} MiB; each image at most 0.25 MiB.')
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
