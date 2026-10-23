"""Observe PID 1 independently, before shutdown makes synchronous queries stall."""
import json
import os
import subprocess
import tempfile
import threading
import time
import device_adapter as d
import persistent_health as health


def query():
    try:
        result = subprocess.run(['/usr/bin/systemctl','is-system-running'],
            stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
            timeout=.5,universal_newlines=True)
        return result.stdout.strip() == 'stopping'
    except (OSError,subprocess.TimeoutExpired): return False


def record(transaction):
    from intent_runtime import boot_identity
    try:health.ROOT.mkdir(mode=0o700)
    except FileExistsError:pass
    d.trusted_dir(health.ROOT)
    fd,name=tempfile.mkstemp(dir=health.ROOT,prefix='.shutdown-')
    try:
        with os.fdopen(fd,'w') as out:
            json.dump(dict(transaction=transaction,boot=boot_identity(),issued=time.monotonic()),out)
        os.replace(name,health.path(transaction).with_suffix('.shutdown'))
    finally:
        if os.path.exists(name):os.unlink(name)


def stopping(transaction=None):
    if transaction is not None:
        try:
            from intent_runtime import boot_identity
            d.trusted_dir(health.ROOT)
            v=d.safe_json(health.path(transaction).with_suffix('.shutdown'))
            from persistent_lease import finite
            if (v.get('transaction') == transaction and v.get('boot') == boot_identity()
                    and finite(v.get('issued')) and 0 <= time.monotonic()-v['issued'] < 5):
                return True
        except (OSError,ValueError):pass
    return query()


def monitor(transaction):
    stop=threading.Event()
    def observe():
        while not stop.is_set():
            try:
                if query():record(transaction)
            except (OSError,ValueError):pass  # Unknown never authorizes preserving intent.
            stop.wait(.25)
    threading.Thread(target=observe,daemon=True).start()
    return stop
