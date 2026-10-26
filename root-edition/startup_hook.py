"""Private guarded startup wrappers. Legacy receipts authorize migration/removal only."""
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

HOOK = Path('/var/lib/webosbrew/init.d/50-clean-your-tv-root')
STATE = Path('/var/lib/clean-your-tv-root')
INSTALLED = Path('/media/developer/apps')
EXPECTED_UID = 0
OWNERS = {'com.cleanyourtv.root.preview':'/var/lib/clean-your-tv-root',
          'com.cleanyourtv.root.updater':'/var/lib/clean-your-tv-root-updater',
          'com.cleanyourtv.system.updater':'/var/lib/clean-your-tv-system-updater'}
CONTENT = b'#!/bin/sh\nexec /usr/bin/python3 /var/lib/clean-your-tv-root/runtime/boot_gate.py mark\n'


def managed_content():
    return ('#!/bin/sh\nexec /bin/sh '+str(STATE/'service/boot-recover.sh')+' mark\n').encode()


def previous_managed_content():
    return ('#!/bin/sh\nexec '+str(STATE/'python-launcher')+' /var/lib/clean-your-tv-root/runtime/boot_gate.py mark\n').encode()


def packaged_content(owner):
    state=OWNERS[owner]
    app='/media/developer/apps/usr/palm/applications/'+owner
    prefix='#!/bin/sh\nset -eu\nunset NODE_OPTIONS NODE_PATH\n[ "$#" -eq 0 ] || exit 2\n[ -f '+app+'/appinfo.json ] || exit 0\n'
    if owner=='com.cleanyourtv.root.preview':
        return (prefix+'[ -f '+state+'/service/boot-recover.sh ] || exit 0\nexec /bin/sh '+state+'/service/boot-recover.sh mark\n').encode()
    runner='run-system-updater.py' if owner=='com.cleanyourtv.system.updater' else 'run-updater.py'
    return (prefix+'[ -f '+state+'/code/python_boot.js ] || exit 0\n[ -f '+state+'/code/'+runner+' ] || exit 0\n/usr/bin/node '+state+'/code/python_boot.js '+state+' '+state+'/code/'+runner+' worker </dev/null >/dev/null 2>&1 &\n').encode()


def trusted_directory(path):
    for parent in (path,*path.parents):
        info=parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid!=EXPECTED_UID or info.st_mode&0o022:
            raise ValueError('Unsafe startup hook directory')


def regular(path, secure):
    trusted_directory(path.parent)
    info=path.lstat()
    if (not stat.S_ISREG(info.st_mode) or info.st_uid!=EXPECTED_UID
            or info.st_nlink!=1 or info.st_mode&0o022):raise ValueError('Unsafe startup hook file')
    return secure(path)


def target_path(owner):
    if owner not in OWNERS:raise ValueError('Foreign startup owner')
    return INSTALLED/'usr/palm/applications'/owner/'startup.sh'


def target_receipt(secure,hook,owner,missing=False):
    # Saved exact v2 shape authorizes unlink/migration without trusting its target.
    return dict(version=2,path=str(hook),target=str(target_path(owner)),owner_app=owner,
                target_sha256=hashlib.sha256(packaged_content(owner)).hexdigest())


def private_content(owner):
    if owner not in OWNERS:raise ValueError('Foreign startup owner')
    state=OWNERS[owner];code=state if owner=='com.cleanyourtv.root.preview' else state+'/code'
    return ('#!/bin/sh\nunset NODE_OPTIONS NODE_PATH PYTHONHOME PYTHONPATH\n'
            'exec /usr/bin/node '+code+'/python_boot.js '+state+' '+code+'/startup_guard.py '+owner+'\n').encode()


def private_receipt(hook,owner):
    return dict(version=3,path=str(hook),owner_app=owner,sha256=hashlib.sha256(private_content(owner)).hexdigest())


def legacy_receipt(saved,hook,legacy):
    if (not isinstance(saved,dict) or set(saved)!={'version','path','content'}
            or type(saved.get('version')) is not int or saved['version']!=1
            or saved.get('path')!=str(hook) or saved.get('content') not in [b.decode() for b in legacy]):
        raise ValueError('Unexpected startup hook receipt')
    return saved['content'].encode()


def verify_link(hook,saved):
    info=hook.lstat()
    if (not stat.S_ISLNK(info.st_mode) or info.st_uid!=EXPECTED_UID
            or os.readlink(hook)!=saved['target']):raise ValueError('Startup hook drift')


def owned_legacy(owner,state):
    if owner=='com.cleanyourtv.root.preview':return (CONTENT,managed_content(),previous_managed_content())
    if owner not in OWNERS:raise ValueError('Foreign startup owner')
    code=Path(state)/'code';runner='run-system-updater.py' if owner=='com.cleanyourtv.system.updater' else 'run-updater.py'
    tail=' '+str(code/runner)+' worker </dev/null >/dev/null 2>&1 &\n'
    return (('#!/bin/sh\n/usr/bin/python3'+tail).encode(),
            ('#!/bin/sh\nunset NODE_OPTIONS NODE_PATH\n/usr/bin/node '+str(code/'python_boot.js')+' '+str(state)+tail).encode())


def verify_previous(saved,hook,owner,legacy):
    if not isinstance(saved,dict) or type(saved.get('version')) is not int:raise ValueError('Unexpected previous startup receipt')
    if saved['version']==1:legacy_receipt(saved,hook,legacy)
    elif saved!=target_receipt(None,hook,owner):raise ValueError('Unexpected previous startup receipt')


def verify_existing(secure,state,hook,owner,legacy,saved):
    if not isinstance(saved,dict) or type(saved.get('version')) is not int:raise ValueError('Unexpected startup hook receipt')
    if saved['version']==1:
        content=legacy_receipt(saved,hook,legacy)
        if os.path.lexists(hook) and (regular(hook,secure)!=content or stat.S_IMODE(hook.lstat().st_mode)!=0o700):raise ValueError('Startup hook drift')
        return
    expected=target_receipt(None,hook,owner) if saved['version']==2 else private_receipt(hook,owner)
    if saved!=expected:raise ValueError('Unexpected startup hook receipt')
    if not os.path.lexists(hook):return
    if saved['version']==2 and stat.S_ISLNK(hook.lstat().st_mode):verify_link(hook,saved);return
    if saved['version']==3 and not hook.is_symlink() and regular(hook,secure)==private_content(owner) and stat.S_IMODE(hook.lstat().st_mode)==0o700:return
    # A new receipt is durable before hook replacement. Exact prior proof survives.
    previous=json.loads(regular(state/'startup-hook.previous.json',secure))
    if previous.get('version') not in (1,2) or previous==saved:raise ValueError('Unexpected previous startup receipt')
    verify_existing(secure,state,hook,owner,legacy,previous)


def install_link(secure,write,state,hook,owner,legacy=()):
    state,hook=Path(state),Path(hook)
    legacy=legacy or owned_legacy(owner,state)
    trusted_directory(hook.parent)
    receipt=state/'startup-hook.json'
    saved=json.loads(regular(receipt,secure)) if os.path.lexists(receipt) else None
    if os.path.lexists(state/'startup-hook.previous.json'):
        if saved is None:raise ValueError('Previous startup receipt without ownership')
        verify_previous(json.loads(regular(state/'startup-hook.previous.json',secure)),hook,owner,legacy)
    if saved is not None:verify_existing(secure,state,hook,owner,legacy,saved)
    elif os.path.lexists(hook):raise ValueError('Startup hook name collision')
    value=private_receipt(hook,owner)
    if saved==value and os.path.lexists(hook) and not hook.is_symlink():return
    from package_data import read
    info=json.loads(read(target_path(owner).parent/'appinfo.json',installed=INSTALLED,uid=EXPECTED_UID))
    if not isinstance(info,dict) or info.get('id')!=owner:raise ValueError('Startup owner identity changed')
    if saved and saved.get('version') in (1,2):
        previous=state/'startup-hook.previous.json'
        proof=saved
        if os.path.lexists(previous):
            prior=json.loads(regular(previous,secure))
            # v2 publication may itself have been interrupted over a v1 hook.
            if saved['version']==2 and os.path.lexists(hook) and not hook.is_symlink():
                legacy_receipt(prior,hook,legacy);proof=prior
            elif prior!=saved:
                legacy_receipt(prior,hook,legacy)
        write(previous,json.dumps(proof))
    write(receipt,json.dumps(value))
    fd,name=tempfile.mkstemp(dir=hook.parent,prefix='.cytv-startup-')
    try:
        with os.fdopen(fd,'wb') as output:
            os.fchmod(output.fileno(),0o700);output.write(private_content(owner));output.flush();os.fsync(output.fileno())
        os.replace(name,hook)
        directory=os.open(hook.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.lexists(name):os.unlink(name)


def remove_link(secure,state,hook,owner,legacy=()):
    state,hook=Path(state),Path(hook)
    legacy=legacy or owned_legacy(owner,state)
    receipt=state/'startup-hook.json'
    if not os.path.lexists(receipt):return
    trusted_directory(hook.parent)
    saved=json.loads(regular(receipt,secure))
    verify_existing(secure,state,hook,owner,legacy,saved)
    if os.path.lexists(hook):hook.unlink()
    # Both receipts survive interrupted/repeated removal.


def install(secure,write):
    install_link(secure,write,STATE,HOOK,'com.cleanyourtv.root.preview',
                 (CONTENT,managed_content(),previous_managed_content()))


def remove(secure):
    remove_link(secure,STATE,HOOK,'com.cleanyourtv.root.preview',
                (CONTENT,managed_content(),previous_managed_content()))
