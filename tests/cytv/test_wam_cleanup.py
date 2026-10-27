import inspect
import subprocess
import tempfile
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from cytv import wam_cleanup as wam
from cytv.errors import UserError


class CleanupTests(unittest.TestCase):
    def test_cleanup_requests_only_two_native_types_once(self):
        self.assertEqual(list(inspect.signature(wam.clean).parameters), ['remote'])
        remote = MagicMock()
        remote.luna.return_value = {'returnValue': True}
        wam.clean(remote)
        remote.luna.assert_called_once_with('com.webos.service.webappmanager/clearBrowsingData',
                                            {'types': ['cache', 'codecache']}, timeout=60)
        remote.run.assert_not_called()

    def test_rejection_malformed_reply_and_disconnect_never_retry_or_delete_files(self):
        self.assertEqual(list(inspect.signature(wam.clean).parameters), ['remote'])
        for reply in ({'returnValue': False}, {}, {'returnValue': 1}, None, UserError('remote-private-data'), OSError(), ValueError('remote-private-data'), RuntimeError('remote-private-data')):
            with self.subTest(reply=reply):
                remote = MagicMock()
                if isinstance(reply, Exception): remote.luna.side_effect = reply
                else: remote.luna.return_value = reply
                with self.assertRaises(UserError) as caught: wam.clean(remote)
                self.assertNotIn('remote-private-data', str(caught.exception))
                self.assertIn('may already have been cleared', str(caught.exception))
                self.assertEqual(remote.luna.call_count, 1)
                remote.run.assert_not_called()

    def test_inspection_reads_only_bounded_counters(self):
        self.assertTrue(hasattr(wam, 'INSPECT'), 'Native cache inspection is missing')
        remote = MagicMock()
        with patch.object(wam, '_run', return_value='CYTV_WAM_CACHE 101292 511948'):
            self.assertEqual(wam.inspect(remote), {'bytes': 101292 * 1024, 'available_kib': 511948})
        remote.luna.assert_not_called()
        for reply in ('CYTV_WAM_CACHE -1 1', 'CYTV_WAM_CACHE 1 99999999999999999999',
                      'CYTV_WAM_CACHE 1 2\nprivate-data', ''):
            with self.subTest(reply=reply), patch.object(wam, '_run', return_value=reply):
                with self.assertRaises(UserError): wam.inspect(remote)

    def test_real_inspection_is_read_only_and_missing_caches_are_zero(self):
        self.assertTrue(hasattr(wam, 'INSPECT'), 'Native cache inspection is missing')
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory).resolve() / 'Default'
            base.mkdir()
            protected = base / 'Session Storage'
            protected.mkdir(); (protected / 'data').write_bytes(b'keep')
            script = wam.INSPECT.replace('/var/lib/wam/Default', str(base)).replace('/usr/bin/luna-send', '/bin/sh')
            prefix = "set -eu\nsafe_mode() { return 0; }\nancestors() { return 0; }\ndf() { printf 'header\\nfixture 1 1 511948 1 /var\\n'; }\n"
            result = subprocess.run(['/bin/sh', '-c', prefix + script], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, 'CYTV_WAM_CACHE 0 511948')
            self.assertEqual((protected / 'data').read_bytes(), b'keep')
            cache = base / 'Cache'; cache.mkdir(); (cache / 'data').write_bytes(b'x' * 8192)
            result = subprocess.run(['/bin/sh', '-c', prefix + script], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertGreater(int(result.stdout.split()[1]), 0)
            self.assertEqual((cache / 'data').read_bytes(), b'x' * 8192)


if __name__ == '__main__': unittest.main()
