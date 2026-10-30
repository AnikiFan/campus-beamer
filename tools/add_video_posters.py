#!/usr/bin/env python3
# Campus Beamer: add local-video first frames to the generated PDF.
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Add first-frame images behind local-video links in a compiled PDF.

The PDF remains a normal clickable document: the poster is a static image and
the existing ``run:`` link still opens the local video.  The operation is
idempotent; content fingerprints detect changed videos and recorded PDF streams
allow replacing posters without painting over old images. FFmpeg is required
only when a PDF contains a local video link.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys

import pymupdf

from images_to_ppt import (
    contain_bounds,
    local_video_for_link,
    video_placeholder_rect,
    video_poster,
    pdf_info_string,
)


MARKER = 'Campus Beamer video posters'
FINGERPRINT_KEY = 'CampusVideoPostersSHA256'
STREAMS_KEY = 'CampusVideoPosterContents'


def video_digest(path: Path) -> str:
    """Fingerprint the video bytes, including same-size/same-timestamp edits."""
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def add_video_posters(pdf_path: Path) -> int:
    """Overlay posters on *pdf_path* and return the number of video links."""
    with pymupdf.open(pdf_path) as source:
        keywords = source.metadata.get('keywords', '') or ''
        previous = pdf_info_string(source, FINGERPRINT_KEY)
        if MARKER in keywords and not previous:
            raise ValueError('This PDF has legacy video posters. Recompile the TeX source '
                             'before updating its video previews.')
        hashes = {}
        videos = []
        for page_index, page in enumerate(source):
            for link in page.get_links():
                video = local_video_for_link(link, pdf_path)
                if video is None:
                    continue
                video_path, _ = video
                if video_path not in hashes:
                    hashes[video_path] = video_digest(video_path)
                frame = video_placeholder_rect(page, link['from']) & page.rect
                if not frame.is_empty:
                    videos.append((page_index, frame, video_path))
        signature = [(index, list(rect), str(path), hashes[path]) for index, rect, path in videos]
        fingerprint = hashlib.sha256(json.dumps(signature).encode('utf-8')).hexdigest()
        if fingerprint == previous or (not videos and not previous):
            return 0
        posters: dict[Path, bytes] = {}
        placements: list[tuple[int, pymupdf.Rect, bytes]] = []
        for page_index, frame, video_path in videos:
            if video_path not in posters:
                posters[video_path] = video_poster(video_path)
            # Drawing coordinates are unrotated; PDF links are displayed coordinates.
            frame = frame * source[page_index].derotation_matrix
            image = pymupdf.Pixmap(posters[video_path])
            left, top, width, height = contain_bounds(
                (frame.x0, frame.y0, frame.width, frame.height), image.width, image.height)
            placements.append((page_index, pymupdf.Rect(left, top, left + width, top + height),
                               posters[video_path]))
        # Remove only streams inserted by this tool, retaining the original
        # page artwork even if a replacement has a different aspect ratio.
        originals = {}
        for page in source:
            _, value = source.xref_get_key(page.xref, STREAMS_KEY)
            old_streams = {int(x) for x in re.findall(r'(\d+) 0 R', value)}
            originals[page.number] = [x for x in page.get_contents() if x not in old_streams]
            source.xref_set_key(page.xref, 'Contents',
                                '[' + ' '.join(f'{x} 0 R' for x in originals[page.number]) + ']')
            source.xref_set_key(page.xref, STREAMS_KEY, 'null')
        for page_index, rect, poster in placements:
            source[page_index].insert_image(rect, stream=poster, keep_proportion=False)
        for page in source:
            added = set(page.get_contents()) - set(originals[page.number])
            if added:
                source.xref_set_key(page.xref, STREAMS_KEY,
                                    '[' + ' '.join(f'{x} 0 R' for x in sorted(added)) + ']')
        metadata = dict(source.metadata)
        if MARKER not in keywords:
            metadata['keywords'] = f"{keywords}; {MARKER}" if keywords else MARKER
        source.set_metadata(metadata)
        _, reference = source.xref_get_key(-1, 'Info')
        source.xref_set_key(int(reference.split()[0]), FINGERPRINT_KEY,
                            pymupdf.get_pdf_str(fingerprint))
        temporary = pdf_path.with_name(f'.{pdf_path.name}.posters.tmp')
        try:
            source.save(temporary, garbage=4, deflate=True)
            os.replace(temporary, pdf_path)
        finally:
            temporary.unlink(missing_ok=True)
        return len(placements)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pdf', type=Path, help='compiled PDF to update in place')
    args = parser.parse_args(argv)
    try:
        count = add_video_posters(args.pdf)
    except (OSError, RuntimeError, ValueError, pymupdf.FileDataError) as exc:
        print(f'Video poster generation failed: {exc}', file=sys.stderr)
        return 1
    if count:
        print(f'PDF video posters: {count} link(s) updated')
    else:
        print('PDF video posters: none needed')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
