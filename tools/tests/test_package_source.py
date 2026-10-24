# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""Source archives must exclude local artifacts and reject unresolved symlinks."""
import subprocess
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
        (self.root / 'examples/sections/01_basics.tex').write_text('Required demo chapter')
        (self.root / 'bibliography/another.bib').write_text('Another bibliography')
        (self.root / 'assets/README.md').write_text('Asset provenance')
        package(self.root, self.output)
        with ZipFile(self.output) as archive:
            names = archive.namelist()
            self.assertIn('docs/notes.example.json', names)
            self.assertNotIn('main.notes.json', names)
            self.assertNotIn('starter.notes.json', names)
            self.assertIn('docs/usage.md', names)
            self.assertIn('examples/sections/01_basics.tex', names)
            self.assertIn('examples/bibliography/refs.bib', names)
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

    def test_theme_configs_remain_but_optional_assets_and_private_themes_are_excluded(self):
        private = self.root / 'theme/private-school'
        private.mkdir()
        (private / 'profile.tex').write_text('Private school configuration')
        package(self.root, self.output)
        with ZipFile(self.output) as archive:
            names = archive.namelist()
            self.assertIn('theme/README.md', names)
            self.assertIn('theme/tsinghua/profile.tex', names)
            self.assertIn('theme/tsinghua/README.md', names)
            for name in ('profile.tex', 'README.md', 'emblem.tex', 'wordmark.tex'):
                self.assertIn('theme/pcl/' + name, names)
            self.assertFalse(any(name.startswith('theme/') and '/assets/' in name
                                 and not name.startswith('theme/general/')
                                 for name in names))
            self.assertIn('theme/general/assets/backdrop.pdf', names)
            for theme in ('general', 'tokyo-night', 'undefined'):
                self.assertIn(f'theme/{theme}/profile.tex', names)
                self.assertIn(f'theme/{theme}/README.md', names)
            self.assertIn('docs/images/preview-tsinghua-cover.png', names)
            self.assertIn('tools/theme_assets.py', names)
            self.assertFalse(any(name.startswith('theme/private-school/') for name in names))

    def test_mermaid_skill_has_its_renderer_and_style_resources(self):
        package(self.root, self.output)
        with ZipFile(self.output) as archive:
            names = set(archive.namelist())
        prefix = '.agents/skills/campus-mermaid/'
        for resource in ('SKILL.md', 'agents/openai.yaml', 'assets/config.json',
                         'scripts/render.mjs', 'references/diagram-selection.md',
                         'references/rendering.md'):
            self.assertIn(prefix + resource, names)

    def test_english_demo_entry_inputs_and_cover_are_distributed(self):
        package(self.root, self.output)
        with ZipFile(self.output) as archive:
            names = set(archive.namelist())
        self.assertIn('example-en.tex', names)
        self.assertIn('docs/images/preview-general-en-cover.png', names)
        for name in ('metadata.tex', 'refs.bib', '01_basics.tex', '02_papers.tex',
                     '03_callouts.tex', '04_navigation.tex', '05_media.tex',
                     'font-guide.tex', 'layout-guide.tex'):
            self.assertIn('examples/english/' + name, names)

    def test_repeated_archives_are_byte_identical(self):
        package(self.root, self.output)
        first = self.output.read_bytes()
        package(self.root, self.output)
        self.assertEqual(first, self.output.read_bytes())

    def test_agent_authored_talk_and_materials_are_not_distributed(self):
        private_files = ('main.tex', 'prompt.md', 'sections/metadata.tex',
                         'sections/01_intro.tex', 'bibliography/main.bib',
                         'sections/talk/legacy.tex', 'bibliography/extra.bib',
                         'materials/paper/main.tex', 'materials/derived/figure.png',
                         'materials/outline.md', 'build/outline-normalized.md')
        for name in private_files:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('Private user content')
        package(self.root, self.output)
        with ZipFile(self.output) as archive:
            names = archive.namelist()
            self.assertIn('example.tex', names)
            self.assertNotIn('prompt.md', names)
            self.assertIn('outline.md', names)
            for directory in ('materials', 'sections', 'bibliography'):
                self.assertEqual([name for name in names if name.startswith(directory + '/')],
                                 [directory + '/.gitkeep'])
            for name in private_files:
                self.assertNotIn(name, names)

    def test_user_directories_are_ignored_but_demo_and_placeholders_are_not(self):
        project = Path(__file__).resolve().parents[2]
        (self.root / '.gitignore').write_bytes((project / '.gitignore').read_bytes())
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True)
        private = ('main.tex', 'sections/metadata.tex', 'sections/code/snippet.py',
                   'sections/talk/legacy.tex', 'bibliography/main.bib',
                   'bibliography/extra.bib', 'materials/paper.pdf')
        public = ('sections/.gitkeep', 'bibliography/.gitkeep', 'materials/.gitkeep',
                  'examples/sections/metadata.tex', 'examples/bibliography/refs.bib')
        result = subprocess.run(['git', 'check-ignore', '--no-index', '--stdin'],
                                input='\n'.join(private + public) + '\n',
                                cwd=self.root, text=True, capture_output=True, check=True)
        self.assertEqual(set(result.stdout.splitlines()), set(private))

    def test_archive_uses_outline_template_without_changing_local_draft(self):
        template = (self.root / 'tools/templates/outline.md').read_bytes()
        outline = self.root / 'outline.md'
        outline.write_text('# Private draft\nUnpublished results and personal notes.\n')
        original = outline.read_bytes()
        package(self.root, self.output)
        first_archive = self.output.read_bytes()
        with ZipFile(self.output) as archive:
            self.assertEqual(archive.read('outline.md'), template)
        self.assertEqual(outline.read_bytes(), original)

        outline.write_text('A different private draft')
        package(self.root, self.output)
        self.assertEqual(self.output.read_bytes(), first_archive)
        self.assertEqual(outline.read_text(), 'A different private draft')

    def test_rejects_symlinks_in_source(self):
        (self.root / 'README.md').unlink()
        (self.root / 'README.md').symlink_to(self.root / 'README.en.md')
        with self.assertRaisesRegex(ValueError, 'symlinks'):
            package(self.root, self.output)
        self.assertFalse(self.output.exists())

    def test_nested_private_files_are_not_distributed(self):
        private_files = ('docs/.env', 'assets/private-slide.pdf',
                         'tools/private.notes.json', '.github/credentials.json',
                         'examples/sections/private-talk.tex', 'bibliography/private.bib')
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
