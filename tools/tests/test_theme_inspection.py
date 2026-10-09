# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""PDF inspection must reject readable-layout and visible-source regressions."""
import sys
import unittest
from pathlib import Path

import pymupdf

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from check_theme import check_caption_below, check_description_rows, check_doc_citations


class ThemeInspectionTests(unittest.TestCase):
    def page(self):
        document = pymupdf.open()
        self.addCleanup(document.close)
        return document.new_page(width=453.55, height=255.12)

    def description(self, *, label_shift=0, body_shift=0):
        page = self.page()
        for label, marker, baseline, shift in (('Alpha', 'TextA', 80, 0),
                                               ('Beta', 'TextB', 110, label_shift)):
            width = pymupdf.get_text_length(label, fontsize=12)
            page.insert_text((140 - width + shift, baseline), label, fontsize=12)
            page.insert_text((155 + (body_shift if marker == 'TextB' else 0), baseline),
                             marker, fontsize=12)
        return page

    def test_aligned_labels_and_explanations_pass(self):
        check_description_rows(self.description(), ('Alpha', 'Beta'), ('TextA', 'TextB'))

    def test_wrong_width_sample_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'right edges'):
            check_description_rows(self.description(label_shift=15),
                                   ('Alpha', 'Beta'), ('TextA', 'TextB'))

    def test_misaligned_explanation_column_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'column starts'):
            check_description_rows(self.description(body_shift=10),
                                   ('Alpha', 'Beta'), ('TextA', 'TextB'))

    def test_caption_below_graphic_passes(self):
        page = self.page()
        page.insert_text((100, 160), 'Diagram caption', fontsize=9)
        check_caption_below(page, 'Diagram caption', 130, footer_top=215)

    def test_missing_caption_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, 'missing figure caption'):
            check_caption_below(self.page(), 'Diagram caption', 130, footer_top=215)

    def test_caption_over_graphic_or_footer_is_rejected(self):
        for baseline, diagnostic in ((130, 'graphic'), (240, 'footer')):
            with self.subTest(baseline=baseline):
                page = self.page()
                page.insert_text((100, baseline), 'Diagram caption', fontsize=9)
                with self.assertRaisesRegex(RuntimeError, diagnostic):
                    check_caption_below(page, 'Diagram caption', 130, footer_top=215)

    def test_clickable_short_label_does_not_replace_visible_url(self):
        page = self.page()
        page.insert_text((305.9, 18), 'Example documentation', fontsize=6, color=(.5, .5, .5))
        page.insert_link({'kind': pymupdf.LINK_URI, 'from': pymupdf.Rect(305, 10, 370, 20),
                          'uri': 'https://example.org/'})
        # Reload so newly inserted annotations are available to get_links().
        page = page.parent.reload_page(page)
        with self.assertRaisesRegex(RuntimeError, 'URL is not visible'):
            check_doc_citations(page.parent, '')

    def test_visible_url_with_wrong_target_is_rejected(self):
        page = self.page()
        page.insert_text((305.9, 18), 'Example documentation', fontsize=6, color=(.5, .5, .5))
        page.insert_text((305.9, 26), 'https://example.org/', fontsize=6, color=(.5, .5, .5))
        page.insert_link({'kind': pymupdf.LINK_URI, 'from': pymupdf.Rect(305, 20, 370, 30),
                          'uri': 'https://example.org/incorrect'})
        page = page.parent.reload_page(page)
        with self.assertRaisesRegex(RuntimeError, 'target/position'):
            check_doc_citations(page.parent, '')


if __name__ == '__main__':
    unittest.main()
