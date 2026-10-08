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
                  'code-windows': 5, 'class-metadata': 3, 'name-layout': 20,
                  'section-toc-spacing': 42, 'date-display': 12,
                  'citation-top-right': 3, 'flow-layout': 1, 'url-layout': 2}


def check_section_toc_spacing(document, log):
    """Reject invisible strut-only rows while allowing real wrapped titles."""
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('section-toc-spacing: overflow or missing glyphs')
    baseline = 13.6 * 72 / 72.27  # normalsize baseline, TeX pt -> PDF pt
    cover = 0
    for section, count in ((1, 3), (2, 4), (3, 5), (4, 6), (5, 6), (10, 12)):
        page = document[cover]
        lines = [line for block in page.get_text('rawdict')['blocks']
                 for line in block.get('lines', [])]
        chars = [char for line in lines for span in line['spans']
                 for char in span['chars'] if not char['c'].isspace()]
        # XeTeX destinations may be reported as named links with resolved pages.
        # Locate numbers by their linked glyphs, independent of font ToUnicode.
        links = [link for link in page.get_links()
                 if link.get('page', -1) in range(cover + 1, cover + count + 1)]
        anchors = {}
        for number in range(1, count + 1):
            linked_chars = [char for char in chars if any(
                link['page'] == cover + number
                and (pymupdf.Rect(char['bbox']).tl + pymupdf.Rect(char['bbox']).br) / 2
                in link['from'] for link in links)]
            if not linked_chars:
                raise RuntimeError(f'section-toc-spacing: broken link {section}.{number}')
            anchors[number] = min(linked_chars, key=lambda c: (c['origin'][1], c['origin'][0]))
        stride = 1 if count < 4 else 2
        starts = [anchors[i]['origin'][1] for i in range(1, count + 1, stride)]
        for i in range(1, count + 1, stride):
            if stride == 2 and i < count:
                if abs(anchors[i]['origin'][1] - anchors[i+1]['origin'][1]) > 0.05:
                    raise RuntimeError('section-toc-spacing: paired cells not top aligned')
        for top, following in zip(starts, starts[1:]):
            last_visible = max(c['origin'][1] for c in chars
                               if top - 0.05 <= c['origin'][1] < following - 0.05)
            if abs(following - last_visible - baseline) > 0.1:
                raise RuntimeError(f'section-toc-spacing: phantom row in section {section}')
        if section == 5 and starts[1] - starts[0] < 2 * baseline - 0.1:
            raise RuntimeError('section-toc-spacing: real multiline title was flattened')
        cover += count + 1


def check_date_display(document):
    """Keep fixed dates, today, empty and custom dates distinct in both layouts."""
    expected = ('2026年10月14日', '2026年10月8日', '', '秋季学期',
                '2026-10-14', 'October 8, 2026')
    for pair, date in enumerate(expected):
        for page in (document[2 * pair], document[2 * pair + 1]):
            text = ''.join(page.get_text().split())
            if date and ''.join(date.split()) not in text:
                raise RuntimeError(f'date-display: missing {date!r}')
            if not date and ('2026' in text or '秋季学期' in text):
                raise RuntimeError('date-display: empty date retained previous value')
    if campus_metadata(document).get('Date') != expected[0]:
        raise RuntimeError('date-display: initial display date metadata changed')


def check_citation_top_right(document, log):
    """Check default citation position, links and clearance from both headers."""
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('citation-top-right: overflow or missing glyphs')
    for page in (document[0], document[1]):
        spans = [span for block in page.get_text('dict')['blocks']
                 for line in block.get('lines', []) for span in line['spans']]
        citations = [pymupdf.Rect(span['bbox']) for span in spans
                     if span['size'] < 7 and span['bbox'][1] < page.rect.height / 3]
        for label in ('第一条较长的中文引用', '第二条合成引用'):
            if not page.search_for(label):
                raise RuntimeError('citation-top-right: missing citation text')
        headers = page.search_for('双行页眉布局')
        headers += page.search_for('较长中文标题与多篇引用共存')
        headers += page.search_for('论文讲解页沿用右上角引用')
        headers = [box for box in headers if box.y0 < page.rect.height / 3]
        if len(headers) != 2 or not citations:
            raise RuntimeError('citation-top-right: missing header/citation boxes')
        for box in citations:
            if box.x0 < page.rect.width / 2:
                raise RuntimeError('citation-top-right: citation not on right')
            if any(box.intersects(header) for header in headers):
                raise RuntimeError('citation-top-right: header/citation collision')
        if not any(link.get('page') == 2 for link in page.get_links()):
            raise RuntimeError('citation-top-right: missing inline reference link')


def check_flow_layout(document, log):
    """Check the public node-and-edge diagram fixture for readable output."""
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('flow-layout: overflow or missing glyphs')
    text = ''.join(page.get_text() for page in document)
    for label in ('本机', '代理', 'SSH', '通道', '远程', '服务器', '请求', '转发'):
        if label not in text:
            raise RuntimeError(f'flow-layout: missing node/edge label {label!r}')
    page = document[0]
    node_boxes = [box for label in ('本机', 'SSH', '远程')
                  for box in page.search_for(label)]
    if len(node_boxes) < 3:
        raise RuntimeError('flow-layout: expected three visible nodes')
    if max(box.y1 for box in node_boxes) - min(box.y0 for box in node_boxes) > 80:
        raise RuntimeError('flow-layout: nodes are not aligned')


def check_url_layout(document, log):
    """Check audience URLs remain visible and retain their exact targets."""
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('url-layout: overflow or missing glyphs')
    expected = (
        'https://missing.csail.mit.edu/',
        'https://guide.bash.academy/',
        'https://themodernsoftware.dev/',
        'https://www.youtube.com/watch?v=example123',
    )
    visible = ''.join(''.join(page.get_text().split()) for page in document)
    targets = {link.get('uri') for page in document for link in page.get_links()
               if link.get('uri')}
    for url in expected:
        if url not in visible:
            raise RuntimeError(f'url-layout: URL is not visible: {url}')
        if url not in targets:
            raise RuntimeError(f'url-layout: URL target changed: {url}')


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
        for expected in ('train_model.py', '中文注释', 'Python again', 'shell output',
                         '输出日志', '~/.ssh/config', 'RemoteForward'):
            if expected not in text:
                raise RuntimeError(f'{name}: missing code text {expected!r}')
        selected = document[2].get_text()
        if 'total = sum(values)' not in selected or 'print(' in selected:
            raise RuntimeError(f'{name}: external source line selection failed')
        caption = document[0].search_for('train_model.py')
        code = document[0].search_for('中文注释')
        if not caption or not code or caption[0].y0 <= code[0].y1:
            raise RuntimeError(f'{name}: code caption is not outside the code area')
        if 'Shell' in document[1].get_text():
            raise RuntimeError(f'{name}: terminal caption still uses Shell')
        config_page = document[4]
        if config_page.search_for('~/.ssh/config') and config_page.search_for('Shell'):
            raise RuntimeError(f'{name}: configuration file was labelled Shell')
        if not config_page.search_for('RemoteForward'):
            raise RuntimeError(f'{name}: configuration content missing')
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
                    'Date': '2026年10月12日', 'Contact': 'test@example.org', 'Language': 'chinese'}
        if campus_metadata(document) != expected or document.metadata['author'] != '甲乙':
            raise RuntimeError('class-metadata: cover metadata did not survive PDF encoding')
        if 'Token not allowed in a PDF string' in log:
            raise RuntimeError('class-metadata: PDF metadata contains unsupported formatting')
        if document.get_toc() != [[1, '章节 & 结果', 2], [2, '子节', 3]]:
            raise RuntimeError('class-metadata: section bookmarks did not survive PDF encoding')


def check_name_layout(document, log):
    """Check rendered name edges, title spacing and optional advisor rows."""
    if any(warning in log for warning in ('Overfull', 'Missing character:')):
        raise RuntimeError('name-layout: overflow or missing glyphs')

    def close(a, b, label):
        if abs(a - b) > 0.05:
            raise RuntimeError(f'name-layout: {label}: {a} != {b}')

    def rows(page):
        chars = [char for block in page.get_text('rawdict')['blocks']
                 for line in block.get('lines', []) for span in line['spans']
                 for char in span['chars']]
        colons = sorted((c for c in chars if c['c'] in (':', '：')),
                        key=lambda c: c['origin'][1])
        return [sorted((c for c in chars if not c['c'].isspace()
                        and abs(c['origin'][1] - colon['origin'][1]) < 0.05
                        and c['bbox'][0] >= colon['bbox'][2] - 0.05),
                       key=lambda c: c['bbox'][0]) for colon in colons]

    def name_box(row, name):
        chars = row[:len(name)]
        if ''.join(c['c'] for c in chars) != name:
            raise RuntimeError(f'name-layout: missing name {name!r}')
        return pymupdf.Rect(chars[0]['bbox']) | pymupdf.Rect(chars[-1]['bbox'])

    for start, presenter, advisor in ((2, '王芳', '张晓明'), (4, '张晓明', '王芳'),
                                      (6, '王芳', '李明'), (10, '王', '欧阳明德')):
        for page in (document[start], document[start + 1]):
            speaker_row, advisor_row = rows(page)
            speaker = name_box(speaker_row, presenter)
            teacher = name_box(advisor_row, advisor)
            close(speaker.x0, teacher.x0, 'name left edges')
            if len(presenter) > 1:
                close(speaker.x1, teacher.x1, 'name right edges')
            glyph_width = advisor_row[0]['bbox'][2] - advisor_row[0]['bbox'][0]
            close(teacher.width, max(len(presenter), len(advisor)) * glyph_width,
                  'name column excludes title/contact')
            if start in (2, 4):
                if ''.join(c['c'] for c in advisor_row[len(advisor):]) != '副教授':
                    raise RuntimeError('name-layout: missing advisor title')
                close(advisor_row[len(advisor)]['bbox'][0] - teacher.x1,
                      glyph_width, 'one-character title gap')
            elif len(advisor_row) != len(advisor):
                raise RuntimeError('name-layout: previous advisor title leaked')
    for start, name in ((0, '张晓明'), (8, '王芳')):
        for page in (document[start], document[start + 1]):
            content = rows(page)
            if len(content) != 1:
                raise RuntimeError('name-layout: omitted/empty advisor is visible')
            box = name_box(content[0], name)
            glyph_width = content[0][0]['bbox'][2] - content[0][0]['bbox'][0]
            close(box.width, len(name) * glyph_width, 'natural name without advisor')
    for start in (14, 16, 18):
        for page in (document[start], document[start + 1]):
            speaker_row = rows(page)[0]
            box = name_box(speaker_row, '王芳')
            glyph_width = speaker_row[0]['bbox'][2] - speaker_row[0]['bbox'][0]
            close(box.width, 2 * glyph_width, 'natural English/legacy/formatted name')
    for page in (document[12], document[13]):
        if not page.search_for('Ada Lovelace') or not page.search_for('Alan Turing Professor'):
            raise RuntimeError('name-layout: English names/title no longer use natural spacing')


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
            bibliography = root / 'tools/fixtures' / f'{name}.bib'
            if bibliography.exists():
                shutil.copy2(bibliography, workspace / bibliography.name)
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
            # Keep the compiled evidence even when a geometry assertion fails.
            shutil.copy2(pdf, output / f'{name}.pdf')
            with pymupdf.open(pdf) as document:
                pages = len(document)
                if pages != expected:
                    raise RuntimeError(f'{name}: expected {expected} pages, got {pages}')
                if name == 'language-layout':
                    check_language_layout(document)
                if name == 'name-layout':
                    check_name_layout(document, result.stdout)
                if name == 'section-toc-spacing':
                    check_section_toc_spacing(document, result.stdout)
                if name == 'date-display':
                    check_date_display(document)
                if name == 'citation-top-right':
                    check_citation_top_right(document, result.stdout)
                if name == 'flow-layout':
                    check_flow_layout(document, result.stdout)
                if name == 'url-layout':
                    check_url_layout(document, result.stdout)
                check_class_fixture(name, document, result.stdout)
            print(f'{name}: {pages} pages compiled; inspect {output / f"{name}.pdf"}')
    check_class_errors(root, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('build/theme-check'))
    args = parser.parse_args()
    check(Path(__file__).resolve().parents[1], args.output.resolve())


if __name__ == '__main__':
    main()
