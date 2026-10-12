#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build transparent general-theme vectors from editable TeX sources."""
from pathlib import Path
import subprocess

import pymupdf


def generate(root: Path) -> None:
    output = root / 'build/general-assets'
    output.mkdir(parents=True, exist_ok=True)
    assets = root / 'theme/general/assets'
    for name, source, color in (
        ('emblem_on_dark', 'theme/general/emblem.tex', 'white'),
        ('emblem_on_light', 'theme/general/emblem.tex', 'brand'),
        ('wordmark_on_dark', 'theme/general/wordmark.tex', 'white'),
        ('wordmark_on_light', 'theme/general/wordmark.tex', 'brand'),
        ('backdrop', 'theme/general/backdrop.tex', 'brand'),
    ):
        with (output / f'{name}.build.log').open('w') as log:
            subprocess.run([
                'xelatex', '-interaction=nonstopmode', '-halt-on-error',
                f'-output-directory={output}', f'-jobname={name}',
                rf'\def\artcolor{{{color}}}\input{{{source}}}',
            ], cwd=root, stdout=log, stderr=subprocess.STDOUT, check=True)
        with pymupdf.open(output / f'{name}.pdf') as pdf:
            if name.startswith('wordmark'):
                bounds = pymupdf.Rect()
                for kind, box in pdf[0].get_bboxlog():
                    if kind == 'fill-text':
                        bounds |= pymupdf.Rect(box)
                pdf[0].set_cropbox(bounds + (-2, -2, 2, 2))
            pdf.save(assets / f'{name}.pdf')
    print(f'General theme assets: {assets}')


if __name__ == '__main__':
    generate(Path(__file__).resolve().parents[1])
