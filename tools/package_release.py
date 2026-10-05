#!/usr/bin/env python3
# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Bundle the public source and demo outputs with release notes and checksums."""
import argparse
import hashlib
from pathlib import Path
import re
import zipfile


def release_notes(root: Path, version: str) -> str:
    """Require a matching changelog section before creating release artifacts."""
    changelog = (root / 'CHANGELOG.md').read_text(encoding='utf-8')
    # Release Please uses plain or linked headings; accept the manual form too.
    heading = rf'(?:\[{re.escape(version)}\](?:\([^\n]*\))?|{re.escape(version)})'
    match = re.search(rf'^## {heading}(?:[ \t][^\n]*)?\n(.*?)(?=^## |\Z)',
                      changelog, flags=re.MULTILINE | re.DOTALL)
    if match is None or not match[1].strip():
        raise ValueError(f'CHANGELOG.md needs a nonempty [{version}] section.')
    notes = f'# Campus Beamer {version}\n\n{match[1].strip()}\n'
    scope = re.search(r'^## 许可与使用范围 / License and scope\n(.*?)(?=^## |\Z)',
                      changelog, flags=re.MULTILINE | re.DOTALL)
    if scope is not None:
        notes += f'\n## 许可与使用范围 / License and scope\n\n{scope[1].strip()}\n'
    return notes


def package(root: Path, version: str) -> Path:
    """Keep older release bundles intact if inputs or changelog are missing."""
    if not re.fullmatch(r'(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)', version):
        raise ValueError('Release version must use MAJOR.MINOR.PATCH, e.g. 0.1.0.')
    files = {
        f'campus-beamer-{version}-source.zip': root / 'build/dist/campus-beamer.zip',
        f'campus-beamer-{version}-example.pdf': root / 'build/example.pdf',
        f'campus-beamer-{version}-example.pptx': root / 'build/example.pptx',
    }
    contents = {name: path.read_bytes() for name, path in files.items()}
    contents['RELEASE_NOTES.md'] = release_notes(root, version).encode('utf-8')
    contents['SHA256SUMS'] = ''.join(
        f'{hashlib.sha256(data).hexdigest()}  {name}\n'
        for name, data in sorted(contents.items())
    ).encode('utf-8')
    output = root / 'build/releases' / f'campus-beamer-v{version}-release.zip'
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
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    print(f'Release bundle: {package(Path(__file__).resolve().parents[1], args.version)}')


if __name__ == '__main__':
    main()
