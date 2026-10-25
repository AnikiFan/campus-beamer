# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Overleaf archives must compile independently and exclude private talk inputs."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_overleaf import package
from package_source import FILES
from theme_assets import ASSET_FILES, THEMES, asset_files, package as package_assets


class OverleafPackageTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = Path(__file__).resolve().parents[2]
        self.output = self.root / 'out/demo.zip'
        for name in (*FILES, *ASSET_FILES):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'Public: {name}\n', encoding='utf-8')
        for name in ('examples/example.tex', 'examples/example-en.tex',
                     'tools/templates/overleaf-latexmkrc', 'tools/templates/overleaf-README.md'):
            shutil.copyfile(self.project / name, self.root / name)

    def test_all_theme_language_ratio_combinations_are_self_contained(self):
        for theme in ('general', *THEMES):
            for language in ('chinese', 'english'):
                for aspect in ('169', '43'):
                    with self.subTest(theme=theme, language=language, aspect=aspect):
                        with patch('theme_assets.urlopen', side_effect=AssertionError('Unexpected network')):
                            package(self.root, self.output, theme, language, aspect)
                        with zipfile.ZipFile(self.output) as archive:
                            names = set(archive.namelist())
                            main = archive.read('main.tex').decode()
                            self.assertIn(r'\documentclass[', main)
                            self.assertIn(r'\campusexampleaspectratio}{' + aspect + '}', main)
                            self.assertIn(r'\campusexampletheme}{' + theme + '}', main)
                            if language == 'english':
                                self.assertIn(f'theme={theme},', main)
                            self.assertIn('theme/campusbeamer.cls', names)
                            self.assertIn(f'theme/{theme}/profile.tex', names)
                            self.assertIn('theme/general/assets/backdrop.pdf', names)
                            self.assertIn(f'theme/{theme}/README.md', names)
                            if theme != 'general':
                                self.assertTrue(set(asset_files(theme)).issubset(names))
                            for other in set(THEMES) - {theme}:
                                self.assertFalse(any(n.startswith(f'theme/{other}/') for n in names))
                            self.assertNotIn('.latexmkrc', names)
                            self.assertNotIn('Makefile', names)
                            self.assertNotIn('assets/campus-beamer-logo.tex', names)
                            self.assertNotIn(b'$out_dir', archive.read('latexmkrc'))
                            self.assertIn(b'./theme//:', archive.read('latexmkrc'))
                            self.assertFalse(any(n.startswith('examples/example') for n in names))

    def test_private_inputs_never_enter_archive_and_repeated_runs_are_identical(self):
        package(self.root, self.output)
        first = self.output.read_bytes()
        for name in ('main.tex', 'outline.md', 'sections/private.tex', 'materials/private.png',
                     'examples/sections/private.tex', 'assets/private.pdf'):
            (self.root / name).write_text('PRIVATE USER DATA')
        package(self.root, self.output)
        self.assertEqual(first, self.output.read_bytes())
        with zipfile.ZipFile(self.output) as archive:
            for name in archive.namelist():
                self.assertNotIn(b'PRIVATE USER DATA', archive.read(name))

    def test_missing_assets_download_checked_bundle_without_altering_local_assets(self):
        bundle = self.root / 'remote/campus-beamer-undefined-assets.zip'
        package_assets(self.root, bundle, 'undefined')
        names = asset_files('undefined')
        original = (self.root / names[0]).read_bytes()
        (self.root / names[0]).unlink()
        (self.root / names[1]).write_bytes(b'Local modified asset')
        with patch('theme_assets.urlopen', side_effect=[
            bundle.with_name('SHA256SUMS').open('rb'), bundle.open('rb')
        ]) as fetch:
            package(self.root, self.output, 'undefined')
        self.assertEqual(fetch.call_count, 2)
        self.assertIn('/theme-assets-undefined/', fetch.call_args_list[0].args[0])
        self.assertFalse((self.root / names[0]).exists())
        self.assertEqual((self.root / names[1]).read_bytes(), b'Local modified asset')
        with zipfile.ZipFile(self.output) as archive:
            self.assertEqual(archive.read(names[0]), original)
            self.assertNotEqual(archive.read(names[1]), b'Local modified asset')

    def test_invalid_download_preserves_previous_zip(self):
        package(self.root, self.output)
        before = self.output.read_bytes()
        bundle = self.root / 'remote/campus-beamer-pcl-assets.zip'
        package_assets(self.root, bundle, 'pcl')
        (self.root / asset_files('pcl')[0]).unlink()
        bundle.write_bytes(b'Corrupt download')
        with patch('theme_assets.urlopen', side_effect=[
            bundle.with_name('SHA256SUMS').open('rb'), bundle.open('rb')
        ]):
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                package(self.root, self.output, 'pcl')
        self.assertEqual(before, self.output.read_bytes())

    def test_symlinked_sources_and_missing_files_preserve_previous_zip(self):
        package(self.root, self.output)
        before = self.output.read_bytes()
        required = self.root / 'theme/campusbeamer.cls'
        required.unlink()
        with self.assertRaises(FileNotFoundError):
            package(self.root, self.output)
        required.symlink_to(self.root / 'LICENSE')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            package(self.root, self.output)
        self.assertEqual(before, self.output.read_bytes())

    def test_changed_demo_entry_fails_explicitly(self):
        entry = self.root / 'examples/example.tex'
        entry.write_text(entry.read_text().replace(r'\providecommand{\campusexampleaspectratio}{169}', ''))
        with self.assertRaisesRegex(ValueError, 'Demo entry changed'):
            package(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_video_links_are_relative_to_overleaf_pdf(self):
        source = self.root / 'examples/sections/05_media.tex'
        source.write_text(r'\href{run:../assets/presentation_demo.mp4}{Video}')
        package(self.root, self.output)
        with zipfile.ZipFile(self.output) as archive:
            self.assertIn(b'run:assets/presentation_demo.mp4', archive.read('examples/sections/05_media.tex'))
        self.assertIn('run:../assets/', source.read_text())

    def test_make_needs_only_python_and_passes_options(self):
        for name in ('Makefile', 'tools/package_overleaf.py', 'tools/package_source.py', 'tools/theme_assets.py'):
            shutil.copyfile(self.project / name, self.root / name)
        (self.root / 'main.tex').write_text('PRIVATE USER TALK')
        for options, expected in (([], 'general-zh-169'),
                                  (['THEME=undefined', 'OVERLEAF_LANGUAGE=english', 'ASPECTRATIO=43'],
                                   'undefined-en-43')):
            result = subprocess.run(['make', 'overleaf', f'PYTHON={sys.executable}',
                                     'UV=false', 'LATEXMK=false', *options], cwd=self.root,
                                    text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((self.root / f'build/overleaf/campus-beamer-{expected}.zip').is_file())
        invalid = subprocess.run(['make', 'overleaf', f'PYTHON={sys.executable}', 'THEME=unknown'],
                                 cwd=self.root, text=True, capture_output=True)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertIn('invalid choice', invalid.stderr)


if __name__ == '__main__':
    unittest.main()
