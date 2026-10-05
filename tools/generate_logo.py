#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Typeset the project wordmark; export outlined SVGs and PDF/PNG previews."""
from pathlib import Path
import subprocess
from xml.etree import ElementTree as ET

import pymupdf


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / 'build' / 'logo'
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'build.log').open('w') as log:
        subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                        '-output-directory=' + str(output),
                        'assets/campus-beamer-logo.tex'], cwd=root,
                       stdout=log, stderr=subprocess.STDOUT, check=True)

    svg_ns = 'http://www.w3.org/2000/svg'
    ET.register_namespace('', svg_ns)
    ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
    with pymupdf.open(output / 'campus-beamer-logo.pdf') as pdf:
        svg = ET.fromstring(pdf[0].get_svg_image(text_as_path=True))
        svg.set('role', 'img')
        svg.set('aria-labelledby', 'logo-title')
        title = ET.Element(f'{{{svg_ns}}}title', id='logo-title')
        title.text = 'Campus Beamer'
        svg.insert(0, title)
        (root / 'assets' / 'campus-beamer-logo.svg').write_bytes(ET.tostring(svg, encoding='utf-8'))
        pdf[0].get_pixmap(dpi=192, alpha=True).save(output / 'campus-beamer-logo.png')

        for element in svg.iter():
            if element.get('fill') not in (None, 'none'):
                element.set('fill', '#ffffff')
        white = ET.tostring(svg, encoding='utf-8')
        (root / 'assets' / 'campus-beamer-logo-white.svg').write_bytes(white)
        with pymupdf.open(stream=white, filetype='svg') as image:
            white_pdf = image.convert_to_pdf()
        with pymupdf.open(stream=white_pdf, filetype='pdf') as reversed_pdf:
            reversed_pdf.save(output / 'campus-beamer-logo-white.pdf')
            reversed_pdf[0].get_pixmap(dpi=192, alpha=True).save(output / 'campus-beamer-logo-white.png')
            # A small proof sheet checks contrast and spacing on both backgrounds.
            with pymupdf.open() as preview:
                page = preview.new_page(width=720, height=340)
                page.draw_rect(page.rect, color=None, fill=(1, 1, 1))
                page.draw_rect(pymupdf.Rect(0, 170, 720, 340), color=None,
                               fill=(85 / 255, 33 / 255, 116 / 255))
                page.show_pdf_page(pymupdf.Rect(35, 25, 685, 145), pdf, 0)
                page.show_pdf_page(pymupdf.Rect(35, 195, 685, 315), reversed_pdf, 0)
                page.get_pixmap(dpi=144).save(output / 'preview.png')

    for suffix in ('.aux', '.log'):
        (output / ('campus-beamer-logo' + suffix)).unlink(missing_ok=True)
    print('Logo SVGs: assets/campus-beamer-logo{,-white}.svg')
    print('PDF/PNG versions and preview: build/logo/')


if __name__ == '__main__':
    main()
