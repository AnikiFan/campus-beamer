# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Keep theme samples comparable and README previews in presentation order."""
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

import pymupdf
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_theme_previews import (GALLERY, THEMES, MAX_PREVIEW_BYTES, MIN_PREVIEW_DPI,
                                   gallery_markup, save_preview, validate_samples)


class ThemePreviewTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.gallery = (('cover', 1, 'Cover', 'Cover', 'Cover'),
                        ('closing', 3, 'Closing', 'Closing', 'Closing'))

    def pdf(self, name, titles=('Cover', 'Body', 'Closing'), section='Section'):
        path = self.root / name
        with pymupdf.open() as document:
            for title in titles:
                page = document.new_page()
                page.insert_text((40, 60), title)
            document.set_toc([[1, section, 2]])
            document.set_metadata({'title': 'Shared example', 'author': 'Author'})
            document.save(path)
        return path

    def test_matching_samples_pass(self):
        with patch('render_theme_previews.GALLERY', self.gallery):
            validate_samples([self.pdf('general.pdf'), self.pdf('school.pdf')])

    def test_small_preview_keeps_pixels_and_dpi(self):
        output = self.root / 'preview.png'
        with pymupdf.open(self.pdf('small.pdf')) as document:
            expected = document[0].get_pixmap(dpi=600, alpha=False)
            save_preview(document[0], output, 600)
        actual = pymupdf.Pixmap(output)
        self.assertEqual(actual.samples, expected.samples)
        self.assertEqual((actual.xres, actual.yres), (600, 600))

    def test_large_preview_fits_budget_with_readable_resolution(self):
        output = self.root / 'preview.png'
        with pymupdf.open() as document:
            page = document.new_page(width=144, height=81)
            noise = pymupdf.Pixmap(pymupdf.csRGB, 1200, 675,
                                  random.Random(42).randbytes(1200 * 675 * 3), False)
            page.insert_image(page.rect, pixmap=noise)
            self.assertGreater(len(page.get_pixmap(dpi=600).tobytes('png')), MAX_PREVIEW_BYTES)
            save_preview(page, output, 600)
            self.assertLessEqual(output.stat().st_size, MAX_PREVIEW_BYTES)
            actual = pymupdf.Pixmap(output)
            self.assertGreaterEqual(actual.xres, MIN_PREVIEW_DPI)
            self.assertLess(actual.xres, 600)
            self.assertAlmostEqual(actual.width / actual.height, 16 / 9, places=2)
            saved = output.read_bytes()
            with self.assertRaisesRegex(ValueError, 'cannot fit'):
                save_preview(page, output, 600, max_bytes=100)
            self.assertEqual(output.read_bytes(), saved)

    def test_documentation_previews_stay_within_size_limit(self):
        images = Path(__file__).resolve().parents[2] / 'docs' / 'images'
        previews = list(images.glob('*.png'))
        self.assertTrue(previews)
        for path in previews:
            with self.subTest(image=path.name):
                self.assertLessEqual(path.stat().st_size, MAX_PREVIEW_BYTES,
                                     'Regenerate documentation previews with make theme-previews')

    def test_palette_fallback_preserves_minimum_resolution(self):
        output = self.root / 'palette.png'
        with pymupdf.open() as document:
            page = document.new_page(width=144, height=81)
            noise = pymupdf.Pixmap(pymupdf.csRGB, 1200, 675,
                                  random.Random(42).randbytes(1200 * 675 * 3), False)
            page.insert_image(page.rect, pixmap=noise)
            save_preview(page, output, 600, max_bytes=60_000)
        with Image.open(output) as image:
            self.assertEqual(image.mode, 'P')
            self.assertAlmostEqual(image.info['dpi'][0], MIN_PREVIEW_DPI, delta=1)
        self.assertLessEqual(output.stat().st_size, 60_000)

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

    def test_readmes_follow_gallery_order_and_end_with_closing(self):
        pages = [item[1] for item in GALLERY]
        self.assertEqual(pages, sorted(set(pages)))
        self.assertEqual(GALLERY[-1][0], 'closing')
        root = Path(__file__).resolve().parents[2]
        for name, english in (('README.md', False), ('README.en.md', True)):
            text = (root / name).read_text()
            self.assertIn(gallery_markup(english), text)
            for theme, _, _ in THEMES:
                self.assertEqual(text.count(f'preview-{theme}-'), len(GALLERY))


if __name__ == '__main__':
    unittest.main()
