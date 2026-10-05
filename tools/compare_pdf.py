#!/usr/bin/env python3
# Campus Beamer: compare PDF page pixels, text and links.
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
"""Compare every PDF page's pixels, text, geometry and link actions.

PDF timestamps, trailer IDs and object numbering are intentionally excluded.
Uses the same locked PyMuPDF dependency as the converter. A byte comparison is
also reported so visual equivalence is never confused with file identity.
"""
import argparse
import hashlib
import json
from pathlib import Path

import pymupdf


def links_for(page):
    return [{key: value for key, value in link.items() if key not in {'xref', 'id'}}
            for link in page.get_links()]


def outline_for(document):
    return [[*entry[:3], {key: value for key, value in entry[3].items()
                         if key not in {'xref', 'id'}}]
            for entry in document.get_toc(simple=False)]


def compare(before, after, dpi=600, strict_bytes=False):
    failures = []
    with pymupdf.open(before) as old, pymupdf.open(after) as new:
        if len(old) != len(new):
            failures.append(f'page count: {len(old)} != {len(new)}')
        for number, (left, right) in enumerate(zip(old, new), 1):
            if left.rect != right.rect or left.rotation != right.rotation:
                failures.append(f'page {number}: geometry changed')
            if left.get_text('rawdict') != right.get_text('rawdict'):
                failures.append(f'page {number}: text or text placement changed')
            if links_for(left) != links_for(right):
                failures.append(f'page {number}: links changed')
            a = left.get_pixmap(dpi=dpi, alpha=False)
            b = right.get_pixmap(dpi=dpi, alpha=False)
            if (a.width, a.height, a.samples) != (b.width, b.height, b.samples):
                failures.append(f'page {number}: pixels changed at {dpi} DPI')
        if outline_for(old) != outline_for(new):
            failures.append('PDF outline changed')
        metadata_keys = set(old.metadata) | set(new.metadata)
        changed_metadata = sorted(key for key in metadata_keys
                                  if old.metadata.get(key) != new.metadata.get(key))
        # Title, author, producer and other document metadata must also survive.
        meaningful = set(changed_metadata) - {'creationDate', 'modDate'}
        if meaningful:
            failures.append(f'metadata changed: {sorted(meaningful)}')
        byte_identical = Path(before).read_bytes() == Path(after).read_bytes()
        if strict_bytes and not byte_identical:
            failures.append('PDF files differ byte for byte')
        return {'pages_before': len(old), 'pages_after': len(new), 'dpi': dpi,
                'byte_identical': byte_identical,
                'sha256_before': hashlib.sha256(Path(before).read_bytes()).hexdigest(),
                'sha256_after': hashlib.sha256(Path(after).read_bytes()).hexdigest(),
                'changed_metadata': changed_metadata, 'failures': failures}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('before', type=Path)
    parser.add_argument('after', type=Path)
    parser.add_argument('--dpi', type=int, default=600)
    parser.add_argument('--strict-bytes', action='store_true',
                        help='also fail on any byte difference, including timestamps')
    args = parser.parse_args()
    if args.dpi <= 0:
        parser.error('--dpi must be positive')
    result = compare(args.before, args.after, args.dpi, args.strict_bytes)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return bool(result['failures'])


if __name__ == '__main__':
    raise SystemExit(main())
