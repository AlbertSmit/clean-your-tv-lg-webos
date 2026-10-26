"""Inline, fixed-path startup-link validation for self-contained TV removal scripts."""
HELPER = r'''
def hook_read(path,state,hook,app,installed,expected):
    for parent in (path.parent,*path.parent.parents):
        info=parent.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid not in (0,os.geteuid())
                or (info.st_mode&0o022 and not info.st_mode&stat.S_ISVTX)):raise ValueError('Startup ownership conflict')
    item=path.lstat()
    private=('#!/bin/sh\nunset NODE_OPTIONS NODE_PATH PYTHONHOME PYTHONPATH\nexec /usr/bin/node '+str(state/'code/python_boot.js')+' '+str(state)+' '+str(state/'code/startup_guard.py')+' '+app+'\n').encode()
    wrapper=dict(version=3,path=str(hook),owner_app=app,sha256=hashlib.sha256(private).hexdigest())
    if not stat.S_ISLNK(item.st_mode):
        raw=read(path)
        if raw!=private:return raw
        if json.loads(read(state/'startup-hook.json'))!=wrapper or stat.S_IMODE(item.st_mode)!=0o700:raise ValueError('Startup ownership conflict')
        return expected
    target=installed/'applications'/app/'startup.sh'
    hashes={'com.cleanyourtv.root.updater': '7c186b2f6ed43136015a163593d7c0b7133998e0d2364a91038942fdb56063d3', 'com.cleanyourtv.system.updater': '8d7e5031eee61e7720113bbd90fea1a7113452fb553d1b1daf98064d4ca1069e'}
    shape=dict(version=2,path=str(hook),target=str(target),owner_app=app,target_sha256=hashes[app])
    receipt=json.loads(read(state/'startup-hook.json'))
    if receipt==wrapper:receipt=json.loads(read(state/'startup-hook.previous.json'))
    if receipt!=shape or item.st_uid!=os.geteuid() or os.readlink(path)!=str(target):raise ValueError('Startup ownership conflict')
    return expected

'''
