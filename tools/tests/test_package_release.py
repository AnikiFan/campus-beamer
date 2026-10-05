# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Release archives contain only public artifacts with verifiable checksums."""
import hashlib
from pathlib import Path
import sys
import tempfile
import unittest
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_release import package


class ReleasePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ('build/dist/campus-beamer.zip', 'build/example.pdf', 'build/example.pptx'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'Public fixture: ' + name.encode())
        (self.root / 'CHANGELOG.md').write_text(
            '# Changes\n\n## [Unreleased]\n\nLater.\n\n## [0.1.0] - Pending\n\n'
            '- Public demo.\n\n## [0.0.1]\n\nOlder.\n', encoding='utf-8')

    def test_public_artifacts_and_checksums(self):
        (self.root / 'build/main.pdf').write_bytes(b'Private user presentation')
        output = package(self.root, '0.1.0')
        with ZipFile(output) as archive:
            self.assertEqual(set(archive.namelist()), {
                'campus-beamer-0.1.0-source.zip', 'campus-beamer-0.1.0-example.pdf',
                'campus-beamer-0.1.0-example.pptx', 'RELEASE_NOTES.md', 'SHA256SUMS'})
            for line in archive.read('SHA256SUMS').decode().splitlines():
                expected, name = line.split('  ', 1)
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), expected)
            notes = archive.read('RELEASE_NOTES.md').decode()
            self.assertIn('Public demo.', notes)
            self.assertNotIn('Later.', notes)
            self.assertNotIn('Older.', notes)

    def test_missing_artifact_preserves_existing_bundle(self):
        output = package(self.root, '0.1.0')
        before = output.read_bytes()
        (self.root / 'build/example.pptx').unlink()
        with self.assertRaises(FileNotFoundError):
            package(self.root, '0.1.0')
        self.assertEqual(output.read_bytes(), before)

    def test_release_please_headings_and_shared_license_scope(self):
        for heading in ('## 0.2.0 (2026-10-06)',
                        '## [0.2.0](https://example.com/compare/v0.1.0...v0.2.0) (2026-10-06)'):
            with self.subTest(heading=heading):
                (self.root / 'CHANGELOG.md').write_text(
                    f'# Changes\n\n{heading}\n\n### Features\n\n- New feature.\n\n'
                    '## [0.1.0] - Pending\n\n- Older baseline.\n\n'
                    '## 许可与使用范围 / License and scope\n\nSeparate asset rights.\n',
                    encoding='utf-8')
                with ZipFile(package(self.root, '0.2.0')) as archive:
                    notes = archive.read('RELEASE_NOTES.md').decode()
                self.assertIn('New feature.', notes)
                self.assertIn('Separate asset rights.', notes)
                self.assertNotIn('Older baseline.', notes)

    def test_heading_must_match_the_exact_version(self):
        (self.root / 'CHANGELOG.md').write_text('# Changes\n## 0.1.00\nWrong version.\n')
        with self.assertRaisesRegex(ValueError, 'CHANGELOG'):
            package(self.root, '0.1.0')

    def test_missing_changelog_section_preserves_existing_bundle(self):
        output = package(self.root, '0.1.0')
        before = output.read_bytes()
        (self.root / 'CHANGELOG.md').write_text('# Changes\n## [Unreleased]\nLater.')
        with self.assertRaisesRegex(ValueError, 'CHANGELOG'):
            package(self.root, '0.1.0')
        self.assertEqual(output.read_bytes(), before)

    def test_version_cannot_escape_output_directory(self):
        for version in ('../private', '0.1.0/../../private', 'v0.1.0', '01.1.0'):
            with self.subTest(version=version), self.assertRaises(ValueError):
                package(self.root, version)
        self.assertFalse((self.root / 'build/releases').exists())

    def test_repeated_bundles_are_byte_identical(self):
        output = package(self.root, '0.1.0')
        before = output.read_bytes()
        package(self.root, '0.1.0')
        self.assertEqual(output.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
