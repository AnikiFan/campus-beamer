# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Structured decoration conversion, transparency, grouping and link tests."""
from contextlib import redirect_stdout, redirect_stderr
from io import BytesIO, StringIO
from pathlib import Path
import sys
import tempfile
import unittest

import pymupdf
from PIL import Image
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from editable_graphics import add_graphics
from editable_text import resolve_font
from images_to_ppt import convert_pdf_to_pptx


def mark(page, role):
    doc = page.parent
    xref = page.get_contents()[-1]
    doc.update_stream(xref, b'/CampusEditable <</Role ('+role.encode()+b')>> BDC\n'
                      + doc.xref_stream(xref) + b'\nEMC')


def descendants(shapes):
    for shape in shapes:
        yield shape
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from descendants(shape.shapes)


class EditableGraphicsTests(unittest.TestCase):
    def test_unmarked_artwork_is_not_guessed_to_be_template_shapes(self):
        with pymupdf.open() as doc:
            page = doc.new_page(width=240, height=135)
            page.draw_rect((10, 10, 100, 100), fill=(1, 0, 0))
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            self.assertIsNone(add_graphics(slide, doc, (0, 0, 3048000, 1714500), 72))
            self.assertEqual(len(slide.shapes), 0)

    def test_emblem_is_transparent_and_background_is_native(self):
        with pymupdf.open() as doc:
            page = doc.new_page(width=240, height=135)
            page.draw_rect(page.rect, color=None, fill=(.5, .5, .5))
            page.draw_rect((10, 0, 40, 30), color=None, fill=(0, 0, 0))
            mark(page, 'logo-background')
            page.draw_polyline([(15, 20), (25, 5), (35, 20), (15, 20)],
                               color=None, fill=(1, 1, 1))
            mark(page, 'emblem')
            before = page.read_contents()
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            groups, report = add_graphics(slide, doc, (0, 0, 3048000, 1714500), 144)
            self.assertEqual(page.read_contents(), before)
            self.assertEqual(slide.shapes[1].shape_type, MSO_SHAPE_TYPE.AUTO_SHAPE)
            self.assertEqual(str(slide.shapes[1].fill.fore_color.rgb), '000000')
            self.assertFalse(slide.shapes[1].shadow.inherit)
            self.assertNotIn('effectRef', slide.shapes[1]._element.xml)
            emblem = slide.shapes[2]
            self.assertEqual(emblem.name, 'Emblem')
            with Image.open(BytesIO(emblem.image.blob)) as png:
                self.assertEqual(png.mode, 'RGBA')
                self.assertEqual(png.getpixel((0, 0))[3], 0)
                self.assertEqual(png.getpixel((png.width//2, png.height//2))[:3], (255, 255, 255))

    def test_callout_and_footer_group_text_links_and_fallback_artwork(self):
        font = resolve_font('Carlito')
        if font is None:
            self.skipTest('Carlito is needed')
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder)/'source.pdf', Path(folder)/'output.pptx'
            with pymupdf.open() as doc:
                page = doc.new_page(width=240, height=135)
                page.draw_rect(page.rect, color=None, fill=(1, 1, 1))
                page.draw_rect((20, 35, 220, 100), color=None, fill=(.8, .9, 1))
                mark(page, 'box-1')
                page.insert_font(fontname='Body', fontfile=font['path'])
                page.insert_text((30, 55), 'Editable callout', fontname='Body', fontsize=12)
                page.insert_text((30, 80), 'a+b', fontname='symb', fontsize=12)
                page.insert_link({'kind': pymupdf.LINK_URI,
                                  'from': page.search_for('Editable callout')[0],
                                  'uri': 'https://example.org'})
                page.draw_rect((0, 120, 240, 135), color=None, fill=(0, 0, 0))
                mark(page, 'footer-test')
                page.insert_text((20, 132), '1/2', fontname='Body', fontsize=8, color=(1, 1, 1))
                doc.save(source)
            before = source.read_bytes()
            with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                convert_pdf_to_pptx(source, output, dpi=96, editable_text=True, auto_notes=False)
            self.assertEqual(source.read_bytes(), before)
            deck = Presentation(output)
            groups = {s.name: s for s in deck.slides[0].shapes if s.shape_type == MSO_SHAPE_TYPE.GROUP}
            box = groups['Template group: box-1']
            children = list(descendants(box.shapes))
            label = next(s for s in children if s.has_text_frame and s.text == 'Editable callout')
            self.assertEqual(label.click_action.hyperlink.address, 'https://example.org')
            self.assertTrue(any(s.shape_type == MSO_SHAPE_TYPE.AUTO_SHAPE for s in children))
            self.assertTrue(any(s.shape_type == MSO_SHAPE_TYPE.PICTURE for s in children))
            footer = groups['Template group: footer-test']
            self.assertIn('1/2', [s.text for s in footer.shapes if s.has_text_frame])
            # Editing a child and moving the group must survive a save/reload.
            label.text_frame.paragraphs[0].runs[0].text = 'Revised callout'
            old_left = box.left
            box.left += 12700
            deck.save(output)
            loaded = Presentation(output)
            moved = next(s for s in loaded.slides[0].shapes if s.name == box.name)
            self.assertEqual(moved.left, old_left+12700)
            self.assertTrue(any(s.has_text_frame and s.text == 'Revised callout' for s in moved.shapes))

    def test_nonrectangular_decoration_stays_an_independent_image(self):
        with pymupdf.open() as doc:
            page = doc.new_page(width=240, height=135)
            page.draw_circle((40, 40), 15, color=None, fill=(1, 0, 0))
            mark(page, 'box-custom')
            prs = Presentation()
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            groups, report = add_graphics(slide, doc, (0, 0, 3048000, 1714500), 72)
            self.assertFalse(groups)
            self.assertEqual(report, [{'role': 'box-custom', 'kind': 'independent image'}])
            self.assertEqual(slide.shapes[0].shape_type, MSO_SHAPE_TYPE.PICTURE)


if __name__ == '__main__':
    unittest.main()
