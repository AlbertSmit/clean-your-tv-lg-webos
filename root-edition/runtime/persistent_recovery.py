"""Bind durable intent to RC13 recovery. No activation, CLI or boot hook is wired.

All effectful orchestration must use this operation lock. Intent is disabled
before an emergency restore; failures retain the binding and recovery evidence.
The returned start_guarded effect is a request, never permission to bypass input,
lease and provisioning readiness checks in the future activation adapter.
"""
from contextlib import contextmanager
import fcntl
import json
import os
import stat
import tempfile
import device_adapter as d
from persistent_lifecycle import identifier
from profile_recovery import validate as validate_route


class Coordinator:
    def __init__(self, store):
        self.store = store
        self.binding = store.root/'persistent-binding.json'

    @contextmanager
    def locked(self, expected):
        d.trusted_dir(self.store.root)
        fd = os.open(self.store.root/'persistent-operation.lock',
                     os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != d.EXPECTED_UID
                    or info.st_nlink != 1 or info.st_mode & 0o022):
                raise ValueError('Unsafe operation lock')
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            if self.store.read() != expected: raise ValueError('Stale operation')
            yield
        finally:
            os.close(fd)

    def write_binding(self, value):
        fd, temp = tempfile.mkstemp(dir=self.store.root, prefix='.binding-')
        try:
            with os.fdopen(fd, 'w') as out:
                json.dump(value, out, sort_keys=True); out.flush(); os.fsync(out.fileno())
            os.replace(temp, self.binding); d.sync(self.store.root)
        finally:
            if os.path.exists(temp): os.unlink(temp)

    def read_binding(self):
        try: value = d.safe_json(self.binding)
        except FileNotFoundError as exc: raise ValueError('No routing transaction binding') from exc
        if (not isinstance(value, dict) or set(value) != {'version','generation','token','transaction','restored'}
                or type(value['version']) is not int or value['version'] != 1
                or type(value['generation']) is not int or value['generation'] < 1
                or type(value['restored']) is not bool
                or not identifier(value['token']) or not identifier(value['transaction'])):
            raise ValueError('Invalid routing transaction binding')
        return value

    def route(self, tx):
        journal = d.safe_json(d.STATE/'profile-trial.json')
        validate_route(journal)
        if journal.get('transaction') != tx: raise ValueError('Different routing transaction')
        return journal

    def bind(self, expected, transaction):
        with self.locked(expected):
            return self._bind(expected, transaction)

    def _bind(self, expected, transaction):
        if self.store.read() != expected: raise ValueError('Stale binding request')
        if expected['phase'] not in ('trial','starting') or not identifier(transaction):
            raise ValueError('Binding requires an unconfirmed attempt')
        journal = self.route(transaction)
        if journal['state'] != 'pending': raise ValueError('Routing trial is not pending')
        value = dict(version=1, generation=expected['generation'], token=expected['token'],
                     transaction=transaction, restored=False)
        if os.path.lexists(self.binding):
            old = self.read_binding()
            if old == value: return old
            if not old['restored']: raise ValueError('Previous binding not restored')
        self.write_binding(value)
        return value

    def event(self, expected, kind, **fields):
        event = dict(kind=kind, generation=expected['generation'], token=expected['token'])
        event.update(fields)
        return self.store.apply(expected, event)

    def exit(self, expected, reason='exit'):
        if reason not in ('exit','fault'): raise ValueError('Invalid stop reason')
        with self.locked(expected):
            intent, effect = self.event(expected, reason)
            return self._recover(intent) if effect == 'recover' else dict(intent=intent,effect=effect)

    def boot(self, expected, boot, token, failsafe):
        with self.locked(expected):
            intent, effect = self.event(expected, 'boot', boot=boot, token=token, failsafe=failsafe)
            return self._recover(intent) if effect == 'recover' else dict(intent=intent,effect=effect)

    def resume_recovery(self, expected):
        with self.locked(expected):
            if expected['phase'] != 'recovering': raise ValueError('No pending intent recovery')
            return self._recover(expected)

    def _recover(self, intent):
        try:
            if not os.path.lexists(self.binding) and not intent['enabled']:
                # A start may fail before any routing journal/binding was made.
                # Only reconcile that absence after independently proving stock.
                from profile_plan import plan
                if (os.path.lexists(d.TARGET) or os.path.lexists(d.STATE/'profile-candidate.stage')):
                    raise ValueError('Unbound profile evidence exists')
                current = d.read()
                plan({'returnValue':True,'profiles':current['profiles']},current['sam_home'])
                if os.path.lexists(d.STATE/'profile-trial.json'):
                    j = d.safe_json(d.STATE/'profile-trial.json'); validate_route(j)
                    if j['state'] != 'restored' or current != j['baseline']:
                        raise ValueError('Unbound routing journal is unresolved')
                updated, effect = self.event(intent, 'restored')
                return dict(intent=updated, effect=effect)
            binding = self.read_binding()
            if binding['generation'] > intent['generation']:
                raise ValueError('Binding belongs to a newer intent')
            if (binding['generation'] == intent['generation']
                    and binding['token'] != intent['token']):
                raise ValueError('Binding attempt mismatch')
            tx = binding['transaction']
            journal = self.route(tx)
            result = d.restore_once(expected_transaction=tx)
            if result != 'restored': raise ValueError('Routing recovery incomplete: '+str(result))
            after = self.route(tx)
            if (after['state'] != 'restored' or after['baseline'] != journal['baseline']
                    or d.read() != journal['baseline']):
                raise ValueError('Routing restoration not verified')
            self.write_binding(dict(binding, restored=True))
            updated, effect = self.event(intent, 'restored')
            return dict(intent=updated, effect=effect, restored_transaction=tx)
        except Exception:
            # Never turn a concurrent explicit stop back on. Recovery stays
            # resumable and the existing routing journal is not discarded.
            if self.store.read() == intent and intent['enabled']:
                self.event(intent, 'fault')
            raise

    def start_trial(self, expected, boot, token):
        # The existing independent 60-second deadline is never removed here.
        import emergency_trial
        with self.locked(expected):
            intent, effect = self.event(expected, 'enable', boot=boot, token=token)
            try:
                result = emergency_trial.start(before_publish=lambda tx:self._bind(intent, tx))
                return dict(intent=intent, trial=result, persistent=False)
            except Exception:
                if self.store.read() == intent: self.event(intent, 'fault')
                raise


def bound_exit(transaction):
    """Return None for a legacy trial; otherwise disable bound intent and restore."""
    from persistent_store import Store
    c = Coordinator(Store(d.STATE))
    if not os.path.lexists(c.binding): return None
    binding = c.read_binding()
    if binding['transaction'] != transaction: return None
    intent = c.store.read()
    if (binding['generation'], binding['token']) != (intent['generation'], intent['token']):
        # A newer lifecycle owns boot recovery; never disable it from an old observer.
        return None
    result = c.exit(intent, reason='fault')
    return result.get('restored_transaction') == transaction
