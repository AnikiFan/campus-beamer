# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Verify localized preview matrices, rendering budgets and source distribution."""
from html.parser import HTMLParser
from pathlib import Path
import random
import re
import sys
import tempfile
import unittest
from unittest.mock import patch

import pymupdf
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_source import FILES
from render_theme_previews import (GALLERY, THEMES,
                                   MAX_PREVIEW_BYTES, MAX_GALLERY_BYTES, MIN_PREVIEW_WIDTH,
                                   gallery_markup, main, preview_names, render_gallery,
                                   save_preview, validate_samples)


class GalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.images = []
        self.alt_texts = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table':
            self.tables.append([])
        elif tag == 'tr':
            self.tables[-1].append([])
        elif tag in ('td', 'th'):
            self.tables[-1][-1].append(tag)
        elif tag == 'img':
            self.images.append(attrs['src'])
            self.alt_texts.append(attrs.get('alt'))
        elif tag == 'a':
            self.links.append(attrs['href'])


class ThemePreviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.gallery = (('cover', 1, 'Cover', 'Cover', 'Cover', 'English cover'),
                        ('closing', 3, 'Closing', 'Closing', 'Closing', 'English closing'))

    def pdf(self, name, titles=('Cover', 'Body', 'Closing'), section='Section'):
        path = self.root / name
        with pymupdf.open() as document:
            for title in titles:
                page = document.new_page(width=144, height=81)
                page.insert_text((10, 30), title)
            document.set_toc([[1, section, 2]])
            document.set_metadata({'title': 'Shared example', 'author': 'Author'})
            document.save(path)
        return path

    def test_matching_samples_pass(self):
        with patch('render_theme_previews.GALLERY', self.gallery):
            validate_samples([self.pdf('general.pdf'), self.pdf('school.pdf')])

    def test_english_has_localized_anchors_and_independent_sections(self):
        english = self.pdf('english.pdf', ('English cover', 'Body', 'English closing'), 'English section')
        with patch('render_theme_previews.GALLERY', self.gallery):
            validate_samples([self.pdf('general.pdf')], english)
            with self.assertRaisesRegex(ValueError, 'gallery anchor'):
                validate_samples([self.pdf('other.pdf')], self.pdf('wrong-language.pdf'))

    def test_small_preview_keeps_requested_pixels(self):
        output = self.root / 'preview.png'
        with pymupdf.open(self.pdf('small.pdf')) as document:
            page = document[0]
            scale = 640 / page.rect.width
            expected = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False)
            save_preview(page, output, 640)
        actual = pymupdf.Pixmap(output)
        self.assertEqual(actual.samples, expected.samples)
        self.assertEqual(actual.width, 640)

    def test_large_preview_fits_budget_without_crossing_width_floor(self):
        output = self.root / 'preview.png'
        with pymupdf.open() as document:
            page = document.new_page(width=144, height=81)
            noise = pymupdf.Pixmap(pymupdf.csRGB, 1200, 675,
                                  random.Random(42).randbytes(1200 * 675 * 3), False)
            page.insert_image(page.rect, pixmap=noise)
            scale = 640 / page.rect.width
            self.assertGreater(len(page.get_pixmap(matrix=pymupdf.Matrix(scale, scale)).tobytes('png')),
                               MAX_PREVIEW_BYTES)
            save_preview(page, output, 640)
            self.assertLessEqual(output.stat().st_size, MAX_PREVIEW_BYTES)
            with Image.open(output) as actual:
                self.assertGreaterEqual(actual.width, MIN_PREVIEW_WIDTH)
                self.assertLess(actual.width, 640)
                self.assertAlmostEqual(actual.width / actual.height, 16 / 9, places=2)
                self.assertEqual(actual.mode, 'P')
            saved = output.read_bytes()
            with self.assertRaisesRegex(ValueError, 'cannot fit'):
                save_preview(page, output, 640, max_bytes=100)
            self.assertEqual(output.read_bytes(), saved)

    def test_documentation_budget_and_packaging_match_used_images(self):
        root = Path(__file__).resolve().parents[2]
        previews = list((root / 'docs/images').glob('*.png'))
        expected = set().union(*(preview_names(theme) for theme in [*(item[0] for item in THEMES), 'general-en']))
        self.assertEqual({path.name for path in previews}, expected)
        self.assertLessEqual(sum(path.stat().st_size for path in previews), MAX_GALLERY_BYTES)
        for path in previews:
            with self.subTest(image=path.name):
                self.assertLessEqual(path.stat().st_size, MAX_PREVIEW_BYTES)
                self.assertIn(path.relative_to(root).as_posix(), FILES)
        references = set()
        for name in ('README.md', 'README.en.md'):
            references.update(re.findall(r'docs/images/([\w-]+\.png)', (root / name).read_text()))
        self.assertEqual(references, expected)
        packaged = {Path(name).name for name in FILES if name.startswith('docs/images/')}
        self.assertEqual(packaged, expected)

    def test_different_page_count_or_sections_fail(self):
        first = self.pdf('general.pdf')
        for titles, section in ((('Cover', 'Closing'), 'Section'),
                                (('Cover', 'Body', 'Closing'), 'Different')):
            with self.subTest(titles=titles, section=section):
                other = self.pdf('school.pdf', titles, section)
                with patch('render_theme_previews.GALLERY', self.gallery):
                    with self.assertRaisesRegex(ValueError, 'share page count'):
                        validate_samples([first, other])

    def test_moved_closing_page_is_rejected(self):
        other = self.pdf('wrong-order.pdf', ('Cover', 'Closing', 'Body'))
        with patch('render_theme_previews.GALLERY', self.gallery):
            with self.assertRaisesRegex(ValueError, 'gallery anchor'):
                validate_samples([other])

    def test_readmes_have_all_theme_rows_and_shared_features(self):
        root = Path(__file__).resolve().parents[2]
        self.assertEqual(GALLERY[-1][0], 'closing')
        for name, english in (('README.md', False), ('README.en.md', True)):
            with self.subTest(readme=name):
                markup = gallery_markup(english)
                self.assertIn(markup, (root / name).read_text())
                parsed = GalleryParser()
                parsed.feed(markup)
                self.assertEqual([len(row) for row in parsed.tables[0]], [5] * (len(THEMES) + 1))
                self.assertEqual([len(row) for row in parsed.tables[1]], [3, 3, 3, 3])
                self.assertEqual(len(parsed.images), 4 * len(THEMES) + 6)
                self.assertTrue(all(parsed.alt_texts))
                self.assertEqual(len(set(parsed.images)), 4 * len(THEMES) + 6)
                for path in parsed.images:
                    self.assertIn(path, parsed.links)
                    self.assertTrue((root / path).is_file())
                general = 'general-en' if english else 'general'
                for key in ('cover', 'section', 'body', 'closing'):
                    self.assertIn(f'docs/images/preview-{general}-{key}.png', parsed.images)
                self.assertEqual(sum(f'preview-{general}-' in path for path in parsed.images), 10)

    def test_renderer_only_emits_selected_pages(self):
        pdf = self.pdf('all.pdf', [f'Page {i}' for i in range(1, 51)])
        for theme, count in (('tsinghua', 4), ('tokyo-night', 4), ('undefined', 4), ('general-en', 10)):
            output = self.root / theme
            output.mkdir()
            render_gallery(pdf, theme, output)
            files = list(output.glob('*.png'))
            self.assertEqual(len(files), count)
            self.assertEqual({path.name for path in files}, preview_names(theme))
            with Image.open(output / f'preview-{theme}-cover.png') as image:
                self.assertEqual(image.width, 1200 if theme == 'general-en' else 640)

    def test_cli_cleans_known_retired_files_but_keeps_unrelated_images(self):
        output = self.root / 'images'
        output.mkdir()
        old = output / 'preview-general-toc.png'
        old.write_bytes(b'old')
        custom = output / 'my-photo.png'
        custom.write_bytes(b'private image')
        pdf = self.pdf('general.pdf')
        with patch('render_theme_previews.GALLERY', self.gallery), patch.object(sys, 'argv', [
                'render_theme_previews', '--pdf', str(pdf), '--theme', 'general', '--output', str(output)]):
            main()
        self.assertFalse(old.exists())
        self.assertEqual(custom.read_bytes(), b'private image')
        self.assertTrue((output / 'preview-general-cover.png').is_file())


if __name__ == '__main__':
    unittest.main()
