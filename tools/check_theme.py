#!/usr/bin/env python3
# Campus Beamer: compile theme fixtures and check expected output.
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Compile theme fixtures without touching the user's main PDF or intermediates."""
from pathlib import Path
import argparse
import os
import shutil
import subprocess
import tempfile

import pymupdf
from images_to_ppt import campus_metadata

EXPECTED_PAGES = {'brand-variants': 4, 'layout-guides': 5, 'layout-guides-off': 3,
                  'single-header': 5,
                  'demo-without-guides': 42, 'language-layout': 10,
                  'class-options': 6, 'class-handout': 1, 'class-mixed-language': 2,
                  'code-windows': 4, 'class-metadata': 3}


def check_class_fixture(name, document, log):
    if 'biblatex.sty' not in log:
        raise RuntimeError(f'{name}: automatic bibliography support did not load')
    if name == 'brand-variants':
        expected = document[0].get_pixmap(dpi=96).samples
        if any(page.get_pixmap(dpi=96).samples != expected for page in (document[1], document[2])):
            raise RuntimeError('brand-variants: default, primary and legacy-star covers differ')
    if name in ('brand-variants', 'layout-guides', 'layout-guides-off'):
        for number, page in enumerate(document, 1):
            has_guides = any(drawing.get('color') == (1.0, 0.0, 0.0)
                             for drawing in page.get_drawings())
            if has_guides != (name == 'layout-guides'):
                raise RuntimeError(f'{name}: unexpected diagnostic state on page {number}')
    if name.startswith('class-') and 'Missing character:' in log:
        raise RuntimeError(f'{name}: missing glyphs in class-generated content')
    text = '\n'.join(page.get_text() for page in document)
    if name == 'code-windows':
        for warning in ('Missing character:', 'Overfull'):
            if warning in log:
                raise RuntimeError(f'{name}: {warning} in code fixture')
        for expected in ('train_model.py', '中文注释', 'Python again', 'shell output'):
            if expected not in text:
                raise RuntimeError(f'{name}: missing code text {expected!r}')
        selected = document[2].get_text()
        if 'total = sum(values)' not in selected or 'print(' in selected:
            raise RuntimeError(f'{name}: external source line selection failed')
    if name == 'class-options':
        for expected in ('References', 'Citations:', 'Fixture source', 'Institution:', 'Thank you'):
            if expected not in text:
                raise RuntimeError(f'{name}: missing English text {expected!r}')
        if 'authoryear.bbx' not in log:
            raise RuntimeError('class-options: custom bibliography style did not load')
    elif name == 'class-handout':
        if 'First overlay.' not in text or 'Second overlay.' not in text:
            raise RuntimeError('class-handout: handout did not preserve both overlay items')
        if 'xeCJK.sty' in log:
            raise RuntimeError('class-handout: English auto mode loaded xeCJK')
    elif name == 'class-mixed-language':
        if '用户内容保留原语言' not in text or 'Speaker' not in text:
            raise RuntimeError('class-mixed-language: language labels or Chinese content missing')
    elif name == 'class-metadata':
        expected = {'Title': '中文 (标题) & PPT', 'Subtitle': '方法 & 结果',
                    'Group': '实验组 <A>', 'Advisor': '王老师 副教授',
                    'Date': '2026-10-12', 'Contact': 'test@example.org', 'Language': 'chinese'}
        if campus_metadata(document) != expected or document.metadata['author'] != '甲乙':
            raise RuntimeError('class-metadata: cover metadata did not survive PDF encoding')
        if 'Token not allowed in a PDF string' in log:
            raise RuntimeError('class-metadata: PDF metadata contains unsupported formatting')
        if document.get_toc() != [[1, '章节 & 结果', 2], [2, '子节', 3]]:
            raise RuntimeError('class-metadata: section bookmarks did not survive PDF encoding')


def check_class_errors(root, output):
    cases = (
        ('bad-language', 'language=french', '', 'xelatex', 'Unknown language'),
        ('bad-cjk', 'cjk=invalid', '', 'xelatex', 'Unknown cjk setting'),
        ('bad-mathfont', 'mathfont=invalid', '', 'xelatex', 'Unknown mathfont'),
        ('removed-bib-false', 'biblatex=false', '',
         'xelatex', 'Bibliography support is always enabled'),
        ('removed-bib-true', 'biblatex=true', '',
         'xelatex', 'Bibliography support is always enabled'),
        ('wrong-engine', 'language=english', '', 'pdflatex', 'XeLaTeX is required'),
        ('white-title-background', 'language=english', r'\titlebackground{white}',
         'xelatex', 'Only primary is supported for title backgrounds'),
        ('image-title-background', 'language=english', r'\titlebackground{assets/sigs_building}',
         'xelatex', 'Only primary is supported for title backgrounds'),
        ('removed-guides-on', 'language=english', r'\campuslayoutguidestrue',
         'xelatex', 'Undefined control sequence'),
        ('removed-guides-off', 'language=english', r'\campuslayoutguidesfalse',
         'xelatex', 'Undefined control sequence'),
    )
    with tempfile.TemporaryDirectory(prefix='campus-class-errors-') as temp:
        workspace = Path(temp)
        shutil.copytree(root / 'theme', workspace / 'theme')
        # These negative checks call engines directly, bypassing .latexmkrc.
        env = os.environ.copy()
        env['TEXINPUTS'] = str(workspace / 'theme') + '//' + os.pathsep + env.get('TEXINPUTS', '')
        (workspace / 'assets').symlink_to(root / 'assets', target_is_directory=True)
        for name, options, preamble, engine, expected in cases:
            source = (f'\\documentclass[{options}]{{campusbeamer}}\n{preamble}\n'
                      '\\begin{document}\\begin{frame}{Test}Body\\end{frame}\\end{document}\n')
            (workspace / f'{name}.tex').write_text(source)
            result = subprocess.run([engine, '-interaction=nonstopmode', '-halt-on-error',
                                     '-file-line-error', f'{name}.tex'], cwd=workspace, env=env,
                                    text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            (output / f'{name}.build.log').write_text(result.stdout)
            if not result.returncode or ''.join(expected.split()) not in ''.join(result.stdout.split()):
                raise RuntimeError(f'{name}: expected a clear failure containing {expected!r}')
            print(f'{name}: rejected with the expected class error')


def check_language_layout(document):
    """Compare actual PDF typography and anchors across the language switch."""
    def close(a, b, label):
        if abs(a - b) > 0.05:
            raise RuntimeError(f'language-layout: {label}: {a} != {b}')

    def chars(page):
        return [(char, span['size'])
                for block in page.get_text('rawdict')['blocks']
                for line in block.get('lines', [])
                for span in line['spans'] for char in span['chars']]

    for offset in (0, 3, 4):  # cover, closing, closing without title
        chinese, english = document[offset], document[offset + 5]
        for name in ('Ada Lovelace', 'Alan Turing', 'Shared typography'):
            a, b = chinese.search_for(name)[0], english.search_for(name)[0]
            # Label widths depend on language; metadata keeps its vertical grid.
            for i in ((0, 1, 2, 3) if name == 'Shared typography' else (1, 3)):
                close(a[i], b[i], f'{name} box edge {i}')
        # Label letters stretch; colons and the following names share a column.
        for page in (chinese, english):
            colons = [c for c, _ in chars(page) if c['c'] in (':', '：')]
            if len(colons) != 2:
                raise RuntimeError('language-layout: expected two label colons')
            close(colons[0]['origin'][0], colons[1]['origin'][0], 'colon column')
            close(page.search_for('Ada Lovelace')[0].x0,
                  page.search_for('Alan Turing')[0].x0, 'name column')
        # Ignore inserted PDF extraction spaces between the distributed letters.
        for word, name in [('Speaker', 'Ada Lovelace'), ('Advisor', 'Alan Turing')]:
            name_box = english.search_for(name)[0]
            letters = [c for c, _ in chars(english)
                       if name_box.y0 <= c['origin'][1] <= name_box.y1
                       and c['bbox'][0] < colons[0]['origin'][0]
                       and c['c'].isalpha()]
            if ''.join(c['c'] for c in letters) != word:
                raise RuntimeError(f'language-layout: missing {word} label')
            bounds = (letters[0]['bbox'][0], letters[-1]['bbox'][2])
            natural_width = max(document[7].search_for(label)[0].width
                                for label in ('Speaker', 'Advisor'))
            close(bounds[1] - bounds[0], natural_width, 'natural label column width')
            if word == 'Speaker':
                presenter_bounds = bounds
            else:
                for a, b in zip(presenter_bounds, bounds):
                    close(a, b, 'distributed label edges')
    for a, b in ((0, 3), (5, 8)):
        cover = document[a].search_for('Language layout')[0]
        closing = document[b].search_for('Language layout')[0]
        close(cover.y0, closing.y0, 'cover/closing title top')
        close(cover.y1, closing.y1, 'cover/closing title bottom')
    # The font changes language, never size: compare metadata and thank-you sizes.
    for a, b in ((0, 5), (1, 6), (2, 7), (3, 8), (4, 9)):
        sizes_a = {round(size, 2) for c, size in chars(document[a]) if not c['c'].isspace()}
        sizes_b = {round(size, 2) for c, size in chars(document[b]) if not c['c'].isspace()}
        if sizes_a != sizes_b:
            raise RuntimeError(f'language-layout: font sizes differ on pages {a+1}/{b+1}')


def check(root, output):
    if not shutil.which('latexmk'):
        raise RuntimeError('latexmk is required for theme checks')
    output.mkdir(parents=True, exist_ok=True)
    for name, expected in EXPECTED_PAGES.items():
        with tempfile.TemporaryDirectory(prefix=f'campus-{name}-') as temp:
            workspace = Path(temp)
            for filename in ['example.tex', '.latexmkrc']:
                shutil.copy2(root / filename, workspace / filename)
            shutil.copytree(root / 'bibliography', workspace / 'bibliography')
            shutil.copytree(root / 'theme', workspace / 'theme')
            shutil.copytree(root / 'chapters', workspace / 'chapters')
            (workspace / 'assets').symlink_to(root / 'assets', target_is_directory=True)
            shutil.copy2(root / 'tools/fixtures' / f'{name}.tex', workspace / f'{name}.tex')
            if name == 'class-options':
                shutil.copy2(root / 'tools/fixtures/class-options.bib', workspace / 'class-options.bib')
            result = subprocess.run(['latexmk', '-xelatex', '-interaction=nonstopmode',
                                     '-halt-on-error', '-file-line-error', f'{name}.tex'],
                                    cwd=workspace, text=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            (output / f'{name}.build.log').write_text(result.stdout)
            if (workspace / 'build' / f'{name}.log').exists():
                shutil.copy2(workspace / 'build' / f'{name}.log', output / f'{name}.log')
            if result.returncode:
                raise RuntimeError(f'{name} failed; see {output / f"{name}.build.log"}')
            pdf = workspace / 'build' / f'{name}.pdf'
            with pymupdf.open(pdf) as document:
                pages = len(document)
                if pages != expected:
                    raise RuntimeError(f'{name}: expected {expected} pages, got {pages}')
                if name == 'language-layout':
                    check_language_layout(document)
                check_class_fixture(name, document, result.stdout)
            shutil.copy2(pdf, output / f'{name}.pdf')
            print(f'{name}: {pages} pages compiled; inspect {output / f"{name}.pdf"}')
    check_class_errors(root, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('build/theme-check'))
    args = parser.parse_args()
    check(Path(__file__).resolve().parents[1], args.output.resolve())


if __name__ == '__main__':
    main()
