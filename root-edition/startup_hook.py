"""Exact package-owned startup links. Legacy receipts authorize migration/removal only."""
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
    target=target_path(owner)
    expected=packaged_content(owner)
    value=dict(version=2,path=str(hook),target=str(target),owner_app=owner,
               target_sha256=hashlib.sha256(expected).hexdigest())
    if missing and not os.path.lexists(target):return value
    if regular(target,secure)!=expected or stat.S_IMODE(target.lstat().st_mode)!=0o755:raise ValueError('Startup target changed')
    info=json.loads(regular(target.parent/'appinfo.json',secure))
    if info.get('id')!=owner:raise ValueError('Startup owner identity changed')
    return value


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


def verify_existing(secure,state,hook,owner,legacy,saved):
    if not isinstance(saved,dict):raise ValueError('Unexpected startup hook receipt')
    if saved.get('version')==1:
        content=legacy_receipt(saved,hook,legacy)
        if os.path.lexists(hook) and (regular(hook,secure)!=content or stat.S_IMODE(hook.lstat().st_mode)!=0o700):
            raise ValueError('Startup hook drift')
        return
    if type(saved.get('version')) is not int or saved!=target_receipt(secure,hook,owner,missing=True):raise ValueError('Unexpected startup hook receipt')
    if not os.path.lexists(hook):return
    if stat.S_ISLNK(hook.lstat().st_mode):verify_link(hook,saved);return
    # Receipt publication precedes atomic replacement; a crash retains both proofs.
    previous=json.loads(regular(state/'startup-hook.previous.json',secure))
    content=legacy_receipt(previous,hook,legacy)
    if regular(hook,secure)!=content or stat.S_IMODE(hook.lstat().st_mode)!=0o700:raise ValueError('Startup hook drift')


def install_link(secure,write,state,hook,owner,legacy=()):
    state,hook=Path(state),Path(hook)
    trusted_directory(hook.parent)
    receipt=state/'startup-hook.json'
    saved=json.loads(regular(receipt,secure)) if os.path.lexists(receipt) else None
    if saved is not None:verify_existing(secure,state,hook,owner,legacy,saved)
    elif os.path.lexists(hook):raise ValueError('Startup hook name collision')
    value=target_receipt(secure,hook,owner)
    if saved==value and os.path.lexists(hook) and hook.is_symlink():return
    if saved and saved.get('version')==1:
        previous=state/'startup-hook.previous.json'
        if os.path.lexists(previous):
            if json.loads(regular(previous,secure))!=saved:raise ValueError('Previous startup receipt conflict')
        else:write(previous,json.dumps(saved))
    write(receipt,json.dumps(value))
    fd,name=tempfile.mkstemp(dir=hook.parent,prefix='.cytv-startup-')
    os.close(fd);os.unlink(name)
    try:
        os.symlink(value['target'],name)
        os.replace(name,hook)
        directory=os.open(hook.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
        try:os.fsync(directory)
        finally:os.close(directory)
    finally:
        if os.path.lexists(name):os.unlink(name)


def remove_link(secure,state,hook,owner,legacy=()):
    state,hook=Path(state),Path(hook)
    receipt=state/'startup-hook.json'
    if not os.path.lexists(receipt):return
    trusted_directory(hook.parent)
    saved=json.loads(regular(receipt,secure))
    verify_existing(secure,state,hook,owner,legacy,saved)
    if os.path.lexists(hook):hook.unlink()
    # Both receipts survive interrupted/repeated removal.


def install(secure,write):
    install_link(secure,write,STATE,HOOK,'com.cleanyourtv.root.preview',
                 (CONTENT,managed_content()))


def remove(secure):
    remove_link(secure,STATE,HOOK,'com.cleanyourtv.root.preview',
                (CONTENT,managed_content(),previous_managed_content()))
