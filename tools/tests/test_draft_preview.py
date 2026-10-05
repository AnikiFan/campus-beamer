# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""Draft selection, diagnostic provenance and stale-page regression tests."""
from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
import unittest

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from draft_preview import create_preview, layout_warnings, select_pages


class DraftTests(unittest.TestCase):
    def test_page_selection(self):
        self.assertEqual(select_pages('3,1-3,5', 5), [1, 2, 3, 5])
        self.assertEqual(select_pages('all', 3), [1, 2, 3])
        for spec in ('0', '6', '3-1', '2,', '', '1-999999999', 'one'):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                select_pages(spec, 5)

    def test_log_line_numbers_and_wrapped_diagnostics(self):
        log = (
            'Package loaded\n'
            'Overfull \\hbox (12.0pt too wide) in paragraph at lines 9--11\n'
            '[]\n'
            'Underfull \\vbox (badness 10000) has occurred while \\output is active []\n'
            'Overfull \\vbox (20.0pt too high) detected at\n'
            'lines 30--31\n'
        )
        warnings = layout_warnings(log)
        self.assertEqual([w['log_line'] for w in warnings], [2, 4, 5])
        self.assertEqual([w['kind'] for w in warnings], ['overfull', 'underfull', 'overfull'])
        self.assertIn('lines 30--31', warnings[2]['message'])
        self.assertTrue(all('page' not in w for w in warnings))

    def test_full_subset_and_shrinking_document(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pdf, log, out = root/'deck.pdf', root/'deck.log', root/'preview'
            with pymupdf.open() as doc:
                for number in range(13):
                    page = doc.new_page(width=160, height=90)
                    page.insert_text((12, 24), f'Page {number+1}')
                doc.save(pdf)
            log.write_text('Overfull \\hbox (1pt too wide) detected at line 6\n')
            with redirect_stdout(StringIO()):
                report = create_preview(pdf, out, log, dpi=72)
            self.assertEqual(len(report['contact_sheets']), 2)
            self.assertEqual(len(list(out.glob('page-*.png'))), 13)
            self.assertEqual(report['overfull'], 1)
            self.assertEqual(json.loads((out/'report.json').read_text()), report)
            original_sha = report['pdf_sha256']
            # The rendered PNG matches the actual PDF page pixels.
            with pymupdf.open(pdf) as doc:
                self.assertEqual(pymupdf.Pixmap(out/'page-0001.png').samples,
                                 doc[0].get_pixmap(dpi=72, alpha=False).samples)
            (out/'keep.txt').write_text('user file')
            with redirect_stdout(StringIO()):
                report = create_preview(pdf, out, log, dpi=72, pages='2,5-6')
            self.assertEqual(report['preview_pages'], [2, 5, 6])
            self.assertEqual(len(list(out.glob('page-*.png'))), 3)
            self.assertFalse((out/'contact-002.png').exists())
            self.assertTrue((out/'keep.txt').exists())
            with pymupdf.open() as doc:
                doc.new_page(width=160, height=90)
                doc.save(pdf)
            with redirect_stdout(StringIO()):
                report = create_preview(pdf, out, root/'missing.log', dpi=72)
            self.assertFalse(report['log_available'])
            self.assertIsNone(report['overfull'])
            self.assertNotEqual(report['pdf_sha256'], original_sha)
            self.assertEqual([p.name for p in out.glob('page-*.png')], ['page-0001.png'])
            self.assertIn('diagnostics unknown', (out/'index.html').read_text())
            with self.assertRaises(ValueError):
                create_preview(pdf, out, log, pages='2')
            # Validation failures do not delete the last successful preview.
            self.assertTrue((out/'page-0001.png').exists())


if __name__ == '__main__':
    unittest.main()
