# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Rebuild explicitly tagged template decorations in PDF painting order.

Unmarked artwork is never guessed to be a template element. Raster segments
between tagged objects keep their transparency and stacking, including formulas
and photographs inside callouts. The input PDF is not modified.
"""
from io import BytesIO

import pikepdf
import pymupdf
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_SHAPE_TYPE
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn

PREFIX = 'campus-editable:'
PATH_PAINT = {'f', 'F', 'f*', 'S', 's', 'B', 'B*', 'b', 'b*'}
TEXT_PAINT = {'Tj', 'TJ', "'", '"'}
PAINT = PATH_PAINT | TEXT_PAINT | {'Do', 'sh', 'INLINE IMAGE'}


def paint_segments(instructions):
    """Associate paint instructions with the template's marked-content roles."""
    stack, segments = [], []
    for index, inst in enumerate(instructions):
        op = str(inst.operator)
        if op in ('BDC', 'BMC'):
            name = None
            if op == 'BDC' and str(inst.operands[0]) == '/CampusEditable':
                name = PREFIX + str(inst.operands[1]['/Role'])
            stack.append(name)
        elif op == 'EMC':
            if stack:
                stack.pop()
        elif op in PAINT:
            name = next((s for s in reversed(stack) if s), None)
            if not segments or segments[-1][0] != name:
                segments.append((name, []))
            segments[-1][1].append(index)
    return segments


def isolate(instructions, keep):
    """Suppress painting, preserving transforms, clipping and text advances."""
    result, render_mode, modes = [], 0, []
    for index, inst in enumerate(instructions):
        op = str(inst.operator)
        if op == 'q':
            modes.append(render_mode)
        elif op == 'Q' and modes:
            render_mode = modes.pop()
        elif op == 'Tr':
            render_mode = int(inst.operands[0])
        if op not in PAINT or index in keep:
            result.append(inst)
        elif op in PATH_PAINT:
            result.append(([], pikepdf.Operator('n')))
        elif op in TEXT_PAINT:
            result.extend([([3], pikepdf.Operator('Tr')), inst,
                           ([render_mode], pikepdf.Operator('Tr'))])
    return pikepdf.unparse_content_stream(result)


def rectangle(drawing):
    """Accept a single solid rectangle, including PGF's zero-radius corners."""
    if drawing['type'] != 'f' or drawing['fill'] is None:
        return False
    box = drawing['rect']
    if box.is_empty:
        return False
    points = []
    for item in drawing['items']:
        if item[0] == 're':
            if len(drawing['items']) != 1:
                return False
            return True
        if item[0] not in ('l', 'c'):
            return False
        vertices = item[1:]
        if not (max(p.x for p in vertices)-min(p.x for p in vertices) < .02
                or max(p.y for p in vertices)-min(p.y for p in vertices) < .02):
            return False
        if not points:
            points.append(vertices[0])
        elif abs(points[-1]-vertices[0]) > .02:
            return False
        points.append(vertices[-1])
    if len(points) < 4:
        return False
    area = abs(sum(a.x*b.y-b.x*a.y for a, b in zip(points, points[1:]+points[:1])))/2
    return abs(area-box.get_area()) < max(.02, box.get_area()*.0001)


def bounds(rect, page_rect, placement):
    left, top, width, _ = placement
    scale = width/page_rect.width
    return (round(left+rect.x0*scale), round(top+rect.y0*scale),
            max(1, round(rect.width*scale)), max(1, round(rect.height*scale)))


def add_rectangle(slide, drawing, page_rect, placement, name):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, *bounds(drawing['rect'], page_rect, placement))
    shape.name = name
    shape.shadow.inherit = False
    # Some viewers still apply effectRef from the default shape style even
    # with an empty effectLst. All appearance is explicit, so omit that style.
    style = shape._element.find(qn('p:style'))
    if style is not None:
        shape._element.remove(style)
    shape.fill.solid()
    color = drawing['fill']
    if len(color) == 1:
        color *= 3
    shape.fill.fore_color.rgb = RGBColor(*(round(min(1, max(0, c))*255) for c in color))
    opacity = drawing.get('fill_opacity', 1)
    if opacity < 1:
        alpha = OxmlElement('a:alpha')
        alpha.set('val', str(round(opacity*100000)))
        shape._element.spPr.solidFill[0].append(alpha)
    shape.line.fill.background()
    return shape


def add_graphics(slide, clean, placement, dpi):
    """Return groups/report, or None for an untagged legacy PDF page."""
    page_rect = clean[0].rect
    groups, report = {}, []
    with pikepdf.open(BytesIO(clean.tobytes())) as pdf:
        page = pdf.pages[0]
        instructions = pikepdf.parse_content_stream(page)
        segments = paint_segments(instructions)
        if not any(name for name, _ in segments):
            return None
        for number, (name, indexes) in enumerate(segments):
            role = name.removeprefix(PREFIX) if name else None
            page.Contents = pdf.make_stream(isolate(instructions, set(indexes)))
            buffer = BytesIO()
            pdf.save(buffer)
            with pymupdf.open(stream=buffer.getvalue(), filetype='pdf') as fragment:
                paths = fragment[0].get_drawings()
                native = (role and role != 'emblem' and paths
                          and all(str(instructions[i].operator) in PATH_PAINT for i in indexes)
                          and all(rectangle(d) for d in paths))
                if native:
                    group = groups.setdefault(role, dict(rect=pymupdf.Rect(), shapes=[]))
                    for path in paths:
                        shape = add_rectangle(slide, path, page_rect, placement, 'Template: '+role)
                        group['shapes'].append(shape)
                        group['rect'] |= path['rect']
                    report.append(dict(role=role, kind='native shapes', count=len(paths)))
                    continue
                rect = pymupdf.Rect()
                for kind, box in fragment[0].get_bboxlog():
                    if kind != 'ignore-text':
                        rect |= pymupdf.Rect(box)
                rect = (rect+(-1, -1, 1, 1)) & page_rect
                if rect.is_empty:
                    continue
                pix = fragment[0].get_pixmap(dpi=dpi, clip=rect, alpha=True, annots=False)
                # Pixmap rounds the clip to device pixels; place those actual
                # bounds to avoid rescaling edges or shifting a cropped emblem.
                actual = pymupdf.Rect(pix.x, pix.y, pix.x+pix.width, pix.y+pix.height)* (72/dpi)
                shape = slide.shapes.add_picture(BytesIO(pix.tobytes('png')),
                                                *bounds(actual, page_rect, placement))
                shape.name = 'Emblem' if role == 'emblem' else 'Artwork: '+(role or str(number))
            if role:
                report.append(dict(role=role, kind='independent image'))
    return groups, report


def group_template_objects(slide, groups, records, page_rect, placement):
    """Group callout/footer decoration with its contained text and link areas."""
    text_boxes = {}
    for _, rect, _, shape in records:
        if shape.shape_id not in text_boxes:
            text_boxes[shape.shape_id] = pymupdf.Rect()
        text_boxes[shape.shape_id] |= rect
    used = set()
    for role, group in sorted(groups.items(), key=lambda pair: pair[1]['rect'].get_area()):
        if not role.startswith(('box-', 'footer-')):
            continue
        rect = group['rect']
        # bounds() returns x/y/width/height rather than x0/y0/x1/y1.
        x, y, w, h = bounds(rect, page_rect, placement)
        padding = 3*placement[2]/page_rect.width
        members = list(group['shapes'])
        member_ids = {s.shape_id for s in members}
        for shape in list(slide.shapes):
            if shape.shape_id in used or shape.shape_id in member_ids:
                continue
            if shape.shape_type == MSO_SHAPE_TYPE.MEDIA:
                continue
            text_box = text_boxes.get(shape.shape_id)
            if text_box is not None:
                include = rect.contains((text_box.tl+text_box.br)/2)
            else:
                include = (shape.left >= x-padding and shape.top >= y-padding
                           and shape.left+shape.width <= x+w+padding
                           and shape.top+shape.height <= y+h+padding)
            if include:
                members.append(shape)
                member_ids.add(shape.shape_id)
        if members:
            combined = slide.shapes.add_group_shape(members)
            combined.name = 'Template group: '+role
            used.update(member_ids)
            used.add(combined.shape_id)
