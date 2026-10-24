import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'app/src/main/python/android_bridge.py'


class BridgeTests(unittest.TestCase):
    def module(self):
        self.assertTrue(SOURCE.exists(), 'Android Python adapter is not implemented')
        spec = importlib.util.spec_from_file_location('android_bridge', SOURCE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_rejects_invalid_or_unapproved_commands_before_connecting(self):
        module = self.module()
        for request in ({'host': 'bad;cmd', 'edition': 'root'},
                        {'host': '192.168.1.2', 'edition': 'root', 'action': 'uninstall'},
                        {'host': '192.168.1.2', 'edition': 'other'},
                        {'host': '192.168.1.2', 'edition': 'root', 'port': 0}):
            with self.subTest(request=request), self.assertRaises(ValueError):
                module.arguments(request, '/private/profiles')

    def test_edition_defaults_and_identity_path(self):
        module = self.module()
        args = module.arguments({'host': '192.168.1.2', 'edition': 'no-root'}, '/private/profiles')
        self.assertIn('9922', args)
        self.assertNotIn('--yes', args)
        self.assertNotIn('--non-interactive', args)
        args = module.arguments({'host': '192.168.1.2', 'edition': 'root', 'action': 'restore'}, '/private/profiles', '/private/key')
        self.assertEqual(args[0], 'restore')
        self.assertEqual(args[args.index('--identity') + 1], '/private/key')

    def test_secrets_are_requested_without_echo_and_trust_is_explicit(self):
        module = self.module()
        class Callbacks:
            def __init__(self): self.events = []; self.answers = iter(['sensitive', 'no', 'yes'])
            def emit(self, value): self.events.append(json.loads(value))
            def request(self, value): self.events.append(json.loads(value)); return next(self.answers)
        callbacks = Callbacks()
        adapter = module.Callbacks(callbacks)
        self.assertEqual(adapter.secret('Passphrase:'), 'sensitive')
        self.assertFalse(adapter.trust('SHA256:test', True))
        self.assertTrue(adapter.trust('SHA256:test', True))
        self.assertNotIn('sensitive', json.dumps(callbacks.events))
        self.assertEqual(callbacks.events[0]['kind'], 'secret')
        self.assertEqual(callbacks.events[1]['fingerprint'], 'SHA256:test')

    def test_dispatch_injects_payload_and_does_not_report_cancel_as_success(self):
        module = self.module()
        class Callbacks:
            def __init__(self): self.events = []
            def emit(self, value): self.events.append(json.loads(value))
        callbacks = Callbacks()
        with tempfile.TemporaryDirectory() as tmp, patch('cytv.cli.main', return_value=130) as main:
            module.run(json.dumps({'host': '192.168.1.2', 'edition': 'root'}), tmp, '/payload', '', callbacks)
            self.assertEqual(main.call_args.kwargs['payload_root'], '/payload')
            self.assertEqual(callbacks.events[-1]['kind'], 'finished')
            self.assertEqual(callbacks.events[-1]['code'], 130)

    def test_cancelled_prompt_stops_before_connecting(self):
        module = self.module()
        class Callbacks:
            def request(self, value): return None
        with self.assertRaises(EOFError):
            module.Callbacks(Callbacks()).secret('Passphrase:')

    def test_password_choice_does_not_reuse_an_older_saved_key(self):
        module = self.module()
        profile = {'host': '192.168.1.2', 'edition': 'root', 'port': 22, 'identity': '/older/key'}
        adapter = module.Callbacks(object())
        with patch.object(module.SSH, 'connect') as connect:
            adapter.connect(profile, '/private', lambda _: '', lambda *_: False)
            self.assertNotIn('identity', connect.call_args.args[0])

    def test_cli_verifies_injected_payload_without_using_desktop_directory(self):
        from cytv import cli
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            (path / 'public.txt').write_bytes(b'public')
            (path / 'payload.json').write_text(json.dumps({'files': {'public.txt': hashlib.sha256(b'public').hexdigest()}}))
            output = []
            with patch('cytv.cli.payload_dir', side_effect=AssertionError('Desktop payload path accessed')):
                code = cli.main(['--check-payload', '--data-dir', str(path / 'profiles'), '--language', 'en'],
                                payload_root=path, write=output.append)
            self.assertEqual(code, 0)
            self.assertIn('Embedded payload verified', '\n'.join(output))


if __name__ == '__main__': unittest.main()
