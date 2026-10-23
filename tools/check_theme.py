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
from images_to_ppt import campus_metadata, pdf_info_string

EXPECTED_PAGES = {'brand-variants': 4, 'layout-guides': 5, 'layout-guides-off': 3,
                  'single-header': 5,
                  'profile-tokyo-night': 9, 'profile-general': 8, 'profile-general-legacy': 3, 'profile-pcl': 8, 'profile-selection': 6, 'profile-selection-legacy': 6,
                  'demo-without-guides': 50, 'language-layout': 10,
                  'toc-overview': 7, 'page-styles': 10,
                  'class-options': 6, 'class-handout': 1, 'class-mixed-language': 2,
                  'code-windows': 6, 'class-metadata': 3, 'name-layout': 20,
                  'section-toc-spacing': 42, 'date-display': 12,
                  'citation-top-right': 3, 'flow-layout': 1, 'url-layout': 2,
                  'doc-citations': 7, 'description-alignment': 4, 'callout-layout': 1,
                  'overlays': 6, 'overlays-handout': 3,
                  'native-notes': 4, 'native-notes-screen': 4}


def prepare_profile_fixture(workspace):
    """Create a self-contained synthetic brand; never depend on Tsinghua assets."""
    directory = workspace / 'theme/fixture-brand'
    assets = directory / 'assets'
    assets.mkdir(parents=True)
    colors = dict(maincolor='245C80', tipcolor='167048', notecolor='4F4A8C',
                  alertcolor='B52D35', examplecolor='247878', definitioncolor='925919')
    lines = [rf'\definecolor{{{name}}}{{HTML}}{{{value}}}'
             for name, value in colors.items()]
    for kind in ('emblem', 'wordmark'):
        for ground in ('dark', 'light'):
            name = f'{kind}-{ground}'
            lines.append(rf'\newcommand{{\school{kind}on{ground}}}'
                         rf'{{\campusthemedir/assets/{name}.pdf}}')
            with pymupdf.open() as document:
                page = document.new_page(width=120, height=120 if kind == 'emblem' else 30)
                color = (1, 1, 1) if ground == 'dark' else (.14, .36, .5)
                page.draw_rect(page.rect + (2, 2, -2, -2), color=color, width=2)
                page.insert_text((6, page.rect.height / 2), name, fontsize=10, color=color)
                document.save(assets / f'{name}.pdf')
    profile = '\n'.join(lines) + '\n'
    (directory / 'profile.tex').write_text(profile)
    return profile



def check_tokyo_night(document, log):
    """Assert rendered dark surfaces and readable body/code/citation colors."""
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('profile-tokyo-night: overflow or missing glyphs')
    for number in (0, 4, 6, 7):
        pixmap = document[number].get_pixmap()
        if any(abs(a-b) > 1 for a, b in zip(pixmap.pixel(2, 80), (26, 27, 38))):
            raise RuntimeError(f'profile-tokyo-night: dark body surface lost on page {number+1}')
    for number, required in ((4, {0xC0CAF5}), (6, {0xBB9AF7, 0x9ECE6A}), (7, {0x9AA5CE})):
        colors = {span['color'] for block in document[number].get_text('dict')['blocks']
                  for line in block.get('lines', []) for span in line['spans']}
        if not required <= colors:
            raise RuntimeError(f'profile-tokyo-night: missing foreground colors on page {number+1}')
    if not document[7].get_links():
        raise RuntimeError('profile-tokyo-night: citation URL is not clickable')


def check_profile_selection(document, log):
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('profile-selection: overflow or missing glyphs')
    text = '\n'.join(page.get_text() for page in document)
    for marker in ('emblem-dark', 'emblem-light', 'wordmark-dark', 'wordmark-light'):
        if marker not in text:
            raise RuntimeError(f'profile-selection: selected asset missing: {marker}')
    spans = [span for block in document[3].get_text('dict')['blocks']
             for line in block.get('lines', []) for span in line['spans']]
    for label, color in (('Primary', 0x245C80), ('Tip', 0x167048), ('Note', 0x4F4A8C),
                         ('Alert', 0xB52D35), ('Example', 0x247878), ('Definition', 0x925919)):
        if not any(span['text'].strip() == label and span['color'] == color for span in spans):
            raise RuntimeError(f'profile-selection: wrong functional color: {label}')
    for index in (0, 1, 5):
        pixmap = document[index].get_pixmap()
        if any(abs(a - b) > 1 for a, b in
               zip(pixmap.pixel(pixmap.width - 3, 60), (36, 92, 128))):
            raise RuntimeError('profile-selection: cover/section background did not switch')
    for page in (document[3], document[4]):
        pixmap = page.get_pixmap()
        if any(abs(a - b) > 1 for a, b in
               zip(pixmap.pixel(2, pixmap.height - 3), (36, 92, 128))):
            raise RuntimeError('profile-selection: footer did not switch')


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
    caption = '本机代理经 SSH 通道连接远程服务器的示意路径'
    caption_boxes = caption_rects(page, caption)
    caption_top = min((box.y0 for box in caption_boxes), default=page.rect.height - 40)
    node_boxes = [box for label in ('本机', 'SSH', '远程')
                  for box in page.search_for(label) if 45 < box.y0 < caption_top]
    if len(node_boxes) != 3:
        raise RuntimeError('flow-layout: expected three visible nodes')
    bottom = max(box.y1 for label in ('本机', '代理', 'SSH', '通道', '远程', '服务器', '请求', '转发')
                 for box in page.search_for(label) if 45 < box.y0 < caption_top)
    # Node rectangles extend beyond their text; use their painted geometry too.
    bodies = [drawing['rect'] for drawing in page.get_drawings()
              if drawing.get('fill') and 45 < drawing['rect'].y0
              and drawing['rect'].y1 < caption_top]
    if bodies:
        bottom = max(bottom, max(box.y1 for box in bodies))
    nodes = sorted((box for box in bodies if box.width > 80 and box.height > 20),
                   key=lambda box: box.x0)
    check_flow_geometry(nodes)
    check_caption_below(page, caption, bottom, footer_top=page.rect.height - 40)


def check_flow_geometry(nodes):
    """Inspect the fixture's three equal peer nodes and actual border gaps."""
    if len(nodes) != 3:
        raise RuntimeError('flow-layout: expected three painted node borders')
    for dimension in (lambda r: r.width, lambda r: r.height,
                      lambda r: (r.y0 + r.y1) / 2):
        values = [dimension(node) for node in nodes]
        if max(values) - min(values) > .5:
            raise RuntimeError('flow-layout: node sizes or centers are not aligned')
    gaps = [right.x0 - left.x1 for left, right in zip(nodes, nodes[1:])]
    if abs(gaps[0] - gaps[1]) > .5:
        raise RuntimeError('flow-layout: peer-node gaps are not equal')
    # The fixture uses 2.2 mm arrowheads. Require a shaft at least that long too.
    if min(gaps) < 2 * 2.2 * 72 / 25.4:
        raise RuntimeError('flow-layout: connector gap leaves no clear arrow shaft')


def prepare_background_fixtures(workspace):
    """Generate vector probes with a centered square, no external assets."""
    (workspace / 'build').mkdir(exist_ok=True)
    for name, width, height in (('wide', 400, 100), ('tall', 100, 400)):
        with pymupdf.open() as document:
            page = document.new_page(width=width, height=height)
            page.draw_rect(page.rect, color=None, fill=(.2, .6, .8))
            page.draw_rect(pymupdf.Rect(width / 2 - 5, height / 2 - 5,
                                       width / 2 + 5, height / 2 + 5),
                           color=None, fill=(1, 0, 0))
            document.save(workspace / 'build' / f'style-{name}.pdf')


def check_toc_overview(document, log):
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('toc-overview: overflow or missing glyphs')
    overviews = [document[index] for index in (0, 3, 5)]
    pixels = [page.get_pixmap().samples for page in overviews]
    if any(value != pixels[0] for value in pixels[1:]):
        raise RuntimeError('toc-overview: appearance depends on current section')
    for page in overviews:
        entries = [span for block in page.get_text('dict')['blocks']
                   for line in block.get('lines', []) for span in line['spans']
                   if span['text'] in ('Alpha', 'Beta')]
        if len(entries) != 2 or len({(s['color'], s['size'], s['font']) for s in entries}) != 1:
            raise RuntimeError('toc-overview: sections do not have uniform emphasis')
        targets = {link.get('page') for link in page.get_links()}
        if not {1, 4}.issubset(targets):
            raise RuntimeError('toc-overview: missing section jumps')
    if document[2].get_pixmap().samples == pixels[0]:
        raise RuntimeError('toc-overview: default current-section highlight was lost')


def check_page_styles(document, log):
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('page-styles: overflow or missing glyphs')
    for index, page in enumerate(document):
        focus = 1 <= index <= 8
        # Context is the subsection label in both the header and nav footer.
        if ('Context' in page.get_text()) == focus:
            raise RuntimeError('page-styles: header/navigation style leaked or was ignored')
        if not page.search_for('Template check | Page styles'):
            raise RuntimeError('page-styles: bottom footer is missing')
    for index, scale, opacity in ((2, 2.55118, 1), (3, 2.55118, 1),
                                  (4, 4.53543, .5)):
        page = document[index]
        probes = [drawing for drawing in page.get_drawings()
                  if drawing.get('fill') == (1., 0., 0.)]
        if len(probes) != 1:
            raise RuntimeError('page-styles: missing background center probe')
        probe = probes[0]
        rect = probe['rect']
        if (abs(rect.width - 10 * scale) > .1 or abs(rect.height - rect.width) > .1
                or abs((rect.x0 + rect.x1) / 2 - page.rect.width / 2) > .1
                or abs((rect.y0 + rect.y1) / 2 - page.rect.height / 2) > .1
                or abs(probe['fill_opacity'] - opacity) > .01):
            raise RuntimeError('page-styles: cover scale, center or opacity is wrong')
        # Sampling corners below the header and above the footer also checks crop coverage.
        pixmap = page.get_pixmap()
        expected = tuple(round(255 * (1 - opacity + opacity * c)) for c in (.2, .6, .8))
        for x, y in ((2, 60), (pixmap.width - 3, 60),
                     (2, pixmap.height - 25), (pixmap.width - 3, pixmap.height - 25)):
            if any(abs(a - b) > 3 for a, b in zip(pixmap.pixel(x, y), expected)):
                raise RuntimeError('page-styles: background leaves an uncovered edge')
    for index in (1, 5, 6, 7, 8, 9):
        if document[index].get_pixmap().pixel(2, 60) != (255, 255, 255):
            raise RuntimeError('page-styles: invisible background or restoration is wrong')


def check_description_rows(page, labels, markers, *, tolerance=.5):
    """Check logical text edges rather than inferring widths from character counts."""
    right_edges = []
    starts = []
    for label, marker in zip(labels, markers):
        boxes = page.search_for(label)
        bodies = page.search_for(marker)
        if not boxes or len(bodies) != 1:
            raise RuntimeError(f'description-alignment: missing or ambiguous row {label!r}')
        right_edges.append(max(box.x1 for box in boxes))
        starts.append(bodies[0].x0)
    if max(right_edges) - min(right_edges) > tolerance:
        raise RuntimeError('description-alignment: label right edges differ')
    if max(starts) - min(starts) > tolerance:
        raise RuntimeError('description-alignment: explanation column starts differ')
    if min(starts) <= max(right_edges):
        raise RuntimeError('description-alignment: labels overlap explanations')


def check_description_alignment(document, log):
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('description-alignment: overflow or missing glyphs')
    cases = (
        (0, ('Host / HostName', 'User', 'IdentityFile', 'IdentitiesOnly'),
         ('TextA', 'TextB', 'TextC', 'TextD')),
        (1, ('主机别名与地址', '用户', '认证文件'), ('TextA', 'TextB', 'TextC')),
        (2, ('Host 主机名', 'User 用户', 'IdentityFile 密钥路径'), ('TextA', 'TextB', 'TextC')),
        (3, ('User', 'IdentitiesOnly'), ('TextA', 'TextB')),
        (3, ('来源', '本地材料路径'), ('TextC', 'TextD')),
    )
    for index, labels, markers in cases:
        check_description_rows(document[index], labels, markers)


def caption_rects(page, text):
    boxes = page.search_for(text)
    if boxes:
        return boxes
    # CJK/Latin spacing in PDF extraction can differ from the TeX source.
    needle = ''.join(text.split())
    return [pymupdf.Rect(line['bbox']) for block in page.get_text('dict')['blocks']
            for line in block.get('lines', [])
            if needle in ''.join(''.join(span['text'] for span in line['spans']).split())]


def check_caption_below(page, text, graphic_bottom, *, footer_top):
    """A visible caption must follow the graphic and clear the footer."""
    boxes = caption_rects(page, text)
    if not boxes:
        raise RuntimeError('flow-layout: missing figure caption')
    if min(box.y0 for box in boxes) <= graphic_bottom:
        raise RuntimeError('flow-layout: caption overlaps the graphic')
    if max(box.y1 for box in boxes) >= footer_top:
        raise RuntimeError('flow-layout: caption overlaps the footer')


def check_callout_layout(document, log):
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('callout-layout: overflow or missing glyphs')
    page = document[0]
    labels = [box for text in ('大纲阶段', '制作阶段') for box in page.search_for(text)]
    title = page.search_for('制作前提')
    condition = page.search_for('详细大纲已确认')
    if len(labels) != 2 or not title or not condition:
        raise RuntimeError('callout-layout: missing primary structure or condition heading')
    if title[0].y0 <= max(box.y1 for box in labels) or condition[0].y0 <= title[0].y1:
        raise RuntimeError('callout-layout: conditions do not follow the primary structure')
    if condition[0].y1 >= page.rect.height - 40:
        raise RuntimeError('callout-layout: condition box touches the footer')


DOC_SOURCE_CASES = (
    (('Example documentation', 'https://example.org/'),),
    (('配置文档', 'https://example.org/config#Options'),),
    (('Configuration reference', 'https://example.org/config#Forward'),
     ('Video reference', 'https://example.org/watch?v=demo123&lang=zh&q=alpha%20beta')),
    (('Detailed reference', 'https://example.org/documentation/configuration/network/connection/settings?mode=reference&lang=en#Forward'),),
    (('Extended reference', 'https://example.org/documentation/configuration/network/connection/settings/advanced/troubleshooting?mode=reference&lang=en#Forward'),),
    (('Wide reference', 'https://example.org/width'),),
    (('Default reference', 'https://example.org/reset'),),
)


def check_doc_citations(document, log):
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('doc-citations: overflow or missing glyphs')
    for index, (page, sources) in enumerate(zip(document, DOC_SOURCE_CASES)):
        spans = [span for block in page.get_text('dict')['blocks']
                 for line in block.get('lines', []) for span in line['spans']]
        corner = [span for span in spans if span['bbox'][0] > page.rect.width / 2
                  and span['bbox'][1] < 90 and span['size'] < 7]
        headers = [pymupdf.Rect(span['bbox']) for span in spans
                   if span['bbox'][1] < 45 and span['size'] > 10]
        visible = ''.join(page.get_text().split())
        corner_text = ''.join(''.join(span['text'].split()) for span in corner)
        for label, url in sources:
            if ''.join(label.split()) not in corner_text:
                raise RuntimeError(f'doc-citations: missing corner source {label!r}')
            if url not in visible or (index != 4 and url not in corner_text):
                raise RuntimeError(f'doc-citations: URL is not visible in its source block: {url}')
            links = [link for link in page.get_links() if link.get('uri') == url]
            if not links or (index != 4 and not all(link['from'].y0 < 90 for link in links)):
                raise RuntimeError(f'doc-citations: URL target/position changed: {url}')
            if index == 4 and not any(link['from'].y0 > 90 for link in links):
                raise RuntimeError('doc-citations: compact source lacks a full body URL')
        for span in corner:
            box = pymupdf.Rect(span['bbox'])
            gray = all(abs(((span['color'] >> shift) & 255) - 128) <= 1
                       for shift in (16, 8, 0))
            if abs(span['size'] - 6 * 72 / 72.27) > .05 or not gray:
                raise RuntimeError('doc-citations: citation font/color changed or was reduced')
            if any(box.intersects(header) for header in headers) or box.x1 > page.rect.width - 10:
                raise RuntimeError('doc-citations: header/page-edge collision')
        if not corner or min(span['bbox'][1] for span in corner) > 20:
            raise RuntimeError('doc-citations: top-right anchor changed')
    # Explicit frame width must not leak into the next frame.
    wide = document[5].search_for('Wide reference')[0]
    default = document[6].search_for('Default reference')[0]
    if abs(default.x0 - wide.x0 - (5 * 72 / 2.54 - document[6].rect.width * .3)) > .5:
        raise RuntimeError('doc-citations: width override leaked between frames')


def check_native_notes(document, log, *, shown=False):
    """A hidden PDF must not carry note text; a notes screen keeps every stage."""
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('native-notes: overflow or missing glyphs')
    if pdf_info_string(document, 'CampusNotesLayout') != ('right' if shown else 'none'):
        raise RuntimeError('native-notes: wrong PDF layout marker')
    expected = ('第一阶段', '第二阶段', '', '总结')
    for page, marker in zip(document, expected):
        if abs(page.rect.width / page.rect.height - (32 / 9 if shown else 16 / 9)) > .001:
            raise RuntimeError('native-notes: wrong page aspect ratio')
        if not shown:
            if 'SpeakerOnly' in page.get_text():
                raise RuntimeError('native-notes: notes leaked into the default PDF')
        else:
            left = pymupdf.Rect(0, 0, page.rect.width / 2, page.rect.height)
            right = pymupdf.Rect(page.rect.width / 2, 0, page.rect.width, page.rect.height)
            audience = page.get_text(clip=left)
            notes = page.get_text(clip=right).strip()
            if 'SpeakerOnly' in audience or (marker and marker not in notes) or (not marker and notes):
                raise RuntimeError('native-notes: note content leaked or shifted between stages')
            if marker == '第二阶段' and 'CC0-1.0' not in notes:
                raise RuntimeError('native-notes: numeric note text changed during extraction')


def check_overlays(document, log, *, handout=False):
    """Reveal states must survive compilation without shifting retained content."""
    if 'Overfull' in log or 'Missing character:' in log:
        raise RuntimeError('overlays: overflow or missing glyphs')
    states = (('Alpha', 'Beta', 'Gamma'), ('AfterState',), ()) if handout else (
        ('Alpha',), ('Alpha', 'Beta'), ('Alpha', 'Beta', 'Gamma'),
        ('BeforeState',), ('AfterState',), ())
    labels = ('Alpha', 'Beta', 'Gamma', 'BeforeState', 'AfterState')
    for index, (page, expected) in enumerate(zip(document, states)):
        text = page.get_text()
        for label in labels:
            if (label in text) != (label in expected):
                raise RuntimeError(f'overlays: wrong reveal state on page {index + 1}: {label}')
        if 'Ordered explanation' not in text:
            raise RuntimeError('overlays: missing subsection header')
        style = document.xref_get_key(page.xref, 'Trans/S')[1]
        expected_style = '/Fade' if not handout and index in (1, 2) else (
            '/Dissolve' if not handout and index == 4 else '/R')
        if style != expected_style:
            raise RuntimeError(f'overlays: transition leaked or disappeared on page {index + 1}')
        if document.xref_get_key(page.xref, 'Dur')[0] != 'null':
            raise RuntimeError('overlays: unexpected automatic advance')
    if not handout:
        boxes = [page.search_for('Alpha')[0] for page in list(document)[:3]]
        if max(box.y0 for box in boxes) - min(box.y0 for box in boxes) > .5:
            raise RuntimeError('overlays: cumulative list jumps between stages')


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


def check_public_demo(document):
    """The public tour must exercise real reveal states and working links."""
    guide = next(page for page in document if page.search_for('版式对齐检查'))
    blocks = [drawing['rect'] for drawing in guide.get_drawings()
              if drawing.get('fill') == (0.0, 0.0, 0.0)
              and abs(drawing['rect'].y0) < .1
              and 0 < drawing['rect'].x0 < 50
              and drawing['rect'].width < 80]
    # Default 11pt Beamer fonts: Huge baseline 30pt + tiny baseline 7pt.
    # PDF coordinates use 72 points/inch; TeX dimensions use 72.27.
    if len(blocks) != 1 or abs(blocks[0].width - 37 * 72 / 72.27) > .1:
        raise RuntimeError('public demo: emblem block must be Huge + tiny baselines (37pt)')
    guide_text = ''.join(guide.get_text().split())
    if r'1baselineskip(\Huge)+1baselineskip(\tiny)=37.0pt' not in guide_text:
        raise RuntimeError('public demo: emblem width annotation is out of sync')
    overview = document[1]
    if not overview.search_for('目录') or len(overview.get_links()) != 5:
        raise RuntimeError('public demo: missing complete overview and section links')
    # The current-section TOC keeps other entries legible on general's black.
    inactive_colors = caption_colors(document[19], '基础页面与图像')
    if not inactive_colors or any(color < 0x808080 for color in inactive_colors):
        raise RuntimeError('public demo: inactive TOC entries are too dark')
    for title in ('简洁页面', '居中图片背景'):
        page = next(page for page in document if page.search_for(title))
        if page.search_for('基础页面') or not page.search_for('| Campus Beamer'):
            raise RuntimeError('public demo: focus frame header/footer is wrong')
    diagram = next(page for page in document if page.search_for('流程图布局'))
    nodes = sorted((drawing['rect'] for drawing in diagram.get_drawings()
                    if drawing.get('fill') and drawing['rect'].width > 80
                    and drawing['rect'].height > 20
                    and 50 < drawing['rect'].y0 < drawing['rect'].y1 < 200),
                   key=lambda rect: rect.x0)
    check_flow_geometry(nodes)
    reveals = [page for page in document if page.search_for('按讲述顺序呈现要点')]
    replacements = [page for page in document if page.search_for('在固定区域内替换内容')]
    if len(reveals) != 3 or len(replacements) != 2:
        raise RuntimeError('public demo: missing overlay stages')
    for stage, page in enumerate(reveals):
        for item, marker in enumerate(('问题：', '证据：', '结论：')):
            if bool(page.search_for(marker)) != (item <= stage):
                raise RuntimeError('public demo: wrong cumulative reveal state')
        style = document.xref_get_key(page.xref, 'Trans/S')[1]
        if stage > 0 and style != '/Fade':
            raise RuntimeError('public demo: missing fade transition')
    if len({tuple(page.search_for('先明确这一页要回答什么。')[0])
            for page in reveals}) != 1:
        raise RuntimeError('public demo: retained reveal content moved')
    markers = ('输入：自由草稿', '输出：详细大纲')
    for stage, page in enumerate(replacements):
        if not page.search_for(markers[stage]) or page.search_for(markers[1-stage]):
            raise RuntimeError('public demo: wrong replacement state')
    if replacements[0].search_for(markers[0])[0].tl != replacements[1].search_for(markers[1])[0].tl:
        raise RuntimeError('public demo: replacement region moved')
    if document.xref_get_key(replacements[1].xref, 'Trans/S')[1] != '/Dissolve':
        raise RuntimeError('public demo: missing dissolve transition')
    notes = next(page for page in document if page.search_for('正文与备注分工'))
    for marker in ('shownotes=false', 'shownotes=true'):
        if not notes.search_for(marker):
            raise RuntimeError(f'public demo: missing notes option {marker}')
    navigation = next(page for page in document if page.search_for('导航与帧标签'))
    targets = {link.get('page') for link in navigation.get_links()}
    if not {reveals[0].number, notes.number} <= targets:
        raise RuntimeError('public demo: frame label links target the wrong stage')
    if any(page.search_for('讲者提示：') for page in document):
        raise RuntimeError('public demo: speaker-only note leaked into default PDF')


def caption_colors(page, text):
    """Read the painted colors of a caption substring, including mixed fonts."""
    rectangles = page.search_for(text)
    colors = {span['color']
              for block in page.get_text('rawdict')['blocks'] if block['type'] == 0
              for line in block['lines'] for span in line['spans']
              for char in span['chars']
              if any((pymupdf.Rect(char['bbox']).tl +
                      pymupdf.Rect(char['bbox']).br) / 2 in rect for rect in rectangles)}
    if not colors:
        raise RuntimeError(f'missing caption text: {text}')
    return colors


def check_caption_style(page, label, body, label_color, body_color):
    if caption_colors(page, label) != {label_color}:
        raise RuntimeError(f'caption label color differs from figures: {label}')
    if caption_colors(page, body) != {body_color}:
        raise RuntimeError(f'caption body color differs from figures: {body}')


def check_class_fixture(name, document, log):
    if name != 'profile-general-legacy' and 'biblatex.sty' not in log:
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
    if name == 'demo-without-guides':
        check_public_demo(document)
        reference = next(page for page in document if page.search_for('图:'))
        label_color, = caption_colors(reference, '图:')
        reference = next(page for page in document
                         if page.search_for('横向标志素材的适配效果'))
        body_color, = caption_colors(reference, '横向标志素材的适配效果')
        for page in document:
            if page.search_for('保留缩进，便于讲解函数结构。'):
                check_caption_style(page, '代码:', '保留缩进，便于讲解函数结构。',
                                    label_color, body_color)
            if page.search_for('原创动画：大纲'):
                check_caption_style(page, '视频:', '原创动画：大纲', label_color, body_color)
    if name == 'code-windows':
        label_color, = caption_colors(document[5], 'Figure:')
        body_color, = caption_colors(document[5], 'Figure caption body.')
        for label, body in (('Figure:', 'Figure caption body.'),
                            ('Table:', 'Table caption body.'),
                            ('Video:', 'Video caption body.')):
            check_caption_style(document[5], label, body, label_color, body_color)
        if len(document[5].search_for('Video:')) != 1:
            raise RuntimeError('code-windows: empty video caption left a label')
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
        # Check actual painted code boundaries, not just relative text order.
        cases = (
            (0, 'train_model.py', 'Python', 'print', '保留缩进并显示中文注释。'),
            (1, 'Terminal', 'Shell', 'shell output', '静态命令与输出示例。'),
            (1, 'reset.py', 'Python', 'Python again', None),
            (2, 'normalize.py', 'Python', 'total', '从文件读取选定行。'),
            (3, 'demo.cpp', 'C++', 'return', None),
            (3, '输出日志', 'Output', 'A long output', '输出不会覆盖相邻列。'),
            (4, '~/.ssh/config', 'Config', 'RemoteForward', 'SSH 配置示例。'),
        )
        for index, filename, label, code, caption in cases:
            page = document[index]
            bodies = [drawing['rect'] for drawing in page.get_drawings()
                      if drawing.get('fill') and all(
                          abs(actual - expected / 255) < .001
                          for actual, expected in zip(drawing['fill'], (32, 36, 44)))]
            code_rects = page.search_for(code)
            matching = [body for body in bodies
                        if any(body.contains(rect) for rect in code_rects)]
            if len(matching) != 1:
                raise RuntimeError(f'{name}: {filename}: code is not inside one code area')
            body = matching[0]
            for marker in (filename, label):
                if not any(body.x0 <= rect.x0 < rect.x1 <= body.x1
                           and body.y0 - 25 <= rect.y0 < rect.y1 <= body.y0
                           for rect in page.search_for(marker)):
                    raise RuntimeError(f'{name}: {filename}: {marker} is not above code')
            if caption:
                check_caption_style(page, 'Code:', caption, label_color, body_color)
                rects = page.search_for(caption)
                # Mixed CJK/Latin fonts can yield multiple rectangles for one caption.
                occurrences = ''.join(page.get_text().split()).count(''.join(caption.split()))
                if occurrences != 1 or not rects or not all(
                        body.y1 < rect.y0 < body.y1 + 15
                        and body.x0 <= rect.x0 < rect.x1 <= body.x1 for rect in rects):
                    raise RuntimeError(f'{name}: {filename}: caption outside expected area')
        if document[4].search_for('Shell'):
            raise RuntimeError(f'{name}: configuration file was labelled Shell')
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
        ('unknown-theme', 'theme=missing-school', '', 'xelatex', 'Unknown theme'),
        ('invalid-theme', 'theme=../tsinghua', '', 'xelatex', 'Invalid theme name'),
        ('incomplete-palette', 'theme=missing-color', '', 'xelatex', "missing color 'tipcolor'"),
        ('incomplete-identity', 'theme=missing-logo', '', 'xelatex', "missing 'schoolwordmarkonlight'"),
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
        ('image-title-background', 'language=english', r'\titlebackground{theme/tsinghua/assets/sigs_building}',
         'xelatex', 'Only primary is supported for title backgrounds'),
        ('removed-guides-on', 'language=english', r'\campuslayoutguidestrue',
         'xelatex', 'Undefined control sequence'),
        ('removed-guides-off', 'language=english', r'\campuslayoutguidesfalse',
         'xelatex', 'Undefined control sequence'),
        ('bad-toc-style', 'language=english', r'\sectiontocpage[unknown]',
         'xelatex', 'Unknown sectiontocpage style'),
        ('bad-opacity-low', 'language=english',
         r'\begin{frame}[campusfocus,campusbackgroundopacity=-.1]{Test}Body\end{frame}',
         'xelatex', 'Background opacity must be between 0 and 1'),
        ('bad-opacity-high', 'language=english',
         r'\begin{frame}[campusfocus,campusbackgroundopacity=1.1]{Test}Body\end{frame}',
         'xelatex', 'Background opacity must be between 0 and 1'),
    )
    with tempfile.TemporaryDirectory(prefix='campus-class-errors-') as temp:
        workspace = Path(temp)
        shutil.copytree(root / 'theme', workspace / 'theme')
        profile = prepare_profile_fixture(workspace)
        for name, omitted in (('missing-color', r'\definecolor{tipcolor}'),
                              ('missing-logo', r'\newcommand{\schoolwordmarkonlight}')):
            directory = workspace / 'theme' / name
            directory.mkdir()
            (directory / 'profile.tex').write_text('\n'.join(
                line for line in profile.splitlines() if not line.startswith(omitted)))
        # These negative checks call engines directly, bypassing .latexmkrc.
        env = os.environ.copy()
        env['TEXINPUTS'] = str(workspace / 'theme') + '//' + os.pathsep + env.get('TEXINPUTS', '')
        (workspace / 'assets').symlink_to(root / 'assets', target_is_directory=True)
        for name, options, preamble, engine, expected in cases:
            body = r'\begin{frame}{Test}Body\end{frame}'
            if name in ('bad-toc-style', 'bad-opacity-low', 'bad-opacity-high'):
                body, preamble = preamble, ''
            source = (f'\\documentclass[{options}]{{campusbeamer}}\n{preamble}\n'
                      f'\\begin{{document}}{body}\\end{{document}}\n')
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
            shutil.copytree(root / 'examples', workspace / 'examples')
            shutil.copytree(root / 'theme', workspace / 'theme')
            (workspace / 'assets').symlink_to(root / 'assets', target_is_directory=True)
            shutil.copy2(root / 'tools/fixtures' / f'{name}.tex', workspace / f'{name}.tex')
            if name == 'page-styles':
                prepare_background_fixtures(workspace)
            if name.startswith('profile-general'):
                shutil.rmtree(workspace / 'theme/tsinghua')
                shutil.rmtree(workspace / 'theme/pcl')
            if name.startswith('profile-selection'):
                prepare_profile_fixture(workspace)
                shutil.rmtree(workspace / 'theme/tsinghua')
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
                if name.startswith('profile-general'):
                    if 'Overfull' in result.stdout or 'Missing character:' in result.stdout:
                        raise RuntimeError(f'{name}: overflow or missing glyphs')
                    body = document[4 if name == 'profile-general' else 1]
                    pixmap = body.get_pixmap()
                    if pixmap.pixel(2, pixmap.height - 3) != (0, 0, 0):
                        raise RuntimeError(f'{name}: default primary color must be pure black')
                    if 'CAMPUS' not in document[0].get_text():
                        raise RuntimeError(f'{name}: default cover must use the project wordmark')
                if name == 'profile-tokyo-night':
                    check_tokyo_night(document, result.stdout)
                if name == 'profile-pcl':
                    if 'Overfull' in result.stdout or 'Missing character:' in result.stdout:
                        raise RuntimeError('profile-pcl: overflow or missing glyphs')
                    for page in (document[4], document[5]):
                        pixmap = page.get_pixmap()
                        if any(abs(a - b) > 1 for a, b in
                               zip(pixmap.pixel(2, pixmap.height - 3), (26, 86, 158))):
                            raise RuntimeError('profile-pcl: incorrect primary color')
                if name.startswith('profile-selection'):
                    check_profile_selection(document, result.stdout)
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
                if name == 'toc-overview':
                    check_toc_overview(document, result.stdout)
                if name == 'page-styles':
                    check_page_styles(document, result.stdout)
                if name == 'url-layout':
                    check_url_layout(document, result.stdout)
                if name == 'doc-citations':
                    check_doc_citations(document, result.stdout)
                if name == 'description-alignment':
                    check_description_alignment(document, result.stdout)
                if name == 'callout-layout':
                    check_callout_layout(document, result.stdout)
                if name in ('overlays', 'overlays-handout'):
                    check_overlays(document, result.stdout, handout=name.endswith('-handout'))
                if name in ('native-notes', 'native-notes-screen'):
                    check_native_notes(document, result.stdout, shown=name.endswith('-screen'))
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
