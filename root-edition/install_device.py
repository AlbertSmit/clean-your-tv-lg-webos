"""Bounded local webOS adapter for the shared product coordinator.

This module executes bundled code only. Retained code is hashed as data before
using its receipts; no module is imported from a retained installation.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from installation import classify, device_snapshot, read_journal
from updater.package import safe_bytes, inspect_package, verify_payload, members
from updater.store import Store

ROOT=Path('/var/lib/clean-your-tv-root')
UPDATER=Path('/var/lib/clean-your-tv-root-updater')
SUPERVISOR=Path('/var/lib/clean-your-tv-system-updater')
INSTALLED=Path('/media/developer/apps')
APP='com.cleanyourtv.root.preview'


def checked_store(path, uid=0):
    # Read-only inspection must never provision a state directory.
    store=Store.__new__(Store);store.root=str(path);store.uid=uid
    return store


def sha(raw): return hashlib.sha256(raw).hexdigest()


def verify_package_modes(raw, installed):
    import io
    import stat
    import tarfile
    with tarfile.open(fileobj=io.BytesIO(members(raw)['data.tar.gz']),mode='r:gz') as tar:
        for member in tar:
            # inspect_package/archive validated paths and regular-file types first.
            if member.isfile():
                info=(Path(installed)/member.name).stat()
                if stat.S_IMODE(info.st_mode)&0o7111 != member.mode&0o7111:
                    raise ValueError('installed_executable_mode_mismatch')


def current_root(root=ROOT, updater=UPDATER, installed=INSTALLED, uid=0):
    """Verify current trusted descriptors and mutable profile separately."""
    from updater.device import Device
    from updater.profile import validate
    from updater.store import encode
    store=checked_store(updater,uid)
    device=Device(store,code=updater/'code',root_state=root,installed=installed)
    device.integrity()
    descriptor=store.read('current')
    device.descriptor(descriptor)
    raw=safe_bytes(device.cached(descriptor),uid=uid)
    verify_payload(installed,inspect_package(raw,descriptor))
    verify_package_modes(raw,installed)
    tx=store.read('transaction')
    if tx is not None:
        if tx.get('phase') not in ('complete','rolled-back','aborted') or tx.get('homeResumePhase')!=tx.get('phase'):
            raise ValueError('root_update_requires_recovery')
        profile=validate(store.read(tx['profile']))
        if sha(encode(profile))!=tx['profileDigest']: raise ValueError('profile_integrity_mismatch')
    return descriptor


def current_updater(updater=UPDATER, installed=INSTALLED, uid=0, hashes=None):
    value={'schema':1,'files':hashes,'executable':None} if hashes is not None else checked_store(updater,uid).read('installed-package')
    if not isinstance(value,dict) or set(value)!={'schema','files','executable'} or value.get('schema')!=1 or not isinstance(value['files'],dict) or not value['files']:
        raise ValueError('updater_package_inventory_requires_migration')
    executable=value['executable']
    if hashes is None and (not isinstance(executable,list) or len(executable)!=len(set(executable)) or any(name not in value['files'] for name in executable)):
        raise ValueError('updater_executable_inventory_unknown')
    prefixes=('usr/palm/applications/com.cleanyourtv.root.updater/',
              'usr/palm/services/com.cleanyourtv.root.updater.service/')
    for name,digest in value['files'].items():
        if not (name.startswith(prefixes) or name=='usr/palm/packages/com.cleanyourtv.root.updater/packageinfo.json'):
            raise ValueError('foreign_updater_package_file')
        if sha(safe_bytes(installed/name))!=digest: raise ValueError('updater_package_mismatch')
        if hashes is None and (installed/name).stat().st_mode & 0o7111 != (0o111 if name in executable else 0):
            raise ValueError('updater_executable_mode_mismatch')
    return True


def _has_inventory(files):
    raw=files.get('usr/palm/applications/'+APP+'/apps.js',b'')
    try:
        value=json.loads(raw.decode().split('=',1)[1].strip().rstrip(';'))
        return isinstance(value,dict) and isinstance(value.get('apps'),list) and bool(value['apps'])
    except (ValueError,IndexError,UnicodeError): return False


def _capture_migrated_baseline(bundle):
    """Make rollback match the exact explicitly migrated installed bytes."""
    import io
    import tarfile
    import root_package
    manifest=json.loads(safe_bytes(bundle/'bundle.json'))
    path=bundle/manifest['package'];raw=safe_bytes(path)
    parts=root_package.read_ar(raw);files=root_package.data_files(raw)
    receipt=json.loads(safe_bytes(ROOT/'personalization.json',uid=0))
    for name,digest in receipt['files'].items():
        root_package.safe_name(name)
        target='usr/palm/applications/'+APP+'/'+name
        data=safe_bytes(INSTALLED/target)
        if sha(data)!=digest: raise ValueError('personalization_changed')
        files[target]=data
    with tarfile.open(fileobj=io.BytesIO(parts['data.tar.gz']),mode='r:gz') as tar:
        executable={m.name for m in tar if m.isfile() and m.mode&0o111}
    parts['data.tar.gz']=root_package.tgz(files,executable=executable,directories=False)
    raw=root_package.ar(parts);path.write_bytes(raw)
    release=json.loads(safe_bytes(bundle/'release.json'))
    release['files']={n:sha(b) for n,b in files.items()}
    (bundle/'release.json').write_text(json.dumps(release))
    (bundle/'SHA256SUMS').write_text(sha(raw)+'  '+manifest['package']+'\n')
    manifest['files']={name:sha(safe_bytes(bundle/name)) for name in manifest['files']}
    (bundle/'bundle.json').write_text(json.dumps(manifest))


class LocalDevice:
    def __init__(self):
        self.payload=None

    def preflight(self, payload, options):
        import deploy
        from updater.bootstrap import verify_bundle
        deploy.require_device();deploy.require_node()
        self.payload=Path(payload)
        deploy.verify_bundle(self.payload/'root')
        verify_bundle(self.payload/'root-updater')
        if options['prepare_supervisor']:
            self.system_setup().verify_bundle(self.payload/'supervisor')
        from python_binding import launcher_bytes
        launcher_bytes(sys.executable)
        self.options=options

    def system_setup(self):
        import system_setup
        return system_setup

    def inspect(self):
        import deploy
        try:
            deploy.require_device();deploy.require_node()
            if sys.version_info<(3,9): raise RuntimeError('unsupported_python')
        except (OSError,PermissionError,RuntimeError):
            return classify(dict(supported=False,packages_match=False,receipts_match=False,pending=False,retained=False,complete=False,migration_supported=False))
        operation=getattr(self,'operation',None)
        values=device_snapshot(owned_operation=operation['id'] if operation else None)
        # device_snapshot intentionally refuses to bless lifecycle markers alone.
        # Complete descriptor/profile readback adds the missing package evidence.
        if not any(values[k] for k in ('pending','retained')) and os.path.lexists(ROOT) and os.path.lexists(UPDATER):
            try:
                if os.path.lexists(SUPERVISOR): self.verify_supervisor()
                current_updater(hashes=getattr(self,'supervisor_updater',None));current_root()
                values.update(packages_match=True,receipts_match=True,complete=True)
            except (OSError,ValueError,TypeError,KeyError,RuntimeError,subprocess.SubprocessError):
                values['retained']=True
        return classify(values)

    def deploy(self, payload, options):
        import deploy
        root=Path(payload)/'root'
        if not options['migrate']:
            import root_package
            manifest=json.loads(safe_bytes(root/'bundle.json'))
            files=root_package.data_files(safe_bytes(root/manifest['package']))
            # Host cytv provides its inventory; a generic offline Root has the
            # empty placeholder and must discover apps locally before deployment.
            if b'window.TV_APPS = {apps:[],inputs:[]}' in files.get('usr/palm/applications/'+APP+'/apps.js',b'') or not _has_inventory(files):
                result=subprocess.run(['/usr/bin/node','-e',"require(process.argv[1])().then(function(a){process.stdout.write(JSON.stringify(a));},function(){process.exit(1);});",str(Path(__file__).parent/'app-inventory.js')],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=15)
                apps=json.loads(result.stdout)
                inventory={'apps':[{k:a[k] for k in ('id','title','icon','iconColor')} for a in apps if not a.get('hidden') and isinstance(a.get('id'),str) and isinstance(a.get('title'),str)],'inputs':[]}
                root_package.personalize_root(root,inventory)
        result=deploy.install(root,migrate=options['migrate'])
        if options['migrate']: _capture_migrated_baseline(root)
        return result

    def updater(self, payload, options):
        from updater.bootstrap import apply
        return apply(Path(payload)/'root-updater',Path(payload)/'root')

    def supervisor(self, payload, options):
        if os.path.lexists(SUPERVISOR): return self.verify_supervisor()
        setup=self.system_setup()
        baseline=Path(payload)/'captured-baseline'
        # Exact personalized installed bytes, never the generic offline baseline.
        setup.snapshot(Path(payload)/'supervisor','root',baseline)
        return setup.provision(Path(payload)/'supervisor',baseline)

    def verify_supervisor(self):
        # Import the trusted bundled implementation, never the retained worker.
        source=Path(__file__).parent/'system_updater/device.py'
        if not source.is_file(): raise ValueError('supervisor_inspector_unavailable')
        from system_updater.device import Device
        store=checked_store(SUPERVISOR)
        device=Device(store,code=SUPERVISOR/'code')
        receipt=store.read('infrastructure')
        if not isinstance(receipt,dict) or receipt.get('schema')!=1 or not isinstance(receipt.get('code'),dict) or not receipt['code']:
            raise ValueError('supervisor_infrastructure_unknown')
        for name,digest in receipt['code'].items():
            from pathlib import PurePosixPath
            relative=PurePosixPath(name)
            if relative.is_absolute() or '..' in relative.parts or str(relative)!=name or sha(safe_bytes(SUPERVISOR/'code'/name,uid=0))!=digest:
                raise ValueError('supervisor_infrastructure_mismatch')
        lockdown=store.read('legacy-lockdown')
        if not isinstance(lockdown,dict) or lockdown.get('schema')!=1: raise ValueError('supervisor_lockdown_unknown')
        for name,entry in lockdown['files'].items():
            if name not in device._legacy_lockdown_paths() or safe_bytes(name,uid=0)!=entry['disabled'].encode():
                raise ValueError('supervisor_lockdown_mismatch')
        baseline=device._baseline('root')
        if not device.verify_baseline(baseline): raise ValueError('supervisor_baseline_mismatch')
        updater=next(item for item in baseline['components'] if item['name']=='root-updater')
        raw=device.cache_bytes(updater)
        self.supervisor_updater=device.inspect(raw,updater)
        verify_package_modes(raw,INSTALLED)
        return baseline

    def readback(self):
        if os.path.lexists(SUPERVISOR): self.verify_supervisor()
        current_updater(hashes=getattr(self,'supervisor_updater',None));descriptor=current_root()
        return {'verified':True,'installed':APP,'home_changed':False,'baseline_sha':descriptor['sha256']}

    @staticmethod
    def log(error):
        import traceback
        traceback.print_exception(type(error),error,error.__traceback__,file=sys.stderr)

    def validate_root_driver(self):
        """Hash retained executable support/runtime as data before spawning it."""
        import deploy
        from updater.device import Device
        if not os.path.lexists(ROOT): return
        bundle=read_journal(ROOT/'bundle.json')
        if not isinstance(bundle,dict) or not isinstance(bundle.get('files'),dict):
            raise ValueError('root_recovery_requires_existing_cytv_recovery')
        files=bundle['files']
        for name in ('provision.py','startup_hook.py','activity.py','python_binding.py','system_permissions.py'):
            if files.get(name)!=sha(safe_bytes(ROOT/name,uid=0)):
                raise ValueError('root_recovery_support_mismatch')
        proof=read_journal(ROOT/'recovery-provision.json')
        if proof is not None:
            if proof.get('version')!=1 or proof.get('mode')!='recovery-only' or not isinstance(proof.get('files'),dict):
                raise ValueError('root_recovery_protocol_unknown')
            runtime={name:proof['files'].get(str(ROOT/'runtime'/name)) for name in deploy.RUNTIME_FILES}
        else:
            runtime={name:files.get('runtime/'+name) for name in deploy.RUNTIME_FILES}
        for name,digest in runtime.items():
            if digest!=sha(safe_bytes(ROOT/'runtime'/name,uid=0)):
                raise ValueError('root_recovery_runtime_mismatch')
        Device.require_home_resume_runtime(ROOT)

    def restore(self):
        import deploy
        self.validate_root_driver()
        return deploy.restore()

    @staticmethod
    def rpc(method, payload):
        from updater.luna import call
        return call('luna://'+method,payload)

    @staticmethod
    def cleanup(name, *args):
        if name not in ('root_updater','system_updater','legacy_permissions','app_permissions','root_archive'):
            raise ValueError('unsupported_cleanup')
        result=subprocess.run([sys.executable,str(Path(__file__).parent/('cleanup_'+name+'.py')),*args],
                              check=True,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=90)
        if name in ('legacy_permissions','app_permissions'):
            expected={'legacy_permissions':b'CYTV_LEGACY_PERMISSIONS_REMOVED','app_permissions':b'CYTV_APP_PERMISSIONS_REMOVED'}[name]
            if result.stdout.strip()!=expected: raise ValueError('cleanup_unconfirmed')
            return True
        return json.loads(result.stdout)

    def apps(self):
        value=self.rpc('com.webos.applicationManager/dev/listApps',{})
        apps=value.get('apps')
        if not isinstance(apps,list) or not all(isinstance(a,dict) and isinstance(a.get('id'),str) for a in apps):
            raise ValueError('invalid_app_inventory')
        return {a['id'] for a in apps}

    @staticmethod
    def package_paths(app):
        service=app+'.renewal' if app=='com.gathin.tvhome' else app+'.service'
        return [INSTALLED/'usr/palm'/folder/name for folder,name in (
            ('applications',app),('packages',app),('services',service))]

    def absent(self, app, terminal=None):
        paths=self.package_paths(app)
        package=paths[1]
        # Empty package remainders are removed only with a saved subscribed
        # terminal for this request. Absence never manufactures terminal proof.
        if terminal and terminal.get('completed') is True and os.path.lexists(package):
            if package.is_symlink() or not package.is_dir(): raise ValueError('unsafe_package_remainder')
            package.rmdir()
        if any(os.path.lexists(p) for p in paths): raise ValueError('package_remains')

    def remove(self, checkpoint):
        import deploy
        import time
        import uuid
        from observed_install import remove
        from installation import Ownership
        ownership=self.ownership
        # The product journal owns this entire sequence, including permission
        # cleanup and final routing readback. Never call guarded component CLIs.
        lease=ownership.status()
        if lease is None or lease['owner']!='product' or lease['terminal']:
            raise ValueError('product_lease_required')
        journal=ownership.store
        name='removal-'+lease['id']
        if journal.read(name) is not None: raise ValueError('removal_already_started')
        record={'schema':1,'root_updater_archive':str(UPDATER)+'.archive-'+uuid.uuid4().hex,
                'system_updater_archive':str(SUPERVISOR)+'.archive-'+uuid.uuid4().hex,'removals':{}}
        journal.write(name,record)
        def save(stage):
            record['stage']=stage;journal.write(name,record);checkpoint(stage)
        self.validate_root_driver()
        idle=self.rpc('com.webos.appInstallService/status',{'subscribe':True})
        if idle.get('status',{}).get('apps')!=[]: raise ValueError('installer_not_idle')
        apps=self.apps()
        legacy='com.cleanyourtv.updater';home='com.gathin.tvhome';helper='com.local.nativehome'
        if legacy in apps:
            status=self.rpc(legacy+'.service/status',{}).get('result')
            if not isinstance(status,dict) or 'transaction' not in status: raise ValueError('legacy_updater_unknown')
            tx=status['transaction']
            if tx is not None and (not isinstance(tx,dict) or tx.get('status') not in ('complete','rolled-back')):
                raise ValueError('legacy_update_pending')
        supervisor='com.cleanyourtv.system.updater'
        system_needed=supervisor in apps or os.path.lexists(SUPERVISOR)
        if system_needed:
            self.cleanup('system_updater','status',record['system_updater_archive'])
            save('supervisor-disable')
            if self.cleanup('system_updater','disable',record['system_updater_archive']).get('disabled') is not True:
                raise ValueError('supervisor_disable_unconfirmed')
        save('root-updater-disable')
        if self.cleanup('root_updater','disable',record['root_updater_archive']).get('disabled') is not True:
            raise ValueError('root_updater_disable_unconfirmed')
        if APP in apps:
            save('root-remove-submitting')
            result=deploy.uninstall()
            if result.get('removed')!=APP: raise ValueError('root_remove_unconfirmed')
            save('root-remove-terminal')
        self.absent(APP)
        if helper in apps:
            save('helper-disable')
            self.rpc(helper+'.service/disable',{})
        if home in apps:
            # Existing EIM ownership is the fixed Home identity. Readback must
            # establish removal; an accepted request alone is insufficient.
            self.rpc('com.webos.service.eim/deleteDevice',{'appId':home})
            devices=self.rpc('com.webos.service.eim/getAllInputStatus',{}).get('devices')
            if not isinstance(devices,list) or any(d.get('id')==home or d.get('appId')==home for d in devices):
                raise ValueError('legacy_input_registration_remains')
        self.rpc('com.webos.applicationManager/launch',{'id':'com.webos.app.home'})
        save('legacy-permissions')
        self.cleanup('legacy_permissions')
        for app in ('com.cleanyourtv.root.updater',legacy,helper,home,supervisor):
            if app in apps:
                record['removals'][app]={'state':'submitted'};save('package-remove-submitting')
                terminal=remove(app,timeout=150)
                record['removals'][app]={'state':'terminal','evidence':terminal};save('package-remove-terminal')
                self.absent(app,terminal)
            else:
                self.absent(app)
            # Keep the exact terminal; do not replace it with a done/absence flag.
        save('app-permissions')
        self.cleanup('app_permissions')
        save('root-updater-archive')
        final=self.cleanup('root_updater','finalize',record['root_updater_archive'])
        if final.get('removed') is not True: raise ValueError('root_updater_cleanup_incomplete')
        if system_needed:
            save('supervisor-archive')
            if self.cleanup('system_updater','archive',record['system_updater_archive']).get('removed') is not True:
                raise ValueError('supervisor_cleanup_incomplete')
        save('removal-readback')
        self.verify_removed()
        if os.path.lexists(ROOT):
            deadline=time.monotonic()+60
            while self.cleanup('root_archive','inspect').get('busy') is not False:
                if time.monotonic()>=deadline: raise ValueError('old_root_processes_running_restart_required')
                time.sleep(1)
        save('removal-verified')
        return {'removed':True,'applications_services_startup_removed':True,'recovery_retained':str(ROOT),
                'updater_archive':final.get('archive'),'system_updater_archive':record['system_updater_archive'] if system_needed else None}

    def verify_removed(self):
        apps=(APP,'com.cleanyourtv.root.updater','com.cleanyourtv.updater','com.gathin.tvhome','com.local.nativehome','com.cleanyourtv.system.updater')
        if self.apps().intersection(apps): raise ValueError('project_apps_remain')
        for app in apps: self.absent(app)
        paths=['/var/lib/webosbrew/init.d/'+n for n in ('50-clean-your-tv-root','51-clean-your-tv-root-updater','52-clean-your-tv-system-updater')]
        paths+=['/var/luna-service2/manifests.d/com.cleanyourtv.root.preview.recovery.json','/var/webos-profile/override/clean-your-tv-root.json']
        if any(os.path.lexists(p) for p in paths): raise ValueError('project_routing_remains')
        for folder in ('services.d','roles.d','client-permissions.d','api-permissions.d','manifests.d'):
            if any(p.name.startswith(tuple(a+'.' for a in apps)) for p in (Path('/var/luna-service2-dev')/folder).iterdir()):
                raise ValueError('project_bus_registration_remains')
        settings=self.rpc('com.webos.settingsservice/getSystemSettings',{'category':'general','keys':['defaultApps']})
        profiles=self.rpc('com.webos.service.systemprofile/getProfiles',{'names':['defaultApps','idleApp'],'subscribe':False})['profiles']
        routes=(settings['settings']['defaultApps']['home'],profiles['defaultApps']['categories']['home'],profiles['idleApp']['appId'])
        if routes!=('com.webos.app.home',)*3: raise ValueError('lg_home_routing_unconfirmed')
