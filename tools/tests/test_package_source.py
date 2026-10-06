# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""Source archives must exclude local artifacts and reject unresolved symlinks."""
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from package_source import FILES, package


class SourcePackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in FILES:
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            (self.root / name).write_text(f'Source file: {name}')
        self.output = self.root / 'build/dist/campus-beamer.zip'

    def test_private_root_talk_and_build_products_are_excluded(self):
        (self.root / 'private-talk.tex').write_text('Private talk')
        (self.root / 'private-talk.notes.json').write_text('Private notes')
        (self.root / 'main.notes.json').write_text('Old generated root notes')
        (self.root / 'starter.notes.json').write_text('Old generated starter notes')
        (self.root / '.venv').mkdir()
        (self.root / '.venv/local.txt').write_text('Local environment')
        (self.root / 'build').mkdir()
        (self.root / 'build/demo.pdf').write_bytes(b'Generated PDF')
        (self.root / 'build/main.notes.json').write_text('Generated build notes')
        (self.root / 'tools/__pycache__').mkdir()
        (self.root / 'tools/__pycache__/module.pyc').write_bytes(b'Bytecode')
        (self.root / 'tools/fixture.log').write_text('Generated log')
        (self.root / 'docs/usage.md').write_text('Manual')
        (self.root / 'docs/notes.example.json').write_text('Format example')
        (self.root / 'chapters/01_basics.tex').write_text('Required demo chapter')
        (self.root / 'bibliography/another.bib').write_text('Another bibliography')
        (self.root / 'assets/README.md').write_text('Asset provenance')
        package(self.root, self.output)
        with ZipFile(self.output) as archive:
            names = archive.namelist()
            self.assertIn('docs/notes.example.json', names)
            self.assertNotIn('main.notes.json', names)
            self.assertNotIn('starter.notes.json', names)
            self.assertIn('docs/usage.md', names)
            self.assertIn('chapters/01_basics.tex', names)
            self.assertIn('bibliography/refs.bib', names)
            self.assertNotIn('bibliography/another.bib', names)
            for name in ('Dockerfile', 'Dockerfile.dockerignore', 'entrypoint.sh'):
                self.assertIn('docker/' + name, names)
            for name in ('refs.bib', 'Dockerfile', '.dockerignore', 'tools/docker-entrypoint.sh'):
                self.assertNotIn(name, names)
            for name in ('campusbeamer.cls', 'beamerthemecampus.sty', 'campuscolor.sty', 'campuscode.sty'):
                self.assertIn('theme/' + name, names)
                self.assertNotIn(name, names)
            self.assertFalse(any('private-talk' in name or '__pycache__' in name
                                 or name.startswith('.venv/') or name.startswith('build/')
                                 or name.endswith('.log') for name in names))

    def test_repeated_archives_are_byte_identical(self):
        package(self.root, self.output)
        first = self.output.read_bytes()
        package(self.root, self.output)
        self.assertEqual(first, self.output.read_bytes())

    def test_agent_authored_talk_and_materials_are_not_distributed(self):
        private_files = ('main.tex', 'chapters/talk/metadata.tex',
                         'chapters/talk/01_intro.tex', 'bibliography/main.bib',
                         'materials/paper/main.tex', 'materials/derived/figure.png')
        for name in private_files:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Private user content')
        package(self.root, self.output)
        with ZipFile(self.output) as archive:
            names = archive.namelist()
            self.assertIn('example.tex', names)
            self.assertIn('prompt.md', names)
            self.assertEqual([name for name in names if name.startswith('materials/')],
                             ['materials/.gitkeep'])
            for name in private_files:
                self.assertNotIn(name, names)

    def test_rejects_symlinks_in_source(self):
        (self.root / 'README.md').unlink()
        (self.root / 'README.md').symlink_to(self.root / 'README.en.md')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            package(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_nested_private_files_are_not_distributed(self):
        private_files = ('docs/.env', 'assets/private-slide.pdf',
                         'tools/private.notes.json', '.github/credentials.json',
                         'chapters/private-talk.tex', 'bibliography/private.bib')
        for name in private_files:
            (self.root / name).write_text('Synthetic private content')
        (self.root / 'docs/unknown-link').symlink_to(self.root / 'README.md')
        package(self.root, self.output)
        with ZipFile(self.output) as archive:
            self.assertEqual(set(archive.namelist()), set(FILES))

    def test_symlinked_parent_directory_does_not_replace_previous_zip(self):
        package(self.root, self.output)
        previous = self.output.read_bytes()
        (self.root / 'docs').rename(self.root / 'external-docs')
        (self.root / 'docs').symlink_to(self.root / 'external-docs', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            package(self.root, self.output)
        self.assertEqual(previous, self.output.read_bytes())

    def test_missing_required_source_does_not_replace_previous_zip(self):
        package(self.root, self.output)
        previous = self.output.read_bytes()
        (self.root / 'theme/campusbeamer.cls').unlink()
        with self.assertRaises(FileNotFoundError):
            package(self.root, self.output)
        self.assertEqual(previous, self.output.read_bytes())


if __name__ == '__main__':
    unittest.main()
