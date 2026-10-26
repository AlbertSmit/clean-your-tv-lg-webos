"""Inline, fixed-path startup-link validation for self-contained TV removal scripts."""
HELPER = r'''
def hook_read(path,state,hook,app,installed,expected):
    if not stat.S_ISLNK(path.lstat().st_mode):return read(path)
    for parent in (path.parent,*path.parent.parents):
        info=parent.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid not in (0,os.geteuid())
                or (info.st_mode&0o022 and not info.st_mode&stat.S_ISVTX)):raise ValueError('Startup ownership conflict')
    target=installed/'applications'/app/'startup.sh'
    hashes={'com.cleanyourtv.root.updater': '7c186b2f6ed43136015a163593d7c0b7133998e0d2364a91038942fdb56063d3', 'com.cleanyourtv.system.updater': '8d7e5031eee61e7720113bbd90fea1a7113452fb553d1b1daf98064d4ca1069e'}
    shape=dict(version=2,path=str(hook),target=str(target),owner_app=app,target_sha256=hashes[app])
    receipt=json.loads(read(state/'startup-hook.json'))
    if receipt!=shape or path.lstat().st_uid!=os.geteuid() or os.readlink(path)!=str(target):raise ValueError('Startup ownership conflict')
    if os.path.lexists(target):
        for parent in (target.parent,*target.parent.parents):
            info=parent.lstat()
            if (not stat.S_ISDIR(info.st_mode) or info.st_uid not in (0,os.geteuid())
                    or (info.st_mode&0o022 and not info.st_mode&stat.S_ISVTX)):raise ValueError('Startup ownership conflict')
        if hashlib.sha256(read(target)).hexdigest()!=hashes[app] or json.loads(read(target.parent/'appinfo.json')).get('id')!=app:raise ValueError('Startup ownership conflict')
    return expected

'''
