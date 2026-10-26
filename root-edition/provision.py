#!/usr/bin/env python3
"""Device-side recovery provisioning. Never changes Home or upstream Homebrew files."""
import argparse
import hashlib
import fcntl
import json
import os
from pathlib import Path
import stat
import select
import time
import subprocess
from python_binding import verify_binding

NAME = 'com.cleanyourtv.root.preview.service'
SERVICE = Path('/media/developer/apps/usr/palm/services') / NAME
STATE = Path('/var/lib/clean-your-tv-root')
BASE = Path('/var/luna-service2-dev')
PRIVATE_SERVICE = STATE/'service'
RUNNER = STATE/'run-recovery-service'
PRIVATE_FILES = ('service.js','startup-diagnostics.js','app-inventory.js','handlers.js','services.json','package.json','activity.json','boot-recover.sh')
SYSTEM_FILES = tuple(Path(x) for x in ('/usr/bin/node','/usr/palm/services/jsservicelauncher/bootstrap-node.js','/usr/palm/services/jsservicelauncher/bootstrap.js'))
RUNTIME = STATE / 'runtime'
FILES = {'service': BASE/'services.d'/(NAME+'.service'),
         'role': BASE/'roles.d'/(NAME+'.service.json'),
         'client': BASE/'client-permissions.d'/(NAME+'.service.json'),
         'api': BASE/'api-permissions.d'/(NAME+'.api.json')}

def sha(data):
    return hashlib.sha256(data).hexdigest()

def secure(path):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != 0 or info.st_mode & 0o022:
        raise ValueError('Unsafe root file: '+str(path))
    for parent in path.parents:
        info = parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('Unsafe parent directory: '+str(parent))
    return path.read_bytes()

def write(path, data, mode=0o600):
    if isinstance(data, str): data = data.encode()
    temporary = path.with_name(path.name+'.root-preview-tmp')
    fd = os.open(str(temporary), os.O_WRONLY|os.O_CREAT|os.O_EXCL, mode)
    try:
        with os.fdopen(fd, 'wb') as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(str(temporary), str(path))
        directory = os.open(str(path.parent), os.O_RDONLY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally:
        if temporary.exists(): temporary.unlink()

def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2)+'\n').encode()

def runner_bytes():
    # Follow the firmware's bootstrap argument contract, without evaluating a
    # writable Homebrew wrapper or modifying the system run-js-service script.
    return ('#!/bin/sh\nset -eu\n[ "$#" -eq 0 ] || exit 2\n'
            'cd '+str(PRIVATE_SERVICE)+'\n'
            'export NODE_PATH=/usr/palm/frameworks:/usr/lib/nodejs:/usr/lib/node_modules\n'
            'exec /usr/bin/node --require '+str(PRIVATE_SERVICE/'startup-diagnostics.js')+' /usr/palm/services/jsservicelauncher/bootstrap-node.js -- '
            +str(STATE/'bootstrap.pid')+' /var/palm/ls2-dev '+str(PRIVATE_SERVICE)+'\n').encode()

def prepare_private_service():
    for path in SYSTEM_FILES:
        secure(path)
    # release.json was copied into the private root state before installation.
    release = json.loads(secure(STATE/'release.json'))
    from deploy import checked_file
    contents = {}
    for name in PRIVATE_FILES:
        data = checked_file(SERVICE, name)
        key = 'usr/palm/services/'+NAME+'/'+name
        if sha(data) != release.get('files',{}).get(key):
            raise ValueError('Installed recovery payload mismatch: '+name)
        contents[name] = data
    if PRIVATE_SERVICE.is_symlink(): raise ValueError('Indirect private service')
    PRIVATE_SERVICE.mkdir(mode=0o700,exist_ok=True)
    if PRIVATE_SERVICE.stat().st_mode & 0o022: raise ValueError('Writable private service directory')
    for name,data in contents.items():
        path=PRIVATE_SERVICE/name
        if os.path.lexists(path):
            if secure(path)!=data: raise ValueError('Private recovery service drift: '+name)
        else: write(path,data,0o700 if name=='boot-recover.sh' else 0o600)
    if os.path.lexists(RUNNER):
        if secure(RUNNER)!=runner_bytes(): raise ValueError('Private runner drift')
    else: write(RUNNER,runner_bytes(),0o700)


def plan(original):
    expected = 'Exec=/usr/bin/run-js-service -n '+str(SERVICE)
    if original['service'].splitlines().count(expected) != 1:
        raise ValueError('Unexpected installed service launcher')
    role = json.loads(original['role'])
    if role.get('appId') != NAME: raise ValueError('Unexpected installed role')
    role['allowedNames'] = [NAME]
    role['permissions'] = [{'service':NAME,
        'inbound':['com.webos.lunasend-*','com.webos.service.activitymanager','com.cleanyourtv.root.preview','com.cleanyourtv.root.preview-*'],
        'outbound':['com.webos.service.activitymanager','com.palm.activitymanager']}]
    return {'service': original['service'].replace(expected,'Exec='+str(RUNNER)).encode(),
            'role':encoded(role), 'client':encoded({NAME:['activity.operation'],'com.cleanyourtv.root.preview':[NAME+'.control'],'com.cleanyourtv.root.preview-*':[NAME+'.control']}),
            'api':encoded({NAME+'.control':[NAME+'/'+x for x in ('status','restore','enable','confirm','listApps')],'activities.callbacks':[NAME+'/boot'],NAME+'.admin':[NAME+'/'+x for x in ('status','restore','register','unregister')]})}

def manifest():
    callback = PRIVATE_SERVICE/'boot-recover.sh'
    if b'/var/lib/clean-your-tv-root/runtime/cli.py boot' not in secure(callback):
        raise ValueError('Unexpected boot callback')
    verify_binding(STATE)
    binding = [STATE/name for name in ('python_binding.py','python_boot.js','python-launcher','python-runtime.json') if os.path.lexists(STATE/name)]
    paths = binding + [RUNNER] + [PRIVATE_SERVICE/name for name in PRIVATE_FILES] + sorted(RUNTIME.glob('*.py'))
    if RUNTIME/'cli.py' not in paths: raise ValueError('Missing runtime')
    return {'version':1,'mode':'recovery-only','boot_callback':str(callback),
            'files':{str(path):sha(secure(path)) for path in paths}}

def apply():
    if os.geteuid() != 0: raise ValueError('Root required')
    prepare_private_service()
    if json.loads(secure(PRIVATE_SERVICE/'services.json')).get('id') != NAME: raise ValueError('Wrong installed service')
    pending = manifest()
    original = {key:secure(path).decode() for key,path in FILES.items()}
    updated = plan(original)
    STATE.mkdir(mode=0o700, exist_ok=True)
    snapshot = STATE/'ls2-provision-snapshot.json'
    if snapshot.exists() or snapshot.is_symlink() or (STATE/'recovery-provision.json').exists():
        raise ValueError('Provision already exists; inspect or rollback first')
    saved = {'version':1,'service':NAME,'files':{str(path):{'original':original[key],
        'original_sha256':sha(original[key].encode()),'installed_sha256':sha(updated[key]),
        'mode':stat.S_IMODE(path.stat().st_mode),'uid':path.stat().st_uid,'gid':path.stat().st_gid}
        for key,path in FILES.items()}}
    write(snapshot,encoded(saved))
    write(STATE/'recovery-provision.pending.json',encoded(pending))
    for key,path in FILES.items():
        mode = saved['files'][str(path)]['mode']
        write(path,updated[key],mode)
        os.chown(path,saved['files'][str(path)]['uid'],saved['files'][str(path)]['gid'])
    return {'returnValue':True,'next':'Refresh LS2 registration, then finalize. Trials remain disabled.'}

def repair_pending():
    """Upgrade only incomplete recovery provisioning, never an active trial."""
    if os.path.lexists(STATE/'recovery-provision.json') or os.path.lexists(STATE/'profile-trial.json'):
        raise ValueError('Only never-activated provisioning may be repaired')
    path=STATE/'ls2-provision-snapshot.json'
    saved=json.loads(secure(path))
    if saved.get('phase') is not None or saved.get('service')!=NAME or set(saved['files'])!={str(p) for p in FILES.values()}:
        raise ValueError('Unexpected pending snapshot')
    original={key:saved['files'][str(file)]['original'] for key,file in FILES.items()}
    updated=plan(original)
    for key,file in FILES.items():
        entry=saved['files'][str(file)]
        if sha(entry['original'].encode())!=entry['original_sha256'] or sha(secure(file)) not in (entry['installed_sha256'],entry.get('previous_installed_sha256')):
            raise ValueError('Pending provision drift')
        newhash=sha(updated[key])
        if newhash!=entry['installed_sha256']:
            if entry.get('previous_installed_sha256'): raise ValueError('Only one pending repair supported')
            entry['previous_installed_sha256']=entry['installed_sha256']
            entry['installed_sha256']=newhash
    write(path,encoded(saved))
    for key,file in FILES.items():
        entry=saved['files'][str(file)]
        write(file,updated[key],entry['mode']);os.chown(file,entry['uid'],entry['gid'])
    return {'returnValue':True,'repaired_pending':True}


class RecoveryRPCError(ValueError):
    def __init__(self, reason, code=None):
        super().__init__('Recovery RPC failed: '+reason)
        self.details = {'reason': reason}
        if type(code) is int and -(2**31) <= code < 2**31:
            self.details['luna_error_code'] = code


def startup_record():
    try:
        path = STATE/'recovery-service.json'
        if path.lstat().st_size > 32768: return None
        value = json.loads(secure(path))
        return value if isinstance(value, dict) and value.get('schema') == 1 else None
    except (OSError, ValueError):
        return None


def rpc(method):
    if method in ('register','unregister'):
        import activity
        return activity.manage(method,secure,write)
    if method not in ('status','register','restore','unregister'):
        raise ValueError('Unsupported recovery method')
    uri = 'luna://'+NAME+'/'+method
    try:
        process = subprocess.Popen(['/usr/bin/luna-send','-n','1',uri,'{}'],
                                   stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    except OSError as error:
        raise RecoveryRPCError('client-start-failed') from error
    try:
        # This TV exits luna-send early if stdin closes before its first reply.
        deadline = time.monotonic()+(610 if method == 'restore' else 45)
        data, total = b'', 0
        streams = [process.stdout, process.stderr]
        while time.monotonic() < deadline:
            ready = select.select(streams, [], [], max(0, deadline-time.monotonic()))[0]
            if not ready: break
            for stream in ready:
                chunk = os.read(stream.fileno(), 4096)
                if not chunk:
                    if stream is process.stdout:
                        reason = 'invalid-reply' if data else 'client-exited'
                        raise RecoveryRPCError(reason)
                    streams.remove(stream)
                    continue
                total += len(chunk)
                if total > 65536: raise RecoveryRPCError('oversized-client-output')
                if stream is process.stderr: continue  # Drain, but never export raw errors.
                data += chunk
                try: reply = json.loads(data)
                except ValueError: continue
                if not isinstance(reply,dict) or type(reply.get('returnValue')) is not bool:
                    raise RecoveryRPCError('invalid-reply')
                if reply['returnValue'] is False:
                    error = RecoveryRPCError('negative-reply', reply.get('errorCode'))
                    text = reply.get('errorText')
                    text = text[:1024].lower() if isinstance(text, str) else ''
                    for category, phrases in (('permission-denied', ('denied methods call', 'permission denied', 'access denied')),
                                              ('service-missing', ('service does not exist', 'service is not registered')),
                                              ('method-missing', ('unknown method', 'method does not exist'))):
                        if any(phrase in text for phrase in phrases):
                            error.details['luna_reason'] = category
                            break
                    raise error
                return reply
        reason = 'client-exited' if process.poll() is not None else 'timeout'
        raise RecoveryRPCError(reason)
    except RecoveryRPCError as error:
        code = process.poll()  # Before cleanup, so our terminate() is not reported as the cause.
        if type(code) is int and 0 <= code <= 255: error.details['client_exit_status'] = code
        raise
    finally:
        if process.poll() is None: process.terminate()
        # Never re-buffer arbitrary output through communicate() during cleanup.
        for stream in (process.stdin, process.stdout, process.stderr):
            try: stream.close()
            except OSError: pass
        try: process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill(); process.wait(timeout=1)

def refresh():
    executable = next((path for path in (Path('/usr/bin/ls-control'),Path('/usr/sbin/ls-control')) if path.is_file()),None)
    if executable is None: raise ValueError('ls-control unavailable')
    subprocess.run([str(executable),'scan-services'],check=True,timeout=15,
                   stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return {'returnValue':True,'operation':'scan-services','effective_registration_verified':False}

def finalize():
    before = startup_record()
    phase = 'manifest'
    try:
        expected = json.loads(secure(STATE/'recovery-provision.pending.json'))
        if manifest() != expected: raise ValueError('Runtime changed since provisioning')
        phase = 'status'
        reply = rpc('status')
        if reply.get('root') is not True:
            raise ValueError('Recovery callback process is not root')
        phase = 'register'
        reply = rpc('register')
        if reply.get('root') is not True or reply.get('registered') is not True or reply.get('activityName') != NAME+'.recovery':
            raise ValueError('Recovery activity not verified')
        phase = 'startup-hook'
        import startup_hook
        startup_hook.install(secure,write)
        phase = 'publish'
        write(STATE/'recovery-provision.json',encoded(expected))
        return {'returnValue':True,'mode':'recovery-only','activity':reply}
    except Exception as error:
        report = {'schema':1, 'phase':phase, 'reason':'failed'}
        attempt = os.environ.get('CYTV_ROOT_INSTALL_ATTEMPT', '')
        import re
        if re.fullmatch('[a-f0-9]{32}', attempt): report['attempt'] = attempt
        if isinstance(error, RecoveryRPCError): report.update(error.details)
        after = startup_record()
        report['startup_state'] = 'unavailable' if after is None else 'stale'
        if after is not None and after != before and after.get('phase') in ('starting','exited'):
            report['startup_state'] = after['phase']
            code = after.get('exit_status')
            if type(code) is int and 0 <= code <= 255: report['startup_exit_status'] = code
            exception = after.get('exception', {})
            if isinstance(exception, dict):
                if exception.get('name') in ('Error','TypeError','SyntaxError','ReferenceError','RangeError'):
                    report['exception_name'] = exception['name']
                if exception.get('code') in ('MODULE_NOT_FOUND','ERR_DLOPEN_FAILED','EACCES','EPERM','ENOENT'):
                    report['exception_code'] = exception['code']
        try: write(STATE/'recovery-failure.json',encoded(report))
        except (OSError, ValueError): pass
        raise


def disable_trials():
    # Serialize readiness revocation with the runtime's trial publication lock.
    # begin() rechecks this manifest after acquiring that same lock.
    fd = os.open(STATE/'profile-trial.lock', os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
        readiness = STATE/'recovery-provision.json'
        if readiness.exists(): readiness.unlink()
        directory = os.open(STATE, os.O_RDONLY)
        try: os.fsync(directory)
        finally: os.close(directory)
    finally: os.close(fd)

def rollback():
    saved = json.loads(secure(STATE/'ls2-provision-snapshot.json'))
    if saved.get('version') != 1 or saved.get('service') != NAME or set(saved['files']) != {str(p) for p in FILES.values()}:
        raise ValueError('Invalid provision snapshot')
    if saved.get('phase') == 'rolled-back':
        if os.path.lexists(STATE/'recovery-provision.json'):
            raise ValueError('Unexpected readiness after rollback')
        for path,entry in saved['files'].items():
            file = Path(path)
            if sha(entry['original'].encode()) != entry['original_sha256'] or sha(secure(file)) != entry['original_sha256']:
                raise ValueError('Restored LS2 file drift: '+path)
            info = file.stat()
            if (stat.S_IMODE(info.st_mode),info.st_uid,info.st_gid) != (entry['mode'],entry['uid'],entry['gid']):
                raise ValueError('Restored LS2 metadata drift: '+path)
        import system_permissions
        system_permissions.remove(secure)
        import startup_hook
        startup_hook.remove(secure)
        return {'returnValue':True,'already_rolled_back':True,'next':'Refresh LS2 registration before package removal.'}
    if saved.get('phase') not in (None, 'restoring'):
        raise ValueError('Unknown provisioning phase')
    if saved.get('phase') == 'restoring' and os.path.lexists(STATE/'recovery-provision.json'):
        raise ValueError('Unexpected readiness during rollback')
    # Refuse any drift before canceling activity or touching files. A partial apply
    # can contain original or installed bytes, both exactly recorded here.
    for path, entry in saved['files'].items():
        if sha(entry['original'].encode()) != entry['original_sha256'] or sha(secure(Path(path))) not in (entry['original_sha256'],entry['installed_sha256'],entry.get('previous_installed_sha256')):
            raise ValueError('LS2 file drift: '+path)
    if saved.get('phase') != 'restoring':
        disable_trials()
        restored = rpc('restore')
        runtime = restored.get('result')
        if not isinstance(runtime,dict) or runtime.get('returnValue') is not True or runtime.get('result') not in ('restored','absent'):
            raise ValueError('Recovery is not terminal; keep boot activity registered')
        rpc('unregister')
        saved['phase'] = 'restoring'
        write(STATE/'ls2-provision-snapshot.json',encoded(saved))
    import system_permissions
    system_permissions.remove(secure)
    import startup_hook
    startup_hook.remove(secure)
    for path,entry in saved['files'].items():
        write(Path(path),entry['original'],entry['mode'])
        os.chown(path,entry['uid'],entry['gid'])
    saved['phase'] = 'rolled-back'
    write(STATE/'ls2-provision-snapshot.json',encoded(saved))
    pending = STATE/'recovery-provision.pending.json'
    if pending.exists(): pending.unlink()
    return {'returnValue':True,'next':'Refresh LS2 registration; uninstall package only after recovery succeeds.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan','apply','refresh','finalize','rollback','repair_pending'])
    command = parser.parse_args().command
    if os.geteuid() != 0 and command != 'plan': raise ValueError('Root required')
    if command == 'plan':
        print(json.dumps({'service':NAME,'files':{k:str(v) for k,v in FILES.items()},
                          'runner':str(RUNNER),'activity':json.loads((SERVICE/'activity.json').read_text()),
                          'sequence':['install package and runtime','apply','refresh LS2','finalize'],
                          'rollback':['restore runtime','cancel owned activity','restore exact LS2 snapshots','refresh LS2']} ,indent=2))
    else:
        fd = os.open(STATE/'provision.lock', os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW, 0o600)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX|fcntl.LOCK_NB)
            print(json.dumps(globals()[command]()))
        finally: os.close(fd)

if __name__ == '__main__':
    main()
