# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""Ensure PDF comparison catches visual and invisible behavior regressions."""
import sys
import tempfile
import unittest
from pathlib import Path

import pymupdf
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from compare_pdf import compare


class ComparePdfTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.before = Path(self.temp.name) / 'before.pdf'
        self.after = Path(self.temp.name) / 'after.pdf'
        with pymupdf.open() as doc:
            page = doc.new_page(width=160, height=90)
            page.insert_text((10, 20), 'A presentation')
            page.insert_link({'kind': pymupdf.LINK_URI, 'from': pymupdf.Rect(10, 10, 90, 30),
                              'uri': 'https://example.org/before'})
            doc.set_toc([[1, 'Opening', 1]])
            doc.set_metadata({'title': 'Demo'})
            doc.save(self.before)

    def edit(self, callback):
        with pymupdf.open(self.before) as doc:
            callback(doc)
            doc.save(self.after)
        return compare(self.before, self.after, dpi=72)

    def test_ignores_creation_timestamp_and_object_rewriting(self):
        result = self.edit(lambda d: d.set_metadata(dict(d.metadata, creationDate='D:20000101000000Z')))
        self.assertFalse(result['failures'])
        self.assertFalse(result['byte_identical'])
        strict = compare(self.before, self.after, dpi=72, strict_bytes=True)
        self.assertIn('PDF files differ byte for byte', strict['failures'])

    def test_changed_link_with_identical_pixels_fails(self):
        def change(doc):
            link = doc[0].get_links()[0]
            link['uri'] = 'https://example.org/after'
            doc[0].update_link(link)
        result = self.edit(change)
        self.assertIn('page 1: links changed', result['failures'])
        self.assertFalse(any('pixels' in s for s in result['failures']))

    def test_changed_pixels_fail(self):
        result = self.edit(lambda d: d[0].draw_rect((100, 40, 110, 50), fill=(1, 0, 0)))
        self.assertIn('page 1: pixels changed at 72 DPI', result['failures'])

    def test_changed_page_count_fails(self):
        result = self.edit(lambda d: d.new_page(width=160, height=90))
        self.assertIn('page count: 1 != 2', result['failures'])

    def test_changed_title_and_outline_fail(self):
        def change(doc):
            doc.set_metadata({'title': 'Changed'})
            doc.set_toc([[1, 'Changed', 1]])
        result = self.edit(change)
        self.assertIn('PDF outline changed', result['failures'])
        self.assertTrue(any('metadata changed' in s for s in result['failures']))


if __name__ == '__main__':
    unittest.main()
