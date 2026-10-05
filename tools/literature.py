#!/usr/bin/env python3
# Campus Beamer: fetch DBLP BibTeX and DOI-matched citation snapshots.
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""Search DBLP, fetch its BibTeX, and obtain DOI-matched citation snapshots.

Python standard library only. Network failures never produce a zero count or
replace a previous file. BibTeX goes to stdout unless --output is supplied;
merging into bibliography/refs.bib is deliberately a separate, reviewed authoring step.
"""
import argparse
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlsplit, unquote
from urllib.request import HTTPRedirectHandler, Request, build_opener


DBLP_HOSTS = ("dblp.org", "dblp.uni-trier.de")
SOURCES = ("openalex", "semantic-scholar")


class LiteratureError(Exception):
    """An actionable API, identifier, or metadata error."""


class ServiceRedirects(HTTPRedirectHandler):
    """Keep service credentials on their original host during redirects."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        origin, target = urlsplit(req.full_url), urlsplit(newurl)
        allowed = DBLP_HOSTS if origin.hostname in DBLP_HOSTS else (origin.hostname,)
        if target.scheme != "https" or target.hostname not in allowed:
            raise LiteratureError("API redirected outside its HTTPS service; request stopped.")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def request_text(url, *, timeout=20, headers=None):
    request = Request(url, headers={"User-Agent": "CampusBeamer-Literature/0.1",
                                    **(headers or {})})
    service = urlsplit(url).hostname
    for attempt in range(3):
        try:
            with build_opener(ServiceRedirects()).open(request, timeout=timeout) as response:
                data = response.read().decode("utf-8-sig")
            if re.match(r"\s*<(?:!doctype|html)", data, re.I):
                raise LiteratureError(
                    f"{service} returned an HTML verification/error page, not API data. "
                    "For DBLP try --dblp-host dblp.uni-trier.de, or download the single "
                    "BibTeX entry in a browser and use fetch --input-bib FILE.")
            return data
        except HTTPError as exc:
            status = exc.code
            retry_after = exc.headers.get("Retry-After", 2 ** attempt)
            exc.close()
            if status in (429, 500, 502, 503, 504) and attempt < 2:
                try:
                    delay = float(retry_after)
                except (ValueError, TypeError):
                    delay = 2 ** attempt
                if math.isfinite(delay) and 0 <= delay <= 8:
                    time.sleep(delay)
                    continue
            hints = {401: "Check the service API key.",
                     403: "Access denied; check the API key or service restrictions.",
                     404: "Record not found; check the identifier and publication version.",
                     429: "Rate limit reached; wait before retrying or configure an API key."}
            # Never print HTTPError itself: its URL can contain an OpenAlex key.
            raise LiteratureError(f"{service}: HTTP {status}. "
                                  + hints.get(status, "Try again later.")) from None
        except (URLError, TimeoutError, OSError, UnicodeError):
            raise LiteratureError(f"Cannot read {service}; check network access and timeout.") from None


def request_json(url, **kwargs):
    try:
        result = json.loads(request_text(url, **kwargs))
    except json.JSONDecodeError:
        raise LiteratureError(f"{urlsplit(url).hostname} returned invalid JSON.") from None
    if not isinstance(result, dict):
        raise LiteratureError("Unexpected API response: expected a JSON object.")
    return result


def normalize_doi(value):
    if not isinstance(value, str):
        raise LiteratureError("Expected a DOI string.")
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I)
    if not re.fullmatch(r"10\.\d{4,9}/[^\s{}]+", value, flags=re.I):
        raise LiteratureError("Expected a DOI such as 10.18653/v1/D17-1115.")
    return value.lower()


def normalize_dblp_key(value):
    value = value.strip()
    if value.startswith(("https://", "http://")):
        parsed = urlsplit(value)
        if parsed.hostname not in DBLP_HOSTS or not parsed.path.startswith("/rec/"):
            raise LiteratureError("Expected a DBLP /rec/ URL or publication key.")
        value = unquote(parsed.path[5:])
    value = re.sub(r"^DBLP:", "", value)
    value = re.sub(r"\.(?:html|bib|xml)$", "", value)
    if not re.fullmatch(r"[A-Za-z0-9_:/.-]+", value) or "/" not in value or any(
            part in ("", ".", "..") for part in value.split("/")):
        raise LiteratureError("Invalid DBLP publication key.")
    return value


def search_dblp(query, *, limit=10, offset=0, host="dblp.org", timeout=20):
    url = f"https://{host}/search/publ/api?" + urlencode(
        {"q": query, "format": "json", "h": limit, "f": offset, "c": 0})
    data = request_json(url, timeout=timeout)
    try:
        hits = data["result"]["hits"]
        raw = hits.get("hit", [])
        raw = [raw] if isinstance(raw, dict) else raw
        records = []
        for hit in raw:
            info = hit["info"]
            authors = info.get("authors", {}).get("author", [])
            authors = [authors] if isinstance(authors, (str, dict)) else authors
            key = normalize_dblp_key(info.get("key") or info["url"])
            records.append({
                "key": key, "title": info["title"], "year": info.get("year"),
                "authors": [author.get("text", "") if isinstance(author, dict) else author
                            for author in authors],
                "venue": info.get("venue"), "type": info.get("type"),
                "doi": info.get("doi"), "url": f"https://{host}/rec/{key}",
                "bibtex_url": f"https://{host}/rec/{key}.bib?param=1",
            })
        total = int(hits["@total"])
    except (KeyError, TypeError, ValueError, AttributeError):
        raise LiteratureError("Unexpected DBLP search response; no records were imported.") from None
    return {"source": "DBLP", "query": query, "total": total,
            "offset": offset, "results": records}


def parse_bibtex(text):
    """Read one literal DBLP entry; retain TeX braces and reject macros/extra entries.

    This is intentionally not a general BibTeX database parser. DBLP param=1
    supplies a self-contained entry. For an offline file, export one entry in
    that format, with no @string directives or field concatenation.
    """
    def skip(pos):
        while pos < len(text):
            if text[pos].isspace():
                pos += 1
            elif text[pos] == "%":
                end = text.find("\n", pos)
                pos = len(text) if end < 0 else end + 1
            else:
                break
        return pos

    pos = skip(0)
    match = re.match(r"@([A-Za-z]+)\s*\{\s*([^,\s{}]+)\s*,", text[pos:])
    if not match or match[1].lower() in ("string", "comment", "preamble"):
        raise LiteratureError("Expected one self-contained DBLP BibTeX entry, not HTML or directives.")
    kind, key = match[1], match[2]
    pos += match.end()
    fields = {}
    while True:
        pos = skip(pos)
        if pos < len(text) and text[pos] == "}":
            if skip(pos + 1) != len(text):
                raise LiteratureError("Expected exactly one BibTeX entry; export DBLP with param=1.")
            break
        match = re.match(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*", text[pos:])
        if not match:
            raise LiteratureError("Malformed BibTeX field.")
        name = match[1].lower()
        if name in fields:
            raise LiteratureError(f"Duplicate BibTeX field: {name}.")
        pos += match.end()
        start = pos
        depth = 0
        quoted = False
        delimiter = text[pos:pos + 1]
        if delimiter not in ("{", '"'):
            number = re.match(r"\d+", text[pos:])
            if not number:
                raise LiteratureError("Use literal BibTeX values; macros and concatenation are unsupported.")
            pos += number.end()
        while pos < len(text):
            if delimiter not in ("{", '"'):
                break
            char = text[pos]
            if char == "\\":
                pos += 2
                continue
            if char == '"' and depth == 0:
                quoted = not quoted
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
            pos += 1
            if depth == 0 and not quoted:
                break
        raw = text[start:pos].strip()
        if depth or quoted or not raw:
            raise LiteratureError("Unbalanced or empty BibTeX field.")
        pos = skip(pos)
        if text[pos:pos + 1] not in (",", "}"):
            raise LiteratureError("Expected a field delimiter; concatenation is unsupported.")
        if (raw.startswith("{") and raw.endswith("}")) or (
                raw.startswith('"') and raw.endswith('"')):
            value = raw[1:-1]
        elif raw.isdecimal():
            value = raw
        else:
            raise LiteratureError("Use literal BibTeX values; macros and concatenation are unsupported.")
        fields[name] = value
        if text[pos] == ",":
            pos += 1
    if not fields.get("title") or not fields.get("author") or not (
            fields.get("year") or fields.get("date")):
        raise LiteratureError("BibTeX lacks title, author, or publication year/date.")
    if "crossref" in fields or "xdata" in fields:
        raise LiteratureError("BibTeX depends on another entry; download DBLP with param=1.")
    return kind, key, fields


def render_bibtex(kind, key, fields):
    if not re.fullmatch(r"[A-Za-z0-9_:/.-]+", key):
        raise LiteratureError("Citation key may contain only letters, digits, _ : / . -.")
    return f"@{kind}{{{key},\n" + "".join(
        f"  {name} = {{{value}}},\n" for name, value in fields.items()) + "}\n"


def citation_snapshot(doi, *, source="openalex", timeout=20):
    doi = normalize_doi(doi)
    if source == "openalex":
        params = {"select": "id,doi,title,publication_year,cited_by_count"}
        api_key = os.environ.get("OPENALEX_API_KEY")
        if api_key:
            params["api_key"] = api_key
        data = request_json("https://api.openalex.org/works/https://doi.org/"
                            + quote(doi, safe="") + "?" + urlencode(params), timeout=timeout)
        returned_doi = data.get("doi")
        count, url, year = data.get("cited_by_count"), data.get("id"), data.get("publication_year")
        label = "OpenAlex"
    elif source == "semantic-scholar":
        headers = {}
        api_key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
        if api_key:
            headers["x-api-key"] = api_key
        data = request_json("https://api.semanticscholar.org/graph/v1/paper/DOI:"
                            + quote(doi, safe="") + "?" + urlencode(
                                {"fields": "title,year,citationCount,externalIds,url"}),
                            timeout=timeout, headers=headers)
        identifiers = data.get("externalIds")
        returned_doi = identifiers.get("DOI") if isinstance(identifiers, dict) else None
        count, url, year = data.get("citationCount"), data.get("url"), data.get("year")
        label = "Semantic Scholar"
    else:
        raise LiteratureError("Unknown citation-count source.")
    if not returned_doi or normalize_doi(returned_doi) != doi:
        raise LiteratureError(f"{label} returned a different/missing DOI; count was not accepted.")
    if type(count) is not int or count < 0:
        raise LiteratureError(f"{label} has no valid citation count; this is not zero citations.")
    if not isinstance(url, str) or not isinstance(data.get("title"), str) or not data["title"]:
        raise LiteratureError(f"{label} returned incomplete record metadata.")
    now = datetime.now(timezone.utc)
    return {"source": label, "doi": doi, "title": data["title"], "year": year,
            "count": count, "record_url": url, "retrieved_at": now.isoformat(),
            "bibtex_fields": {"usere": str(count), "userf": f"{label}, {now.date().isoformat()}"}}


def fetch_bibtex(key, *, cite_key=None, source="openalex", input_bib=None,
                 host="dblp.org", timeout=20):
    key = normalize_dblp_key(key)
    url = f"https://{host}/rec/{key}.bib?param=1"
    text = input_bib.read_text(encoding="utf-8-sig") if input_bib else request_text(url, timeout=timeout)
    kind, original_key, fields = parse_bibtex(text)
    if original_key != f"DBLP:{key}":
        raise LiteratureError("BibTeX record key does not match the selected DBLP publication.")
    snapshot = None
    if source != "none":
        if not fields.get("doi"):
            raise LiteratureError("This DBLP entry has no DOI. Fetch with --source none; "
                                  "verify any citation-count match manually.")
        snapshot = citation_snapshot(fields["doi"], source=source, timeout=timeout)
        fields.update(snapshot["bibtex_fields"])
    output_key = cite_key or original_key
    output = render_bibtex(kind, output_key, fields)
    report = {"bibtex_source": "DBLP", "dblp_key": key, "cite_key": output_key,
              "bibtex_url": url, "input_bib": str(input_bib) if input_bib else None,
              "citation_snapshot": snapshot,
              "retrieved_at": datetime.now(timezone.utc).isoformat()}
    return output, report


def write_atomic(path, text):
    """Replace output only after all requests and validation have succeeded."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix="." + path.name, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
        temporary.replace(path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def make_arguments(command):
    """Read Make variables from the environment, never as interpolated shell code."""
    names = {"search": "QUERY", "fetch": "DBLP_KEY", "citations": "DOI"}
    name = names[command]
    value = os.environ.get(name, "")
    if not value.strip():
        raise LiteratureError(f"Set {name} when invoking this Make target.")
    args = ["--dblp-host", os.environ.get("DBLP_HOST") or "dblp.org", command, value]
    if command != "search":
        args += ["--source", os.environ.get("CITATION_SOURCE") or "openalex"]
    if command == "fetch":
        for option, variable in (("--cite-key", "CITE_KEY"), ("--output", "BIB_OUTPUT"),
                                 ("--report", "BIB_REPORT"), ("--input-bib", "INPUT_BIB")):
            if os.environ.get(variable):
                args += [option, os.environ[variable]]
    return args


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if len(argv) == 2 and argv[0] == "--make-target" and argv[1] in ("search", "fetch", "citations"):
        try:
            argv = make_arguments(argv[1])
        except LiteratureError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=float, default=20, help="Per-request timeout in seconds")
    parser.add_argument("--dblp-host", choices=DBLP_HOSTS, default="dblp.org")
    sub = parser.add_subparsers(dest="command", required=True)
    search = sub.add_parser("search", help="List candidates as JSON; never auto-select the first hit")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=10)
    search.add_argument("--offset", type=int, default=0)
    fetch = sub.add_parser("fetch", help="Fetch one DBLP BibTeX entry, optionally with a citation count")
    fetch.add_argument("key", help="DBLP publication key or /rec/ URL")
    fetch.add_argument("--cite-key", help="Override the DBLP citation key")
    fetch.add_argument("--source", choices=(*SOURCES, "none"), default="openalex")
    fetch.add_argument("--input-bib", type=Path, help="Use a browser-downloaded single DBLP entry")
    fetch.add_argument("--report", type=Path, help="Write provenance and citation snapshot as JSON")
    citations = sub.add_parser("citations", help="Look up a verified DOI; emit JSON and usere/userf")
    citations.add_argument("doi")
    citations.add_argument("--source", choices=SOURCES, default="openalex")
    for command in (search, fetch, citations):
        command.add_argument("--output", type=Path, help="Save result instead of writing stdout")
    args = parser.parse_args(argv)
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and positive")
    if args.command == "search" and not (1 <= args.limit <= 1000 and args.offset >= 0):
        parser.error("--limit must be 1..1000; --offset must be nonnegative")
    try:
        if args.command == "search":
            data = search_dblp(args.query, limit=args.limit, offset=args.offset,
                               host=args.dblp_host, timeout=args.timeout)
            result = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        elif args.command == "citations":
            data = citation_snapshot(args.doi, source=args.source, timeout=args.timeout)
            result = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        else:
            if args.output and args.input_bib and args.output.resolve() == args.input_bib.resolve():
                raise LiteratureError("--output must not overwrite the input BibTeX file.")
            if args.report and ((args.output and args.report.resolve() == args.output.resolve()) or
                                (args.input_bib and args.report.resolve() == args.input_bib.resolve())):
                raise LiteratureError("--report must be separate from BibTeX input and output.")
            result, report = fetch_bibtex(args.key, cite_key=args.cite_key, source=args.source,
                                          input_bib=args.input_bib, host=args.dblp_host,
                                          timeout=args.timeout)
            if args.report:
                write_atomic(args.report, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        if args.output:
            write_atomic(args.output, result)
            print(f"Saved {args.output}", file=sys.stderr)
        else:
            sys.stdout.write(result)
        return 0
    except (LiteratureError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
