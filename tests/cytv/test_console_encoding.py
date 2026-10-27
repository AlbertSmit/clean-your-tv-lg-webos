"""Run real CLI entrypoints with redirected legacy and Unicode streams."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
COMMAND = ([os.environ['CYTV_CONSOLE_EXECUTABLE']] if os.environ.get('CYTV_CONSOLE_EXECUTABLE')
           else [sys.executable, '-m', 'cytv'])


class ConsoleEncodingTests(unittest.TestCase):
    def test_localized_help_and_errors_survive_strict_cp1252(self):
        for language in ('ru', 'ko', 'zh-Hans', 'hi'):
            for arguments, code in ((['--help'], 0), (['--invalid-option'], 2)):
                with self.subTest(language=language, arguments=arguments), tempfile.TemporaryDirectory() as directory:
                    result = subprocess.run([*COMMAND, '--data-dir', directory,
                                             '--language', language, *arguments], cwd=ROOT,
                        env=dict(os.environ, PYTHONIOENCODING='cp1252:strict'), capture_output=True, timeout=30)
                    self.assertEqual(result.returncode, code, result.stderr.decode('ascii', 'backslashreplace'))
                    output = result.stdout if code == 0 else result.stderr
                    self.assertIn(b'--language' if code == 0 else b'--invalid-option', output)
                    if not os.environ.get('CYTV_CONSOLE_EXECUTABLE'):
                        self.assertIn(b'\\u', output)
                    self.assertNotIn(b'Traceback', result.stderr)

    @unittest.skipIf(os.environ.get('CYTV_CONSOLE_EXECUTABLE'),
                     'Frozen Python selects its own native stream encoding')
    def test_utf8_output_preserves_localized_text(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([*COMMAND, '--data-dir', directory,
                                     '--language', 'ru', '--help'], cwd=ROOT,
                env=dict(os.environ, PYTHONIOENCODING='utf-8:strict'), capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('установ'.encode('utf-8'), result.stdout)
            self.assertNotIn(b'\\u', result.stdout)
