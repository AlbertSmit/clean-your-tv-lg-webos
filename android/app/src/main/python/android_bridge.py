"""Android callbacks around the existing CYTV CLI. No device logic is duplicated."""
import json
from pathlib import Path

from cytv import cli, state
from cytv.transport import SSH


def arguments(config, directory, identity=''):
    action = config.get('action', 'install')
    if action not in ('install', 'status', 'doctor', 'restore'):
        raise ValueError('Unsupported Android operation')
    profile = state.target(config.get('host', ''), config.get('edition', ''), config.get('port'))
    language = config.get('language', 'ru')
    if language not in ('ru', 'en'):
        raise ValueError('Unsupported Android language')
    result = [action, '--host', profile['host'], '--edition', profile['edition'],
              '--port', str(profile['port']), '--no-discovery', '--language', language,
              '--data-dir', str(directory)]
    if identity and profile['edition'] == 'root':
        result += ['--identity', str(identity)]
    return result


class Callbacks:
    def __init__(self, native, identity=''):
        self.native = native
        self.identity = identity
        self.context = []

    def emit(self, **event):
        self.native.emit(json.dumps(event, ensure_ascii=False))

    def write(self, message):
        message = str(message)
        self.context.append(message)
        self.context = self.context[-60:]
        self.emit(kind='log', text=message)

    def request(self, **event):
        answer = self.native.request(json.dumps(event, ensure_ascii=False))
        if answer is None:
            raise EOFError
        return str(answer)

    def ask(self, prompt):
        return self.request(kind='question', text=prompt, context='\n'.join(self.context))

    def secret(self, prompt):
        return self.request(kind='secret', text=prompt)

    def trust(self, value, root):
        return self.request(kind='trust', fingerprint=value, root=root) == 'yes'

    def connect(self, profile, directory, secret, trust):
        if profile['edition'] == 'root' and not self.identity:
            profile.pop('identity', None)
        def approve(fingerprint, root):
            if not self.trust(fingerprint, root):
                raise EOFError
            return True
        return SSH.connect(profile, directory, secret, approve)


def run(config_json, directory, payload, identity, native):
    callbacks = Callbacks(native, identity)
    try:
        config = json.loads(config_json)
        args = arguments(config, directory, identity)
        # All text and confirmations use the same desktop localization and policies.
        code = cli.main(args, ask=callbacks.ask, write=callbacks.write,
                        secret=callbacks.secret, connect=callbacks.connect, payload_root=payload)
    except Exception as error:
        # Do not emit exception messages, which may contain credentials/paths.
        callbacks.emit(kind='error', text=type(error).__name__)
        code = 2
    callbacks.emit(kind='finished', code=code)
    return code
