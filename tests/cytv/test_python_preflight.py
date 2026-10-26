"""Preflight errors retain safe facts, including the failing space boundary."""
import json
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from cytv import diagnostics, python_runtime as runtime, state
from cytv.errors import UserError


class PreflightTests(unittest.TestCase):
    def test_low_space_survives_selection_and_is_exported_without_remote_text(self):
        class Remote:
            def run(self, command, **kwargs):
                if 'CYTV_SYSTEM_PYTHON' in command:
                    return ''
                return 'CYTV_TARGET_ERROR space 27648 327680 424296'
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(UserError) as caught:
                runtime.select_python(Remote(), directory, lambda _: None, provision=True)
            error = caught.exception
            self.assertIn('27 MiB', str(error))
            self.assertIn('320 MiB', str(error))
            self.assertIn('Session Storage', str(error))
            report = json.loads(diagnostics.create_report(state.Store(directory), 'install', None, 'preflight', error).read_text())
            self.assertEqual(report['python_runtime'], {'reason': 'space', 'available_kib': 27648,
                'required_kib': 327680, 'wam_session_kib': 424296})

    def test_display_does_not_round_a_space_deficit_away(self):
        from cytv.errors import PythonPreflightError
        self.assertIn('319.9 MiB', str(PythonPreflightError('space', 327679, 327680)))

    def test_specific_failures_and_untrusted_output(self):
        for reply, reason in [('CYTV_TARGET_ERROR abi', 'abi'),
                              ('CYTV_TARGET_ERROR ownership', 'ownership'),
                              ('CYTV_TARGET_ERROR space-query', 'space-query'),
                              ('CYTV_TARGET_ERROR space 1 327680 -1', 'space'),
                              ('CYTV_TARGET_ERROR space 1 327680 private-secret', 'unknown'),
                              ('private-secret', 'unknown')]:
            with self.subTest(reply=reply), patch.object(runtime, '_run', return_value=reply):
                with self.assertRaises(UserError) as caught:
                    runtime._preflight(None)
                self.assertEqual(caught.exception.reason, reason)
                self.assertNotIn('private-secret', str(caught.exception))

    @unittest.skipUnless(os.name == 'posix', 'Requires POSIX shell')
    def test_space_check_runs_at_boundary_and_reuses_existing_slot(self):
        with tempfile.TemporaryDirectory() as directory:
            for available, existing, expected in [(327679, False, 'space'), (327680, False, 'READY'),
                                                   (0, True, 'READY'), ('bad', False, 'space-query'), ('9223372036854775808', False, 'space-query')]:
                slot = directory + '/slot'
                if existing: os.mkdir(slot)
                prefix = 'set -eu\nbase=/var/lib\nslot=' + slot + '\n'
                prefix += 'df() { printf "header\\nfixture 1 1 %s 1 /var\\n" "$CYTV_AVAILABLE"; }\n'
                prefix += 'ancestors() { return 1; }\n'
                result = subprocess.run(['/bin/sh', '-c', prefix + runtime._space_script(327680)],
                    env=dict(os.environ, CYTV_AVAILABLE=str(available)), capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, result.stdout)
                if existing: os.rmdir(slot)

    @unittest.skipUnless(os.name == 'posix', 'Requires POSIX shell')
    def test_failed_measurements_never_become_success_or_definite_wam_size(self):
        for command, expected in [
            ('df() { printf "fixture 1 1 999999 1 /var\\n"; return 1; }', 'space-query'),
            ('df() { printf "fixture 1 1 1 1 /var\\n"; }', 'space 1 327680 -1')]:
            prefix = 'set -eu\nbase=/var/lib\nslot=\n' + command + '\n'
            prefix += 'ancestors() { return 0; }\nsafe_mode() { return 0; }\n'
            prefix += 'du() { printf "999999 ignored\\n"; return 1; }\n'
            prefix += 'readlink() { printf "/bin/du"; }\n'
            result = subprocess.run(['/bin/sh', '-c', prefix + runtime._space_script(327680)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(expected, result.stdout)

    def test_staging_recheck_reports_changed_space_before_upload(self):
        with patch.object(runtime, '_run', return_value='CYTV_TARGET_ERROR space 1024 250000 -1'):
            with self.assertRaises(UserError) as caught:
                runtime._check_space(None, 250000)
            self.assertIn('1 MiB', str(caught.exception))
            self.assertEqual(caught.exception.required_kib, 250000)
