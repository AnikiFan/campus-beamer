#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create a theme starter or preview any local theme with the public feature tour."""
import argparse
from pathlib import Path
import re
import shutil
import subprocess

from theme_assets import checked_path


STARTER_FILES = (
    'profile.tex', 'emblem.tex', 'wordmark.tex', 'backdrop.tex',
    'assets/emblem_on_dark.pdf', 'assets/emblem_on_light.pdf',
    'assets/wordmark_on_dark.pdf', 'assets/wordmark_on_light.pdf', 'assets/backdrop.pdf',
)


def theme_directory(root: Path, name: str) -> Path:
    """Use the same name alphabet as the TeX loader, with no path components."""
    if not re.fullmatch(r'[A-Za-z0-9][-A-Za-z0-9_]*', name):
        raise ValueError('Choose a theme name using letters, digits, hyphens or underscores; '
                         'start with a letter or digit.')
    return checked_path(root, f'theme/{name}')


def create_theme(root: Path, name: str) -> Path:
    """Copy only public starter files; never overwrite an existing theme."""
    root = root.resolve()
    destination = theme_directory(root, name)
    if destination.exists():
        raise ValueError(f'Theme already exists: {destination}; choose a new name.')
    contents = {filename: checked_path(root, f'theme/general/{filename}').read_bytes()
                for filename in STARTER_FILES}
    contents['BASE_ASSETS.md'] = checked_path(root, 'theme/general/README.md').read_bytes()
    contents['README.md'] = checked_path(root, 'tools/templates/theme-README.md').read_text(
        encoding='utf-8').replace('@THEME@', name).encode('utf-8')
    contents['demo-images.tex'] = checked_path(root, 'tools/templates/theme-demo-images.tex').read_bytes()
    # Read the entire starter before creating anything, so a missing dependency
    # cannot leave an incomplete theme directory behind.
    destination.mkdir()
    try:
        for filename, data in contents.items():
            target = destination / filename
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    except OSError:
        shutil.rmtree(destination)
        raise
    return destination


def preview_theme(root: Path, name: str, *, make: str = 'make') -> None:
    """Build both ratios without selecting or modifying a private talk."""
    root = root.resolve()
    theme_directory(root, name)
    if not checked_path(root, f'theme/{name}/profile.tex').is_file():
        raise ValueError(f'Missing theme/{name}/profile.tex; create or copy the theme first.')
    for ratio in ('169', '43'):
        entry = f'build/theme-review-{name}-{ratio}'
        source = checked_path(root, f'{entry}.tex')
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text('% Generated theme review; edit files under theme/ instead.\n'
                          rf'\providecommand{{\campusexampletheme}}{{{name}}}' + '\n'
                          rf'\providecommand{{\campusexampleaspectratio}}{{{ratio}}}' + '\n'
                          '\\input{examples/example.tex}\n', encoding='utf-8')
        subprocess.run([make, '--no-print-directory', 'draft', f'MAIN={entry}'],
                       cwd=root, check=True)
        print(f'{ratio} preview: build/draft/theme-review-{name}-{ratio}/index.html', flush=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('new', 'preview'))
    parser.add_argument('--theme', required=True)
    parser.add_argument('--make', default='make')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        if args.command == 'new':
            destination = create_theme(root, args.theme)
            print(f'Created {destination.relative_to(root)}; edit profile.tex, assets and README.md.')
            print(f'Preview both ratios: make theme-preview THEME={args.theme}')
        else:
            preview_theme(root, args.theme, make=args.make)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f'Theme contribution: {error}\n')


if __name__ == '__main__':
    main()
