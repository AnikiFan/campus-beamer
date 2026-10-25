# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""Make must select the user's deck while keeping the reference demo buildable."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class MakeEntryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        project = Path(__file__).resolve().parents[2]
        shutil.copyfile(project / 'Makefile', self.root / 'Makefile')
        (self.root / 'examples').mkdir()
        (self.root / 'examples/example.tex').write_text('Reference demo')

    def commands(self, *args):
        """Dry-run the real recipes without invoking TeX or the converter."""
        result = subprocess.run(['make', '-n', *args], cwd=self.root,
                                text=True, capture_output=True, check=True)
        return result.stdout

    def test_fresh_copy_builds_example(self):
        commands = self.commands()
        self.assertIn('"examples/example.tex"', commands)
        self.assertIn('tools/export_presentation.py "examples/example.tex"', commands)

    def test_nested_entry_and_shorthand_share_flat_output_paths(self):
        for main in ('example', 'examples/example', str(self.root / 'examples/example')):
            with self.subTest(main=main):
                commands = self.commands('draft', f'MAIN={main}')
                self.assertIn('"build/example.pdf"', commands)
                self.assertIn('"build/example.log"', commands)
                self.assertIn('"build/draft/example"', commands)
                self.assertNotIn('"build/examples/', commands)
        self.assertIn('"examples/example.tex"', self.commands('MAIN=example'))

    def test_generated_main_is_selected_with_matching_preview_path(self):
        (self.root / 'main.tex').write_text('User talk')
        commands = self.commands()
        self.assertIn('tools/export_presentation.py "main.tex"', commands)
        preview = self.commands('draft')
        self.assertIn('"build/draft/main"', preview)
        self.assertNotIn('images_to_ppt.py', preview)

    def test_explicit_entry_overrides_automatic_selection(self):
        (self.root / 'main.tex').write_text('User talk')
        commands = self.commands('MAIN=examples/example')
        self.assertIn('tools/export_presentation.py "examples/example.tex"', commands)
        commands = self.commands('MAIN=talk')
        self.assertIn('tools/export_presentation.py "talk.tex"', commands)

    def test_release_uses_public_demo_even_with_private_entry(self):
        (self.root / 'main.tex').write_text('Private user presentation')
        commands = self.commands('release', 'MAIN=main')
        self.assertIn('"examples/example.tex"', commands)
        self.assertIn('tools/export_presentation.py "examples/example.tex"', commands)
        for entry in ('example-43', 'example-en', 'example-tsinghua', 'example-pcl', 'example-tokyo-night', 'example-undefined'):
            self.assertIn(f'"examples/{entry}.tex"', commands)
            self.assertNotIn(f'tools/export_presentation.py "examples/{entry}.tex"', commands)
        self.assertNotIn('"main.tex"', commands)
        self.assertNotIn('"build/main.pdf"', commands)


if __name__ == '__main__':
    unittest.main()
