# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Conservative, opt-in PDF text reconstruction for PowerPoint.

One text box per line, split at font/style boundaries to preserve baselines.
Unsupported lines remain in the original rendered background. No OCR, font
substitution, font embedding, or changes to the input PDF are performed.
"""
from collections import Counter
from functools import lru_cache
from pathlib import Path
import re
import shutil
import subprocess
import unicodedata

import pymupdf
from pptx.dml.color import RGBColor
from pptx.opc.constants import RELATIONSHIP_TYPE
from pptx.oxml.ns import qn
from pptx.enum.text import MSO_AUTO_SIZE, MSO_ANCHOR
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml import parse_xml
from pptx.util import Pt


def font_key(name):
    name = re.sub(r'^[A-Z]{6}\+', '', name).removesuffix('-Identity-H')
    return re.sub(r'[^a-z0-9]', '', name.lower()).removesuffix('regular')


@lru_cache(maxsize=256)
def resolve_font(name):
    """Require an exact installed/TeX font; never accept fontconfig's fallback."""
    if not shutil.which('fc-match') or not shutil.which('fc-scan'):
        return None
    candidates = []
    result = subprocess.run(['fc-match', '-f', '%{file}', name], capture_output=True,
                            text=True, timeout=10, check=False)
    if result.returncode == 0 and result.stdout:
        candidates.append(result.stdout)
    if shutil.which('kpsewhich') and re.fullmatch(r'[\w.-]+', name):
        for extension in ('otf', 'ttf'):
            result = subprocess.run(['kpsewhich', f'{name}.{extension}'],
                                    capture_output=True, text=True, timeout=10, check=False)
            if result.returncode == 0:
                candidates.append(result.stdout.strip())
    for path in dict.fromkeys(candidates):
        result = subprocess.run(['fc-scan', '--format', '%{postscriptname}\n%{family}\n%{style}\n', path],
                                capture_output=True, text=True, timeout=10, check=False)
        fields = result.stdout.splitlines()
        if len(fields) < 3 or font_key(name) not in {font_key(n) for n in fields[0].split(',')}:
            continue
        try:
            font = pymupdf.Font(fontfile=path)
        except (RuntimeError, ValueError):
            continue
        return dict(family=fields[1].split(',')[0], path=str(Path(path).resolve()),
                    font=font, style=fields[2])
    return None


def line_text(line):
    return ''.join(c['c'] for s in line['spans'] for c in s['chars'])


def text_lines(page):
    lines = [line for block in page.get_text('rawdict')['blocks']
             for line in block.get('lines', [])]
    # ActualText supplies correct Unicode but can assign zero-width boxes to
    # several old-style digits. Recover only a one-to-one, verified glyph run;
    # never infer missing characters or expand ligatures speculatively.
    for trace in page.get_texttrace():
        candidates = [(span, char) for line in lines for span in line['spans']
                      if span['font'] == trace['font']
                      and abs(span['size'] - trace['size']) < .01
                      for char in span['chars']
                      if not char.get('synthetic')
                      and abs(char['origin'][1] - trace['chars'][0][2][1]) < .01
                      and trace['bbox'][0]-.01 <= char['origin'][0] <= trace['bbox'][2]+.01] if trace['chars'] else []
        if not any(pymupdf.Rect(c['bbox']).is_empty for _, c in candidates):
            continue
        if len(candidates) != len(trace['chars']):
            continue
        if any(code != 0xfffd and chr(code) != c['c']
               for (_, c), (code, _, _, _) in zip(candidates, trace['chars'])):
            continue
        for (span, char), (_, _, origin, bbox) in zip(candidates, trace['chars']):
            char.update(origin=origin, bbox=bbox)
        for line in lines:
            for span in line['spans']:
                span['chars'] = [c for c in span['chars'] if not (
                    c.get('synthetic') and span['font'] == trace['font']
                    and abs(c['origin'][1] - trace['chars'][0][2][1]) < .01
                    and trace['bbox'][0]-.01 <= c['origin'][0] <= trace['bbox'][2]+.01)]
    for line in lines:
        line['spans'] = [s for s in line['spans'] if s['chars']]
        rect = pymupdf.Rect()
        for span in line['spans']:
            box = pymupdf.Rect()
            for char in span['chars']:
                box |= pymupdf.Rect(char['bbox'])
            span.update(bbox=tuple(box), origin=span['chars'][0]['origin'])
            rect |= box
        line['bbox'] = tuple(rect)
    return [line for line in lines if line['spans']]


def char_counts(lines):
    return Counter(c['c'] for line in lines for s in line['spans']
                   for c in s['chars'] if not c['c'].isspace())


def rejection_reason(line, page, excluded):
    if page.rotation or line['wmode'] or tuple(line['dir']) != (1., 0.):
        return 'rotated or vertical text'
    rect = pymupdf.Rect(line['bbox'])
    if not page.rect.contains(rect):
        return 'text crosses page edge'
    if any(rect.intersects(area) for area in excluded):
        return 'video region'
    baselines = [s['origin'][1] for s in line['spans'] if s['chars']]
    if baselines and max(baselines) - min(baselines) > .5:
        return 'superscript, subscript or mixed baselines'
    for span in line['spans']:
        text = ''.join(c['c'] for c in span['chars'])
        if not text.strip():
            continue
        if re.search(r'(math|symbol|cmsy|cmex|cmmi|msam|msbm|cmr|cmss|cmbx|cmtt|cmti|lmroman|lmmath|caladea)',
                     span['font'], re.I):
            return 'math or special TeX font'
        if span.get('alpha', 255) != 255 or span.get('char_flags', 16) & (1 | 2 | 32):
            return 'opacity, decoration or clipping'
        if not span.get('char_flags', 16) & 16:
            return 'non-filled text'
        if any(unicodedata.category(c) in ('Co', 'Cc', 'Cs') or c == '\ufffd' for c in text):
            return 'unreliable Unicode text'
        resolved = resolve_font(span['font'])
        if resolved is None:
            return 'exact font unavailable: ' + span['font']
        font = resolved['font']
        if any(not font.has_glyph(ord(c)) for c in text if not c.isspace()):
            return 'font lacks extracted character'
        # XeTeX's legacy Carlito old-style digit map is not Unicode text.
        # Do not guess replacements: the Make exporter recompiles with ActualText.
        if 'carlito' in span['font'].lower() and any('\u0170' <= c <= '\u017f' for c in text):
            return 'legacy TeX character map; recompile with ActualText'
    return None


def prepare_text(page, excluded=()):
    """Return a disposable one-page PDF, editable lines, and an audit report."""
    lines = []
    for line in text_lines(page):
        spans = line['spans']
        # The footer's vertical separator is a TeX symbol, not an equation.
        # Keep that glyph as artwork without flattening the author/title text.
        if line['bbox'][1] > page.rect.height*.94 and any(
                ''.join(c['c'] for c in s['chars']).strip() == '|' for s in spans):
            lines.extend(dict(line, spans=[s], bbox=s['bbox']) for s in spans)
            continue
        # List markers are decoration, not part of a mathematical expression.
        # A TeX symbol font used for the marker must not flatten the label too.
        if len(spans) > 1 and ''.join(c['c'] for c in spans[0]['chars']).strip() in {
                '▶', '•', '●', '▪', '◦', '‣'}:
            label_box = pymupdf.Rect()
            for span in spans[1:]:
                label_box |= pymupdf.Rect(span['bbox'])
            label = dict(line, spans=spans[1:], bbox=tuple(label_box))
            if rejection_reason(label, page, excluded) is None:
                lines.append(dict(line, spans=spans[:1], bbox=spans[0]['bbox']))
                lines.append(label)
                continue
        lines.append(line)
    reasons = [rejection_reason(line, page, excluded) for line in lines]
    traces = page.get_texttrace()
    paint = page.get_bboxlog()
    drawings = page.get_drawings()
    strokes = {d['seqno']: d for d in drawings if d['type'] == 's'}
    # Text raised above the background would change stacking. Preserve text
    # intersected by later graphics or images rather than flattening that order.
    for i, line in enumerate(lines):
        if reasons[i]:
            continue
        rect = pymupdf.Rect(line['bbox'])
        seq = [t['seqno'] for t in traces if pymupdf.Rect(t['bbox']).intersects(rect)]
        if seq and any(kind in ('fill-image', 'fill-path', 'stroke-path', 'fill-shade')
                       and pymupdf.Rect(box).intersects(rect)
                       and (index not in strokes or stroke_overlaps(strokes[index], rect, page.rect))
                       for index, (kind, box) in enumerate(paint) if index > min(seq)):
            reasons[i] = 'overlapping later artwork'
    # A tiny interior rectangle removes a glyph without touching neighboring
    # line boxes. Reject intersecting fallback text before applying redactions.
    points = []
    for line in lines:
        dots = []
        for span in line['spans']:
            for char in span['chars']:
                rect = pymupdf.Rect(char['bbox'])
                if rect.is_empty:
                    continue
                center = (rect.tl + rect.br) / 2
                dots.append(pymupdf.Rect(center.x-.01, center.y-.01, center.x+.01, center.y+.01))
        points.append(dots)
    while True:
        changed = False
        retained = [pymupdf.Rect(c['bbox']) for i, line in enumerate(lines) if reasons[i]
                    for s in line['spans'] for c in s['chars']]
        for i, dots in enumerate(points):
            if not reasons[i] and any(r.intersects(dot) for r in retained for dot in dots):
                reasons[i] = 'overlap with retained text'
                changed = True
        if not changed:
            break
    clean = pymupdf.open()
    clean.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
    target = clean[0]
    selected = [line for i, line in enumerate(lines) if not reasons[i]]
    for i, dots in enumerate(points):
        if not reasons[i]:
            for dot in dots:
                target.add_redact_annot(dot, fill=None, cross_out=False)
    if selected:
        target.apply_redactions(images=0, graphics=0, text=0)
        expected = char_counts([line for i, line in enumerate(lines) if reasons[i]])
        if char_counts(text_lines(target)) != expected:
            clean.close()
            clean = pymupdf.open()
            clean.insert_pdf(page.parent, from_page=page.number, to_page=page.number)
            reasons = [reason or 'text removal verification failed' for reason in reasons]
            selected = []
    report = dict(page=page.number+1, editable_lines=len(selected),
                  retained=[dict(text=line_text(line), reason=reason)
                            for line, reason in zip(lines, reasons) if reason],
                  fonts=sorted({resolve_font(s['font'])['family'] for line in selected
                                for s in line['spans'] if ''.join(c['c'] for c in s['chars']).strip()}))
    # Match the actual colored footer bands, including optional navigation
    # rows. Center native glyph ink in each band rather than relying on a
    # client's default font leading or the old-style PDF digit metrics.
    bands = [d['rect'] for d in drawings
             if d['type'] == 'f' and d['rect'].width >= page.rect.width*.99
             and d['rect'].y0 > page.rect.height*.8
             and 0 < d['rect'].height < page.rect.height*.06]
    for line in selected:
        for band in bands:
            if all(band.y0 < s['origin'][1] <= band.y1 for s in line['spans']):
                line['footer_center'] = (band.y0 + band.y1)/2
                break
    return clean, selected, report


def stroke_overlaps(drawing, rect, page_rect):
    """Resolve inflated miter bounds without ignoring real overpainted text."""
    with pymupdf.open() as doc:
        page = doc.new_page(width=page_rect.width, height=page_rect.height)
        shape = page.new_shape()
        for item in drawing['items']:
            if item[0] == 'l':
                shape.draw_line(*item[1:])
            elif item[0] == 'c':
                shape.draw_bezier(*item[1:])
            elif item[0] == 're':
                shape.draw_rect(item[1])
            elif item[0] == 'qu':
                shape.draw_quad(item[1])
            else:
                return True
        shape.finish(width=drawing['width'], color=(0, 0, 0),
                     lineCap=max(drawing['lineCap']), lineJoin=int(drawing['lineJoin']),
                     dashes=drawing['dashes'], closePath=drawing['closePath'],
                     stroke_opacity=drawing.get('stroke_opacity', 1))
        shape.commit()
        pix = page.get_pixmap(clip=rect & page_rect, dpi=144, alpha=True)
        return any(pix.samples[3::4])


@lru_cache(maxsize=512)
def ink_center(font_path, text, size):
    """Measure native-font ink relative to its baseline (PDF coordinates)."""
    with pymupdf.open() as doc:
        page = doc.new_page(width=2000, height=200)
        page.insert_font(fontname='Measure', fontfile=font_path)
        page.insert_text((20, 100), text, fontname='Measure', fontsize=size)
        boxes = [box for kind, box in page.get_bboxlog() if kind == 'fill-text']
        return (min(b[1] for b in boxes)+max(b[3] for b in boxes))/2-100


def add_text(slide, lines, page_rect, placement, links=()):
    """Place native, unwrapped text; style spans retain their original x origins."""
    records = []
    left, top, width, _ = placement
    scale = width / page_rect.width
    for line in lines:
        # Distributed labels and separately positioned table entries must not
        # collapse into natural-width text. Split only explicit extra gaps;
        # ordinary words, kerning and ligature sequences stay together.
        pieces = []
        for span in line['spans']:
            chunks = [[]]
            for char in span['chars']:
                if chunks[-1]:
                    previous = chunks[-1][-1]
                    gap = char['origin'][0] - previous['bbox'][2]
                    if gap > span['size'] * .15 and not previous['c'].isspace():
                        chunks.append([])
                chunks[-1].append(char)
            for chars in chunks:
                if chars:
                    rect = pymupdf.Rect()
                    for char in chars:
                        rect |= pymupdf.Rect(char['bbox'])
                    pieces.append(dict(span, chars=chars, origin=chars[0]['origin'], bbox=tuple(rect)))
        for span in pieces:
            text = ''.join(c['c'] for c in span['chars'])
            if not text.strip():
                continue
            resolved = resolve_font(span['font'])
            font = resolved['font']
            x, baseline = span['origin']
            size = span['size']
            if 'footer_center' in line:
                baseline = line['footer_center'] - ink_center(resolved['path'], text, size)
            # DrawingML's first line sits one em below the unpadded box top.
            # Do not use the PDF subset's ascent (often altered by XeTeX).
            y = baseline - size
            w = max(pymupdf.Rect(span['bbox']).width, font.text_length(text, fontsize=size)) + size*.25
            h = size * (font.ascender - font.descender) + 2
            shape = slide.shapes.add_textbox(round(left+x*scale), round(top+y*scale),
                                           round(w*scale), round(h*scale))
            shape.name = 'Editable text: ' + text[:60]
            frame = shape.text_frame
            frame.clear()
            frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
            frame.word_wrap = False
            frame.auto_size = MSO_AUTO_SIZE.NONE
            frame.vertical_anchor = MSO_ANCHOR.TOP
            paragraph = frame.paragraphs[0]
            paragraph.space_before = paragraph.space_after = Pt(0)
            groups = []
            for char in span['chars']:
                box = pymupdf.Rect(char['bbox'])
                center = (box.tl + box.br) / 2
                owners = tuple(i for i, link in enumerate(links)
                               if link.get('from') is not None
                               and center in pymupdf.Rect(link['from']))
                if not groups or groups[-1][0] != owners:
                    groups.append((owners, []))
                groups[-1][1].append(char)
            for owners, chars in groups:
                run = paragraph.add_run()
                run.text = ''.join(c['c'] for c in chars)
                run.font.name = resolved['family']
                run.font.size = Pt(round(size*scale/12700, 2))
                run.font.bold = 'bold' in resolved['style'].lower() or bool(span['flags'] & 16)
                run.font.italic = 'italic' in resolved['style'].lower() or bool(span['flags'] & 2)
                run.font.underline = False
                run.font.color.rgb = RGBColor.from_string(f"{span['color']:06X}")
                properties = run._r.get_or_add_rPr()
                properties.set('kern', '0')
                for tag in ('a:ea', 'a:cs'):
                    element = OxmlElement(tag)
                    element.set('typeface', resolved['family'])
                    properties.append(element)
                rect = pymupdf.Rect()
                for char in chars:
                    rect |= pymupdf.Rect(char['bbox'])
                records.append((run, rect, owners, shape))
    return records


def bind_text_link(slide, records, index, rect, *, target=None, uri=None):
    """Bind native text runs; omit the overlay only for a text-sized link area."""
    matched = [(run, box, shape) for run, box, owners, shape in records if owners == (index,)]
    if not matched:
        return False
    union = pymupdf.Rect()
    for run, box, shape in matched:
        union |= box
        if all(owners == (index,) or not other.text.strip()
               for other, _, owners, owner_shape in records if owner_shape is shape):
            # A link on the textbox itself stays one editable object and avoids
            # clients (notably WPS) replacing the text color/underline style.
            if target is not None:
                shape.click_action.target_slide = target
            else:
                shape.click_action.hyperlink.address = uri
            continue
        if target is not None:
            properties = run._r.get_or_add_rPr()
            click = properties.get_or_add_hlinkClick()
            click.set(qn('r:id'), slide.part.relate_to(target.part, RELATIONSHIP_TYPE.SLIDE))
            click.set('action', 'ppaction://hlinksldjump')
        else:
            run.hyperlink.address = uri
        # Office's hyperlink-color extension keeps the source text color.
        # MS-ODRAWXML 2.35; plain solidFill alone can be overridden by the theme.
        click = run._r.rPr.hlinkClick
        extensions = OxmlElement('a:extLst')
        extension = OxmlElement('a:ext')
        extension.set('uri', '{A12FA001-AC4F-418D-AE19-62706E023703}')
        extension.append(parse_xml(
            '<ahyp:hlinkClr xmlns:ahyp="http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor" val="tx"/>'))
        extensions.append(extension)
        click.append(extensions)
        run.font.underline = False
    # Buttons, images and wide navigation cells retain their full hit areas.
    # Ordinary text annotations have only a small border around their glyphs.
    return (union + (-3, -3, 3, 3)).contains(pymupdf.Rect(rect))
