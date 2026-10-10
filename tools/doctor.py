#!/usr/bin/env python3
# Campus Beamer: check local build prerequisites.
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
"""Check local build prerequisites without installing anything or compiling TeX."""
import shutil
import subprocess
import sys


COMMANDS = (
    ('make', '--version'), ('uv', '--version'), ('xelatex', '--version'),
    ('latexmk', '-v'), ('biber', '--version'), ('kpsewhich', '--version'),
)
TEX_FILES = (
    'beamer.cls', 'pgfpages.sty', 'kvoptions.sty', 'xeCJK.sty', 'biblatex.sty', 'ieee.bbx', 'ieee.cbx',
    'tikz.sty', 'tcolorbox.sty', 'environ.sty', 'caladea.sty', 'carlito.sty',
    'listings.sty', 'fontawesome5.sty', 'xeCJK-listings.sty',
    'pzdr.tfm',
    'FandolSong-Regular.otf', 'FandolHei-Regular.otf',
    'FandolKai-Regular.otf', 'FandolFang-Regular.otf',
)


def probe(args):
    try:
        result = subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    output = result.stdout.strip()
    return result.returncode == 0 and bool(output), output or 'no output'


def check():
    failures = 0

    def report(ok, name, detail):
        nonlocal failures
        failures += int(not ok)
        first_line = detail.splitlines()[0] if detail else 'no output'
        print(f'[{"OK" if ok else "MISSING/ERROR"}] {name}: {first_line}')

    report(sys.version_info >= (3, 10), 'Python >= 3.10', sys.version.splitlines()[0])
    found = {}
    for name, flag in COMMANDS:
        executable = shutil.which(name)
        found[name] = executable
        ok, detail = probe([executable, flag]) if executable else (False, 'not found in PATH')
        report(ok, name, detail)

    if found['kpsewhich']:
        for filename in TEX_FILES:
            ok, detail = probe([found['kpsewhich'], filename])
            report(ok, filename, detail)
    else:
        print('[SKIPPED] TeX package/font lookup: kpsewhich is unavailable')

    if failures:
        print(f'\n{failures} prerequisite check(s) failed. See docs/installation.md.')
    else:
        print('\nPrerequisite checks passed. Give your brief and local materials to the agent; '
              'preview the reference demo with make draft MAIN=example.')
    print('This checks default tools and TeX files in PATH, not version compatibility, '
          'Python dependencies or slide layout. It creates no build files.')
    ffmpeg = shutil.which('ffmpeg')
    ok, detail = probe([ffmpeg, '-version']) if ffmpeg else (False, 'not found in PATH')
    print(f'[{"OK" if ok else "OPTIONAL MISSING"}] ffmpeg (local video export): '
          f'{detail.splitlines()[0]}')
    if not ok:
        print('Install FFmpeg to generate local-video previews in PDF/PPTX. Non-video exports do not need it.')
    return int(bool(failures))


if __name__ == '__main__':
    sys.exit(check())
