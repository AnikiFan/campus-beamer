#!/usr/bin/env python3
# Campus Beamer: render draft page previews and a layout report.
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
"""Render the final PDF layout for fast visual iteration, using PyMuPDF only."""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from html import escape
import json
from pathlib import Path
import re

import pymupdf


def select_pages(spec: str, count: int) -> list[int]:
    """Return sorted, unique, 1-based PDF pages; reject typos and reversed ranges."""
    if spec.strip().lower() == 'all':
        return list(range(1, count + 1))
    selected = set()
    for token in spec.split(','):
        token = token.strip()
        if not re.fullmatch(r'\d+(?:-\d+)?', token):
            raise ValueError('Pages must be all or a list such as 2,5-8.')
        ends = [int(part) for part in token.split('-')]
        start, end = ends[0], ends[-1]
        if not 1 <= start <= end <= count:
            raise ValueError(f'Page range {token!r} is outside 1..{count} or reversed.')
        selected.update(range(start, end + 1))
    return sorted(selected)


def layout_warnings(log_text: str) -> list[dict]:
    """Keep actual log line numbers, not guessed PDF pages or TeX filenames."""
    lines = log_text.splitlines()
    warnings = []
    for index, line in enumerate(lines):
        match = re.match(r'(Overfull|Underfull) \\([hv])box\b', line)
        if not match:
            continue
        message = line
        # TeX wraps long diagnostics at its print-line limit.
        if 'line' not in line and 'active' not in line:
            for continuation in lines[index + 1:index + 3]:
                if not continuation.strip() or re.match(r'(Overfull|Underfull)', continuation):
                    break
                message += ' ' + continuation.strip()
                if 'line' in continuation or 'active' in continuation:
                    break
        warnings.append({'kind': match[1].lower(), 'box': match[2],
                         'log_line': index + 1, 'message': message})
    return warnings


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        sha = hashlib.sha256()
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(chunk)
    return sha.hexdigest()


def create_preview(pdf_path: Path, output: Path, log_path: Path, dpi=96, pages='all') -> dict:
    if type(dpi) is not int or dpi <= 0:
        raise ValueError('DPI must be a positive integer.')
    pdf_path, output, log_path = map(Path, (pdf_path, output, log_path))
    log_text = log_path.read_text(encoding='utf-8', errors='replace') if log_path.is_file() else None
    warnings = layout_warnings(log_text) if log_text is not None else []
    counts = Counter(warning['kind'] for warning in warnings)
    generated = set()
    with pymupdf.open(pdf_path) as pdf:
        if not pdf.is_pdf or pdf.needs_pass or not len(pdf):
            raise ValueError('Input must be a nonempty, unencrypted PDF.')
        selected = select_pages(pages, len(pdf))
        output.mkdir(parents=True, exist_ok=True)
        for number in selected:
            name = f'page-{number:04d}.png'
            pdf[number - 1].get_pixmap(dpi=dpi, alpha=False).save(output / name)
            generated.add(name)

        # Bounded contact sheets remain legible even for a long deck.
        sheets = []
        for offset in range(0, len(selected), 12):
            group = selected[offset:offset + 12]
            with pymupdf.open() as contact:
                sheet = contact.new_page(width=1080, height=((len(group) + 2) // 3) * 240)
                for position, number in enumerate(group):
                    x, y = position % 3 * 360, position // 3 * 240
                    sheet.insert_text((x + 8, y + 16), f'PDF page {number}', fontsize=11)
                    sheet.insert_image(pymupdf.Rect(x + 8, y + 24, x + 352, y + 232),
                                       filename=str(output / f'page-{number:04d}.png'))
                name = f'contact-{len(sheets) + 1:03d}.png'
                sheet.get_pixmap(alpha=False).save(output / name)
                sheets.append(name)
                generated.add(name)
        report = {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'pdf': str(pdf_path.resolve()), 'pdf_sha256': digest(pdf_path),
            'page_count': len(pdf), 'preview_pages': selected, 'dpi': dpi,
            'log': str(log_path.resolve()),
            'log_sha256': digest(log_path) if log_text is not None else None,
            'log_available': log_text is not None,
            'overfull': counts['overfull'] if log_text is not None else None,
            'underfull': counts['underfull'] if log_text is not None else None,
            'warnings': warnings, 'contact_sheets': sheets,
            'limitations': 'Warnings cover the whole log, not just selected pages. '
                'Log line numbers are not PDF page numbers. No warnings does not prove '
                'good layout: inspect every final page for density, overlap and readability.',
        }

    status = (f"Overfull: {counts['overfull']}; Underfull: {counts['underfull']}"
              if log_text is not None else 'Log unavailable: layout diagnostics unknown.')
    details = '\n'.join(f"log:{w['log_line']}  {w['message']}" for w in warnings)
    (output / 'report.txt').write_text(
        f"PDF: {pdf_path}\nGenerated: {report['generated_at']}\n"
        f"PDF SHA256: {report['pdf_sha256']}\n"
        f"Pages: {report['page_count']}; preview: {selected}; DPI: {dpi}\n"
        f"{status}\n{report['limitations']}\n\n{details}\n", encoding='utf-8')
    cards = '\n'.join(
        f'<figure><a href="page-{n:04d}.png"><img loading="lazy" '
        f'src="page-{n:04d}.png" alt="PDF page {n}"></a>'
        f'<figcaption>PDF page {n}</figcaption></figure>' for n in selected)
    (output / 'index.html').write_text(
        '<!doctype html><html lang="en"><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Slide draft</title><style>body{font:16px system-ui;margin:24px;background:#eee}'
        'main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}'
        'figure{margin:0;padding:8px;background:white}img{width:100%}'
        'pre{white-space:pre-wrap;overflow-wrap:anywhere}</style>'
        f'<h1>{escape(pdf_path.name)} — draft</h1><p>{escape(report["generated_at"])}</p>'
        f'<p>{escape(status)} · <a href="report.txt">Report</a> · '
        '<a href="report.json">JSON</a></p>'
        f'<p>{escape(report["limitations"])}</p><main>{cards}</main>'
        f'<details><summary>LaTeX box diagnostics</summary><pre>{escape(details)}</pre></details></html>',
        encoding='utf-8')
    # Remove only this tool's image filenames so page deletion/subsets cannot
    # leave obsolete previews looking current. Never remove arbitrary assets.
    for path in output.iterdir():
        if re.fullmatch(r'(page-\d{4,}|contact-\d{3,})\.png', path.name) and path.name not in generated:
            path.unlink()
    # Commit metadata last. After a failed run old reports must not be treated
    # as current; the make exit code remains the authoritative success signal.
    (output / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Draft: {output / 'index.html'}\nPreviews: {len(selected)}/{report['page_count']} pages at {dpi} DPI")
    print(f"{status}\nAgent: read {output / 'report.txt'}, inspect contact-*.png and page-*.png.")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--log', type=Path)
    parser.add_argument('--dpi', type=int, default=96)
    parser.add_argument('--pages', default='all', help='1-based PDF pages: all or 2,5-8')
    args = parser.parse_args()
    try:
        create_preview(args.pdf, args.output, args.log or args.pdf.with_suffix('.log'), args.dpi, args.pages)
    except (OSError, RuntimeError, ValueError) as exc:
        parser.exit(1, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
