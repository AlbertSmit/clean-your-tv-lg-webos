"""Intent-bound trial, explicit promotion and guarded boot recovery."""
import os
import fcntl
import stat
import json
import tempfile
import time
from pathlib import Path
import uuid
import device_adapter as d
from persistent_store import Store
from persistent_recovery import Coordinator
from persistent_lifecycle import identifier


def boot_identity(proc=None, session=None):
    # Firmware snapshots can reuse boot_id; btime moves with clock correction.
    # The tested cold-start path clears this private volatile directory.
    from boot_gate import ROOT
    proc = d.PROC if proc is None else Path(proc)
    boot = (proc/'sys/kernel/random/boot_id').read_text().strip()
    if not identifier(boot) or len(boot) > 64: raise ValueError('Invalid kernel boot identity')
    root = ROOT if session is None else Path(session)
    try: root.mkdir(mode=0o700)
    except FileExistsError: pass
    d.trusted_dir(root)
    fd = os.open(root/'session.lock', os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK, 0o600)
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != d.EXPECTED_UID
                or info.st_nlink != 1 or info.st_mode & 0o022):
            raise ValueError('Unsafe session lock')
        for attempt in range(50):
            try:
                fcntl.flock(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if attempt == 49: raise
                time.sleep(.01)
        try: value = d.safe_json(root/'session.json')
        except FileNotFoundError: value = None
        else:
            if (not isinstance(value,dict) or set(value) != {'version','kernel','token'}
                    or type(value['version']) is not int or value['version'] != 1
                    or not isinstance(value['kernel'],str) or not identifier(value['kernel'])
                    or not isinstance(value['token'],str) or len(value['token']) != 32
                    or any(c not in '0123456789abcdef' for c in value['token'])):
                raise ValueError('Invalid startup session')
        if value is None or value['kernel'] != boot:
            value = dict(version=1,kernel=boot,token=uuid.uuid4().hex)
            temp_fd, name = tempfile.mkstemp(dir=root,prefix='.session-')
            try:
                with os.fdopen(temp_fd,'w') as out: json.dump(value,out)
                os.replace(name,root/'session.json')
            finally:
                if os.path.lexists(name): os.unlink(name)
        return boot+':session-'+value['token']
    finally: os.close(fd)


def coordinator():
    if not os.path.lexists(d.STATE/'persistent-intent.json'): return None
    return Coordinator(Store(d.STATE))


def start():
    from provision import verify
    from helper_bridge import require_idle
    verify(); require_idle()
    c = Coordinator(Store(d.STATE)); intent = c.store.read()
    if intent['phase'] != 'disabled':
        raise ValueError('Restore previous intent before starting another trial')
    return c.start_trial(intent, boot_identity(), str(uuid.uuid4()))


def enable():
    from provision import verify
    from helper_bridge import require_idle
    verify(); require_idle()
    c = Coordinator(Store(d.STATE))
    return c.enable(c.store.read(), boot_identity(), str(uuid.uuid4()))


def later_legacy_trial(c):
    if not os.path.lexists(c.binding) or not os.path.lexists(d.STATE/'profile-trial.json'):
        return False
    from profile_recovery import validate
    binding = c.read_binding()
    journal = d.safe_json(d.STATE/'profile-trial.json'); validate(journal)
    return binding['restored'] and journal.get('transaction') != binding['transaction']


def restore():
    c = coordinator()
    if c is None or later_legacy_trial(c): return None
    intent = c.store.read()
    if intent['phase'] == 'disabled': return None
    result = c.exit(intent)
    return 'restored' if result.get('restored_transaction') else None


def boot():
    if not os.path.lexists(d.STATE/'persistent-intent.json'): return None
    d.trusted_dir(d.STATE)
    fd=os.open(d.STATE/'boot-dispatch.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
    try:
        info=os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != d.EXPECTED_UID
                or info.st_nlink != 1 or info.st_mode & 0o022):
            raise ValueError('Unsafe boot dispatch lock')
        try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:return 'boot-in-progress'
        try:return _boot()
        except Exception as exc:
            from boot_gate import audit
            audit('boot-error',error=type(exc).__name__+': '+str(exc))
            raise
    finally:os.close(fd)


def _boot():
    c = coordinator()
    if c is None or later_legacy_trial(c): return None
    intent = c.store.read()
    try: identity = boot_identity()
    except (OSError,ValueError):
        c.exit(intent,reason='fault')
        raise
    failsafe = d.FAILSAFE.exists() or not d.home_present()
    if not failsafe and identity == intent['boot']:
        if intent['phase'] == 'stopping':
            c.shutdown(intent)
            return 'shutdown-pending'
        try: journal = d.safe_json(d.STATE/'profile-trial.json')
        except FileNotFoundError: journal = None
        if journal is not None and d.active_guardian(journal): return 'guarded-intent-trial'
        if intent['phase'] == 'disabled': return 'restored'
        # Expired trial or interrupted startup in this same boot: disable intent,
        # never infer health from an application merely existing in /proc.
        from boot_gate import audit, observation
        try:
            audit('same-session-fault',phase=intent['phase'],generation=intent['generation'],
                  observation=observation())
        except Exception: pass  # Diagnostic storage must never block fault recovery.
        c.exit(intent, reason='fault')
        return 'restored'
    # Restore first. Normal startup also sets FAILSAFE temporarily; only the
    # current-boot init.d marker plus a cleared flag permits reactivation.
    from boot_gate import audit, observation
    audit('recover-before-gate',prior=intent,boot=identity,observation=observation())
    result = c.boot(intent, identity, str(uuid.uuid4()), False if identity != intent['boot'] else failsafe)
    if result['effect'] == 'start_guarded':
        from boot_gate import wait
        ready = wait()
        audit('gate-complete',prior=intent,boot=identity,ready=ready,observation=observation())
        if not ready:
            c.exit(result['intent'], reason='fault')
            return 'restored'
        result = c.restart(result['intent'])
        if isinstance(result,dict):
            result['presentation'] = present_boot(c,result)
            try: audit('boot-presentation',outcome=result['presentation'],boot=identity)
            except Exception: pass
        return result
    return 'restored'


def present_boot(c, result):
    """One optional startup request; never retry or replace input protection."""
    try:
        intent = result['intent']; tx = result['trial']['transaction']
        if intent['phase'] != 'active' or intent['enabled'] is not True: return 'unavailable'
        sam = d.sam_transport()
        settings = sam.call('luna://com.webos.settingsservice/getSystemSettings',
                            {'category':'general','keys':['homeAutoLaunch']},timeout=.5)
        if settings.get('settings',{}).get('homeAutoLaunch') != 'on':
            return 'preserved-startup-setting'
        boot = sam.call('luna://com.webos.bootManager/getBootStatus',{},timeout=.5)
        if (boot.get('bootTarget') != 'hardware' or boot.get('powerStatus') != 'active'
                or boot.get('bootStatus') != 'normal' or boot.get('firstAppLaunched') is not True):
            return 'preserved-startup-setting'
        from persistent_health import require_fresh
        require_fresh(tx)
        foreground = sam.call('luna://com.webos.applicationManager/getForegroundAppInfo',{},timeout=.5)
        if foreground.get('appId') not in ('com.webos.app.livetv','com.webos.app.home'):
            return 'preserved-foreground'
        if c.store.read() != intent or d.FAILSAFE.exists(): return 'unavailable'
        # Never hold the operation lock over optional RPC: an off request must win.
        # Foreground observation and launch are separate platform calls; an app
        # switch after this last observation can still race this single request.
        sam.call('luna://com.webos.applicationManager/launch',{'id':d.CANDIDATE},timeout=.5)
        return 'launch-requested' if c.store.read() == intent else 'superseded'
    except Exception:
        # Missing/slow optional APIs must not disable otherwise healthy Home control.
        return 'unavailable'


def confirm(transaction=None):
    c = coordinator()
    if c is None: raise ValueError('No intent-bound trial to confirm')
    if transaction != c.read_binding()['transaction']: raise ValueError('Stale confirmation transaction')
    return c.confirm(c.store.read())
