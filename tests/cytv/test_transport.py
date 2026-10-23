import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from cytv.transport import JsonReplies, terminal_reply, SSH


class RejectedAuthTransport:
    auth_handler = SimpleNamespace(auth_event=SimpleNamespace(is_set=lambda: True))
    def is_active(self): return True
    def is_authenticated(self): return False


class TransportTests(unittest.TestCase):
    def test_luna_keeps_stdin_open_until_reply(self):
        class Channel:
            eof = False
            def shutdown_write(self):
                self.eof = True
            def close(self):
                pass
        ssh, channel = object.__new__(SSH), Channel()
        ssh.root = True
        ssh.channel = lambda _: channel
        ssh.chunks = lambda connection, timeout: [] if channel.eof else [b'{"returnValue":true}']
        self.assertTrue(ssh.luna('test/status', {})['returnValue'])

    @unittest.skipUnless(__import__('importlib.util').util.find_spec('paramiko'), 'Requires SSH build dependencies')
    def test_passwordless_root_does_not_request_or_log_password(self):
        from cytv.transport import root_auth
        class Transport:
            def auth_none(self, username):
                self.username = username
                return []
        transport = Transport()
        root_auth(lambda _: self.fail('Password was requested')).authenticate(transport)
        self.assertEqual(transport.username, 'root')

    def test_root_agent_login_precedes_all_credential_questions_and_closes_agent(self):
        import paramiko
        from cytv.transport import root_auth
        calls = []
        class Transport(RejectedAuthTransport):
            def auth_none(self, username):
                calls.append('none')
                raise paramiko.BadAuthenticationType('key required', ['publickey'])
            def auth_publickey(self, username, key):
                calls.append(('key', key))
                return []
        class Agent:
            def get_keys(self): return ('agent-key',)
            def close(self): calls.append('agent-close')
        with patch.object(paramiko, 'Agent', return_value=Agent()):
            root_auth(lambda _: self.fail('Password requested'),
                      identity_prompt=lambda: self.fail('Key path requested')).authenticate(Transport())
        self.assertEqual(calls, ['none', ('key', 'agent-key'), 'agent-close'])

    def test_root_fallback_key_is_requested_only_after_automatic_attempts(self):
        import paramiko
        from cytv.transport import root_auth
        calls, profile = [], {'edition': 'root'}
        class Transport(RejectedAuthTransport):
            def auth_none(self, username):
                calls.append('none'); raise paramiko.AuthenticationException()
            def auth_publickey(self, username, key):
                calls.append(key)
                if key != 'selected-key': raise paramiko.AuthenticationException()
                return []
        class Agent:
            def get_keys(self): return ('agent-key',)
            def close(self): calls.append('agent-close')
        def choose():
            calls.append('choose-key'); return '/chosen/private-key'
        with patch.object(paramiko, 'Agent', return_value=Agent()), \
             patch('cytv.transport.load_identity', return_value='selected-key'):
            root_auth(lambda _: self.fail('Password requested'), profile=profile,
                      identity_prompt=choose).authenticate(Transport())
        self.assertEqual(calls, ['none', 'agent-key', 'choose-key', 'selected-key', 'agent-close'])
        self.assertEqual(profile['identity'], '/chosen/private-key')

    def test_root_failed_agent_then_password_and_cancel_are_not_swallowed(self):
        import paramiko
        from cytv.transport import root_auth
        class Transport(RejectedAuthTransport):
            def auth_none(self, username): raise paramiko.AuthenticationException()
            def auth_password(self, username, password):
                self.password = password; return []
        class Agent:
            closed = False
            def get_keys(self): return ()
            def close(self): self.closed = True
        agent, connection = Agent(), Transport()
        with patch.object(paramiko, 'Agent', return_value=agent):
            root_auth(lambda _: 'test-secret', identity_prompt=lambda: None).authenticate(connection)
        self.assertEqual(connection.password, 'test-secret')
        self.assertTrue(agent.closed)
        def cancel(): raise EOFError
        with patch.object(paramiko, 'Agent', return_value=agent), self.assertRaises(EOFError):
            root_auth(lambda _: self.fail('Password requested after cancel'), identity_prompt=cancel).authenticate(Transport())

    def test_root_does_not_continue_after_network_failure_or_partial_auth(self):
        import paramiko
        from cytv.transport import root_auth
        from cytv.errors import UserError
        class Broken:
            def auth_none(self, username): raise OSError('test-only network failure')
        with patch.object(paramiko, 'Agent') as agent, self.assertRaises(OSError):
            root_auth(lambda _: self.fail('Password requested')).authenticate(Broken())
        agent.assert_not_called()
        class Partial:
            def auth_none(self, username): return ['password']
        with self.assertRaises(UserError):
            root_auth(lambda _: self.fail('Password requested')).authenticate(Partial())

    def test_rejected_key_is_not_saved_and_automatic_attempts_are_bounded(self):
        import paramiko
        from cytv.transport import root_auth
        tried, profile = [], {}
        class Transport(RejectedAuthTransport):
            def auth_none(self, username): raise paramiko.AuthenticationException()
            def auth_publickey(self, username, key):
                tried.append(key); raise paramiko.AuthenticationException()
        class Agent:
            def get_keys(self): return tuple(range(10))
            def close(self): pass
        with patch.object(paramiko, 'Agent', return_value=Agent()), \
             patch('cytv.transport.load_identity', return_value='selected-key'), \
             self.assertRaises(paramiko.AuthenticationException):
            root_auth(lambda _: self.fail('Unexpected password retry'), profile=profile,
                      identity_prompt=lambda: '/rejected-key').authenticate(Transport())
        self.assertEqual(tried, [0, 1, 2, 'selected-key'])
        self.assertNotIn('identity', profile)

    def test_paramiko_auth_timeout_and_eof_do_not_advance_to_more_credentials(self):
        import paramiko
        from paramiko.auth_handler import AuthHandler
        import threading
        from cytv.transport import root_auth
        class Transport:
            auth_timeout = 0.01
            def __init__(self, active):
                self.active = active
                self.auth_handler = AuthHandler(self)
                self.auth_handler.auth_event = threading.Event()
            def is_active(self): return self.active
            def is_authenticated(self): return False
            def get_exception(self): return None
            def auth_none(self, username):
                return self.auth_handler.wait_for_response(self.auth_handler.auth_event)
        for active in (True, False):
            with self.subTest(active=active), patch.object(paramiko, 'Agent') as agent, \
                 self.assertRaises(paramiko.AuthenticationException):
                root_auth(lambda _: self.fail('Password requested after network failure'),
                          identity_prompt=lambda: self.fail('Key requested after network failure')).authenticate(Transport(active))
            agent.assert_not_called()

    @unittest.skipUnless(__import__('importlib.util').util.find_spec('paramiko'), 'Requires SSH build dependencies')
    def test_encrypted_root_identity_is_unlocked_with_hidden_passphrase(self):
        import paramiko
        from cytv.transport import load_identity
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'id_rsa'
            original = paramiko.RSAKey.generate(2048)
            original.write_private_key_file(str(path), password='private-test-passphrase')
            prompts = []
            key = load_identity(path, lambda prompt: prompts.append(prompt) or 'private-test-passphrase')
            self.assertEqual(key.asbytes(), original.asbytes())
            self.assertEqual(len(prompts), 1)

    def test_json_stream_handles_split_utf8_and_multiple_events(self):
        replies = JsonReplies()
        raw = '{"returnValue":true,"label":"ТВ"}\n{"details":{"state":"installed"}}'.encode()
        events = []
        for byte in raw:
            events.extend(replies.feed(bytes([byte])))
        self.assertEqual(events, [{'returnValue': True, 'label': 'ТВ'}, {'details': {'state': 'installed'}}])
        with self.assertRaises(ValueError):
            replies.feed(b'x' * 1048577)

    def test_acceptance_is_not_terminal_and_failure_is_never_success(self):
        self.assertFalse(terminal_reply({'returnValue': True}, 'installed'))
        self.assertFalse(terminal_reply({'details': {'state': 'installing'}}, 'installed'))
        self.assertTrue(terminal_reply({'details': {'state': 'installed'}}, 'installed'))
        self.assertTrue(terminal_reply({'details': {'state': 'SUCCESS'}}, 'removed'))
        with self.assertRaises(RuntimeError):
            terminal_reply({'returnValue': False, 'details': {'state': 'installed'}}, 'installed')
        with self.assertRaises(RuntimeError):
            terminal_reply({'details': {'state': 'FAILED'}}, 'installed')

    @unittest.skipIf(__import__('os').name == 'nt', 'TV upload script is POSIX, desktop need not be')
    def test_upload_script_atomically_replaces_only_after_hash_and_mode_checks(self):
        # Run the actual TV upload script against a local temp directory, not a shell mock.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'ssap-key.json'
            path.write_bytes(b'old')
            ssh = object.__new__(SSH)
            def execute(command, data=None, timeout=30):
                result = subprocess.run(['sh', '-c', command], input=data, capture_output=True)
                if result.returncode:
                    raise RuntimeError('upload failed')
                return result.stdout.decode()
            ssh.run = execute
            # BSD stat has a different interface; use the portable mode readback through ls.
            ssh.upload(str(path), b'{"key":"private"}', mode=0o640)
            self.assertEqual(path.read_bytes(), b'{"key":"private"}')
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            self.assertEqual(sorted(p.name for p in Path(tmp).iterdir()), ['ssap-key.json'])


if __name__ == '__main__':
    unittest.main()
