#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Make the PCL lettering white and trim transparent side margins."""
from pathlib import Path

from PIL import Image


def _trim_horizontal(artwork: Image.Image) -> Image.Image:
    """Remove only transparent left/right margins from the derived PNG."""
    if artwork.size == (1108, 224):
        # The downloaded WebP has a 94 px margin on the left and 128 px on the
        # right. Retain the original vertical padding and crop without resampling.
        if artwork.getchannel('A').getbbox() != (94, 0, 980, 223):
            raise ValueError('Recheck the transparent margins for the new source.')
        artwork = artwork.crop((94, 0, 980, 224))
    elif artwork.size != (886, 224):
        raise ValueError('Recheck the PCL wordmark source dimensions before trimming.')
    if artwork.getchannel('A').getbbox() != (0, 0, 886, 223):
        raise ValueError('The trimmed PCL wordmark does not fill the expected bounds.')
    return artwork


def recolor(source: Path, output: Path) -> None:
    """Split at the transparent gutter after trimming the reviewed source."""
    with Image.open(source) as image:
        artwork = _trim_horizontal(image.convert('RGBA'))
    # After trimming, the original x=316..352 gutter becomes x=222..258;
    # the recoloring boundary lies inside it at x=242 (originally x=336).
    if artwork.getchannel('A').crop((222, 0, 258, 224)).getbbox():
        raise ValueError('The expected transparent emblem/text gutter is occupied.')
    letters = artwork.crop((242, 0, artwork.width, artwork.height))
    white = Image.new('RGBA', letters.size, (255, 255, 255, 0))
    white.putalpha(letters.getchannel('A'))
    artwork.paste(white, (242, 0))
    artwork.save(output)


if __name__ == '__main__':
    assets = Path(__file__).resolve().parents[1] / 'theme/pcl/assets'
    with Image.open(assets / 'wordmark.png') as image:
        _trim_horizontal(image.convert('RGBA')).save(assets / 'wordmark.png')
    recolor(assets / 'wordmark.png', assets / 'wordmark_on_dark.png')
