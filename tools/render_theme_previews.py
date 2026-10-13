#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render a small, deterministic preview set for each public theme sample."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import pymupdf


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
    lines = ['<!-- demo-gallery:start -->', '<div align="center">']
    for start in range(0, len(GALLERY), 4):
        lines.append('  <p>')
        for name, _, chinese, english_label, _ in GALLERY[start:start + 4]:
            label = english_label if english else chinese
            lines.append(f'    <img src="docs/images/preview-{name}.png" alt="{label}" width="200">')
        lines.append('  </p>')
    lines.extend(['</div>', '<!-- demo-gallery:end -->'])
    return '\n'.join(lines)


def render_gallery(pdf: Path, output: Path, dpi: int) -> None:
    with pymupdf.open(pdf) as document:
        for name, number, _, _, _ in GALLERY:
            document[number - 1].get_pixmap(dpi=dpi, alpha=False).save(output / f'preview-{name}.png')
        document[0].get_pixmap(dpi=dpi, alpha=False).save(output / 'cover.png')
        document[23].get_pixmap(dpi=dpi, alpha=False).save(output / 'citations.png')


def render(pdf: Path, theme: str, output: Path, dpi: int = 600) -> None:
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    with pymupdf.open(pdf) as document:
        if len(document) < 6:
            raise ValueError(f'{pdf}: expected at least six pages, got {len(document)}')
        output.mkdir(parents=True, exist_ok=True)
        # Cover, section page, and ordinary body page make the profile differences
        # visible while keeping the README compact.
        for label, index in (('cover', 0), ('section', 2), ('body', 5)):
            page = document[index]
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            pixmap.save(output / f'theme-{theme}-{label}.png')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='append', required=True)
    parser.add_argument('--theme', action='append', required=True)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--update-readme', action='store_true')
    parser.add_argument('--output', type=Path, default=Path('docs/images'))
    parser.add_argument('--dpi', type=int, default=600)
    args = parser.parse_args()
    if args.dpi < 600:
        raise ValueError('Preview DPI must be at least 600.')
    if len(args.pdf) != len(args.theme):
        parser.error('--pdf and --theme must be supplied in matching pairs')
    validate_samples([Path(pdf) for pdf in args.pdf])
    if args.check_only:
        print('Theme samples: shared page count, sections, metadata and preview order verified.')
        return
    for pdf, theme in zip(args.pdf, args.theme):
        render(Path(pdf), theme, args.output, args.dpi)
        if theme == 'general':
            render_gallery(Path(pdf), args.output, args.dpi)
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
