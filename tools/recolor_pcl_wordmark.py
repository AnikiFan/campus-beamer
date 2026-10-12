#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Make the PCL lettering white, preserving the original emblem and alpha."""
from pathlib import Path

from PIL import Image


def recolor(source: Path, output: Path) -> None:
    """Split at the transparent gutter in the reviewed 1108 x 224 source."""
    with Image.open(source) as image:
        artwork = image.convert('RGBA')
    if artwork.size != (1108, 224):
        raise ValueError('Recheck the emblem/text boundary for the new source dimensions.')
    # The emblem ends at x=315; the lettering starts at x=352.
    # Check the gutter before applying the fixed boundary to a replacement asset.
    if artwork.getchannel('A').crop((316, 0, 352, 224)).getbbox():
        raise ValueError('The expected transparent emblem/text gutter is occupied.')
    letters = artwork.crop((336, 0, artwork.width, artwork.height))
    white = Image.new('RGBA', letters.size, (255, 255, 255, 0))
    white.putalpha(letters.getchannel('A'))
    artwork.paste(white, (336, 0))
    artwork.save(output)


if __name__ == '__main__':
    assets = Path(__file__).resolve().parents[1] / 'theme/pcl/assets'
    recolor(assets / 'wordmark.png', assets / 'wordmark_on_dark.png')
