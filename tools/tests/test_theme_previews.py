# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Keep theme samples comparable and README previews in presentation order."""
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from render_theme_previews import GALLERY, gallery_markup, validate_samples


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


if __name__ == '__main__':
    unittest.main()
