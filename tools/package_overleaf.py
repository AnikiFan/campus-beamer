#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Create a self-contained Overleaf demo ZIP using only Python's standard library."""
import argparse
from pathlib import Path
import tempfile
import zipfile

from package_source import FILES
from theme_assets import THEMES, asset_files, checked_path, download

LANGUAGES = ('chinese', 'english')
ASPECT_RATIOS = ('169', '43')


def public_files(theme: str, language: str) -> list[str]:
    """Select only reviewed demo dependencies, never a user's local talk."""
    directories = ['assets/', 'examples/sections/code/']
    if language == 'chinese':
        directories += ['examples/sections/', 'examples/bibliography/']
    else:
        directories += ['examples/english/']
    selected = {'LICENSE', 'examples/theme-images.tex'}
    for name in FILES:
        path = Path(name)
        if any(name.startswith(prefix) for prefix in directories) and name != 'assets/campus-beamer-logo.tex':
            selected.add(name)
        if path.parent.as_posix() == 'theme' and path.suffix in ('.cls', '.sty'):
            selected.add(name)
        for profile in {'general', theme}:
            if name.startswith(f'theme/{profile}/') and (
                path.name in ('profile.tex', 'section-art.tex') or path.suffix in ('.md', '.txt')
                or '/assets/' in name
            ):
                selected.add(name)
    return sorted(selected)


def main_document(root: Path, theme: str, language: str, aspectratio: str) -> str:
    entry = 'examples/example-en.tex' if language == 'english' else 'examples/example.tex'
    source = checked_path(root, entry).read_text(encoding='utf-8')
    # Keep the actual documentclass in the root entry for Overleaf's main-file detection.
    aspect = r'\providecommand{\campusexampleaspectratio}{169}'
    theme_declaration = (r'\newcommand{\campusexampletheme}{general}' if language == 'english'
                         else r'\providecommand{\campusexampletheme}{general}')
    replacements = {
        aspect: rf'\providecommand{{\campusexampleaspectratio}}{{{aspectratio}}}',
        theme_declaration: theme_declaration.replace('{general}', '{' + theme + '}'),
    }
    if language == 'english':
        replacements['  theme=general,'] = f'  theme={theme},'
    for old, new in replacements.items():
        if source.count(old) != 1:
            raise ValueError(f'Demo entry changed; cannot configure {entry}: {old}')
        source = source.replace(old, new)
    # Repository-only build comments do not apply to this standalone project.
    source = source[source.index(r'\providecommand'):]
    return '% !TeX program = xelatex\n% Overleaf main document\n' + source


def package(root: Path, output: Path, theme: str = 'general', language: str = 'chinese',
            aspectratio: str = '169') -> int:
    if theme not in ('general', *THEMES) or language not in LANGUAGES or aspectratio not in ASPECT_RATIOS:
        raise ValueError('Unknown theme, language or aspect ratio.')
    root = root.resolve()
    contents = {name: checked_path(root, name).read_bytes() for name in public_files(theme, language)}
    contents['main.tex'] = main_document(root, theme, language, aspectratio).encode('utf-8')
    for source, destination in (('overleaf-latexmkrc', 'latexmkrc'), ('overleaf-README.md', 'README.md')):
        contents[destination] = checked_path(root, f'tools/templates/{source}').read_bytes()
    if theme != 'general':
        names = asset_files(theme)
        # Download into staging when incomplete; never overwrite or mix partial local edits.
        if all(checked_path(root, name).is_file() for name in names):
            contents.update({name: checked_path(root, name).read_bytes() for name in names})
        else:
            with tempfile.TemporaryDirectory(prefix='campus-overleaf-assets-') as temporary:
                staging = Path(temporary)
                download(staging, theme)
                contents.update({name: checked_path(staging, name).read_bytes() for name in names})
    for name, data in contents.items():
        if name.startswith('examples/') and name.endswith('.tex'):
            # Overleaf emits its PDF at the project root, unlike the local build/ workflow.
            contents[name] = data.replace(b'run:../assets/', b'run:assets/')
    output.parent.mkdir(parents=True, exist_ok=True)
    # Atomic replacement also preserves a previous good archive on download/read failure.
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as stream:
        temporary_zip = Path(stream.name)
    try:
        with zipfile.ZipFile(temporary_zip, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(contents.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        temporary_zip.replace(output)
    finally:
        temporary_zip.unlink(missing_ok=True)
    return len(contents)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--theme', choices=('general', *THEMES), default='general')
    parser.add_argument('--language', choices=LANGUAGES, default='chinese')
    parser.add_argument('--aspectratio', choices=ASPECT_RATIOS, default='169')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    code = 'en' if args.language == 'english' else 'zh'
    output = args.output or Path('build/overleaf') / f'campus-beamer-{args.theme}-{code}-{args.aspectratio}.zip'
    try:
        count = package(Path(__file__).resolve().parents[1], output,
                        args.theme, args.language, args.aspectratio)
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Overleaf package: {error}\n')
    print(f'Overleaf ZIP: {output} ({count} files)')
    print('Upload as a new Overleaf project; select main.tex and XeLaTeX.')


if __name__ == '__main__':
    main()
