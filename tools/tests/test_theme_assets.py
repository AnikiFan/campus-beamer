# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Per-theme assets must install completely without escaping or overwriting local edits."""
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from theme_assets import THEMES, ASSET_FILES, asset_files, archive_name, NOTICE_NAME, download, install, package


class ThemeAssetTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.source = self.root / 'source'
        self.target = self.root / 'target'
        self.target.mkdir()
        self.theme = 'tsinghua'
        self.files = asset_files(self.theme)
        for name in (*self.files, 'theme/tsinghua/README.md', 'theme/pcl/README.md'):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'Public asset: {name}')
        self.archive = self.root / archive_name(self.theme)
        package(self.source, self.archive, self.theme)

    def digest(self):
        return hashlib.sha256(self.archive.read_bytes()).hexdigest()

    def test_package_is_deterministic_allowlisted_and_includes_rights(self):
        first = self.archive.read_bytes()
        (self.source / 'theme/tsinghua/assets/private.png').write_text('Private')
        package(self.source, self.archive, self.theme)
        self.assertEqual(first, self.archive.read_bytes())
        with zipfile.ZipFile(self.archive) as archive:
            self.assertEqual(set(archive.namelist()), set(self.files) | {NOTICE_NAME})
            self.assertIn(b'Asset licenses vary by theme and file', archive.read(NOTICE_NAME))
        self.assertEqual(self.archive.with_name('SHA256SUMS').read_text(),
                         f'{self.digest()}  {archive_name(self.theme)}\n')

    def test_install_is_complete_idempotent_and_preserves_source_files(self):
        profile = self.target / 'theme/tsinghua/profile.tex'
        profile.parent.mkdir(parents=True)
        profile.write_text('Custom profile')
        self.assertEqual(install(self.target, self.archive, self.digest(), self.theme), len(self.files))
        for name in self.files:
            self.assertEqual((self.target / name).read_bytes(), (self.source / name).read_bytes())
        self.assertEqual(profile.read_text(), 'Custom profile')
        self.assertEqual(install(self.target, self.archive, self.digest(), self.theme), 0)
        with patch('theme_assets.urlopen', side_effect=AssertionError('Unexpected network')):
            self.assertEqual(download(self.target, self.theme), 0)

    def test_checksum_and_missing_member_fail_without_installing(self):
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            install(self.target, self.archive, '0' * 64, self.theme)
        with zipfile.ZipFile(self.archive, 'w') as archive:
            archive.writestr(self.files[0], b'Only one file')
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            install(self.target, self.archive, self.digest(), self.theme)
        self.assertEqual(list(self.target.iterdir()), [])

    def test_installed_notice_matches_bundle_without_replacing_old_readme(self):
        readme = self.target / f'theme/{self.theme}/README.md'
        readme.parent.mkdir(parents=True)
        readme.write_text('Old source notice with local edits')
        install(self.target, self.archive, self.digest(), self.theme)
        records = readme.parent / '.installed-assets'
        with zipfile.ZipFile(self.archive) as bundle:
            self.assertEqual((records / NOTICE_NAME).read_bytes(), bundle.read(NOTICE_NAME))
        receipt = json.loads((records / 'receipt.json').read_text())
        self.assertEqual(receipt['archive_sha256'], self.digest())
        self.assertEqual(receipt['asset_sha256'][self.files[0]],
                         hashlib.sha256((self.target / self.files[0]).read_bytes()).hexdigest())
        self.assertEqual(readme.read_text(), 'Old source notice with local edits')
        (self.source / f'theme/{self.theme}/README.md').write_text('Updated source notice')
        package(self.source, self.archive, self.theme)
        install(self.target, self.archive, self.digest(), self.theme, update=True)
        self.assertIn('Updated source notice', (records / NOTICE_NAME).read_text())
        self.assertEqual(readme.read_text(), 'Old source notice with local edits')

    def test_symlinked_installation_record_fails_before_any_assets_are_written(self):
        records = self.target / f'theme/{self.theme}/.installed-assets'
        records.parent.mkdir(parents=True)
        records.symlink_to(self.source, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            install(self.target, self.archive, self.digest(), self.theme)
        self.assertFalse((self.target / self.files[0]).exists())

    def test_download_verifies_the_remote_checksum(self):
        checksum = self.archive.with_name('SHA256SUMS')
        with patch('theme_assets.urlopen', side_effect=[checksum.open('rb'), self.archive.open('rb')]) as fetch:
            self.assertEqual(download(self.target, self.theme), len(self.files))
        self.assertEqual(fetch.call_count, 2)

    def test_pcl_bundle_is_independent_and_wrong_theme_is_rejected(self):
        for name in asset_files('pcl'):
            path = self.source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'PCL: {name}')
        package(self.source, self.archive, 'pcl')
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            install(self.target, self.archive, self.digest(), 'tsinghua')
        self.assertEqual(install(self.target, self.archive, self.digest(), 'pcl'), len(asset_files('pcl')))
        self.assertFalse((self.target / 'theme/tsinghua').exists())
        with zipfile.ZipFile(self.archive) as archive:
            self.assertEqual(set(archive.namelist()), set(asset_files('pcl')) | {NOTICE_NAME})

    def test_every_theme_packages_and_downloads_independently_from_source_zip(self):
        from package_source import FILES, package as package_source
        project = self.source
        public_themes = {Path(name).parent.name for name in FILES
                         if name.startswith('theme/') and name.endswith('/profile.tex')}
        self.assertEqual(set(THEMES), public_themes - {'general'})
        for name in (*FILES, *ASSET_FILES):
            path = project / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'Public file: {name}')
        self.assertFalse(set(ASSET_FILES) & set(FILES))
        source_zip = self.root / 'source.zip'
        package_source(project, source_zip)
        for theme in THEMES:
            with self.subTest(theme=theme):
                target = self.root / theme
                with zipfile.ZipFile(source_zip) as source:
                    source.extractall(target)
                bundled = {p.relative_to(target).as_posix() for p in (target / 'theme').glob('*/assets/*')}
                self.assertTrue(bundled)
                self.assertTrue(all(name.startswith('theme/general/assets/') for name in bundled))
                bundle = self.root / theme / archive_name(theme)
                package(project, bundle, theme)
                checksum = bundle.with_name('SHA256SUMS')
                with zipfile.ZipFile(bundle) as archive:
                    self.assertEqual(set(archive.namelist()), set(asset_files(theme)) | {NOTICE_NAME})
                with patch('theme_assets.urlopen', side_effect=[checksum.open('rb'), bundle.open('rb')]) as fetch:
                    self.assertEqual(download(target, theme), len(asset_files(theme)))
                self.assertIn(f'/theme-assets-{theme}/', fetch.call_args_list[0].args[0])
                installed = {p.relative_to(target).as_posix() for p in (target / 'theme').glob('*/assets/*')}
                self.assertEqual(installed - bundled, set(asset_files(theme)))
                for name in installed:
                    self.assertEqual((target / name).read_bytes(), (project / name).read_bytes())

    def test_partial_install_preserves_modified_assets_until_explicit_update(self):
        existing = self.target / self.files[-1]
        existing.parent.mkdir(parents=True)
        existing.write_bytes(b'Local edit')
        with self.assertRaisesRegex(ValueError, 'Existing asset differs'):
            install(self.target, self.archive, self.digest(), self.theme)
        self.assertFalse((self.target / self.files[0]).exists())
        self.assertEqual(existing.read_bytes(), b'Local edit')
        self.assertEqual(install(self.target, self.archive, self.digest(), self.theme, update=True), len(self.files))

    def test_unsafe_archive_paths_and_symlinks_are_rejected_before_writes(self):
        original = self.archive.read_bytes()
        for name in ('../escape.png', '/tmp/escape.png', 'theme/tsinghua/assets/../profile.tex',
                     'theme/tsinghua/profile.tex', 'theme/tsinghua/assets/run.py',
                     'theme/pcl/assets/unrelated.png',
                     'theme/tsinghua/assets/link.png'):
            with self.subTest(name=name):
                self.archive.write_bytes(original)
                with zipfile.ZipFile(self.archive, 'a') as archive:
                    info = zipfile.ZipInfo(name)
                    if name.endswith('link.png'):
                        info.external_attr = 0o120777 << 16
                    archive.writestr(info, b'Unsafe')
                with self.assertRaises(ValueError):
                    install(self.target, self.archive, self.digest(), self.theme)
                self.assertEqual(list(self.target.iterdir()), [])

    def test_symlinked_destination_is_rejected(self):
        outside = self.root / 'outside'
        outside.mkdir()
        (self.target / 'theme').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            install(self.target, self.archive, self.digest(), self.theme)
        self.assertEqual(list(outside.iterdir()), [])

    def test_invalid_source_does_not_replace_previous_bundle(self):
        first = self.archive.read_bytes()
        asset = self.source / self.files[0]
        asset.unlink()
        with self.assertRaises(FileNotFoundError):
            package(self.source, self.archive, self.theme)
        asset.symlink_to(self.source / self.files[1])
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            package(self.source, self.archive, self.theme)
        self.assertEqual(first, self.archive.read_bytes())


if __name__ == '__main__':
    unittest.main()
