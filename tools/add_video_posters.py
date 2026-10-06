#!/usr/bin/env python3
# Campus Beamer: add local-video first frames to the generated PDF.
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Add first-frame images behind local-video links in a compiled PDF.

The PDF remains a normal clickable document: the poster is a static image and
the existing ``run:`` link still opens the local video.  The operation is
idempotent; a metadata marker prevents repeated ``make`` calls from stacking
the same image over itself.  FFmpeg is required only when a PDF contains a
local video link.
"""

from __future__ import annotations

import argparse
from io import BytesIO
import os
from pathlib import Path
import sys

import pymupdf

from images_to_ppt import (
    contain_bounds,
    local_video_for_link,
    video_placeholder_rect,
    video_poster,
)


MARKER = 'Campus Beamer video posters'


def add_video_posters(pdf_path: Path) -> int:
    """Overlay posters on *pdf_path* and return the number of video links."""
    with pymupdf.open(pdf_path) as source:
        keywords = source.metadata.get('keywords', '') or ''
        if MARKER in keywords:
            return 0

        posters: dict[Path, bytes] = {}
        placements: list[tuple[int, pymupdf.Rect, bytes]] = []
        for page_index, page in enumerate(source):
            for link in page.get_links():
                video = local_video_for_link(link, pdf_path)
                if video is None:
                    continue
                video_path, _ = video
                if video_path not in posters:
                    posters[video_path] = video_poster(video_path)
                frame = video_placeholder_rect(page, link['from']) & page.rect
                if frame.is_empty:
                    continue
                # Link rectangles are in the displayed page orientation;
                # drawing APIs place images in unrotated page coordinates.
                frame *= page.derotation_matrix
                # Fill the complete link area; the poster itself is the PDF
                # preview, so no placeholder frame needs to remain visible.
                image = pymupdf.Pixmap(posters[video_path])
                left, top, width, height = contain_bounds(
                    (frame.x0, frame.y0, frame.width, frame.height),
                    image.width, image.height)
                placements.append((page_index,
                                   pymupdf.Rect(left, top, left + width, top + height),
                                   posters[video_path]))

        if not placements:
            return 0

        for page_index, rect, poster in placements:
            source[page_index].insert_image(rect, stream=poster, keep_proportion=False)
        metadata = dict(source.metadata)
        metadata['keywords'] = f"{keywords}; {MARKER}" if keywords else MARKER
        source.set_metadata(metadata)
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
