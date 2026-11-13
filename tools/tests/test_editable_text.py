# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Real PDF/PPTX tests for selective removal and native text reconstruction."""
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pymupdf
from pptx import Presentation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from editable_text import prepare_text, resolve_font, text_lines, line_text
from images_to_ppt import convert_pdf_to_pptx
import export_presentation


class EditableTextTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'input.pdf'
        self.pptx = self.root / 'output.pptx'

    def fixture(self):
        font = resolve_font('Carlito')
        if font is None:
            self.skipTest('Carlito and fontconfig are needed for rendered font tests')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=225)
            page.draw_rect(page.rect, color=None, fill=(.2, .3, .4))
            page.insert_font(fontname='Body', fontfile=font['path'])
            page.insert_text((20, 50), 'Editable text 123', fontname='Body', fontsize=18,
                             color=(1, 1, 1))
            # A formula in an unsupported math font remains in the background.
            page.insert_text((20, 100), 'a + b = c', fontname='symb', fontsize=18)
            page.insert_link({'kind': pymupdf.LINK_URI, 'from': pymupdf.Rect(20, 30, 160, 55),
                              'uri': 'https://example.org'})
            doc.save(self.pdf)

    def test_native_text_style_notes_links_and_source_preserved(self):
        self.fixture()
        before = self.pdf.read_bytes()
        notes = self.root / 'notes.json'
        notes.write_text(json.dumps(['Speaker note']))
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            result = convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72,
                editable_text=True, strict_links=True, notes_path=notes)
        self.assertEqual(self.pdf.read_bytes(), before)
        self.assertEqual(result.external, 1)
        prs = Presentation(self.pptx)
        texts = [s for s in prs.slides[0].shapes if s.name.startswith('Editable text:')]
        self.assertEqual([s.text for s in texts], ['Editable text 123'])
        run = texts[0].text_frame.paragraphs[0].runs[0]
        self.assertEqual(run.font.name, 'Carlito')
        self.assertEqual(str(run.font.color.rgb), 'FFFFFF')
        self.assertAlmostEqual(run.font.size.pt, 18 * prs.slide_width / 400 / 12700, places=2)
        self.assertIn('Speaker note', prs.slides[0].notes_slide.notes_text_frame.text)
        report = json.loads(self.pptx.with_suffix('.text-report.json').read_text())
        self.assertEqual(report['pages'][0]['editable_lines'], 1)
        self.assertTrue(report['pages'][0]['retained'])

    def test_removal_keeps_background_and_formula(self):
        self.fixture()
        with pymupdf.open(self.pdf) as doc:
            original = doc[0].get_pixmap()
            clean, lines, _ = prepare_text(doc[0])
            try:
                self.assertEqual([line_text(l) for l in lines], ['Editable text 123'])
                self.assertNotIn('Editable', clean[0].get_text())
                self.assertIn('a', clean[0].get_text())
                rendered = clean[0].get_pixmap()
                self.assertEqual(original.pixel(10, 10), rendered.pixel(10, 10))
                # Formula region remains pixel-for-pixel identical.
                clip = pymupdf.Rect(0, 70, 200, 115)
                self.assertEqual(doc[0].get_pixmap(clip=clip).samples,
                                 clean[0].get_pixmap(clip=clip).samples)
            finally:
                clean.close()

    def test_unknown_font_and_rotation_remain_images(self):
        self.fixture()
        with pymupdf.open(self.pdf) as doc:
            with patch('editable_text.resolve_font', return_value=None):
                clean, lines, report = prepare_text(doc[0])
                self.assertEqual(lines, [])
                self.assertIn('Editable', clean[0].get_text())
                clean.close()
            doc[0].set_rotation(90)
            clean, lines, report = prepare_text(doc[0])
            self.assertEqual(lines, [])
            self.assertTrue(all('rotated' in r['reason'] for r in report['retained']))
            clean.close()

    def test_default_mode_has_no_native_text(self):
        self.fixture()
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72, auto_notes=False)
        self.assertFalse(any(s.name.startswith('Editable text:')
                             for s in Presentation(self.pptx).slides[0].shapes))
        self.assertFalse(self.pptx.with_suffix('.text-report.json').exists())

    def test_symbol_bullet_does_not_flatten_linked_toc_label(self):
        font = resolve_font('Carlito')
        if font is None:
            self.skipTest('Carlito is needed')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=225)
            page.insert_font(fontname='Body', fontfile=font['path'])
            page.insert_text((20, 50), '•', fontname='symb', fontsize=18)
            xref = page.get_contents()[-1]
            doc.update_stream(xref, b'/Span <</ActualText <FEFF25B6>>> BDC '
                              + doc.xref_stream(xref) + b' EMC')
            page.insert_text((35, 50), 'Introduction', fontname='Body', fontsize=18)
            self.assertEqual(len(text_lines(page)), 1)
            clean, lines, report = prepare_text(page)
            self.assertEqual([line_text(l).strip() for l in lines], ['Introduction'])
            self.assertEqual([r['text'] for r in report['retained']], ['▶'])
            self.assertNotIn('Introduction', clean[0].get_text())
            self.assertEqual(page.get_pixmap(clip=pymupdf.Rect(15, 25, 32, 55)).samples,
                             clean[0].get_pixmap(clip=pymupdf.Rect(15, 25, 32, 55)).samples)
            clean.close()
            doc.new_page(width=400, height=225)
            page = doc[0]
            page.insert_link({'kind': pymupdf.LINK_GOTO,
                              'from': page.search_for('Introduction')[0], 'page': 1})
            doc.save(self.pdf)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72, editable_text=True, auto_notes=False)
        deck = Presentation(self.pptx)
        label = deck.slides[0].shapes[1]
        self.assertEqual(label.text, 'Introduction')
        self.assertIs(label.click_action.target_slide, deck.slides[1])

    def test_partial_text_link_is_a_run_in_the_same_textbox(self):
        self.fixture()
        with pymupdf.open(self.pdf) as doc:
            page = doc[0]
            for link in page.get_links():
                page.delete_link(link)
            rect = page.search_for('text')[0]
            page.insert_link({'kind': pymupdf.LINK_URI, 'from': rect,
                              'uri': 'https://example.org/native'})
            doc.saveIncr()
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            result = convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72,
                                         editable_text=True, auto_notes=False, strict_links=True)
        slide = Presentation(self.pptx).slides[0]
        self.assertEqual(len(slide.shapes), 2)  # background plus one native textbox
        shape = slide.shapes[1]
        self.assertEqual(shape.text, 'Editable text 123')
        runs = shape.text_frame.paragraphs[0].runs
        self.assertEqual([(r.text, r.hyperlink.address) for r in runs],
                         [('Editable ', None), ('text', 'https://example.org/native'), (' 123', None)])
        self.assertEqual(result.external, 1)
        color = runs[1]._r.rPr.hlinkClick.find(
            './/{http://schemas.microsoft.com/office/drawing/2018/hyperlinkcolor}hlinkClr')
        self.assertEqual(color.get('val'), 'tx')
        self.assertEqual(str(runs[1].font.color.rgb), 'FFFFFF')
        runs[1].text = 'changed'
        self.assertEqual(runs[1].hyperlink.address, 'https://example.org/native')

    def test_native_text_internal_link_targets_slide_part(self):
        self.fixture()
        with pymupdf.open(self.pdf) as doc:
            doc.new_page(width=400, height=225)
            page = doc[0]
            for link in page.get_links():
                page.delete_link(link)
            page.insert_link({'kind': pymupdf.LINK_GOTO,
                              'from': page.search_for('Editable text 123')[0], 'page': 1})
            doc.saveIncr()
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            result = convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72,
                                         editable_text=True, auto_notes=False, strict_links=True)
        prs = Presentation(self.pptx)
        slide = prs.slides[0]
        self.assertEqual(len(slide.shapes), 2)
        shape = slide.shapes[1]
        self.assertIs(shape.click_action.target_slide, prs.slides[1])
        self.assertIsNone(shape.text_frame.paragraphs[0].runs[0]._r.rPr.hlinkClick)
        self.assertEqual(result.internal, 1)

    def test_actualtext_zero_width_digits_do_not_flatten_cover(self):
        font = resolve_font('Carlito')
        if font is None:
            self.skipTest('Carlito is needed')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=225)
            page.insert_font(fontname='Body', fontfile=font['path'])
            page.insert_text((20, 40), 'Cover title', fontname='Body', fontsize=24)
            page.insert_text((20, 80), 'x123a', fontname='Body', fontsize=18)
            # Carlito old-style digits have no Unicode cmap entries. XeTeX
            # wraps such runs in ActualText, which MuPDF can extract with
            # zero-width glyph boxes and a spurious synthetic space.
            xref = page.get_contents()[-1]
            data = doc.xref_stream(xref).replace(b'019001910192', b'017401750176')
            doc.update_stream(xref, b'/Span <</ActualText (x123a)>> BDC ' + data + b' EMC')
            clean, lines, report = prepare_text(page)
            self.assertEqual([line_text(l) for l in lines], ['Cover title', 'x123a'])
            self.assertEqual(report['retained'], [])
            self.assertFalse(clean[0].get_text().strip())
            clean.close()
            doc.save(self.pdf)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72, editable_text=True, auto_notes=False)
        self.assertEqual(''.join(s.text for s in Presentation(self.pptx).slides[0].shapes
                                 if s.name.startswith('Editable text:')), 'Cover titlex123a')

    def test_footer_ink_is_centered_in_its_band(self):
        font = resolve_font('Carlito')
        if font is None:
            self.skipTest('Carlito is needed')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=225)
            page.draw_rect(pymupdf.Rect(0, 213, 400, 225), color=None, fill=(0, 0, 0))
            page.insert_font(fontname='Body', fontfile=font['path'])
            page.insert_text((20, 220), '1/20', fontname='Body', fontsize=8, color=(1, 1, 1))
            doc.save(self.pdf)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72, editable_text=True, auto_notes=False)
        shape = Presentation(self.pptx).slides[0].shapes[1]
        run = shape.text_frame.paragraphs[0].runs[0]
        # Independently render the native font at the exported baseline.
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=225)
            page.insert_font(fontname='Body', fontfile=font['path'])
            page.insert_text((shape.left/12700, shape.top/12700+run.font.size.pt),
                             shape.text, fontname='Body', fontsize=run.font.size.pt)
            box = page.get_bboxlog()[0][1]
            self.assertAlmostEqual((box[1]+box[3])/2, 219, places=3)

    def test_whole_text_link_uses_textbox_action_without_link_style(self):
        self.fixture()
        with pymupdf.open(self.pdf) as doc:
            page = doc[0]
            for link in page.get_links():
                page.delete_link(link)
            page.insert_link({'kind': pymupdf.LINK_URI,
                              'from': page.search_for('Editable text 123')[0],
                              'uri': 'https://example.org/native'})
            doc.saveIncr()
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72, editable_text=True, auto_notes=False)
        slide = Presentation(self.pptx).slides[0]
        self.assertEqual(len(slide.shapes), 2)
        shape = slide.shapes[1]
        self.assertEqual(shape.click_action.hyperlink.address, 'https://example.org/native')
        run = shape.text_frame.paragraphs[0].runs[0]
        self.assertIsNone(run._r.rPr.hlinkClick)
        self.assertEqual(str(run.font.color.rgb), 'FFFFFF')
        self.assertFalse(run.font.underline)

    def test_cjk_text_and_bold_font_are_native(self):
        chinese, bold = resolve_font('FandolHei-Regular'), resolve_font('Carlito-Bold')
        if chinese is None or bold is None:
            self.skipTest('TeX CJK fonts and Carlito are needed')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=225)
            page.insert_font(fontname='Chinese', fontfile=chinese['path'])
            page.insert_font(fontname='Bold', fontfile=bold['path'])
            page.insert_text((20, 50), '中文正文', fontname='Chinese', fontsize=18, color=(1, 0, 0))
            page.insert_text((20, 100), 'Bold text', fontname='Bold', fontsize=18)
            doc.save(self.pdf)
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72, editable_text=True, auto_notes=False)
        shapes = [s for s in Presentation(self.pptx).slides[0].shapes
                  if s.name.startswith('Editable text:')]
        self.assertEqual([s.text for s in shapes], ['中文正文', 'Bold text'])
        cjk = shapes[0].text_frame.paragraphs[0].runs[0]
        self.assertIn('typeface="FandolHei"', cjk._r.xml)
        self.assertEqual(str(cjk.font.color.rgb), 'FF0000')
        self.assertTrue(shapes[1].text_frame.paragraphs[0].runs[0].font.bold)

    def test_later_covering_artwork_keeps_text_in_background(self):
        self.fixture()
        with pymupdf.open(self.pdf) as doc:
            doc[0].draw_rect(pymupdf.Rect(20, 35, 160, 55), fill=(1, 0, 0))
            clean, lines, report = prepare_text(doc[0])
            self.assertEqual(lines, [])
            self.assertIn('overlapping later artwork', [r['reason'] for r in report['retained']])
            self.assertEqual(clean[0].get_pixmap().samples, doc[0].get_pixmap().samples)
            clean.close()

    def test_inflated_stroke_bounds_do_not_flatten_uncovered_text(self):
        for y, editable in ((58, True), (43, False)):
            with self.subTest(stroke_y=y):
                self.fixture()
                with pymupdf.open(self.pdf) as doc:
                    page = doc[0]
                    page.draw_line((20, y), (160, y), color=(1, 0, 0), width=.5)
                    clean, lines, report = prepare_text(page)
                    self.assertEqual('Editable text 123' in [line_text(l) for l in lines], editable)
                    clean.close()

    def test_footer_separator_does_not_flatten_author_and_title(self):
        font = resolve_font('Carlito')
        if font is None:
            self.skipTest('Carlito is needed')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=225)
            page.insert_font(fontname='Body', fontfile=font['path'])
            page.insert_text((20, 222), 'Author', fontname='Body', fontsize=8)
            page.insert_text((44, 222), '|', fontname='symb', fontsize=8)
            page.insert_text((49, 222), 'Title', fontname='Body', fontsize=8)
            clean, lines, report = prepare_text(page)
            self.assertEqual(''.join(line_text(l).strip() for l in lines), 'AuthorTitle')
            self.assertEqual(clean[0].get_text().strip(), '|')
            clean.close()

    def test_editable_variant_enables_actualtext_without_changing_source(self):
        source = Path('examples/example.tex')
        writes = []
        with patch.object(Path, 'write_text', lambda path, text: writes.append((path, text))), \
                patch.object(export_presentation.subprocess, 'run'):
            output = export_presentation.render_variant(source, 'editable', 'latexmk')
        self.assertEqual(output, Path('build/example.editable-slides.pdf'))
        self.assertIn('\\XeTeXgenerateactualtext=1', writes[0][1])
        self.assertIn('\\def\\campusnotesmode{slides}', writes[0][1])
        self.assertNotEqual(writes[0][0], source)


if __name__ == '__main__':
    unittest.main()
