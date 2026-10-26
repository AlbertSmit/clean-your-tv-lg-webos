"""Private boot entry: shared package identity is DATA, never executable input."""
import json
import os
from pathlib import Path
import subprocess
import sys
from package_data import read

OWNERS={'com.cleanyourtv.root.preview':Path('/var/lib/clean-your-tv-root'),
        'com.cleanyourtv.root.updater':Path('/var/lib/clean-your-tv-root-updater'),
        'com.cleanyourtv.system.updater':Path('/var/lib/clean-your-tv-system-updater')}
INSTALLED=Path('/media/developer/apps')


def present(owner):
    try:
        info=json.loads(read(INSTALLED/'usr/palm/applications'/owner/'appinfo.json',installed=INSTALLED))
        return isinstance(info,dict) and info.get('id')==owner and info.get('type')=='web'
    except (OSError,ValueError,TypeError):return False


def start(owner):
    if owner not in OWNERS:raise ValueError('Foreign startup owner')
    if not present(owner):return False
    state=OWNERS[owner]
    if owner=='com.cleanyourtv.root.preview':
        subprocess.run(['/bin/sh',str(state/'service/boot-recover.sh'),'mark'],check=True)
    else:
        code=state/'code'
        runner='run-system-updater.py' if owner=='com.cleanyourtv.system.updater' else 'run-updater.py'
        subprocess.Popen(['/usr/bin/node',str(code/'python_boot.js'),str(state),str(code/runner),'worker'],
                         stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                         start_new_session=True,close_fds=True)
    return True


if __name__=='__main__':
    if os.geteuid()!=0 or len(sys.argv)!=2:raise SystemExit('Root owner boot required')
    start(sys.argv[1])
