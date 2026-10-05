# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""End-to-end regression tests using real PDF annotations and PPTX relationships."""

from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime
from io import StringIO
from pathlib import Path
import sys
import tempfile
import json
import shutil
import subprocess
import unittest
import zipfile
from uuid import UUID
from xml.etree import ElementTree as ET
from unittest.mock import patch

import pymupdf
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.oxml.ns import qn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import images_to_ppt as converter
import add_video_posters as poster_tool


class ConversionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'source.pdf'
        self.pptx = self.root / 'export' / 'slides.pptx'

    def convert(self, **kwargs):
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            return converter.convert_pdf_to_pptx(self.pdf, self.pptx, dpi=72, **kwargs)

    def video_fixture(self, path, size='160x90'):
        if not shutil.which('ffmpeg'):
            self.skipTest('FFmpeg is needed for real video export tests')
        path.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-nostdin', '-f', 'lavfi',
                        '-i', f'color=c=red:s={size}:d=0.12', '-c:v', 'mpeg4',
                        '-y', str(path)], capture_output=True, check=True, timeout=30)
        return path

    def fixture(self, unsupported=False):
        with pymupdf.open() as doc:
            for _ in range(4):
                doc.new_page(width=400, height=200)
            # Named destinations, including a literal percent and Unicode.
            dest_name = 'section-A'
            names = (
                f'<< /Dests << /Names [{pymupdf.get_pdf_str(dest_name)} '
                f'[{doc[3].xref} 0 R /XYZ 0 200 0]] >> >>'
            )
            doc.xref_set_key(doc.pdf_catalog(), 'Names', names)
            page = doc[0]
            annotations = [
                ('<< /S /GoTo /D [PAGE 0 R /XYZ 0 200 0] >>'.replace('PAGE', str(doc[2].xref))),
                f'<< /S /GoTo /D {pymupdf.get_pdf_str(dest_name)} >>',
                '<< /S /URI /URI (https://example.org/paper#page=3) >>',
                '<< /S /URI /URI (mailto:test@example.org) >>',
                '<< /S /GoToR /F (assets/demo video.mp4) /D [0 /Fit] >>',
                '<< /S /GoToR /F (assets/paper.pdf) /D [2 /Fit] >>',
                '<< /S /Named /N /LastPage >>',
                '<< /S /URI /URI (#page=2) >>',
            ]
            if unsupported:
                annotations.append(r'<< /S /JavaScript /JS (app.alert\(1\)) >>')
            for i, action in enumerate(annotations):
                rect = pymupdf.Rect(10 + i * 35, 20, 35 + i * 35, 40)
                page.draw_rect(rect, color=(1, 0, 0), fill=(1, 1, 0))
                page.insert_link({'kind': pymupdf.LINK_URI, 'from': rect, 'uri': 'https://placeholder.invalid'})
                page = doc.reload_page(page)
                doc.xref_set_key(page.get_links()[-1]['xref'], 'A', action)
            # A visible link on a rotated page should rotate once, not twice.
            page = doc[1]
            rect = pymupdf.Rect(10, 20, 60, 40)
            page.draw_rect(rect, fill=(0, 1, 0))
            page.insert_link({'kind': pymupdf.LINK_URI, 'from': rect, 'uri': 'https://example.org/rotated'})
            page.set_rotation(90)
            # CropBox offsets must not shift the clickable region.
            page = doc[2]
            page.set_cropbox(pymupdf.Rect(20, 10, 180, 190))
            page.draw_rect(pymupdf.Rect(10, 20, 60, 40), fill=(0, 0, 1))
            page.insert_link({'kind': pymupdf.LINK_URI, 'from': pymupdf.Rect(10, 20, 60, 40), 'uri': 'https://example.org/cropped'})
            doc.save(self.pdf)

    def document_fixture(self, toc=None, metadata=None, campus=None):
        with pymupdf.open() as doc:
            for _ in range(4):
                doc.new_page(width=400, height=200)
            if toc:
                doc.set_toc(toc)
            if metadata:
                doc.set_metadata(metadata)
            if campus:
                kind, reference = doc.xref_get_key(-1, 'Info')
                if kind != 'xref':
                    doc.set_metadata({'title': ''})
                    _, reference = doc.xref_get_key(-1, 'Info')
                for key, value in campus.items():
                    doc.xref_set_key(int(reference.split()[0]), 'Campus' + key,
                                     pymupdf.get_pdf_str(value))
            doc.save(self.pdf)

    def sections(self):
        with zipfile.ZipFile(self.pptx) as archive:
            root = ET.fromstring(archive.read('ppt/presentation.xml'))
        ns = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
              'p14': 'http://schemas.microsoft.com/office/powerpoint/2010/main'}
        extension = root.find("p:extLst/p:ext[@uri='{521415D9-36F7-43E2-AB2F-B90AF26B5E84}']", ns)
        return [] if extension is None else extension.findall('p14:sectionLst/p14:section', ns)

    def test_native_sections_cover_each_slide_once_and_ignore_subsections(self):
        self.document_fixture(toc=[[1, '方法 & <结果>', 2], [2, '子节', 3], [1, '方法 & <结果>', 4]],
                              campus={'Language': 'chinese'})
        self.convert()
        sections = self.sections()
        self.assertEqual([item.get('name') for item in sections], ['封面与导读', '方法 & <结果>', '方法 & <结果>'])
        ids = [UUID(item.get('id')) for item in sections]
        self.assertEqual(len(set(ids)), 3)
        groups = [[int(slide.get('id')) for slide in item[0]] for item in sections]
        slides = [slide.slide_id for slide in Presentation(self.pptx).slides]
        self.assertEqual(groups, [slides[:1], slides[1:3], slides[3:]])

    def test_sections_starting_on_first_page_need_no_prelude(self):
        self.document_fixture(toc=[[1, 'Opening', 1], [1, 'Body', 3]])
        self.convert()
        self.assertEqual([s.get('name') for s in self.sections()], ['Opening', 'Body'])

    def test_empty_sections_do_not_duplicate_slides(self):
        self.document_fixture(toc=[[1, 'Empty', 1], [1, 'Body', 1]])
        self.convert()
        self.assertEqual([s.get('name') for s in self.sections()], ['Body'])
        self.assertEqual(len(self.sections()[0][0]), 4)

    def test_absent_outline_and_metadata_do_not_invent_content(self):
        self.document_fixture()
        self.convert()
        self.assertEqual(self.sections(), [])
        core = Presentation(self.pptx).core_properties
        for key in ('title', 'author', 'subject', 'keywords', 'last_modified_by', 'comments'):
            self.assertEqual(getattr(core, key), '')
        self.assertGreaterEqual(core.created.year, 2026)
        with zipfile.ZipFile(self.pptx) as archive:
            self.assertNotIn('docProps/custom.xml', archive.namelist())
            props = ET.fromstring(archive.read('docProps/app.xml'))
            ns = '{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}'
            self.assertEqual(props.find(ns + 'Application').text, 'Campus Beamer')
            self.assertEqual(props.find(ns + 'Slides').text, '4')
            self.assertEqual(props.find(ns + 'Notes').text, '4')
            self.assertEqual(props.find(ns + 'MMClips').text, '0')
            self.assertEqual(props.find(ns + 'PresentationFormat').text, 'Custom')

    def test_out_of_order_sections_preserve_previous_output(self):
        self.document_fixture(toc=[[1, 'Later', 3], [1, 'Earlier', 2]])
        self.pptx.parent.mkdir()
        self.pptx.write_bytes(b'previous presentation')
        with self.assertRaisesRegex(ValueError, 'page order'):
            self.convert()
        self.assertEqual(self.pptx.read_bytes(), b'previous presentation')

    def test_standard_and_cover_metadata_round_trip_with_unicode(self):
        self.document_fixture(metadata={'title': 'PDF title - subtitle', 'author': '范潇 & Ada',
                                       'subject': '主题', 'keywords': 'Beamer, 中文',
                                       'creationDate': "D:20261005120000+08'00'"},
                              campus={'Title': '汇报 (标题)', 'Subtitle': '方法 & <结果>',
                                      'Group': '课题组', 'Advisor': '王老师', 'Date': '2026-10-12',
                                      'Contact': 'test@example.org', 'Language': 'chinese'})
        self.convert()
        core = Presentation(self.pptx).core_properties
        self.assertEqual(core.title, '汇报 (标题)')
        self.assertEqual(core.author, '范潇 & Ada')
        self.assertEqual(core.subject, '主题')
        self.assertEqual(core.keywords, 'Beamer, 中文')
        self.assertEqual(core.created, datetime(2026, 10, 5, 4))
        self.assertEqual(core.last_modified_by, '')
        with zipfile.ZipFile(self.pptx) as archive:
            props = ET.fromstring(archive.read('docProps/custom.xml'))
            self.assertEqual({p.get('name'): p[0].text for p in props}, {
                'Subtitle': '方法 & <结果>', 'Group': '课题组', 'Advisor': '王老师',
                'PresentationDate': '2026-10-12', 'Contact': 'test@example.org'})
            self.assertEqual([p.get('pid') for p in props], ['2', '3', '4', '5', '6'])
            relationships = ET.fromstring(archive.read('_rels/.rels'))
            rel = [r for r in relationships if r.get('Type').endswith('/custom-properties')]
            self.assertEqual(len(rel), 1)
            self.assertEqual(rel[0].get('Target'), 'docProps/custom.xml')
            self.assertIn(b'custom-properties+xml', archive.read('[Content_Types].xml'))

    def test_long_core_property_is_preserved_in_custom_properties(self):
        title = '中文标题' * 100
        self.document_fixture(metadata={'title': title, 'creationDate': 'invalid'})
        self.convert()
        self.assertEqual(Presentation(self.pptx).core_properties.title, title[:255])
        with zipfile.ZipFile(self.pptx) as archive:
            props = ET.fromstring(archive.read('docProps/custom.xml'))
            self.assertEqual(props[0].get('name'), 'FullTitle')
            self.assertEqual(props[0][0].text, title)

    def test_real_links_and_relationships(self):
        self.fixture()
        summary = self.convert()
        self.assertEqual(summary, converter.LinkSummary(internal=3, external=6, skipped=1))
        prs = Presentation(self.pptx)
        self.assertEqual(len(prs.slides), 4)
        shapes = prs.slides[0].shapes
        for shape_index, slide_index in ((1, 2), (2, 3), (7, 3)):
            self.assertEqual(shapes[shape_index].click_action.target_slide.slide_id, prs.slides[slide_index].slide_id)
        for shape_index, url in (
            (3, 'https://example.org/paper#page=3'),
            (4, 'mailto:test@example.org'),
            (5, '../assets/demo%20video.mp4'),
            (6, '../assets/paper.pdf#page=3'),
        ):
            self.assertEqual(shapes[shape_index].click_action.hyperlink.address, url)
        for shape in list(shapes)[1:]:
            self.assertEqual(shape._element.spPr.solidFill[0].find(qn('a:alpha')).get('val'), '1000')

    def test_existing_local_video_is_embedded(self):
        self.fixture()
        video = self.root / 'assets' / 'demo video.mp4'
        self.video_fixture(video)

        summary = self.convert()

        self.assertEqual(summary, converter.LinkSummary(internal=3, external=5, embedded=1, skipped=1))
        prs = Presentation(self.pptx)
        movies = [shape for shape in prs.slides[0].shapes if shape.shape_type == MSO_SHAPE_TYPE.MEDIA]
        self.assertEqual(len(movies), 1)
        self.assertEqual(movies[0].name, 'Embedded video: demo video.mp4')
        with zipfile.ZipFile(self.pptx) as archive:
            media = [name for name in archive.namelist() if name.startswith('ppt/media/') and name.endswith('.mp4')]
            self.assertEqual(len(media), 1)
            self.assertEqual(archive.read(media[0]), video.read_bytes())
            props = ET.fromstring(archive.read('docProps/app.xml'))
            self.assertEqual(props.find('{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}MMClips').text, '1')
            slide_xml = archive.read('ppt/slides/slide1.xml').decode('utf-8')
            self.assertIn('<p14:media', slide_xml)

    def test_video_has_real_poster_fits_border_and_clears_placeholder(self):
        video = self.video_fixture(self.root / 'demo.mp4')
        frame = pymupdf.Rect(100, 50, 300, 150)
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=200)
            page.draw_rect(page.rect, color=None, fill=(0.2, 0.4, 0.6))
            # Match TeX fbox: four separately drawn rules; link covers only text.
            for a, b in ((frame.tl, frame.tr), (frame.tr, frame.br),
                         (frame.br, frame.bl), (frame.bl, frame.tl)):
                page.draw_line(a, b, color=(1, 1, 0))
            page.insert_text((170, 105), 'PLAY')
            page.insert_text((10, 185), 'Keep this caption')
            page.insert_link({'kind': pymupdf.LINK_LAUNCH,
                              'from': pymupdf.Rect(170, 90, 210, 110), 'file': video.name})
            page.insert_link({'kind': pymupdf.LINK_URI,
                              'from': pymupdf.Rect(10, 170, 95, 185), 'uri': 'https://example.org'})
            doc.save(self.pdf)
        original = self.pdf.read_bytes()
        summary = self.convert(strict_links=True)
        self.assertEqual(summary, converter.LinkSummary(external=1, embedded=1))
        self.assertEqual(self.pdf.read_bytes(), original)
        slide = Presentation(self.pptx).slides[0]
        background = slide.shapes[0]
        movie = next(s for s in slide.shapes if s.shape_type == MSO_SHAPE_TYPE.MEDIA)
        self.assertAlmostEqual(movie.width / movie.height, 16 / 9, places=5)
        self.assertAlmostEqual(movie.height / background.height, .5, places=5)
        self.assertAlmostEqual((movie.left + movie.width / 2) / background.width, .5, places=5)
        self.assertAlmostEqual((movie.top + movie.height / 2) / background.height, .5, places=5)
        poster = pymupdf.Pixmap(movie.poster_frame.blob)
        self.assertEqual((poster.width, poster.height), (160, 90))
        self.assertGreater(poster.pixel(80, 45)[0], 200)
        self.assertLess(poster.pixel(80, 45)[1], 20)
        image = pymupdf.Pixmap(background.image.blob)
        # Text, border and letterbox area are cleared back to the blue background.
        for point in ((170, 100), (100, 50), (105, 125), (300, 150)):
            self.assertEqual(image.pixel(*point), (51, 102, 153))
        with pymupdf.open(self.pdf) as doc:
            before = doc[0].get_pixmap(dpi=72, alpha=False)
            self.assertEqual(image.pixel(25, 178), before.pixel(25, 178))

    def test_pdf_video_poster_is_visible_and_idempotent(self):
        video = self.video_fixture(self.root / 'demo.mp4')
        frame = pymupdf.Rect(100, 50, 300, 150)
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=200)
            page.draw_rect(frame, color=(0, 0, 0), fill=(1, 1, 1))
            page.insert_text((170, 105), 'PLAY')
            page.insert_link({'kind': pymupdf.LINK_LAUNCH,
                              'from': pymupdf.Rect(170, 90, 210, 110), 'file': video.name})
            doc.save(self.pdf)
        self.assertEqual(poster_tool.add_video_posters(self.pdf), 1)
        first = self.pdf.read_bytes()
        with pymupdf.open(self.pdf) as doc:
            self.assertIn(poster_tool.MARKER, doc.metadata.get('keywords', ''))
            self.assertEqual(len(doc[0].get_links()), 1)
            images = doc[0].get_images()
            self.assertTrue(images)
            poster = pymupdf.Pixmap(doc.extract_image(images[-1][0])['image'])
            self.assertGreater(poster.pixel(poster.width // 2, poster.height // 2)[0], 200)
        self.assertEqual(poster_tool.add_video_posters(self.pdf), 0)
        self.assertEqual(self.pdf.read_bytes(), first)

    def test_pdf_video_poster_handles_rotated_page(self):
        video = self.video_fixture(self.root / 'rotated.mp4')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=200)
            frame = pymupdf.Rect(100, 50, 300, 150)
            page.draw_rect(frame, color=(0, 0, 0), fill=(1, 1, 1))
            page.insert_link({'kind': pymupdf.LINK_LAUNCH, 'from': frame, 'file': video.name})
            page.set_rotation(90)
            doc.save(self.pdf)
        self.assertEqual(poster_tool.add_video_posters(self.pdf), 1)
        with pymupdf.open(self.pdf) as doc:
            pixmap = doc[0].get_pixmap(alpha=False)
            self.assertGreater(pixmap.pixel(100, 200)[0], 200)
            self.assertLess(pixmap.pixel(100, 200)[1], 20)

    def test_portrait_video_fits_rotated_pdf_placeholder(self):
        video = self.video_fixture(self.root / 'portrait.mp4', '90x160')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=200)
            frame = pymupdf.Rect(100, 50, 300, 150)
            page.draw_rect(frame, color=(1, 0, 0))
            # A whole-box XeTeX link may extend 2pt outside the actual border.
            expanded = pymupdf.Rect(97.8, 47.8, 302.2, 152.2)
            page.insert_link({'kind': pymupdf.LINK_LAUNCH, 'from': expanded, 'file': video.name})
            page.set_rotation(90)
            doc.save(self.pdf)
        self.convert(strict_links=True)
        background, movie = Presentation(self.pptx).slides[0].shapes
        self.assertAlmostEqual(movie.width / movie.height, 9 / 16, places=5)
        self.assertAlmostEqual(movie.width / background.width, .5, places=5)
        self.assertAlmostEqual((movie.left + movie.width / 2) / background.width, .5, places=5)
        self.assertAlmostEqual((movie.top + movie.height / 2) / background.height, .5, places=5)
        image = pymupdf.Pixmap(background.image.blob)
        self.assertEqual(image.pixel(50, 100), (255, 255, 255))

    def test_video_errors_leave_previous_output_intact(self):
        video = self.root / 'invalid.mp4'
        video.write_bytes(b'invalid video')
        with pymupdf.open() as doc:
            page = doc.new_page()
            page.insert_link({'kind': pymupdf.LINK_LAUNCH,
                              'from': pymupdf.Rect(10, 10, 100, 100), 'file': video.name})
            doc.save(self.pdf)
        self.pptx.parent.mkdir()
        self.pptx.write_bytes(b'previous output')
        with patch.object(converter.shutil, 'which', return_value=None):
            with self.assertRaisesRegex(RuntimeError, 'requires FFmpeg'):
                self.convert()
        self.assertEqual(self.pptx.read_bytes(), b'previous output')
        if shutil.which('ffmpeg'):
            with self.assertRaisesRegex(RuntimeError, 'Cannot extract video preview'):
                self.convert()
            self.assertEqual(self.pptx.read_bytes(), b'previous output')

    def test_placeholder_cleanup_preserves_raster_background(self):
        def image_bytes(color):
            image = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 2, 2), False)
            image.set_rect(image.irect, color)
            return image.tobytes('png')
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=200)
            page.insert_image(page.rect, stream=image_bytes((51, 102, 153)))
            frame = pymupdf.Rect(100, 50, 300, 150)
            page.draw_rect(frame, color=(1, 1, 0))
            page.insert_image(pymupdf.Rect(170, 80, 230, 120),
                              stream=image_bytes((0, 255, 0)), keep_proportion=False)
            cleaned = converter.render_page(page, 72, [frame])
            for point in ((200, 100), (100, 50), (110, 125), (20, 20)):
                self.assertEqual(cleaned.pixel(*point), (51, 102, 153))
            # The original page still contains its placeholder image.
            self.assertEqual(page.get_pixmap(dpi=72, alpha=False).pixel(200, 100), (0, 255, 0))

    def test_images_rotation_crop_and_mixed_page_sizes(self):
        self.fixture()
        self.convert()
        prs = Presentation(self.pptx)
        with pymupdf.open(self.pdf) as doc:
            for page, slide in zip(doc, prs.slides):
                expected = page.get_pixmap(dpi=72, alpha=False).tobytes('png')
                self.assertEqual(slide.shapes[0].image.blob, expected)
        # Rotation maps (10,20,60,40) to (160,10,180,60) on a 200x400 page.
        rotated = prs.slides[1]
        image, hotspot = rotated.shapes
        self.assertAlmostEqual(image.width / image.height, 0.5, places=6)
        self.assertAlmostEqual((hotspot.left - image.left) / image.width, 0.8, places=6)
        self.assertAlmostEqual((hotspot.top - image.top) / image.height, 0.025, places=6)
        self.assertAlmostEqual(hotspot.width / image.width, 0.1, places=6)
        self.assertAlmostEqual(hotspot.height / image.height, 0.125, places=6)
        image, hotspot = prs.slides[2].shapes
        self.assertAlmostEqual(image.width / image.height, 160 / 180, places=6)
        self.assertAlmostEqual((hotspot.left - image.left) / image.width, 10 / 160, places=6)
        self.assertAlmostEqual((hotspot.top - image.top) / image.height, 20 / 180, places=6)

    def test_unsupported_annotation_count_and_strict_mode(self):
        self.fixture(unsupported=True)
        summary = self.convert()
        self.assertEqual(summary.skipped, 2)
        original = self.pptx.read_bytes()
        with self.assertRaisesRegex(ValueError, 'Output was not saved'):
            self.convert(strict_links=True)
        self.assertEqual(self.pptx.read_bytes(), original)

    def test_invalid_geometry_is_skipped(self):
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=200)
            page.insert_link({'kind': pymupdf.LINK_URI, 'from': pymupdf.Rect(500, 20, 550, 40), 'uri': 'https://example.org'})
            doc.save(self.pdf)
        summary = self.convert()
        self.assertEqual(summary.skipped, 1)
        self.assertEqual(len(Presentation(self.pptx).slides[0].shapes), 1)

    def test_clipped_geometry(self):
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=200)
            page.insert_link({'kind': pymupdf.LINK_URI, 'from': pymupdf.Rect(-20, 10, 40, 40), 'uri': 'https://example.org'})
            doc.save(self.pdf)
        self.convert()
        prs = Presentation(self.pptx)
        hotspot = prs.slides[0].shapes[1]
        self.assertEqual(hotspot.left, 0)
        self.assertAlmostEqual(hotspot.width / prs.slide_width, 0.1, places=6)

    def test_invalid_inputs_do_not_overwrite_output(self):
        self.fixture()
        self.pptx.parent.mkdir()
        self.pptx.write_bytes(b'existing output')
        with self.assertRaisesRegex(ValueError, 'DPI'):
            converter.convert_pdf_to_pptx(self.pdf, self.pptx, dpi=0)
        with self.assertRaisesRegex(ValueError, 'different files'):
            converter.convert_pdf_to_pptx(self.pdf, self.pdf)
        with self.assertRaisesRegex(ValueError, '.pptx'):
            converter.convert_pdf_to_pptx(self.pdf, self.root / 'bad.ppt')
        self.assertEqual(self.pptx.read_bytes(), b'existing output')

    def test_speaker_notes_are_written_and_auto_detected(self):
        self.fixture()
        notes = self.pdf.with_suffix('.notes.json')
        notes.write_text(json.dumps({'slides': [
            {'notes': '开场：说明本页目标。'},
            '第二页的讲稿。',
        ]}, ensure_ascii=False), encoding='utf-8')
        self.convert()
        prs = Presentation(self.pptx)
        self.assertEqual(prs.slides[0].notes_slide.notes_text_frame.text, '开场：说明本页目标。')
        self.assertEqual(prs.slides[1].notes_slide.notes_text_frame.text, '第二页的讲稿。')
        self.assertEqual(prs.slides[2].notes_slide.notes_text_frame.text, '')

    def test_build_directory_preserves_notes_and_embedded_video(self):
        build = self.root / 'build'
        build.mkdir()
        assets = self.root / 'assets'
        assets.mkdir()
        video = assets / 'demo.mp4'
        self.video_fixture(video)
        self.pdf = build / 'source.pdf'
        self.pptx = build / 'source.pptx'
        with pymupdf.open() as doc:
            page = doc.new_page(width=400, height=200)
            page.insert_link({'kind': pymupdf.LINK_LAUNCH,
                              'from': pymupdf.Rect(20, 20, 100, 50),
                              'file': '../assets/demo.mp4'})
            doc.save(self.pdf)
        (self.root / 'source.notes.json').write_text(json.dumps(['Stale root notes']))
        self.pdf.with_suffix('.notes.json').write_text(json.dumps(['Generated build notes']))
        summary = self.convert(strict_notes=True, strict_links=True)
        self.assertEqual(summary.embedded, 1)
        self.assertEqual(summary.skipped, 0)
        self.assertEqual(Presentation(self.pptx).slides[0].notes_slide.notes_text_frame.text,
                         'Generated build notes')
        with zipfile.ZipFile(self.pptx) as archive:
            media = [archive.read(name) for name in archive.namelist() if name.endswith('.mp4')]
            self.assertEqual(media, [video.read_bytes()])

    def test_explicit_notes_directory_overrides_pdf_sibling(self):
        self.fixture()
        custom = self.root / 'custom-notes'
        custom.mkdir()
        (custom / 'source.notes.json').write_text(json.dumps(['Custom notes'] * 4))
        self.pdf.with_suffix('.notes.json').write_text(json.dumps(['Sibling notes'] * 4))
        self.convert(notes_dir=custom, strict_notes=True)
        self.assertEqual(Presentation(self.pptx).slides[0].notes_slide.notes_text_frame.text,
                         'Custom notes')

    def test_invalid_notes_directory_does_not_replace_output(self):
        self.fixture()
        self.pptx.parent.mkdir()
        self.pptx.write_bytes(b'previous output')
        with self.assertRaisesRegex(ValueError, 'Notes directory'):
            self.convert(notes_dir=self.root / 'missing')
        self.assertEqual(self.pptx.read_bytes(), b'previous output')

    def test_no_notes_disables_directory_lookup(self):
        self.fixture()
        self.convert(notes_dir=self.root / 'missing', auto_notes=False)
        self.assertEqual(Presentation(self.pptx).slides[0].notes_slide.notes_text_frame.text, '')

    def test_notes_page_count_cannot_drift(self):
        self.fixture()
        notes = self.root / 'too-many.json'
        notes.write_text(json.dumps(['x'] * 5), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'only 4 pages'):
            self.convert(notes_path=notes)

    def test_strict_notes_reject_short_file_without_replacing_output(self):
        self.fixture()
        self.pptx.parent.mkdir()
        self.pptx.write_bytes(b'previous presentation')
        notes = self.pdf.with_suffix('.notes.json')
        notes.write_text(json.dumps(['one page']), encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'one entry per page'):
            self.convert(strict_notes=True)
        self.assertEqual(self.pptx.read_bytes(), b'previous presentation')

    def test_strict_notes_round_trip_with_intentional_blanks(self):
        self.fixture()
        expected = ['开场\n说明目的', '', '证据与来源', '总结']
        self.pdf.with_suffix('.notes.json').write_text(
            json.dumps(expected, ensure_ascii=False), encoding='utf-8'
        )
        self.convert(strict_notes=True)
        prs = Presentation(self.pptx)
        self.assertEqual([s.notes_slide.notes_text_frame.text for s in prs.slides], expected)

    def test_strict_notes_allows_missing_file_for_template_demo(self):
        self.fixture()
        self.convert(strict_notes=True)
        self.assertTrue(self.pptx.is_file())

    def test_failed_save_does_not_replace_existing_output(self):
        self.pptx.parent.mkdir()
        self.pptx.write_bytes(b'existing output')
        prs = Presentation()
        def fail(path):
            Path(path).write_bytes(b'partial archive')
            raise OSError('Disk full')
        with patch.object(prs, 'save', side_effect=fail):
            with self.assertRaises(OSError):
                converter.save_presentation(prs, self.pptx)
        self.assertEqual(self.pptx.read_bytes(), b'existing output')
        self.assertEqual(list(self.pptx.parent.iterdir()), [self.pptx])


class ResolutionTests(unittest.TestCase):
    def test_named_destination_precedence_and_no_page_guess(self):
        names = {'Navigation10': {'page': 3}, '17': {'page': 2}, 'NextPage': {'page': 4}}
        for name, expected in (('Navigation10', 3), ('17', 2), ('NextPage', 4)):
            link = {'kind': pymupdf.LINK_NAMED, 'nameddest': name}
            self.assertEqual(converter.resolve_internal_link(link, 0, 20, names), expected)
        for name in ('Navigation10', '17', 'NextPage'):
            link = {'kind': pymupdf.LINK_URI, 'uri': '#nameddest=' + name}
            self.assertIsNone(converter.resolve_internal_link(link, 0, 20, {}))

    def test_legacy_named_fields_and_encoded_names(self):
        names = {'章节 A': {'page': 2}}
        for field in ('name', 'named', 'to'):
            link = {'kind': pymupdf.LINK_NAMED, field: 'nameddest=%E7%AB%A0%E8%8A%82%20A'}
            self.assertEqual(converter.resolve_internal_link(link, 0, 5, names), 2)

    def test_remote_link_never_resolves_inside_presentation(self):
        link = {'kind': pymupdf.LINK_GOTOR, 'page': 1, 'file': 'other.pdf', 'to': 'NextPage'}
        self.assertIsNone(converter.resolve_internal_link(link, 0, 5, {'NextPage': {'page': 2}}))

    def test_page_actions_and_fragments(self):
        for text, expected in (('NextPage', 2), ('PrevPage', 0), ('FirstPage', 0), ('LastPage', 4), ('#page=4&zoom=100', 3), ('#3', 2)):
            link = {'kind': pymupdf.LINK_NAMED, 'name': text}
            self.assertEqual(converter.resolve_internal_link(link, 1, 5, {}), expected)
        self.assertIsNone(converter.resolve_internal_link({'kind': pymupdf.LINK_GOTO, 'page': 10}, 0, 5, {}))


if __name__ == '__main__':
    unittest.main()
