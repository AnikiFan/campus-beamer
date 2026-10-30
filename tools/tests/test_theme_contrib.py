# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Theme starters and reviews stay scoped to public, explicitly selected inputs."""
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from theme_contrib import STARTER_FILES, create_theme, preview_theme


class ThemeContributionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.project = Path(__file__).resolve().parents[2]
        for name in (*[f'theme/general/{n}' for n in STARTER_FILES], 'theme/general/README.md',
                     'tools/templates/theme-README.md', 'tools/templates/theme-demo-images.tex'):
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.project / name, target)

    def test_starter_is_complete_and_retains_sources_without_copying_private_files(self):
        (self.root / 'theme/general/private.txt').write_text('PRIVATE')
        destination = create_theme(self.root, 'my-theme_2')
        for name in STARTER_FILES:
            self.assertEqual((destination / name).read_bytes(),
                             (self.root / 'theme/general' / name).read_bytes())
        self.assertFalse((destination / 'private.txt').exists())
        readme = (destination / 'README.md').read_text()
        self.assertIn('theme=my-theme_2', readme)
        self.assertNotIn('@THEME@', readme)
        self.assertEqual((destination / 'BASE_ASSETS.md').read_bytes(),
                         (self.root / 'theme/general/README.md').read_bytes())
        self.assertIn(r'\campusthemedir/assets/backdrop.pdf',
                      (destination / 'demo-images.tex').read_text())

    def test_existing_theme_is_never_overwritten(self):
        destination = create_theme(self.root, 'my-theme')
        profile = destination / 'profile.tex'
        profile.write_text('LOCAL CHANGES')
        with self.assertRaisesRegex(ValueError, 'already exists'):
            create_theme(self.root, 'my-theme')
        self.assertEqual(profile.read_text(), 'LOCAL CHANGES')

    def test_bad_names_and_symlinks_are_rejected(self):
        for name in ('', '../escape', 'a/b', '-bad', 'a b', 'a;id', 'a$(id)', 'a{b}'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                create_theme(self.root, name)
        (self.root / 'theme/link').symlink_to(self.root / 'theme/general', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            create_theme(self.root, 'link')
        source = self.root / 'theme/general/profile.tex'
        source.unlink()
        source.symlink_to(self.root / 'theme/general/README.md')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            create_theme(self.root, 'new-theme')
        self.assertFalse((self.root / 'theme/new-theme').exists())

    def test_missing_starter_does_not_leave_partial_theme(self):
        (self.root / 'theme/general/assets/backdrop.pdf').unlink()
        with self.assertRaises(FileNotFoundError):
            create_theme(self.root, 'new-theme')
        self.assertFalse((self.root / 'theme/new-theme').exists())

    def test_preview_selects_both_public_entries_and_preserves_private_talk(self):
        create_theme(self.root, 'my-theme')
        private = self.root / 'main.tex'
        private.write_text('PRIVATE TALK')
        with patch('theme_contrib.subprocess.run') as run:
            preview_theme(self.root, 'my-theme')
        self.assertEqual(run.call_count, 2)
        for call, ratio in zip(run.call_args_list, ('169', '43')):
            entry = f'build/theme-review-my-theme-{ratio}'
            self.assertEqual(call.args[0], ['make', '--no-print-directory', 'draft', f'MAIN={entry}'])
            source = (self.root / f'{entry}.tex').read_text()
            self.assertIn(r'\input{examples/example.tex}', source)
            self.assertIn(r'\campusexampleaspectratio}{' + ratio + '}', source)
            self.assertNotIn('main.tex', source)
        self.assertEqual(private.read_text(), 'PRIVATE TALK')

    def test_preview_failure_stops_and_unknown_theme_does_not_invoke_make(self):
        with patch('theme_contrib.subprocess.run') as run:
            with self.assertRaisesRegex(ValueError, 'Missing'):
                preview_theme(self.root, 'missing')
            run.assert_not_called()
        with patch('theme_contrib.subprocess.run', side_effect=subprocess.CalledProcessError(2, 'make')) as run:
            with self.assertRaises(subprocess.CalledProcessError):
                preview_theme(self.root, 'general')
            self.assertEqual(run.call_count, 1)

    def test_make_creation_needs_no_tex_or_uv_and_keeps_input_literal(self):
        for name in ('Makefile', 'tools/theme_contrib.py', 'tools/theme_assets.py'):
            shutil.copyfile(self.project / name, self.root / name)
        for theme, expected in (('my-theme', 0), ('bad; touch injected', 2)):
            result = subprocess.run(['make', 'theme-new', f'THEME={theme}',
                                     f'PYTHON={sys.executable}', 'UV=false', 'LATEXMK=false'],
                                    cwd=self.root, capture_output=True, text=True)
            self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        self.assertTrue((self.root / 'theme/my-theme/profile.tex').is_file())
        self.assertFalse((self.root / 'injected').exists())


if __name__ == '__main__':
    unittest.main()
