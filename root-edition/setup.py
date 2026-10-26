#!/usr/bin/env python3
"""Explicit SSH host controller for an offline Root candidate bundle."""
import argparse
from pathlib import Path
import re
import shlex
import subprocess
import tempfile
import uuid


def ssh_options(alias, identity=None):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', alias):
        raise ValueError('Use a single explicit OpenSSH host alias')
    options = ['-o', 'StrictHostKeyChecking=yes', '-o', 'BatchMode=yes', '-o', 'ConnectTimeout=10']
    if identity is not None:
        options += ['-i', str(Path(identity).expanduser().resolve())]
    return options + [alias]


def bundle_bytes(path, limit=32*1024*1024):
    """Portable host-side read; TV bootstrap retains its strict safe_bytes reader."""
    from deploy import checked_file
    path=Path(path);raw=checked_file(path.parent,path.name)
    if len(raw)>limit:raise ValueError('Oversized bundle file')
    return raw


def execute_product(action, alias, root_bundle, updater_bundle, identity=None, run=subprocess.run,
                    operation=None, migrate=False, python=None, resume=False):
    """Maintained host product entry: fixed coordinator, durable request, no runtime upload."""
    import hashlib,json
    from deploy import checked_file
    from python_binding import launcher_bytes
    selected='/usr/bin/python3' if python is None else python;launcher_bytes(selected)
    if action not in ('install','remove','status','inspect','restore'):raise ValueError('Unsupported product action')
    if operation is None and action in ('install','remove'):operation=uuid.uuid4().hex
    if action in ('install','remove','status') and (not isinstance(operation,str) or not re.fullmatch('[a-f0-9]{32}',operation)):raise ValueError('Product operation UUID required')
    options=ssh_options(alias,identity);folders={'root':Path(root_bundle),'root-updater':Path(updater_bundle)}
    manifests={};hashes={}
    for name,folder in folders.items():
        raw=checked_file(folder,'bundle.json');manifest=json.loads(raw)
        if not isinstance(manifest.get('files'),dict) or not manifest['files']:raise ValueError('Invalid product bundle')
        for relative,digest in manifest['files'].items():
            if hashlib.sha256(checked_file(folder,relative)).hexdigest()!=digest:raise ValueError('Product bundle integrity mismatch')
        manifests[name]=manifest;hashes[name]=hashlib.sha256(raw).hexdigest()
    candidate=hashlib.sha256(json.dumps(hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    remote='/tmp/cytv-product-'+uuid.uuid4().hex
    run(['ssh',*options,'umask 077; test "$(id -u)" = 0 && mkdir '+shlex.quote(remote)],check=True,stdin=subprocess.DEVNULL)
    with tempfile.TemporaryDirectory(prefix='cytv-product-') as tmp:
        local=Path(tmp)
        for name,folder in folders.items():
            for relative in (*manifests[name]['files'],'bundle.json'):
                target=local/name/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(checked_file(folder,relative))
        run(['scp','-O',*options[:-1],'-r',str(local/'root'),str(local/'root-updater'),alias+':'+remote+'/'],check=True,stdin=subprocess.DEVNULL)
    argv=[selected,remote+'/root-updater/install_driver.py',action,'--payload',remote,'--candidate',candidate]
    if action=='status':argv.append('--verify-current')
    if operation:argv+=['--operation',operation]
    if migrate:argv.append('--migrate-packaged-home')
    if resume:argv.append('--resume')
    command='unset PYTHONHOME PYTHONPATH; export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1; exec '+shlex.join(argv)
    return run(['ssh',*options,command],check=True,stdin=subprocess.DEVNULL)


def execute(action, alias, bundle=None, identity=None, run=subprocess.run, migrate=False, transaction=None, python=None, updater_bundle=None, operation=None, resume=False, component_only=False):
    if action=='install' and not component_only:
        if bundle is None or updater_bundle is None:raise ValueError('Product install requires --bundle and --updater-bundle; --component-only is an explicit low-level recovery tool')
        return execute_product('install',alias,bundle,updater_bundle,identity,run,operation,migrate,python,resume)
    if updater_bundle is not None and action in ('status','restore','uninstall'):
        return execute_product('remove' if action=='uninstall' else action,alias,bundle,updater_bundle,identity,run,operation,False,python,resume)
    if action not in ('install', 'status', 'trial', 'emergency-trial', 'intent-trial', 'enable', 'confirm', 'restore', 'uninstall'):
        raise ValueError('Unsupported action')
    if migrate and action != 'install':
        raise ValueError('Migration is only available with install')
    if action == 'confirm' and (not transaction or not re.fullmatch(r'[0-9a-f-]{36}',transaction)):
        raise ValueError('confirm requires the trial transaction ID')
    from python_binding import launcher_bytes
    selected = '/usr/bin/python3' if python is None else python
    launcher_bytes(selected)  # Whitelist before any SSH or staging mutation.
    options = ssh_options(alias, identity)
    remote_driver = '/var/lib/clean-your-tv-root/deploy.py'
    if action == 'install':
        from deploy import verify_bundle, checked_file
        if bundle is None: raise ValueError('install requires --bundle')
        bundle = Path(bundle).resolve()
        manifest = verify_bundle(bundle)
        staging = '/tmp/clean-your-tv-root-' + uuid.uuid4().hex
        # An exclusive, root-owned remote staging directory. No remote shell input
        # is derived from an application ID, profile, or unvalidated alias.
        remote = 'umask 077; test "$(id -u)" = 0 && mkdir ' + shlex.quote(staging)
        run(['ssh', *options, remote], check=True, stdin=subprocess.DEVNULL)
        with tempfile.TemporaryDirectory(prefix='root-bundle-') as temporary:
            local = Path(temporary)
            for name in (*manifest['files'], 'bundle.json'):
                target = local / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(checked_file(bundle, name))
            run(['scp', '-O', *options[:-1], '-r', *[str(p) for p in sorted(local.iterdir())], alias + ':' + staging + '/'],
                check=True, stdin=subprocess.DEVNULL)
        remote_driver = staging + '/deploy.py'
        argv = [selected, remote_driver, 'install', '--bundle', staging]
        if migrate:
            argv.append('--migrate-packaged-home')
        command = shlex.join(argv)
    else:
        argv = [selected, remote_driver, action]
        if action == 'confirm': argv += ['--transaction',transaction]
        command = shlex.join(argv)
    if selected != '/usr/bin/python3':
        command = 'unset PYTHONHOME PYTHONPATH; export PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1; exec '+command
    return run(['ssh', *options, command], check=True, stdin=subprocess.DEVNULL)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('install', 'status', 'trial', 'emergency-trial', 'intent-trial', 'enable', 'confirm', 'restore', 'uninstall'))
    parser.add_argument('--ssh', required=True, help='Explicit, preconfigured OpenSSH alias')
    parser.add_argument('--transaction')
    parser.add_argument('--python', help='Already-provisioned, pinned TV interpreter path')
    parser.add_argument('--identity', type=Path)
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--updater-bundle',type=Path,help='Verified Root Updater bundle for shared product setup')
    parser.add_argument('--operation',help='Original 32-hex shared product UUID')
    parser.add_argument('--resume',action='store_true',help='Explicit continuation of that product request')
    parser.add_argument('--component-only',action='store_true',help='Low-level component install for deliberate recovery only')
    parser.add_argument('--migrate-packaged-home', action='store_true', help='Copy installed Home packaged preferences only; excludes browser storage')
    args = parser.parse_args()
    execute(args.command, args.ssh, args.bundle, args.identity, migrate=args.migrate_packaged_home,transaction=args.transaction,python=args.python,updater_bundle=args.updater_bundle,operation=args.operation,resume=args.resume,component_only=args.component_only)


if __name__ == '__main__':
    main()
