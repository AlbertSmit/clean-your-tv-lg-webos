import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cytv import cli, state


class CLITests(unittest.TestCase):
    def setUp(self):
        from cytv import i18n
        i18n.set_language('en')
        self.addCleanup(i18n.set_language, 'en')
        language = patch('cytv.i18n.system_languages', return_value=['en'])
        language.start()
        self.addCleanup(language.stop)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        preferences = patch('cytv.state.default_dir', return_value=Path(directory.name))
        preferences.start()
        self.addCleanup(preferences.stop)

    def test_existing_root_can_be_left_unchanged_without_pairing_or_issue_report(self):
        class Remote:
            def __init__(self): self.calls = []
            def run(self, command, **kwargs):
                self.calls.append(command)
                if 'CYTV_ROOT_READY' in command: return 'CYTV_ROOT_READY'
                if 'CYTV_EXISTING_ROOT' in command: return 'CYTV_EXISTING_ROOT'
                if 'deploy.json' in command: return '{"stage":"installed-recovery-only"}'
                if 'deploy.py status' in command:
                    return '{"returnValue":true,"result":{"recovery":{"integrity_verified":true},"intent":null}}'
                raise AssertionError('Unexpected remote command: '+command)
            def close(self): pass
        with tempfile.TemporaryDirectory() as tmp, \
             patch('cytv.cli.package.verify_payload', return_value={}), \
             patch('cytv.tv.SSAP') as ssap:
            remote = Remote()
            code, output, calls = self.run_cli(['--host', '192.0.2.10', '--edition', 'root', '--data-dir', tmp], ['', ''], remote=remote)
            self.assertEqual(code, 0, output)
            self.assertIn('Root is already installed', output)
            self.assertIn('left unchanged', output)
            self.assertFalse(list(Path(tmp).glob('reports/*.json')))
            self.assertIsNone(state.Store(tmp).pending(state.target('192.0.2.10','root')))
            ssap.assert_not_called()
            self.assertFalse(any('uninstall' in command for command in remote.calls))
        for flags, answers, expected in [(['--yes'], [''], 0), (['--yes','--non-interactive'], [], 2)]:
            with self.subTest(flags=flags), tempfile.TemporaryDirectory() as tmp, \
                 patch('cytv.cli.package.verify_payload', return_value={}), patch('cytv.tv.SSAP') as ssap:
                remote=Remote()
                code, output, _ = self.run_cli(['--host','192.0.2.10','--edition','root','--data-dir',tmp]+flags, answers, remote=remote)
                self.assertEqual(code, expected, output)
                ssap.assert_not_called()
                self.assertFalse(any('uninstall' in command for command in remote.calls))

    def test_install_checks_pending_state_and_offers_inline_completion(self):
        from unittest.mock import MagicMock
        for resolved, resume, accept in ((True, False, False), (False, True, True), (False, True, False), (False, False, False)):
            with self.subTest(resolved=resolved, resume=resume, accept=accept), tempfile.TemporaryDirectory() as tmp, \
                 patch('cytv.cli.package.verify_payload', return_value={}), \
                 patch('cytv.cli.Installer') as cls, patch('cytv.tv.SSAP') as ssap:
                store = state.Store(tmp); profile = state.target('192.0.2.10', 'root')
                store.begin(profile, 'setup-root-updater', stage='verify', requires_updater=True)
                inst = cls.return_value
                def status():
                    if resolved: store.finish(profile)
                    return {'can_resume_root_setup': resume, 'deployment_stage':'installed-recovery-only', 'device':{'result':{'recovery':{'integrity_verified':True}}}}
                inst.status.side_effect = status
                if resolved:
                    from cytv.errors import ExistingRoot
                    inst.preflight.side_effect = ExistingRoot('existing')
                inst.resume_root_setup.return_value = {'updates_ready':True}
                code, output, _ = self.run_cli(['--host','192.0.2.10','--edition','root','--data-dir',tmp], ['', 'y' if accept else 'n'], remote=MagicMock())
                self.assertEqual(code, 0 if resolved or resume else 2, output)
                inst.status.assert_called()
                self.assertEqual(inst.resume_root_setup.call_count, int(resume and accept))
                inst.install.assert_not_called()
                ssap.assert_not_called()
                if not resolved and not (resume and accept): self.assertIsNotNone(store.pending(profile))

    def test_first_question_explains_how_to_find_the_tv_address(self):
        with tempfile.TemporaryDirectory() as tmp:
            messages = []
            before_question = []
            def ask(prompt):
                before_question.append('\n'.join(messages))
                raise EOFError
            code = cli.main(['--data-dir', tmp], ask=ask, write=messages.append, search=lambda: [])
            self.assertEqual(code, 130)
            for detail in ('Settings', 'Wi-Fi', 'Ethernet', '192.168.'):
                self.assertIn(detail, before_question[0])
            self.assertFalse(list(Path(tmp).glob('reports/*.json')))

    def test_secret_prompt_explains_hidden_tv_passphrase_without_echoing_it(self):
        from cytv.errors import UserError
        with tempfile.TemporaryDirectory() as tmp:
            output, before_secret = [], []
            def secret(prompt):
                before_secret.append('\n'.join(output))
                return 'PRIVATE-TEST-PASSPHRASE'
            def connect(profile, directory, secret, trust):
                secret('Developer Mode passphrase: ')
                raise UserError('Connection cancelled for this test.')
            code = cli.main(['status', '--host', 'tv.local', '--edition', 'no-root', '--data-dir', tmp],
                            write=output.append, connect=connect, secret=secret)
            self.assertEqual(code, 2)
            self.assertIn('hidden', before_secret[0])
            self.assertIn('Key Server', before_secret[0])
            self.assertNotIn('PRIVATE-TEST-PASSPHRASE', '\n'.join(output))

    def test_mistyped_address_and_menu_choice_can_be_corrected_without_issue_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, output, calls = self.run_cli(['--data-dir', tmp], ['', '?', '192.168.1.999', '192.0.2.10', '7', '1', 'maybe', 'n'])
            self.assertEqual(code, 0, output)
            self.assertIn('Cancelled', output)
            self.assertFalse(calls)
            self.assertFalse(list(Path(tmp).glob('reports/*.json')))

    def test_saved_tv_can_be_replaced_in_interactive_install_wizard(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = state.Store(tmp)
            store.save(state.target('192.0.2.10', 'no-root'))
            code, output, calls = self.run_cli(['--data-dir', tmp], ['0', '192.0.2.20', '1', 'n'])
            self.assertEqual(code, 0, output)
            self.assertIn('192.0.2.20', output)
            self.assertFalse(calls)

    def test_discovered_tv_is_selected_without_entering_an_address(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, output, calls = self.run_cli(['--data-dir', tmp], ['', '1', 'n'],
                search=lambda: [{'host': '192.0.2.20', 'name': 'Living room (OLED C3)'}])
            self.assertEqual(code, 0, output)
            self.assertIn('Living room (OLED C3)', output)
            self.assertIn('TV: 192.0.2.20', output)
            self.assertNotIn('Find the IP address', output)
            self.assertFalse(calls)

    def test_search_can_be_repeated_then_a_different_tv_selected(self):
        with tempfile.TemporaryDirectory() as tmp:
            results = iter([[], [{'host': '192.0.2.21', 'name': 'Bedroom'}]])
            code, output, calls = self.run_cli(['--data-dir', tmp], ['r', '', '1', 'n'], search=lambda: next(results))
            self.assertEqual(code, 0, output)
            self.assertIn('TV: 192.0.2.21', output)
            self.assertFalse(calls)

    def test_discovery_network_failure_has_manual_fallback_without_error_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            def denied(): raise PermissionError('private network details')
            code, output, calls = self.run_cli(['--data-dir', tmp], ['192.0.2.10', '1', 'n'], search=denied)
            self.assertEqual(code, 0, output)
            self.assertIn('Local Network', output)
            self.assertNotIn('private network details', output)
            self.assertFalse(calls)
            self.assertFalse(list(Path(tmp).glob('reports/*.json')))

    def test_explicit_host_noninteractive_and_disabled_search_do_not_broadcast(self):
        with tempfile.TemporaryDirectory() as tmp:
            def forbidden(): raise AssertionError('must not search')
            for flags, answers, expected in [
                (['--host', '192.0.2.10'], ['1', 'n'], 0),
                (['--non-interactive'], [], 2),
                (['--no-discovery'], ['192.0.2.10', '1', 'n'], 0),
            ]:
                with self.subTest(flags=flags):
                    code, output, calls = self.run_cli(flags + ['--data-dir', tmp], answers, search=forbidden)
                    self.assertEqual(code, expected, output)
                    self.assertFalse(calls)

    def test_discovered_list_always_offers_manual_address_and_validates_choice(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, output, calls = self.run_cli(['--data-dir', tmp], ['9', '0', '192.0.2.50', '1', 'n'],
                search=lambda: [{'host': '192.0.2.20', 'name': 'Living room'}])
            self.assertEqual(code, 0, output)
            self.assertIn('TV: 192.0.2.50', output)
            self.assertFalse(calls)

    def test_root_connection_is_detected_and_recommended_before_edition_question(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, output, calls = self.run_cli(['--host', '192.0.2.10', '--data-dir', tmp], ['', 'n'],
                inspect=lambda host, port: {'root_ssh': True, 'developer_ssh': False, 'root_port': 22})
            self.assertEqual(code, 0, output)
            self.assertIn('Root SSH detected', output)
            self.assertIn('Root (recommended)', output)
            self.assertIn('Edition: Root', output)
            self.assertNotIn('Root Preview', output)
            self.assertFalse(calls)

    def test_root_install_does_not_ask_for_key_before_connecting(self):
        from cytv.errors import UserError
        with tempfile.TemporaryDirectory() as tmp:
            questions, output = [], []
            answers = iter([''])
            def ask(prompt):
                questions.append(prompt)
                return next(answers)
            def connect(profile, directory, secret, trust):
                self.assertNotIn('identity', profile)
                raise UserError('Stop before TV changes')
            code = cli.main(['--host', '192.0.2.10', '--edition', 'root', '--data-dir', tmp],
                            ask=ask, write=output.append, connect=connect)
            self.assertEqual(code, 2, '\n'.join(output))
            self.assertEqual(len(questions), 1, questions)
            self.assertIn('[Y/n]', questions[0])
            self.assertNotIn('Your existing SSH key', '\n'.join(output))

    def test_first_tv_identity_uses_plain_confirmation_not_fingerprint_entry(self):
        from cytv.errors import UserError
        with tempfile.TemporaryDirectory() as tmp:
            output, questions = [], []
            answers = iter(['?', 'y'])
            def ask(prompt):
                questions.append(prompt)
                return next(answers)
            def connect(profile, directory, secret, trust):
                self.assertTrue(trust('SHA256:test-public-key', True))
                raise UserError('Stop before TV changes')
            code = cli.main(['status', '--host', '192.0.2.10', '--edition', 'root', '--data-dir', tmp],
                            ask=ask, write=output.append, connect=connect)
            self.assertEqual(code, 2)
            self.assertTrue(all('Connect and remember' in prompt for prompt in questions))
            self.assertNotIn('Verified SHA256 fingerprint', '\n'.join(output))
            self.assertIn('SHA256:test-public-key', '\n'.join(output))

    def test_sleeping_tv_waits_for_user_before_retry_and_never_starts_install_on_cancel(self):
        from cytv.errors import TVNotReady
        class Remote:
            def close(self): self.closed = True
        remote = Remote()
        with tempfile.TemporaryDirectory() as tmp, \
             patch('cytv.cli.package.verify_payload', return_value={}), \
             patch('cytv.tv.SSAP') as ssap, patch('cytv.cli.Installer') as installer:
            ssap.return_value.__enter__.side_effect = TVNotReady()
            code, output, calls = self.run_cli(['--host', '192.0.2.10', '--edition', 'root', '--data-dir', tmp], ['', 'q'], remote=remote)
            self.assertEqual(code, 130, output)
            self.assertIn('Turn on your TV', output)
            self.assertIn('Installation has not started', output)
            self.assertEqual(ssap.call_count, 1)
            installer.return_value.install.assert_not_called()
            self.assertIsNone(state.Store(tmp).pending(state.target('192.0.2.10', 'root')))
            self.assertFalse(list(Path(tmp).glob('reports/*.json')))
            self.assertTrue(remote.closed)

    def test_noninteractive_sleeping_tv_reports_clear_reason_without_retry(self):
        from cytv.errors import TVNotReady
        class Remote:
            def close(self): pass
        with tempfile.TemporaryDirectory() as tmp, \
             patch('cytv.cli.package.verify_payload', return_value={}), \
             patch('cytv.tv.SSAP') as ssap, patch('cytv.cli.Installer') as installer:
            ssap.return_value.__enter__.side_effect = TVNotReady()
            code, output, calls = self.run_cli(['--host', '192.0.2.10', '--edition', 'root', '--data-dir', tmp,
                                               '--non-interactive', '--yes'], remote=Remote())
            self.assertEqual(code, 2, output)
            self.assertIn('Installation has not started', output)
            self.assertEqual(ssap.call_count, 1)
            installer.return_value.install.assert_not_called()
            report=json.loads(next(Path(tmp).glob('reports/*.json')).read_text())
            self.assertEqual(report['phase'], 'pair-tv')
            self.assertEqual(report['connection'], {'protocol': 'ssap', 'close_code': 1008, 'reason_code': 'tv-not-ready'})

    def test_waking_tv_retries_only_reading_before_single_install(self):
        from cytv.errors import TVNotReady
        class Remote:
            def close(self): pass
        with tempfile.TemporaryDirectory() as tmp, \
             patch('cytv.cli.package.verify_payload', return_value={}), \
             patch('cytv.cli.payload_dir', return_value=Path(tmp)), \
             patch('cytv.tv.SSAP') as ssap, patch('cytv.cli.Installer') as installer:
            (Path(tmp)/'fallback.png').write_bytes(b'test-fallback')
            inventory = {'apps': [], 'inputs': []}
            session = ssap.return_value
            session.key = None
            session.inventory.return_value = inventory
            session.__enter__.side_effect = [TVNotReady(), session]
            code, output, calls = self.run_cli(['--host', '192.0.2.10', '--edition', 'root', '--data-dir', tmp],
                                               ['', ''], remote=Remote())
            self.assertEqual(code, 0, output)
            self.assertEqual(len(calls), 1)
            self.assertEqual(ssap.call_count, 2)
            session.inventory.assert_called_once_with(b'test-fallback')
            installer.return_value.install.assert_called_once_with(inventory, None, False)
            installer.return_value.trial.assert_not_called()
            self.assertIn('Root is ready', output)
            self.assertNotRegex(output.lower(), r'trial|countdown|keep using|preview release')

    def test_installation_failure_is_never_caught_as_inventory_retry(self):
        from cytv.errors import TVNotReady
        class Remote:
            def close(self): pass
        with tempfile.TemporaryDirectory() as tmp, \
             patch('cytv.cli.package.verify_payload', return_value={}), \
             patch('cytv.cli.payload_dir', return_value=Path(tmp)), \
             patch('cytv.tv.SSAP') as ssap, patch('cytv.cli.Installer') as installer:
            (Path(tmp)/'fallback.png').write_bytes(b'test-fallback')
            ssap.return_value.__enter__.return_value.inventory.return_value = {'apps': [], 'inputs': []}
            installer.return_value.install.side_effect = TVNotReady()
            code, output, calls = self.run_cli(['--host', '192.0.2.10', '--edition', 'root', '--data-dir', tmp, '--yes'], remote=Remote())
            self.assertEqual(code, 2, output)
            self.assertEqual(ssap.call_count, 1)
            installer.return_value.install.assert_called_once()
            report=json.loads(next(Path(tmp).glob('reports/*.json')).read_text())
            self.assertEqual(report['phase'], 'install-packages')
            self.assertNotIn('Installation has not started', output)

    def test_no_root_listener_is_not_presented_as_proven_unrooted(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, output, calls = self.run_cli(['--host', '192.0.2.10', '--data-dir', tmp], ['', 'n'],
                inspect=lambda host, port: {'root_ssh': False, 'developer_ssh': True, 'root_port': 22})
            self.assertEqual(code, 0, output)
            self.assertIn('Root access not confirmed', output)
            self.assertIn('No-root (recommended)', output)
            self.assertNotIn('TV is not rooted', output)
            self.assertIn('SSH port: 9922', output)
            self.assertFalse(calls)

    def test_invalid_target_and_explicit_edition_never_run_connection_check(self):
        with tempfile.TemporaryDirectory() as tmp:
            def forbidden(*args): raise AssertionError('must not inspect')
            code, output, _ = self.run_cli(['--host', '192.0.2.10', '--port', '99999', '--data-dir', tmp], inspect=forbidden)
            self.assertEqual(code, 2, output)
            self.assertIn('Invalid TV address or port', output)
            code, output, _ = self.run_cli(['--host', '192.0.2.10', '--edition', 'no-root', '--data-dir', tmp], ['n'], inspect=forbidden)
            self.assertEqual(code, 0, output)
            self.assertNotIn('Checking TV connections', output)

    def run_cli(self, argv, answers=(), remote=None, search=lambda: [], inspect=lambda host, port: {}):
        output, iterator = io.StringIO(), iter(answers)
        calls = []
        def connect(*args):
            calls.append(args)
            if remote is None:
                raise AssertionError('must not connect')
            return remote
        code = cli.main(argv, ask=lambda _: next(iterator), write=lambda message: output.write(str(message) + '\n'), connect=connect, search=search, inspect=inspect)
        return code, output.getvalue(), calls

    def test_help_and_version_need_no_payload_or_dependencies(self):
        code, output, calls = self.run_cli(['--version'])
        self.assertEqual(code, 0)
        self.assertRegex(output, r'cytv \d+\.\d+\.\d+')
        self.assertFalse(calls)

    def test_wizard_cancel_stops_before_connecting_or_creating_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, output, calls = self.run_cli(['--data-dir', tmp], ['192.0.2.10', '1', 'n'])
            self.assertEqual(code, 0)
            self.assertIn('Cancelled', output)
            self.assertFalse(calls)
            self.assertEqual(state.Store(tmp).profiles(), [])

    def test_missing_target_in_noninteractive_input_fails_before_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, output, calls = self.run_cli(['status', '--non-interactive', '--data-dir', tmp])
        self.assertEqual(code, 2)
        self.assertIn('--host', output)
        self.assertFalse(calls)

    def test_saved_profile_is_reused_for_read_only_status(self):
        class Remote:
            def luna(self, *args, **kwargs):
                return {'returnValue': True, 'apps': [{'id': 'com.gathin.tvhome', 'version': '1.2.2'}]}
            def close(self):
                self.closed = True
        with tempfile.TemporaryDirectory() as tmp:
            store = state.Store(tmp)
            store.save(state.target('192.0.2.10', 'no-root'))
            remote = Remote()
            code, output, calls = self.run_cli(['status', '--data-dir', tmp], remote=remote)
            self.assertEqual(code, 0)
            self.assertIn('1.2.2', output)
            self.assertEqual(calls[0][0]['port'], 9922)
            self.assertTrue(remote.closed)

    def test_unknown_error_never_prints_secrets_or_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = []
            def bad(*args):
                raise RuntimeError('private-password-123')
            code = cli.main(['status', '--host', 'tv.local', '--edition', 'root', '--data-dir', tmp],
                            ask=lambda _: '', write=output.append, connect=bad)
            self.assertEqual(code, 1)
            self.assertNotIn('private-password-123', '\n'.join(output))
            self.assertNotIn('Traceback', '\n'.join(output))


if __name__ == '__main__':
    unittest.main()
