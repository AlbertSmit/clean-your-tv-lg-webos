"""Opt-in Root audio recovery. API success never establishes audible sound."""
from contextlib import contextmanager
import fcntl
import json
import re
import uuid
import os
from pathlib import Path
import select
import stat
import subprocess
import sys
import tempfile
import time
import device_adapter as d
from transport import call as luna

SOUND = 'luna://com.webos.service.audio/'
SETTINGS = 'luna://com.webos.settingsservice/'
POWER = 'luna://com.webos.service.tvpower/power/getPowerState'
UNSET = object()
COMMANDS = ('status', 'enable', 'disable', 'restart-earc', 'restore-hdmi', 'restore-setting', 'boot', 'worker')


class Store:
    def __init__(self, root=d.STATE):
        d.trusted_dir(Path(root))
        self.root = Path(root)/'audio-recovery'
        self.root.mkdir(mode=0o700, exist_ok=True)
        d.trusted_dir(self.root)

    def read(self, name):
        try: return d.safe_json(self.root/(name+'.json'))
        except FileNotFoundError: return None

    def save(self, name, value):
        fd, temporary = tempfile.mkstemp(dir=self.root, prefix='.audio-')
        try:
            with os.fdopen(fd, 'w') as stream:
                json.dump(value, stream); stream.flush(); os.fsync(stream.fileno())
            os.replace(temporary, self.root/(name+'.json')); d.sync(self.root)
        finally:
            if os.path.lexists(temporary): os.unlink(temporary)

    def remove(self, name):
        if self.read(name) is not None:
            (self.root/(name+'.json')).unlink(); d.sync(self.root)

    @contextmanager
    def lock(self, name):
        fd = os.open(self.root/(name+'.lock'), os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK, 0o600)
        try:
            info = os.fstat(fd)
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != d.EXPECTED_UID
                    or info.st_nlink != 1 or info.st_mode & 0o022):
                raise ValueError('Unsafe audio lock')
            fcntl.flock(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
            yield
        finally: os.close(fd)

    def stop_token(self):
        value = self.read('stop')
        if value is None: return None
        if (not isinstance(value, dict) or set(value) != {'schema','token'} or value['schema'] != 1
                or not isinstance(value['token'],str) or not re.fullmatch('[0-9a-f]{32}',value['token'])):
            raise ValueError('Invalid audio stop latch')
        return value['token']

    def policy(self):
        value = self.read('policy')
        if value is None: return dict(schema=1, enabled=False, generation=0, acknowledgedStop=None)
        if (not isinstance(value, dict) or set(value) != {'schema','enabled','generation','acknowledgedStop'}
                or type(value['schema']) is not int or value['schema'] != 1
                or type(value['enabled']) is not bool or type(value['generation']) is not int
                or not 0 <= value['generation'] < 2**53
                or value['acknowledgedStop'] is not None and (not isinstance(value['acknowledgedStop'],str)
                    or not re.fullmatch('[0-9a-f]{32}',value['acknowledgedStop']))):
            raise ValueError('Invalid audio policy')
        if self.stop_token() != value['acknowledgedStop']: value = dict(value, enabled=False)
        return value

    def stop(self):
        self.save('stop', dict(schema=1, token=uuid.uuid4().hex))

    def configure(self, enabled, observed_stop=UNSET, expected=None):
        if type(enabled) is not bool: raise ValueError('Boolean required')
        # Acknowledge only evidence observed when this explicit request began.
        # A newer emergency token always wins, without unlink/check races.
        acknowledged = self.stop_token() if observed_stop is UNSET else observed_stop
        with self.lock('policy'):
            old = self.policy()
            if expected is not None and old != expected: return None
            value = dict(schema=1, enabled=enabled, generation=old['generation']+1,
                         acknowledgedStop=acknowledged if enabled else old['acknowledgedStop'])
            self.save('policy', value)
            return self.policy()

    def pending(self):
        value = self.read('pending')
        if value is not None and value != dict(schema=1, original='on'):
            raise ValueError('Invalid audio restoration receipt')
        return value


class WakeWindow:
    """Initial/reconnected Active snapshots never imply a standby transition."""
    def __init__(self, clock=time.monotonic, boot=False):
        self.clock, self.boot = clock, boot
        self.previous, self.started = None, None

    def event(self, state):
        if state == 'Active':
            if self.previous in ('Active Standby', 'Suspend', 'Standby') or self.previous is None and self.boot:
                self.started = self.clock()
        else: self.started = None
        self.previous = state
        self.boot = False

    def due(self):
        if self.started is None: return False
        elapsed = self.clock()-self.started
        if elapsed < 10: return False
        self.started = None
        return elapsed <= 30


def blocked():
    return (os.path.lexists(d.FAILSAFE) or os.path.lexists(d.STATE/'update-block.json')
            or not d.home_present(purpose='live'))


class Engine:
    def __init__(self, store, call=luna, sleep=time.sleep, clock=time.monotonic, blocked=blocked):
        self.store, self.call, self.sleep, self.clock, self.blocked = store, call, sleep, clock, blocked

    def sound(self):
        output = self.call(SOUND+'getSoundOutput', {})
        settings = self.call(SETTINGS+'getSystemSettings', {'category':'sound','keys':['soundOutput','eArcSupport']})
        if output.get('returnValue') is not True or settings.get('returnValue') is not True:
            raise ValueError('Audio read unavailable')
        configured = output.get('settingsSoundOutputs')
        # No guessed default, and no arbitrary selection from multiple routes.
        configured = configured[0] if isinstance(configured, list) and len(configured) == 1 else None
        persisted = settings.get('settings', {}).get('soundOutput')
        if configured is None: configured = persisted
        elif persisted is not None and persisted != configured: configured = None
        return dict(current=output.get('soundOutput'), configured=configured,
                    earc=settings.get('settings', {}).get('eArcSupport'))

    def active(self):
        reply = self.call(POWER, {})
        return reply.get('returnValue') is True and reply.get('state') == 'Active'

    def automatic_supported(self):
        try:
            reply = self.call(POWER, {'subscribe':True})
            return reply.get('returnValue') is True and reply.get('subscribed') is True and isinstance(reply.get('state'), str)
        except (OSError, ValueError, RuntimeError, TimeoutError): return False

    def write(self, setting):
        result = self.call(SETTINGS+'setSystemSettings', {'category':'sound','settings':{'eArcSupport':setting}})
        if result.get('returnValue') is not True: raise ValueError('Audio write rejected')

    def result(self, result):
        self.store.save('last', dict(result=result, uptime=self.clock()))
        return result

    def perform(self, operation, generation=None):
        if operation not in ('restart-earc','restore-hdmi','restore-setting'):
            raise ValueError('Unsupported audio operation')
        try:
            with self.store.lock('operation'):
                policy = self.store.policy()
                if self.blocked() or generation is not None and (not policy['enabled'] or generation != policy['generation']):
                    return self.result('canceled')
                pending = self.store.pending()
                if pending and operation != 'restore-setting': return self.result('needs-restore')
                if not self.active(): return self.result('unsupported')
                before = self.sound()
                if operation == 'restore-setting':
                    if not pending or before['earc'] not in ('on','off'): return self.result('unsupported')
                    with self.store.lock('policy'):
                        if self.blocked() or self.store.policy() != policy: return self.result('canceled')
                        if before['earc'] != 'on': self.write('on')
                    if self.sound()['earc'] != 'on': return self.result('needs-restore')
                    self.store.remove('pending')
                    return self.result('settings-restored')
                if operation == 'restore-hdmi':
                    if before['configured'] != 'external_arc' or before['current'] != 'tv_speaker':
                        return self.result('unsupported')
                    with self.store.lock('policy'):
                        if self.blocked() or self.store.policy() != policy: return self.result('canceled')
                        reply = self.call(SOUND+'setSoundOutput', {'soundOutput':'external_arc'})
                    if reply.get('returnValue') is not True or self.sound()['current'] != 'external_arc':
                        return self.result('unconfirmed')
                    return self.result('route-restored')
                if before != dict(current='external_arc',configured='external_arc',earc='on'):
                    return self.result('unsupported')
                # Serialize the cancellation check and first write with policy changes.
                # A failed disable request is never reported as a successful cancellation.
                uncertain = False
                with self.store.lock('policy'):
                    if self.blocked() or self.store.policy() != policy:
                        return self.result('canceled')
                    self.store.save('pending', dict(schema=1, original='on'))
                    try: self.write('off')
                    except Exception: uncertain = True
                if not uncertain:
                    if self.sound() != dict(current='external_arc',configured='external_arc',earc='off'):
                        return self.result('needs-restore')
                    self.sleep(2)
                # Cleanup does not depend on enabled/Active: disable or standby must not strand our write.
                current = self.sound()
                if current['current'] != 'external_arc' or current['configured'] != 'external_arc' or current['earc'] not in ('on','off'):
                    return self.result('needs-restore')
                if current['earc'] == 'off': self.write('on')
                if self.sound()['earc'] != 'on' or uncertain:
                    return self.result('needs-restore')
                self.store.remove('pending')
                return self.result('settings-restored')
        except BlockingIOError: return 'busy'
        except (OSError, ValueError, RuntimeError, TimeoutError):
            return self.result('needs-restore' if self.store.pending() else 'unavailable')

    def status(self):
        value = self.sound()
        pending = self.store.pending() is not None
        active = self.active() and not self.blocked()
        supported = self.automatic_supported()
        return dict(returnValue=True, enabled=self.store.policy()['enabled'],
                    observer=observer_live(self.store), autoSupported=supported,
                    canRestart=active and not pending and value == dict(current='external_arc',configured='external_arc',earc='on'),
                    canRestoreRoute=active and not pending and value['configured'] == 'external_arc' and value['current'] == 'tv_speaker',
                    needsRestore=pending, canRestoreSetting=active and pending and value['earc'] in ('on','off'),
                    mode='earc' if value['current'] == 'external_arc' and value['earc'] == 'on' else 'other',
                    last=self.store.read('last'))


def inhibit(root=d.STATE):
    # Old runtimes/never-enabled installations need no new state during emergency restore.
    if os.path.lexists(Path(root)/'audio-recovery'):
        Store(root).stop()


def process_live(store, name, maximum_age):
    try:
        ready = store.read(name)
        if not ready or set(ready) != {'pid','start','boot','uptime','generation','kind'}: return False
        from intent_runtime import boot_identity
        policy = store.policy()
        pid = ready['pid']
        if (not policy['enabled'] or type(pid) is not int or pid <= 0
                or ready['generation'] != policy['generation'] or ready['kind'] not in ('boot','watch')): return False
        command = (d.PROC/str(pid)/'cmdline').read_bytes().split(b'\0')
        return (ready['boot'] == boot_identity() and 0 <= time.monotonic()-ready['uptime'] < maximum_age
                and (d.PROC/str(pid)).stat().st_uid == d.EXPECTED_UID
                and command == [sys.executable.encode(), str(Path(__file__).resolve()).encode(), b'worker',
                                str(policy['generation']).encode(), ready['kind'].encode(), b'']
                and d.process_start(pid) == ready['start'])
    except (OSError, ValueError, KeyError, TypeError): return False


def observer_live(store):
    return process_live(store, 'observer', 10)


def pending_live(store):
    return process_live(store, 'launch', 45)


def launch(store, boot=False):
    from intent_runtime import boot_identity
    with store.lock('launch'):
        if observer_live(store) or pending_live(store): return
        policy = store.policy()
        if not policy['enabled'] or store.pending(): return
        identity = boot_identity()
        consumed = store.read('cold-boot')
        cold = boot and consumed != {'boot':identity} and time.monotonic() < 120
        # Enabling manually consumes this boot too: a later boot callback is not a new power-on.
        store.save('cold-boot', dict(boot=identity))
        kind = 'boot' if cold else 'watch'
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), 'worker', str(policy['generation']), kind],
                                 stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                 close_fds=True, start_new_session=True)
        store.save('launch', dict(pid=child.pid, start=d.process_start(child.pid), boot=identity,
                                 uptime=time.monotonic(), generation=policy['generation'], kind=kind))


def worker(store, generation=None, boot=False):
    from update_guard import control
    from intent_runtime import boot_identity
    with store.lock('worker'):
        policy = store.policy()
        if generation is not None and generation != policy['generation']: return
        if boot:
            from boot_gate import wait
            if not wait():
                store.configure(False, expected=policy); return
        policy = store.policy()
        if (not policy['enabled'] or store.pending()
                or generation is not None and generation != policy['generation']): return
        engine = Engine(store)
        for reconnect in range(3):
            window = WakeWindow(clock=time.monotonic, boot=boot and reconnect == 0)
            child = subprocess.Popen(['/usr/bin/luna-send','-i',POWER,'{"subscribe":true}'],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            data = ''; primed = False; opened = time.monotonic(); last_ready = 0
            try:
                while True:
                    if store.policy() != policy: return
                    if blocked():
                        store.configure(False, expected=policy); return
                    now = time.monotonic()
                    if not primed and now-opened > 5: break
                    if select.select([child.stdout],[],[],.25)[0]:
                        chunk = os.read(child.stdout.fileno(),4096)
                        if not chunk: break
                        data += chunk.decode('utf8')
                        if len(data) > 65536: break
                        while data.strip():
                            data = data.lstrip()
                            try: message, end = json.JSONDecoder().raw_decode(data)
                            except ValueError: break
                            data = data[end:]
                            if (not isinstance(message, dict) or message.get('returnValue') is not True
                                    or not isinstance(message.get('state'), str)
                                    or not primed and message.get('subscribed') is not True):
                                store.configure(False, expected=policy); return
                            window.event(message['state']); primed = True
                    if primed and now-last_ready >= 2:
                        store.save('observer', dict(pid=os.getpid(), start=d.process_start(os.getpid()),
                                   boot=boot_identity(), uptime=now, generation=policy['generation'], kind='boot' if boot else 'watch'))
                        last_ready = now
                    if window.due():
                        try:
                            with control(d.STATE,d.EXPECTED_UID):
                                engine.perform('restart-earc', generation=policy['generation'])
                        except (OSError, ValueError, RuntimeError):
                            engine.result('canceled')
            finally:
                try: store.remove('observer')
                finally:
                    if child.poll() is None: child.terminate()
                    try: child.communicate(timeout=1)
                    except subprocess.TimeoutExpired: child.kill(); child.communicate()
            # Reconnect snapshots are never wake events; bounded retries only.
            time.sleep(1)
        store.configure(False, expected=policy)


def main(command, generation=None, boot=False):
    if os.geteuid() != 0: raise PermissionError('Root required')
    if command not in COMMANDS: raise ValueError('Unknown audio command')
    store = Store()
    engine = Engine(store)
    if command == 'worker':
        worker(store, generation, boot); return dict(returnValue=True)
    if command == 'boot':
        launch(store, boot=True); return dict(returnValue=True)
    if command == 'status': return engine.status()
    if command == 'disable':
        store.stop(); return engine.status()
    # Snapshot before permission/readiness calls: newer emergency or disable wins.
    initial_policy, initial_stop = store.policy(), store.stop_token()
    from update_guard import control
    with control(d.STATE,d.EXPECTED_UID):
        if command == 'enable':
            if (blocked() or store.pending() or not engine.automatic_supported() or not engine.active()
                    or engine.sound() != dict(current='external_arc',configured='external_arc',earc='on')):
                return dict(returnValue=False, errorCode='unavailable')
            if blocked() or store.stop_token() != initial_stop:
                return dict(returnValue=False, errorCode='canceled')
            attempt = store.configure(True, observed_stop=initial_stop, expected=initial_policy)
            if attempt is None or not attempt['enabled']:
                return dict(returnValue=False, errorCode='canceled')
            try:
                launch(store)
                for _ in range(20):
                    if observer_live(store): return engine.status()
                    time.sleep(.1)
            except (OSError, ValueError, RuntimeError): pass
            store.configure(False, expected=attempt)
            return dict(returnValue=False, errorCode='unavailable')
        result = engine.perform(command)
        return dict(returnValue=result in ('settings-restored','route-restored'), result=result)


if __name__ == '__main__':
    try:
        if len(sys.argv) == 4 and sys.argv[1] == 'worker' and sys.argv[2].isdigit() and sys.argv[3] in ('boot','watch'):
            reply = main('worker', int(sys.argv[2]), sys.argv[3] == 'boot')
        else:
            reply = main(sys.argv[1] if len(sys.argv) == 2 and sys.argv[1] != 'worker' else '')
    except Exception:
        reply = dict(returnValue=False, errorCode='unavailable')
    print(json.dumps(reply), flush=True)
