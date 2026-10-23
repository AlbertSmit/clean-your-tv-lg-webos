#!/usr/bin/env python3
"""Device-side recovery provisioning. Never changes Home or Homebrew files."""
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

NAME = 'com.cleanyourtv.root.preview.service'
SERVICE = Path('/media/developer/apps/usr/palm/services') / NAME
STATE = Path('/var/lib/clean-your-tv-root')
BASE = Path('/var/luna-service2-dev')
RUNNER = Path('/media/developer/apps/usr/palm/services/org.webosbrew.hbchannel.service/run-js-service')
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

def plan(original):
    expected = 'Exec=/usr/bin/run-js-service -n '+str(SERVICE)
    if original['service'].splitlines().count(expected) != 1:
        raise ValueError('Unexpected installed service launcher')
    role = json.loads(original['role'])
    if role.get('appId') != NAME: raise ValueError('Unexpected installed role')
    role['allowedNames'] = [NAME]
    role['permissions'] = [{'service':NAME,
        'inbound':['com.webos.lunasend-*','com.webos.service.activitymanager'],
        'outbound':['com.webos.service.activitymanager','com.palm.activitymanager']}]
    return {'service': original['service'].replace(expected,'Exec='+str(RUNNER)+' -n '+str(SERVICE)).encode(),
            'role':encoded(role), 'client':encoded({NAME:['activity.operation']}),
            'api':encoded({'activities.callbacks':[NAME+'/boot'],NAME+'.admin':[NAME+'/'+x for x in ('status','restore','register','unregister')]})}

def manifest():
    callback = SERVICE/'boot-recover.sh'
    if b'/var/lib/clean-your-tv-root/runtime/cli.py boot' not in secure(callback):
        raise ValueError('Unexpected boot callback')
    paths = [callback] + sorted(RUNTIME.glob('*.py'))
    if RUNTIME/'cli.py' not in paths: raise ValueError('Missing runtime')
    return {'version':1,'mode':'recovery-only','boot_callback':str(callback),
            'files':{str(path):sha(secure(path)) for path in paths}}

def apply():
    if os.geteuid() != 0: raise ValueError('Root required')
    secure(RUNNER)
    for name in ('service.js','handlers.js','services.json','package.json','activity.json','boot-recover.sh'):
        secure(SERVICE/name)
    if json.loads(secure(SERVICE/'services.json')).get('id') != NAME: raise ValueError('Wrong installed service')
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

def rpc(method):
    if method not in ('status','register','restore','unregister'):
        raise ValueError('Unsupported recovery method')
    uri = 'luna://'+NAME+'/'+method
    process = subprocess.Popen(['/usr/bin/luna-send','-n','1',uri,'{}'],
                               stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        # This TV exits luna-send early if stdin closes before its first reply.
        deadline = time.monotonic()+(610 if method == 'restore' else 45)
        data = b''
        while time.monotonic() < deadline:
            if not select.select([process.stdout],[],[],max(0,deadline-time.monotonic()))[0]: break
            chunk = os.read(process.stdout.fileno(),4096)
            if not chunk: break
            data += chunk
            if len(data) > 65536: raise ValueError('Oversized recovery reply')
            try: reply = json.loads(data)
            except ValueError: continue
            if not isinstance(reply,dict) or reply.get('returnValue') is not True:
                raise ValueError('Service '+method+' failed')
            return reply
        raise TimeoutError('Recovery service did not reply: '+method)
    finally:
        if process.poll() is None: process.terminate()
        try: process.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            process.kill(); process.communicate()

def refresh():
    executable = next((path for path in (Path('/usr/bin/ls-control'),Path('/usr/sbin/ls-control')) if path.is_file()),None)
    if executable is None: raise ValueError('ls-control unavailable')
    subprocess.run([str(executable),'scan-services'],check=True,timeout=15,
                   stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    return {'returnValue':True,'operation':'scan-services','effective_registration_verified':False}

def finalize():
    expected = json.loads(secure(STATE/'recovery-provision.pending.json'))
    if manifest() != expected: raise ValueError('Runtime changed since provisioning')
    reply = rpc('status')
    if reply.get('root') is not True:
        raise ValueError('Recovery callback process is not root')
    reply = rpc('register')
    if reply.get('root') is not True or reply.get('registered') is not True or reply.get('activityName') != NAME+'.recovery':
        raise ValueError('Recovery activity not verified')
    write(STATE/'recovery-provision.json',encoded(expected))
    return {'returnValue':True,'mode':'recovery-only','activity':reply}

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
        return {'returnValue':True,'already_rolled_back':True,'next':'Refresh LS2 registration before package removal.'}
    if saved.get('phase') not in (None, 'restoring'):
        raise ValueError('Unknown provisioning phase')
    if saved.get('phase') == 'restoring' and os.path.lexists(STATE/'recovery-provision.json'):
        raise ValueError('Unexpected readiness during rollback')
    # Refuse any drift before canceling activity or touching files. A partial apply
    # can contain original or installed bytes, both exactly recorded here.
    for path, entry in saved['files'].items():
        if sha(entry['original'].encode()) != entry['original_sha256'] or sha(secure(Path(path))) not in (entry['original_sha256'],entry['installed_sha256']):
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
    parser.add_argument('command', choices=['plan','apply','refresh','finalize','rollback'])
    command = parser.parse_args().command
    if os.geteuid() != 0 and command != 'plan': raise ValueError('Root required')
    if command == 'plan':
        print(json.dumps({'service':NAME,'files':{k:str(v) for k,v in FILES.items()},
                          'runner':str(RUNNER),'activity':json.loads((Path(__file__).parent/'service/activity.json').read_text()),
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
