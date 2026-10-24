#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Package or install the latest per-theme assets (stdlib only)."""
import argparse
import hashlib
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import tempfile
from urllib.request import urlopen
import zipfile

THEMES = ('tokyo-night', 'undefined', 'tsinghua', 'pcl')
BASE_URL = 'https://github.com/AnikiFan/campus-beamer/releases/download'
NOTICE_NAME = 'THEME_ASSETS_NOTICES.md'
ASSET_FILES = (
    'theme/undefined/assets/emblem_on_dark.pdf',
    'theme/undefined/assets/emblem_on_light.pdf',
    'theme/undefined/assets/wordmark_on_dark.pdf',
    'theme/undefined/assets/wordmark_on_light.pdf',
    'theme/undefined/assets/pearl-earring.png',
    'theme/undefined/assets/mona-lisa.png',
    'theme/undefined/assets/scream.png',
    'theme/undefined/assets/napoleon.png',
    'theme/undefined/assets/starry-night.png',
    'theme/tokyo-night/assets/emblem_on_dark.pdf',
    'theme/tokyo-night/assets/emblem_on_light.pdf',
    'theme/tokyo-night/assets/wordmark_on_dark.pdf',
    'theme/tokyo-night/assets/wordmark_on_light.pdf',
    'theme/tokyo-night/assets/backdrop.pdf',
    'theme/pcl/assets/campus-aerial.jpg',
    'theme/pcl/assets/lakeside-aerial.jpg',
    'theme/pcl/assets/lakeside-building.jpg',
    'theme/pcl/assets/campus-courtyard-source.webp',
    'theme/pcl/assets/campus-buildings-aerial.jpg',
    'theme/pcl/assets/wordmark-source.webp',
    'theme/pcl/assets/campus-courtyard.png',
    'theme/pcl/assets/emblem-source.png',
    'theme/pcl/assets/emblem.pdf',
    'theme/pcl/assets/wordmark.png',
    'theme/pcl/assets/wordmark_on_dark.png',
    'theme/pcl/assets/wordmark_on_dark.pdf',
    'theme/tsinghua/assets/emblem_on_dark.png',
    'theme/tsinghua/assets/emblem_on_light.png',
    'theme/tsinghua/assets/sigs_building.jpg',
    'theme/tsinghua/assets/sigs_dom.jpg',
    'theme/tsinghua/assets/sigs_night.jpg',
    'theme/tsinghua/assets/sigs_wordmark.png',
    'theme/tsinghua/assets/tsinghua_door.png',
    'theme/tsinghua/assets/tsinghua_door1.png',
    'theme/tsinghua/assets/tsinghua_temple.png',
    'theme/tsinghua/assets/wordmark_on_dark.png',
    'theme/tsinghua/assets/wordmark_on_light.png',
    'theme/tsinghua/assets/wordmark.svg',
)


def asset_files(theme: str) -> tuple[str, ...]:
    """Return the reviewed manifest for exactly one theme."""
    if theme not in THEMES:
        raise ValueError(f'Unknown theme: {theme}')
    return tuple(name for name in ASSET_FILES if name.startswith(f'theme/{theme}/assets/'))


def archive_name(theme: str) -> str:
    asset_files(theme)
    return f'campus-beamer-{theme}-assets.zip'


def checked_path(root: Path, name: str) -> Path:
    """Reject symlinked destinations and parents before reading or writing."""
    path = root / name
    for part in (path, *path.parents):
        if part == root:
            break
        if part.is_symlink():
            raise ValueError(f'Theme assets must not use symlinks: {part}')
    return path


def package(root: Path, output: Path, theme: str) -> Path:
    """Build a deterministic, explicitly allowlisted bundle with provenance."""
    root = root.resolve()
    contents = {name: checked_path(root, name).read_bytes() for name in asset_files(theme)}
    notices = ['# Theme asset sources and usage rights\n\n'
               'Asset licenses vary by theme and file; see the source and usage notices below.\n']
    for name in (f'theme/{theme}/README.md',):
        notices.append(f'\n---\n\nSource: `{name}`\n\n' + checked_path(root, name).read_text())
    contents[NOTICE_NAME] = '\n'.join(notices).encode('utf-8')
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.zip.tmp')
    try:
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
            for name, data in sorted(contents.items()):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_name('SHA256SUMS').write_text(f'{digest}  {output.name}\n', encoding='utf-8')
    return output


def install(root: Path, archive_path: Path, checksum: str, theme: str, *, update: bool = False) -> int:
    """Validate the whole download before installing; preserve local edits by default."""
    root = root.resolve()
    if not re.fullmatch(r'[0-9a-fA-F]{64}', checksum):
        raise ValueError('Expected a SHA-256 digest.')
    if hashlib.sha256(archive_path.read_bytes()).hexdigest() != checksum.lower():
        raise ValueError('Theme asset checksum mismatch; retry the download.')
    with zipfile.ZipFile(archive_path) as archive, tempfile.TemporaryDirectory() as temporary:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate theme asset paths.')
        if not set(asset_files(theme)).issubset(names) or NOTICE_NAME not in names:
            raise ValueError('Incomplete theme asset archive.')
        pending = []
        for info in archive.infolist():
            name = info.filename
            path = PurePosixPath(name)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError(f'Symlink in theme asset archive: {name}')
            if name != NOTICE_NAME:
                if (path.as_posix() != name or len(path.parts) != 4
                        or path.parts[0] != 'theme' or path.parts[1] != theme
                        or path.parts[2] != 'assets' or '..' in path.parts or '\\' in name
                        or path.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp', '.svg', '.pdf')):
                    raise ValueError(f'Unexpected theme asset path: {name}')
            # Read all members now so CRC failures cannot cause a partial installation.
            data = archive.read(info)
            if name == NOTICE_NAME:
                continue  # Provenance also lives in each theme's README in the source ZIP.
            destination = checked_path(root, name)
            if destination.exists():
                if destination.read_bytes() == data:
                    continue
                if not update:
                    raise ValueError(f'Existing asset differs: {name}; use --update to replace it.')
            staged = Path(temporary) / name
            staged.parent.mkdir(parents=True, exist_ok=True)
            staged.write_bytes(data)
            pending.append((staged, destination))
        for staged, destination in pending:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as stream:
                replacement = Path(stream.name)
                try:
                    with staged.open('rb') as source:
                        shutil.copyfileobj(source, stream)
                except BaseException:
                    replacement.unlink(missing_ok=True)
                    raise
            try:
                replacement.chmod(0o644)
                replacement.replace(destination)
            finally:
                replacement.unlink(missing_ok=True)
    return len(pending)


def download(root: Path, theme: str, *, update: bool = False) -> int:
    """Fetch the rolling bundle only when missing, or on an explicit update."""
    root = root.resolve()
    if not update and all(checked_path(root, name).is_file() for name in asset_files(theme)):
        print('Theme assets are already present; no download needed. Use --update to refresh.')
        return 0
    name = archive_name(theme)
    url = f'{BASE_URL}/theme-assets-{theme}'
    with tempfile.TemporaryDirectory(prefix='campus-theme-assets-') as temporary:
        with urlopen(f'{url}/SHA256SUMS', timeout=60) as response:
            checksums = response.read().decode('utf-8')
        matches = [line.split()[0] for line in checksums.splitlines()
                   if len(line.split()) == 2 and line.split()[1] == name]
        if len(matches) != 1:
            raise ValueError('Missing or ambiguous theme asset checksum.')
        archive = Path(temporary) / name
        with urlopen(f'{url}/{name}', timeout=60) as response, archive.open('wb') as stream:
            shutil.copyfileobj(response, stream)
        return install(root, archive, matches[0], theme, update=update)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('download', 'package'))
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--theme', required=True, choices=THEMES)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--update', action='store_true', help='Explicitly replace existing theme assets')
    args = parser.parse_args()
    try:
        if args.command == 'package':
            output = args.output or Path('build/theme-assets') / args.theme / archive_name(args.theme)
            print(f'Theme asset bundle: {package(args.root, output, args.theme)}')
        else:
            print(f'Installed {download(args.root, args.theme, update=args.update)} theme assets.')
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        parser.exit(1, f'Theme assets: {error}\n')


if __name__ == '__main__':
    main()
