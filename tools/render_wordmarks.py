#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Render the official compound outlines as transparent theme wordmarks."""
from pathlib import Path
from xml.etree import ElementTree as ET

import pymupdf


def main():
    assets = Path(__file__).resolve().parents[1] / 'assets'
    for variant, color, height in (
        ('dark', '#ffffff', 393), ('light', '#552174', 392),
    ):
        svg = ET.parse(assets / 'wordmark.svg').getroot()
        svg.set('height', str(height))
        for path in svg.findall('{http://www.w3.org/2000/svg}path'):
            path.set('fill', color)
        # Fill complete compound paths together. Rasterizing individual pieces
        # leaves antialiasing seams inside otherwise continuous strokes.
        with pymupdf.open(stream=ET.tostring(svg), filetype='svg') as source:
            data = source.convert_to_pdf()
        with pymupdf.open(stream=data, filetype='pdf') as pdf:
            destination = assets / f'wordmark_on_{variant}.png'
            pdf[0].get_pixmap(alpha=True).save(destination)
            print(destination.relative_to(assets.parent))


if __name__ == '__main__':
    main()
