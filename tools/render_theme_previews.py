#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render a small, deterministic preview set for each public theme sample."""
from __future__ import annotations

import argparse
from pathlib import Path

import pymupdf


def render(pdf: Path, theme: str, output: Path, dpi: int = 600) -> None:
    if not pdf.is_file():
        raise FileNotFoundError(pdf)
    with pymupdf.open(pdf) as document:
        if len(document) < 5:
            raise ValueError(f'{pdf}: expected at least five pages, got {len(document)}')
        output.mkdir(parents=True, exist_ok=True)
        # Cover, section page, and ordinary body page make the profile differences
        # visible while keeping the README compact.
        for label, index in (('cover', 0), ('section', 2), ('body', 4)):
            page = document[index]
            pixmap = page.get_pixmap(dpi=dpi, alpha=False)
            pixmap.save(output / f'theme-{theme}-{label}.png')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', action='append', required=True)
    parser.add_argument('--theme', action='append', required=True)
    parser.add_argument('--output', type=Path, default=Path('docs/images'))
    parser.add_argument('--dpi', type=int, default=600)
    args = parser.parse_args()
    if args.dpi < 600:
        raise ValueError('Preview DPI must be at least 600.')
    if len(args.pdf) != len(args.theme):
        parser.error('--pdf and --theme must be supplied in matching pairs')
    for pdf, theme in zip(args.pdf, args.theme):
        render(Path(pdf), theme, args.output, args.dpi)


if __name__ == '__main__':
    main()
