#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Export a compiled talk using native TeX notes, with legacy JSON compatibility."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys

import pymupdf

from images_to_ppt import convert_pdf_to_pptx, pdf_info_string
from add_video_posters import add_video_posters


def render_variant(source: Path, mode: str, latexmk: str) -> Path:
    """Compile a separate job; never rewrite the user's entry or its options."""
    if any(character in source.as_posix() for character in '{}%\\\n\r'):
        raise ValueError('The entry path contains characters unsafe in a TeX input filename.')
    suffix = 'notes' if mode == 'notes' else 'slides'
    wrapper = Path('build') / f'{source.stem}.{suffix}.tex'
    wrapper.write_text('\\def\\campusnotesmode{' + mode + '}\n'
                       '\\input{\\detokenize{' + source.as_posix() + '}}\n')
    subprocess.run([latexmk, '-xelatex', '-interaction=nonstopmode', '-halt-on-error',
                    '-file-line-error', str(wrapper)], check=True)
    return wrapper.with_suffix('.pdf')


def export(source: Path, *, dpi=600, latexmk='latexmk'):
    """Use a clean slide PDF for images and a separate native note render for text."""
    pdf_path = Path('build') / (source.stem + '.pdf')
    output = pdf_path.with_suffix('.pptx')
    with pymupdf.open(pdf_path) as pdf:
        layout = pdf_info_string(pdf, 'CampusNotesLayout')
    if layout and layout not in ('none', 'right'):
        raise ValueError(f'Unsupported Campus notes layout: {layout}')
    if layout not in ('none', 'right'):
        # Preserve the original exporter behavior for legacy Beamer/theme users.
        legacy = pdf_path.with_suffix('.notes.json')
        return convert_pdf_to_pptx(pdf_path, output, dpi=dpi, strict_links=True,
                                  strict_notes=True, auto_notes=False,
                                  notes_path=legacy if legacy.is_file() else None)
    slides = render_variant(source, 'slides', latexmk) if layout == 'right' else pdf_path
    if layout == 'right':
        add_video_posters(slides)
    native = render_variant(source, 'notes', latexmk)
    has_notes = native.with_suffix('.campus-notes').read_text().strip()
    if has_notes not in ('true', 'false'):
        raise ValueError('Native notes render did not record its source mode.')
    with pymupdf.open(native) as notes_pdf:
        kind, reference = notes_pdf.xref_get_key(-1, 'Info')
        if kind != 'xref':
            raise ValueError('Native notes PDF has no document metadata.')
        fingerprint = hashlib.sha256(slides.read_bytes()).hexdigest()
        notes_pdf.xref_set_key(int(reference.split()[0]), 'CampusSlidesSHA256', f'({fingerprint})')
        notes_pdf.xref_set_key(int(reference.split()[0]), 'CampusHasNotes', f'({has_notes})')
        notes_pdf.saveIncr()
    legacy = pdf_path.with_suffix('.notes.json')
    if has_notes == 'false' and legacy.is_file():
        print('Legacy JSON notes retained; add native note commands to make TeX authoritative.')
        result = convert_pdf_to_pptx(slides, output, dpi=dpi, strict_links=True,
                                     strict_notes=True, auto_notes=False, notes_path=legacy)
    else:
        result = convert_pdf_to_pptx(slides, output, dpi=dpi, strict_links=True,
                                     strict_notes=True, auto_notes=False, notes_pdf_path=native)
    for variant in (native, slides if layout == 'right' else None):
        if variant is not None:
            subprocess.run([latexmk, '-c', str(variant.with_suffix('.tex'))], check=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='Talk entry, e.g. main.tex')
    parser.add_argument('--dpi', type=int, default=600)
    parser.add_argument('--latexmk', default='latexmk')
    args = parser.parse_args()
    try:
        export(args.source, dpi=args.dpi, latexmk=args.latexmk)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f'Presentation export failed: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == '__main__':
    main()
