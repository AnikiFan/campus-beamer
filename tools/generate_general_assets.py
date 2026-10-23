#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Build the bundled institution-neutral theme vectors from editable TeX sources."""
import argparse
from pathlib import Path
import subprocess

import pymupdf


def generate(root: Path, theme: str = 'general') -> None:
    if theme not in ('general', 'tokyo-night'):
        raise ValueError('Select general or tokyo-night.')
    output = root / f'build/{theme}-assets'
    output.mkdir(parents=True, exist_ok=True)
    assets = root / f'theme/{theme}/assets'
    assets.mkdir(parents=True, exist_ok=True)
    for name, source, color in (
        ('emblem_on_dark', f'theme/{theme}/emblem.tex', 'white'),
        ('emblem_on_light', f'theme/{theme}/emblem.tex', 'brand'),
        ('wordmark_on_dark', f'theme/{theme}/wordmark.tex', 'white'),
        ('wordmark_on_light', f'theme/{theme}/wordmark.tex', 'brand'),
        ('backdrop', f'theme/{theme}/backdrop.tex', 'brand'),
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
    print(f'{theme} theme assets: {assets}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', choices=('general', 'tokyo-night'), default='general')
    generate(Path(__file__).resolve().parents[1], parser.parse_args().theme)
