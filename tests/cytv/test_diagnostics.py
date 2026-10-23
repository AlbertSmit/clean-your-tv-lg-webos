import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cytv import cli, diagnostics, state


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        from cytv import i18n
        i18n.set_language('en')
        self.addCleanup(i18n.set_language, 'en')
        language = patch('cytv.i18n.system_languages', return_value=['en'])
        language.start()
        self.addCleanup(language.stop)

    def test_ssap_protocol_metadata_is_allowlisted_without_remote_reason_text(self):
        from cytv.errors import TVConnectionError
        with tempfile.TemporaryDirectory() as tmp:
            error=TVConnectionError('Installer-owned message', close_code=1008, reason_code='PRIVATE-REMOTE-REASON')
            path=diagnostics.create_report(state.Store(tmp), 'install', None, 'pair-tv', error)
            value=json.loads(path.read_text())
            self.assertEqual(value['connection'], {'protocol':'ssap','close_code':1008,'reason_code':'connection-closed'})
            self.assertNotIn('PRIVATE-REMOTE-REASON', path.read_text())

    def test_report_excludes_exception_text_addresses_keys_and_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = state.Store(tmp)
            profile = state.target('192.0.2.55', 'root', identity='/private/secret-personal-key')
            store.begin(profile, 'install')
            store.checkpoint(profile, expected={'private.app.name': 'privatehash'}, eim_registered='unknown')
            try:
                raise RuntimeError('password=ULTRASECRET 192.0.2.55 client-key=PAIRINGKEY private.app.name')
            except RuntimeError as error:
                report = diagnostics.create_report(store, 'install', profile, 'ssh-connect', error)
            raw = report.read_text()
            value = json.loads(raw)
            for private in ('ULTRASECRET', '192.0.2.55', 'PAIRINGKEY', 'private.app.name', 'secret-personal-key'):
                self.assertNotIn(private, raw)
            self.assertEqual(value['phase'], 'ssh-connect')
            self.assertEqual(value['pending'], {'action': 'install', 'stage': 'pending'})
            self.assertTrue(value['trace'])
            self.assertEqual(value['edition'], 'root')

    def test_cli_failure_provides_issue_link_report_and_requested_debug_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = []
            def fail(*args):
                raise OSError('PRIVATE TRANSPORT DATA')
            code = cli.main(['status', '--host', '192.0.2.55', '--edition', 'root', '--data-dir', tmp],
                            write=output.append, connect=fail)
            text = '\n'.join(output)
            self.assertEqual(code, 1)
            self.assertIn('https://github.com/Razdva122/clean-your-tv-lg-webos/issues/new', text)
            self.assertIn('diagnostic-', text)
            self.assertIn('expected', text)
            self.assertNotIn('PRIVATE TRANSPORT DATA', text)
            reports = list(Path(tmp).glob('reports/*.json'))
            self.assertEqual(len(reports), 1)
            self.assertEqual(json.loads(reports[0].read_text())['phase'], 'ssh-connect')


if __name__ == '__main__':
    unittest.main()
