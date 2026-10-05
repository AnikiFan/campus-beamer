# Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
# Part of Campus Beamer. See LICENSE for the GNU GPL v3 notice.
"""Environment checks must report missing prerequisites and fail reliably."""
import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doctor


class DoctorTests(unittest.TestCase):
    def run_check(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = doctor.check()
        return status, output.getvalue()

    def test_missing_commands_are_all_reported_without_running_them(self):
        with patch.object(doctor.shutil, 'which', return_value=None), \
                patch.object(doctor, 'probe') as probe:
            status, output = self.run_check()
        self.assertEqual(status, 1)
        for name, _ in doctor.COMMANDS:
            self.assertIn(f'{name}: not found in PATH', output)
        self.assertIn('[SKIPPED]', output)
        probe.assert_not_called()

    def test_missing_default_font_fails_even_when_commands_work(self):
        def probe(args):
            return (False, 'not found') if args[-1] == 'FandolSong-Regular.otf' else (True, 'found')

        with patch.object(doctor.shutil, 'which', side_effect=lambda name: name), \
                patch.object(doctor, 'probe', side_effect=probe):
            status, output = self.run_check()
        self.assertEqual(status, 1)
        self.assertIn('[MISSING/ERROR] FandolSong-Regular.otf', output)
        self.assertIn('[OK] FandolFang-Regular.otf', output)

    def test_success_returns_zero(self):
        with patch.object(doctor.shutil, 'which', side_effect=lambda name: name), \
                patch.object(doctor, 'probe', return_value=(True, 'found')):
            status, output = self.run_check()
        self.assertEqual(status, 0)
        self.assertIn('Prerequisite checks passed', output)


if __name__ == '__main__':
    unittest.main()
