"""Copy packaged preferences from the user's existing Home into the isolated UI.

Never evaluates JavaScript or reads browser databases. This is explicit migration
from an installed trusted launcher, not an importer for arbitrary downloaded JS.
"""
import os
from pathlib import Path, PurePosixPath
import re
import stat

APP='com.cleanyourtv.root.preview'

def prepare(source):
    source=Path(source)
    if source.is_symlink() or not source.is_dir():raise ValueError('Invalid source directory')
    # Installed developer assets can retain desktop ownership/modes. Treat them
    # strictly as UI data; never evaluate or import them in a root process.
    def read(name,limit):
        p=source/name
        if any(x.is_symlink() for x in (p,*p.parents)):
            raise ValueError('Indirect source')
        fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK)
        with os.fdopen(fd,'rb') as stream:
            before=os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode) or before.st_size>limit:
                raise ValueError('Invalid packaged data file')
            data=stream.read(limit+1);after=os.fstat(stream.fileno())
            if len(data)>limit or (before.st_size,before.st_mtime_ns,before.st_ctime_ns)!=(after.st_size,after.st_mtime_ns,after.st_ctime_ns):
                raise ValueError('Source changed')
            return data
    apps=read('apps.js',4*1024*1024);config=read('config.js',1024*1024)
    if b'window.TV_APPS' not in apps or b'window.CONFIG' not in config:
        raise ValueError('Unexpected packaged preferences')
    files={'apps.js':apps,'config.js':config+b'\nwindow.CONFIG.hiddenApps=(window.CONFIG.hiddenApps||[]).concat(["'+APP.encode()+b'"]);\n'}
    icons=set(re.findall(r'''["'](icons/[^"']+)["']''',apps.decode('utf-8')))
    if len(icons)>200:raise ValueError('Too many icons')
    for name in sorted(icons):
        p=PurePosixPath(name)
        if len(p.parts)!=2 or '..' in p.parts or '\\' in name or p.suffix.lower() not in ('.png','.jpg','.jpeg','.webp'):
            raise ValueError('Invalid icon path')
        files[name]=read(name,256*1024)
    if sum(map(len,files.values()))>16*1024*1024:raise ValueError('Profile too large')
    return files
