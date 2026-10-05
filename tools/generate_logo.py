#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Typeset the project wordmark; export outlined SVGs and PDF/PNG previews."""
from pathlib import Path
import math
import subprocess
from xml.etree import ElementTree as ET

import pymupdf


def frame_wordmark(path, padding=12):
    """Frame the visible letter outlines with equal padding on all four sides."""
    with pymupdf.open(path) as source, pymupdf.open() as framed:
        bounds = pymupdf.Rect()
        for kind, box in source[0].get_bboxlog():
            if kind == 'fill-text':
                # MuPDF adds a 1-point safety margin to text ink bounds.
                bounds |= pymupdf.Rect(box) + (1, 1, -1, -1)
        if bounds.is_empty:
            raise ValueError('The logo contains no visible text.')
        clip = bounds + (-padding, -padding, padding, padding)
        page = framed.new_page(width=clip.width, height=clip.height)
        page.draw_rect(page.rect, color=None, fill=(1, 1, 1))
        midpoint = .618 * page.rect.width
        shift = .5 * page.rect.height / math.tan(math.radians(72))
        panel = [(midpoint + shift, 0), (page.rect.width, 0),
                 (page.rect.width, page.rect.height),
                 (midpoint - shift, page.rect.height)]
        page.draw_polyline(panel, color=None, fill=(85/255, 33/255, 116/255),
                           closePath=True)
        page.show_pdf_page(page.rect, source, 0, clip=clip)
        data = framed.tobytes()
    path.write_bytes(data)
    print(f'Wordmark canvas: {clip.width:.2f} x {clip.height:.2f} pt; '
          f'padding: {padding} pt on all sides')


def main():
    root = Path(__file__).resolve().parents[1]
    output = root / 'build' / 'logo'
    output.mkdir(parents=True, exist_ok=True)
    with (output / 'build.log').open('w') as log:
        subprocess.run(['xelatex', '-interaction=nonstopmode', '-halt-on-error',
                        '-output-directory=' + str(output),
                        'assets/campus-beamer-logo.tex'], cwd=root,
                       stdout=log, stderr=subprocess.STDOUT, check=True)

    frame_wordmark(output / 'campus-beamer-logo.pdf')

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

        # The icon already contains the cover's white-left/purple-right panels.
        # Keep the dark-mode asset identical so the split remains visible on a
        # dark README background; turning every fill white would erase the icon.
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
