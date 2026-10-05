#!/usr/bin/env python3
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
# SPDX-License-Identifier: GPL-3.0-or-later
"""Generate the original CC0 demo animation using only geometric primitives.

Run: uv run --frozen python tools/generate_demo_video.py
Requires the project's existing PyMuPDF dependency and system FFmpeg.
No external footage, images, audio, fonts, or network access are used.
The video illustrates outline -> slides -> speaker notes, not research results.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path
import shutil
import subprocess
import tempfile

import pymupdf


WIDTH, HEIGHT, FPS, SECONDS = 640, 360, 24, 6
PURPLE, PALE, INK, MUTED = '#552174', '#EDE4F3', '#302738', '#B2A5BA'
# Hand-defined geometric lettering, drawn as rectangles rather than a font.
LETTERS = {
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'I': ['11111', '00100', '00100', '00100', '00100', '00100', '11111'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'N': ['10001', '11001', '11001', '10101', '10011', '10011', '10001'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'S': ['01111', '10000', '10000', '01110', '00001', '00001', '11110'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
}


def frame_svg(time: float) -> bytes:
    shapes = []

    def rect(x, y, width, height, color, radius=0, stroke=None):
        border = f' stroke="{stroke}" stroke-width="1.5"' if stroke else ''
        shapes.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
                      f'rx="{radius}" fill="{color}"{border}/>')

    def circle(x, y, radius, color):
        shapes.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>')

    def lettering(text, x, y, pixel=2, color=PURPLE):
        for index, letter in enumerate(text):
            if letter == ' ':
                continue
            for row, values in enumerate(LETTERS[letter]):
                for column, bit in enumerate(values):
                    if bit == '1':
                        rect(x + (index * 6 + column) * pixel,
                             y + row * pixel, pixel, pixel, color)

    # All panels are visible in the first frame, yielding a useful PPT poster.
    rect(0, 0, WIDTH, HEIGHT, '#FAF8FC')
    lettering('OUTLINE TO SLIDES', 40, 28, pixel=3)
    rect(40, 60, 42, 3, PURPLE, 1)
    for x, width, heading in ((40, 154, 'OUTLINE'), (244, 164, 'SLIDES'), (458, 142, 'NOTES')):
        rect(x, 88, width, 199, '#FFFFFF', 12, '#DED3E5')
        lettering(heading, x + 16, 105, pixel=2)

    # Three matching pages/notes, with a smoothly circulating emphasis.
    for row in range(3):
        y = 142 + row * 44
        emphasis = (1 + math.cos(2 * math.pi * (time / SECONDS - row / 3))) / 2
        active = emphasis > .72
        circle(61, y + 9, 4, PURPLE if active else MUTED)
        rect(75, y + 5, 93 - row * 9, 6, PURPLE if active else '#CEC1D6', 3)
        rect(75, y + 17, 68 - row * 7, 4, PALE, 2)

        rect(260, y - 9, 132, 36, PALE if active else '#F8F5FA', 4, '#DED3E5')
        rect(268, y - 3, 42, 4, PURPLE, 2)
        rect(268, y + 7, 55, 3, MUTED, 1)
        rect(268, y + 14, 43, 3, MUTED, 1)
        # A generic image placeholder on each slide, with no logos or data.
        rect(342, y - 2, 41, 21, '#FFFFFF', 2)
        circle(352, y + 4, 3, PURPLE)
        shapes.append(f'<path d="M345 {y+16} L356 {y+7} L363 {y+12} '
                      f'L373 {y+4} L380 {y+16} Z" fill="{PURPLE}"/>')

        rect(474, y - 9, 110, 36, PALE if active else '#F8F5FA', 4)
        for line in range(3):
            rect(484, y - 1 + line * 8, (83, 69, 77)[line], 3,
                 PURPLE if active and line == 0 else MUTED, 1)

    for start in (204, 418):
        end = start + 28
        shapes.append(f'<path d="M{start} 188 H{end} M{end-6} 182 L{end} 188 '
                      f'L{end-6} 194" fill="none" stroke="{PURPLE}" '
                      'stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>')
        # A travelling dot, fading near each arrow's ends for a smooth loop.
        phase = (time / 2 + (start - 204) / 428) % 1
        opacity = math.sin(math.pi * phase) ** 2
        shapes.append(f'<circle cx="{start + 28 * phase:.3f}" cy="188" '
                      f'r="4" fill="{PURPLE}" opacity="{opacity:.3f}"/>')
    rect(40, 319, 560, 3, '#DED3E5', 1)
    for row, x in enumerate((117, 326, 529)):
        radius = 4 + 2 * (1 + math.cos(2 * math.pi * (time / SECONDS - row / 3))) / 2
        circle(x, 320.5, radius, PURPLE)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}">' + ''.join(shapes) + '</svg>').encode()


def generate(output: Path) -> None:
    ffmpeg = shutil.which('ffmpeg')
    if not ffmpeg:
        raise RuntimeError('FFmpeg is required to generate the demo video.')
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='campus-video-') as directory:
        temporary = Path(directory) / 'demo.mp4'
        # Browser/PowerPoint-friendly H.264, square pixels, no audio track.
        args = [ffmpeg, '-v', 'error', '-nostdin', '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                '-s', f'{WIDTH}x{HEIGHT}', '-r', str(FPS), '-i', 'pipe:0', '-an',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '30', '-pix_fmt', 'yuv420p',
                '-movflags', '+faststart', '-threads', '1',
                '-metadata', 'title=Original outline-to-slides demo',
                '-metadata', 'comment=CC0-1.0; generated by tools/generate_demo_video.py',
                '-y', str(temporary)]
        with tempfile.TemporaryFile() as errors:
            process = subprocess.Popen(args, stdin=subprocess.PIPE, stderr=errors)
            try:
                for number in range(FPS * SECONDS):
                    with pymupdf.open(stream=frame_svg(number / FPS), filetype='svg') as frame:
                        page = frame[0]
                        pixmap = page.get_pixmap(
                            matrix=pymupdf.Matrix(WIDTH / page.rect.width, HEIGHT / page.rect.height),
                            colorspace=pymupdf.csRGB, alpha=False,
                        )
                        if (pixmap.width, pixmap.height) != (WIDTH, HEIGHT):
                            raise RuntimeError('Unexpected frame dimensions; output was not replaced.')
                        process.stdin.write(pixmap.samples)
                process.stdin.close()
                code = process.wait(timeout=30)
                if code:
                    raise RuntimeError('FFmpeg failed to encode the demo video.')
            except BaseException:
                if process.poll() is None:
                    process.kill()
                process.wait()
                errors.seek(0)
                detail = errors.read().decode(errors='replace').strip()
                if detail:
                    print(detail)
                raise
        shutil.copyfile(temporary, output)
    print(f'Generated {output}: {WIDTH}x{HEIGHT}, {FPS} fps, {SECONDS}s, '
          f'{output.stat().st_size:,} bytes, no audio, CC0-1.0.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('assets/presentation_demo.mp4'))
    try:
        generate(parser.parse_args().output)
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        parser.exit(1, f'Error: {exc}\n')
