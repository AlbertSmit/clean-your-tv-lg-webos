"""Detached bounded timer; no activation or profile publication."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import device_adapter as d
from profile_guardian import watch


def ready(transaction, deadline):
    try: start_ticks=d.process_start(os.getpid())
    except OSError: start_ticks=None  # Non-Linux fixture; never accepted as live TV guardian.
    fd, name = tempfile.mkstemp(dir=d.STATE, prefix='.profile-ready-')
    try:
        with os.fdopen(fd,'w') as f:
            json.dump({'transaction':transaction,'deadline':deadline,'pid':os.getpid(),'start_ticks':start_ticks},f)
            f.flush(); os.fsync(f.fileno())
        os.replace(name,d.STATE/'profile-guardian-ready.json'); d.sync(d.STATE)
    finally:
        if os.path.exists(name): os.unlink(name)


def restore(transaction):
    for attempt in range(12):
        try:
            from persistent_recovery import bound_exit
            bound = bound_exit(transaction)
            result = 'restored' if bound is True else d.restore_once(expected_transaction=transaction)
        except Exception as exc:
            print(str(exc),flush=True); result='recovering'
        if result not in ('pending','recovering'): return result
        time.sleep(5)
    return 'recovering'


def run(transaction):
    d.trusted_dir(d.STATE)
    return watch(transaction, lambda:d.safe_json(d.STATE/'profile-trial.json'),
                 ready,restore,time.monotonic,time.sleep)


if __name__ == '__main__':
    if os.geteuid()!=0 or len(sys.argv)!=2: raise SystemExit('Root and transaction required')
    print(run(sys.argv[1]),flush=True)
