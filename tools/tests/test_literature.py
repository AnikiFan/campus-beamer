# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""Bibliographic identity, provenance, API failures, and safe staged output."""
import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.request import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import literature as lit


KEY = "conf/example/Author24"
DOI = "10.1234/example.24"
BIB = r'''% A self-contained single-entry DBLP export.
@inproceedings{DBLP:conf/example/Author24,
  author = {Example Author and Other Author},
  title = {An {Example}, with {Nested {Braces}} and \{symbols\}},
  booktitle = {Example Proceedings},
  year = 2024,
  doi = {10.1234/example.24},
}
'''


def openalex(count=12, doi=DOI):
    return {"id": "https://openalex.org/W123", "doi": "https://doi.org/" + doi,
            "title": "An Example", "publication_year": 2024, "cited_by_count": count}


class LiteratureTests(unittest.TestCase):
    def test_identifiers_and_publication_urls(self):
        for doi in (DOI.upper(), "DOI:" + DOI, "https://doi.org/" + DOI,
                    "https://dx.doi.org/" + DOI):
            self.assertEqual(lit.normalize_doi(doi), DOI)
        for key in (KEY, "DBLP:" + KEY, "https://dblp.org/rec/" + KEY + ".html",
                    "https://dblp.uni-trier.de/rec/" + KEY + ".bib?param=1"):
            self.assertEqual(lit.normalize_dblp_key(key), KEY)
        for key in ("https://example.org/rec/" + KEY, "conf/../file", "bad key", "x//y"):
            with self.assertRaises(lit.LiteratureError):
                lit.normalize_dblp_key(key)
        for doi in ("bad", "10.1234/no whitespace", None):
            with self.assertRaises(lit.LiteratureError):
                lit.normalize_doi(doi)

    def test_nested_bibtex_roundtrip_preserves_metadata(self):
        kind, key, fields = lit.parse_bibtex(BIB)
        self.assertEqual(fields["year"], "2024")
        self.assertIn("{Nested {Braces}}", fields["title"])
        self.assertEqual(lit.parse_bibtex(lit.render_bibtex(kind, key, fields)), (kind, key, fields))

    def test_quoted_values_comments_and_optional_trailing_comma(self):
        bib = BIB.replace("year = 2024,", 'year = "2024", % comment\n').replace(
            "doi = {10.1234/example.24},", 'doi = "10.1234/example.24"').replace(
            "title = {An {Example}, with {Nested {Braces}} and \\{symbols\\}},",
            'title = "An {Example}, with nested braces",')
        self.assertEqual(lit.parse_bibtex(bib)[2]["title"], "An {Example}, with nested braces")

    def test_rejects_incomplete_or_unsupported_bibtex(self):
        cases = ["<html>verification</html>", BIB + BIB,
                 BIB.replace("year = 2024,", 'year = jan,'),
                 BIB.replace("year = 2024,", 'year = {20} # {24},'),
                 BIB.replace("year = 2024,", 'year = "20" # "24",'),
                 BIB.replace("year = 2024,", "year = {2024}, year = {2025},"),
                 BIB.replace("doi = {10.1234/example.24},", "crossref = {Other},"),
                 BIB.replace("author = {Example Author and Other Author},", ""), BIB[:-3]]
        for bib in cases:
            with self.subTest(bib=bib), self.assertRaises(lit.LiteratureError):
                lit.parse_bibtex(bib)

    def test_dblp_search_handles_single_or_multiple_authors_and_hits(self):
        info = {"key": KEY, "title": "An Example", "year": "2024",
                "authors": {"author": {"text": "Example Author"}}}
        with patch.object(lit, "request_json", return_value={"result": {"hits": {
                "@total": "2", "hit": {"info": info}}}}) as request:
            data = lit.search_dblp('a title with $(literal) & symbols', offset=10)
        self.assertEqual(data["results"][0]["authors"], ["Example Author"])
        self.assertEqual(data["results"][0]["key"], KEY)
        self.assertEqual(data["total"], 2)
        self.assertIn("f=10", request.call_args.args[0])
        info["authors"]["author"] = ["First", {"text": "Second"}]
        info.pop("key")
        info["url"] = "https://dblp.org/rec/" + KEY
        with patch.object(lit, "request_json", return_value={"result": {"hits": {
                "@total": "1", "hit": [{"info": info}]}}}):
            self.assertEqual(lit.search_dblp("example")["results"][0]["authors"], ["First", "Second"])

    def test_zero_search_results_and_malformed_search(self):
        with patch.object(lit, "request_json", return_value={"result": {"hits": {"@total": "0"}}}):
            self.assertEqual(lit.search_dblp("missing")["results"], [])
        with patch.object(lit, "request_json", return_value={}), self.assertRaises(lit.LiteratureError):
            lit.search_dblp("missing")

    def test_openalex_snapshot_requires_matching_doi_and_valid_count(self):
        for count in (0, 12):
            with patch.object(lit, "request_json", return_value=openalex(count)):
                snapshot = lit.citation_snapshot(DOI)
            self.assertEqual(snapshot["count"], count)
            self.assertEqual(snapshot["bibtex_fields"]["usere"], str(count))
            self.assertRegex(snapshot["bibtex_fields"]["userf"], r"OpenAlex, \d{4}-\d{2}-\d{2}")
            self.assertTrue(snapshot["retrieved_at"].endswith("+00:00"))
        for invalid in (None, -1, True, "12", 12.5):
            with patch.object(lit, "request_json", return_value=openalex(invalid)), \
                    self.assertRaises(lit.LiteratureError):
                lit.citation_snapshot(DOI)
        with patch.object(lit, "request_json", return_value=openalex(12, "10.1234/different")), \
                self.assertRaisesRegex(lit.LiteratureError, "DOI"):
            lit.citation_snapshot(DOI)

    def test_semantic_scholar_snapshot(self):
        data = {"externalIds": {"DOI": DOI}, "citationCount": 7, "year": 2024,
                "title": "An Example", "url": "https://www.semanticscholar.org/paper/abc"}
        with patch.dict(os.environ, {"SEMANTIC_SCHOLAR_API_KEY": "test-secret"}), \
                patch.object(lit, "request_json", return_value=data) as request:
            snapshot = lit.citation_snapshot(DOI, source="semantic-scholar")
        self.assertEqual(snapshot["source"], "Semantic Scholar")
        self.assertEqual(request.call_args.kwargs["headers"], {"x-api-key": "test-secret"})
        self.assertNotIn("test-secret", json.dumps(snapshot))
        data["externalIds"] = None
        with patch.object(lit, "request_json", return_value=data), self.assertRaises(lit.LiteratureError):
            lit.citation_snapshot(DOI, source="semantic-scholar")

    def test_fetch_adds_only_count_and_provenance_fields(self):
        with patch.object(lit, "request_text", return_value=BIB), \
                patch.object(lit, "request_json", return_value=openalex()):
            output, report = lit.fetch_bibtex(KEY, cite_key="Example2024")
        fields = lit.parse_bibtex(output)[2]
        original = lit.parse_bibtex(BIB)[2]
        self.assertEqual({name: fields[name] for name in original}, original)
        self.assertEqual(fields["usere"], "12")
        self.assertNotIn("userb", fields)  # No invented affiliation or venue/date.
        self.assertEqual(report["citation_snapshot"]["doi"], DOI)

    def test_wrong_record_key_or_missing_doi_does_not_query_counts(self):
        for bib in (BIB.replace(KEY, "conf/another/Paper"),
                    BIB.replace("doi = {10.1234/example.24},", "")):
            with patch.object(lit, "request_text", return_value=bib), \
                    patch.object(lit, "citation_snapshot") as count, self.assertRaises(lit.LiteratureError):
                lit.fetch_bibtex(KEY)
            count.assert_not_called()

    def test_offline_download_without_doi_can_be_imported_without_count(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "download.bib"
            path.write_text(BIB.replace("doi = {10.1234/example.24},", ""), encoding="utf-8")
            with patch.object(lit, "request_text") as network:
                output, report = lit.fetch_bibtex(KEY, source="none", input_bib=path)
            network.assert_not_called()
            self.assertIsNone(report["citation_snapshot"])
            self.assertNotIn("usere", lit.parse_bibtex(output)[2])

    def test_failed_fetch_preserves_previous_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            bib, report = Path(folder) / "out.bib", Path(folder) / "out.json"
            bib.write_text("previous bib")
            report.write_text("previous report")
            with patch.object(lit, "request_text", return_value=BIB), \
                    patch.object(lit, "citation_snapshot", side_effect=lit.LiteratureError("failed")), \
                    contextlib.redirect_stderr(io.StringIO()):
                status = lit.main(["fetch", KEY, "--output", str(bib), "--report", str(report)])
            self.assertEqual(status, 1)
            self.assertEqual(bib.read_text(), "previous bib")
            self.assertEqual(report.read_text(), "previous report")

    def test_successful_cli_stages_bib_and_json(self):
        with tempfile.TemporaryDirectory() as folder:
            bib, report = Path(folder) / "out.bib", Path(folder) / "out.json"
            with patch.object(lit, "request_text", return_value=BIB), \
                    patch.object(lit, "request_json", return_value=openalex()), \
                    contextlib.redirect_stderr(io.StringIO()):
                status = lit.main(["fetch", KEY, "--output", str(bib), "--report", str(report)])
            self.assertEqual(status, 0)
            self.assertIn("usere", lit.parse_bibtex(bib.read_text())[2])
            self.assertEqual(json.loads(report.read_text())["citation_snapshot"]["count"], 12)

    def test_cli_rejects_overwriting_input_or_conflicting_report(self):
        with patch.object(lit, "fetch_bibtex") as fetch, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lit.main(["fetch", KEY, "--input-bib", "a.bib", "--output", "a.bib"]), 1)
            self.assertEqual(lit.main(["fetch", KEY, "--report", "a.bib", "--output", "a.bib"]), 1)
        fetch.assert_not_called()

    def test_http_html_and_network_errors_are_actionable(self):
        response = io.BytesIO(b"<!doctype html><html>Bot check</html>")
        with patch.object(lit, "build_opener") as opener:
            opener.return_value.open.return_value = response
            with self.assertRaisesRegex(lit.LiteratureError, "verification/error"):
                lit.request_text("https://dblp.org/search/publ/api")
            opener.return_value.open.side_effect = URLError("network down")
            with self.assertRaisesRegex(lit.LiteratureError, "network"):
                lit.request_text("https://dblp.org/search/publ/api")

    def test_http_retry_and_secret_redaction(self):
        url = "https://api.openalex.org/works/doi?api_key=test-secret"
        with patch.object(lit, "build_opener") as opener, patch.object(lit.time, "sleep") as sleep:
            opener.return_value.open.side_effect = [HTTPError(url, 429, "busy", {}, None),
                                                    io.BytesIO(b'{"ok": true}')]
            self.assertEqual(lit.request_json(url), {"ok": True})
            sleep.assert_called_once_with(1)
            opener.return_value.open.side_effect = HTTPError(url, 401, "test-secret", {}, None)
            with self.assertRaises(lit.LiteratureError) as error:
                lit.request_json(url)
        self.assertNotIn("test-secret", str(error.exception))

    def test_malformed_json_is_rejected(self):
        for text in ("not json", "[]"):
            with patch.object(lit, "request_text", return_value=text), self.assertRaises(lit.LiteratureError):
                lit.request_json("https://dblp.org/search/publ/api")

    def test_redirect_cannot_send_credentials_to_another_host(self):
        req = Request("https://api.semanticscholar.org/graph/v1/paper/example",
                      headers={"x-api-key": "test-secret"})
        with self.assertRaises(lit.LiteratureError):
            lit.ServiceRedirects().redirect_request(req, None, 302, "redirect", {}, "https://example.org/")

    def test_make_values_are_passed_as_literal_arguments(self):
        title = 'a title with `code`, "quotes", & $(literal)'
        with patch.dict(os.environ, {"QUERY": title}, clear=True):
            self.assertEqual(lit.make_arguments("search")[-1], title)
        with patch.dict(os.environ, {}, clear=True), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(lit.main(["--make-target", "fetch"]), 1)

    @unittest.skipUnless(shutil.which("make"), "GNU Make not installed")
    def test_make_offline_fetch_stages_bib_and_provenance(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            download, output, report = root / "download.bib", root / "paper.bib", root / "paper.json"
            download.write_text(BIB, encoding="utf-8")
            project = Path(lit.__file__).resolve().parents[1]
            result = subprocess.run(["make", "--no-print-directory", "bibtex",
                                     f"PYTHON={sys.executable}", f"DBLP_KEY={KEY}",
                                     f"INPUT_BIB={download}", "CITATION_SOURCE=none",
                                     "CITE_KEY=Example2024", f"BIB_OUTPUT={output}",
                                     f"BIB_REPORT={report}"], cwd=project,
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(lit.parse_bibtex(output.read_text())[1], "Example2024")
            self.assertIsNone(json.loads(report.read_text())["citation_snapshot"])
            self.assertEqual(download.read_text(), BIB)

    @unittest.skipUnless(shutil.which("make"), "GNU Make not installed")
    def test_make_does_not_evaluate_title_as_shell_or_make_code(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            marker = root / "must-not-exist"
            title = f'quotes " & `code` $HOME $(shell touch {marker})'
            probe = root / "probe.py"
            probe.write_text('import json, os\nprint(json.dumps(os.environ["QUERY"]))\n')
            makefile = root / "Makefile"
            original = Path(lit.__file__).resolve().parents[1] / "Makefile"
            makefile.write_text(original.read_text().replace(
                '@$(PYTHON) tools/literature.py --make-target search', f'@$(PYTHON) "{probe}"'))
            result = subprocess.run(["make", "--no-print-directory", "literature",
                                     f"PYTHON={sys.executable}", f"QUERY={title}"],
                                    cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), title)
            self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
