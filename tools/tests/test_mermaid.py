# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""The optional renderer resolves theme/font settings without a browser runtime."""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


PROJECT = Path(__file__).resolve().parents[2]
RENDERER = PROJECT / '.agents/skills/campus-mermaid/scripts/render.mjs'


@unittest.skipUnless(shutil.which('node'), 'Node is optional for Mermaid figures')
class MermaidConfigTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.profile = self.root / 'theme/custom/profile.tex'
        self.profile.parent.mkdir(parents=True)

    def run_config(self, *args):
        return subprocess.run(
            ['node', str(RENDERER), '--root', str(self.root), '--profile', 'custom',
             '--config-only', *args], text=True, capture_output=True, check=False,
        )

    def config(self, *args):
        result = self.run_config(*args)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_resolves_current_profile_instead_of_sample_school_colors(self):
        self.profile.write_text(
            '% \\definecolor{maincolor}{HTML}{FF0000}\n'
            '\\definecolor{maincolor}{HTML}{123456}\n', encoding='utf-8',
        )
        config = self.config()
        self.assertEqual(config['themeVariables']['primaryBorderColor'], '#123456')
        self.assertEqual(config['themeVariables']['lineColor'], '#123456')
        self.assertEqual(config['c4']['person_border_color'], '#123456')
        self.assertNotIn('{{', json.dumps(config))
        self.profile.write_text('\\definecolor{maincolor}{RGB/cmyk}{85,33,116/0,0,0,0}')
        self.assertEqual(self.config()['themeVariables']['lineColor'], '#552174')

    def test_normalized_rgb_and_font_size_apply_to_specialized_types(self):
        self.profile.write_text('\\definecolor{maincolor}{rgb}{0.2,0.4,0.6}')
        config = self.config('--font-size', '17')
        self.assertEqual(config['themeVariables']['lineColor'], '#336699')
        self.assertEqual(config['themeVariables']['fontSize'], '17px')
        self.assertEqual(config['sequence']['actorFontSize'], 17)
        self.assertEqual(config['c4']['messageFontSize'], 17)
        self.assertIn('font-size: 17px', config['themeCSS'])

    def test_computed_colors_fail_instead_of_guessing(self):
        self.profile.write_text('\\colorlet{maincolor}{blue!50!black}')
        result = self.run_config()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('literal', result.stderr)

    def test_rejects_invalid_size_and_profile_paths(self):
        self.profile.write_text('\\definecolor{maincolor}{HTML}{123456}')
        self.assertNotEqual(self.run_config('--font-size', '0').returncode, 0)
        self.assertNotEqual(self.run_config('--profile', '../other').returncode, 0)


if __name__ == '__main__':
    unittest.main()
