"""Own exactly one normal-boot marker hook; never edit Homebrew startup code."""
import json
import os
from pathlib import Path

HOOK = Path('/var/lib/webosbrew/init.d/50-clean-your-tv-root')
STATE = Path('/var/lib/clean-your-tv-root')
CONTENT = b'#!/bin/sh\nexec /usr/bin/python3 /var/lib/clean-your-tv-root/runtime/boot_gate.py mark\n'


def install(secure, write):
    receipt=STATE/'startup-hook.json'
    import stat
    for parent in (HOOK.parent, *HOOK.parent.parents):
        info=parent.lstat()
        if not stat.S_ISDIR(info.st_mode) or info.st_uid != 0 or info.st_mode & 0o022:
            raise ValueError('Unsafe startup hook directory')
    # Existing names are never adopted, even if their bytes happen to match.
    if os.path.lexists(receipt):
        saved=json.loads(secure(receipt))
        if saved != {'version':1,'path':str(HOOK),'content':CONTENT.decode()}:
            raise ValueError('Unexpected startup hook receipt')
        if os.path.lexists(HOOK):
            if secure(HOOK) != CONTENT or stat.S_IMODE(HOOK.stat().st_mode) != 0o700:
                raise ValueError('Startup hook drift')
            return
    else:
        if os.path.lexists(HOOK): raise ValueError('Startup hook name collision')
        write(receipt,json.dumps({'version':1,'path':str(HOOK),'content':CONTENT.decode()}))
    write(HOOK,CONTENT,0o700)


def remove(secure):
    receipt=STATE/'startup-hook.json'
    if not os.path.lexists(receipt): return
    saved=json.loads(secure(receipt))
    if saved != {'version':1,'path':str(HOOK),'content':CONTENT.decode()}:
        raise ValueError('Unexpected startup hook receipt')
    if os.path.lexists(HOOK):
        if secure(HOOK) != CONTENT: raise ValueError('Startup hook drift')
        HOOK.unlink()
    # Retain ownership evidence for interrupted/repeated uninstall.
