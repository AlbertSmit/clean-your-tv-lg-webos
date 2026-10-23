"""Serialize activation with updater reservation; explicit recovery stays available."""
from contextlib import contextmanager
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import tempfile

STATE = Path('/var/lib/clean-your-tv-root')


@contextmanager
def locked(root,uid):
    for p in (root,*root.parents):
        st=p.lstat()
        # Ancestors such as /tmp may be sticky. The private state itself may not.
        if not stat.S_ISDIR(st.st_mode) or (p==root and (st.st_uid!=uid or st.st_mode & 0o022)):
            raise ValueError('Unsafe routing lock directory')
    fd=os.open(root/'software-update.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW|os.O_NONBLOCK,0o600)
    try:
        st=os.fstat(fd)
        if not stat.S_ISREG(st.st_mode) or st.st_uid!=uid or st.st_nlink!=1 or st.st_mode & 0o022:raise ValueError('Unsafe routing lock')
        fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
        yield
    finally:os.close(fd)


@contextmanager
def control(root=STATE,uid=0):
    root=Path(root)
    with locked(root,uid):
        if os.path.lexists(root/'update-block.json'):raise RuntimeError('Software update pending; use Root Updater Recovery before enabling Root')
        yield


def read(path,uid):
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
    with os.fdopen(fd) as f:
        st=os.fstat(f.fileno())
        if not stat.S_ISREG(st.st_mode) or st.st_uid!=uid or st.st_nlink!=1 or st.st_size>1024 or st.st_mode & 0o022:raise ValueError('Unsafe reservation')
        return json.load(f)


def sync(root):
    fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:os.fsync(fd)
    finally:os.close(fd)


def reserve(transaction,root=STATE,uid=0):
    if not isinstance(transaction,str) or not re.fullmatch('[a-f0-9]{32}',transaction):raise ValueError('Invalid update identity')
    root=Path(root)
    with locked(root,uid):
        p=root/'update-block.json';value={'transaction':transaction}
        if os.path.lexists(p):
            if read(p,uid)!=value:raise ValueError('Another update owns routing')
            return
        fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'w') as f:json.dump(value,f);f.flush();os.fsync(f.fileno())
        sync(root)


def release(transaction,root=STATE,uid=0):
    root=Path(root)
    with locked(root,uid):
        p=root/'update-block.json'
        if not os.path.lexists(p):return
        if read(p,uid)!={'transaction':transaction}:raise ValueError('Reservation owner mismatch')
        p.unlink();sync(root)
