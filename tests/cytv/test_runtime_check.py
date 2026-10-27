"""The packaging probe must exercise SSH dependencies without a TV or profile."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class RuntimeCheckTests(unittest.TestCase):
    def test_offline_probe_exercises_real_dependencies_without_profile_state(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE='1')
            commands = ([sys.executable, '-m', 'cytv', '--check-runtime'],
                        [sys.executable, '-c', "import runpy,sys; sys.modules['PySide6']=None; sys.argv=['cytv-desktop','--check-runtime']; runpy.run_module('cytv.desktop_entry',run_name='__main__')"])
            for command in commands:
                with self.subTest(entry=command[1:3]):
                    result = subprocess.run(command, cwd=directory, env=env,
                                            capture_output=True, text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertIn('Installer runtime verified', result.stdout)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_broken_native_dependency_fails_probe_with_original_error(self):
        root = Path(__file__).resolve().parents[2]
        with tempfile.TemporaryDirectory() as directory:
            Path(directory, 'paramiko.py').write_text(
                "raise ImportError('fixture: missing OpenSSL symbol')\n")
            env = dict(os.environ, PYTHONPATH=os.pathsep.join((directory, str(root))),
                       PYTHONDONTWRITEBYTECODE='1')
            result = subprocess.run([sys.executable, '-m', 'cytv', '--check-runtime'],
                                    cwd=directory, env=env, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('fixture: missing OpenSSL symbol', result.stderr)
            self.assertNotIn('Installer runtime verified', result.stdout)
