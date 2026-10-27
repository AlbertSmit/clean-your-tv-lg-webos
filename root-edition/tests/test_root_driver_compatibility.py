"""Retained runtime closure belongs to the installed version, not the new bundle."""
import hashlib
import json
import subprocess
import unittest
from install_fixture import CurrentInstallation


class RetainedRuntimeTests(unittest.TestCase):
    def alter(self, fixture, *, legacy=False, omit=()):
        root = fixture.root
        manifest = json.loads((root / 'bundle.json').read_text())
        proof = fixture.root_store.read('recovery-provision')
        if legacy:
            release = json.loads((root / 'release.json').read_text())
            release['version'] = '0.4.0'
            release.pop('runtime_layout', None)
            raw = json.dumps(release).encode()
            (root / 'release.json').write_bytes(raw)
            manifest['files']['release.json'] = hashlib.sha256(raw).hexdigest()
            old_package = manifest['package']
            manifest['package'] = 'com.cleanyourtv.root.preview_0.4.0_all.ipk'
            manifest['files'][manifest['package']] = manifest['files'].pop(old_package)
            omit = ('audio_recovery.py', *omit)
        for name in omit:
            (root / 'runtime' / name).unlink(missing_ok=True)
            manifest['files'].pop('runtime/' + name, None)
            proof['files'].pop(str(root / 'runtime' / name), None)
        (root / 'bundle.json').write_text(json.dumps(manifest))
        fixture.root_store.write('recovery-provision', proof)

    def test_complete_published_040_closure_does_not_require_new_audio_module(self):
        with CurrentInstallation() as fixture:
            self.alter(fixture, legacy=True)
            fixture.device_module.LocalDevice().validate_root_driver()

    def test_current_complete_closure_is_accepted(self):
        with CurrentInstallation() as fixture:
            fixture.device_module.LocalDevice().validate_root_driver()

    def test_legacy_tamper_or_other_missing_member_is_rejected(self):
        for omission in ((), ('intent_runtime.py',)):
            with self.subTest(omission=omission), CurrentInstallation() as fixture:
                self.alter(fixture, legacy=True, omit=omission)
                if not omission:
                    (fixture.root / 'runtime/cli.py').write_text('changed')
                with self.assertRaises((ValueError, OSError)):
                    fixture.device_module.LocalDevice().validate_root_driver()

    def test_current_version_cannot_claim_legacy_closure(self):
        with CurrentInstallation() as fixture:
            self.alter(fixture, omit=('intent_runtime.py',))
            with self.assertRaises((ValueError, OSError)):
                fixture.device_module.LocalDevice().validate_root_driver()

    def test_unbound_or_foreign_release_metadata_cannot_select_legacy_runtime(self):
        for change in ('unbound', 'foreign-app', 'package-version'):
            with self.subTest(change=change), CurrentInstallation() as fixture:
                self.alter(fixture, legacy=True)
                root = fixture.root
                release = json.loads((root / 'release.json').read_text())
                manifest = json.loads((root / 'bundle.json').read_text())
                if change == 'package-version':
                    manifest['package'] = 'com.cleanyourtv.root.preview_0.5.0_all.ipk'
                else:
                    release['application_id'] = 'foreign.application'
                    raw = json.dumps(release).encode()
                    (root / 'release.json').write_bytes(raw)
                    if change != 'unbound':
                        manifest['files']['release.json'] = hashlib.sha256(raw).hexdigest()
                (root / 'bundle.json').write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    fixture.device_module.LocalDevice().validate_root_driver()

    def test_published_050_separate_audio_closure_is_accepted(self):
        with CurrentInstallation() as fixture:
            root=fixture.root
            manifest=json.loads((root/'bundle.json').read_text())
            release=json.loads((root/'release.json').read_text())
            release.pop('runtime_layout',None)
            release['version']='0.5.0'
            old_package=manifest['package']
            manifest['package']='com.cleanyourtv.root.preview_0.5.0_all.ipk'
            manifest['files'][manifest['package']]=manifest['files'].pop(old_package)
            raw=json.dumps(release).encode();(root/'release.json').write_bytes(raw)
            manifest['files']['release.json']=hashlib.sha256(raw).hexdigest()
            raw=b'# Historical separately shipped audio worker fixture\n'
            (root/'runtime/audio_recovery.py').write_bytes(raw)
            manifest['files']['runtime/audio_recovery.py']=hashlib.sha256(raw).hexdigest()
            (root/'bundle.json').write_text(json.dumps(manifest))
            proof=fixture.root_store.read('recovery-provision')
            proof['files'][str(root/'runtime/audio_recovery.py')]=hashlib.sha256(raw).hexdigest()
            fixture.root_store.write('recovery-provision',proof)
            fixture.device_module.LocalDevice().validate_root_driver()

    def test_changed_runtime_proof_without_system_provenance_is_rejected(self):
        with CurrentInstallation() as fixture:
            self.alter(fixture,legacy=True)
            path=fixture.root/'runtime/cli.py';path.write_bytes(path.read_bytes()+b'\n# Different code\n')
            proof=fixture.root_store.read('recovery-provision')
            proof['files'][str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
            fixture.root_store.write('recovery-provision',proof)
            with self.assertRaisesRegex(ValueError,'root_recovery_current_provenance_required'):
                fixture.device_module.LocalDevice().validate_root_driver()

    def test_changed_support_without_system_provenance_is_rejected(self):
        with CurrentInstallation() as fixture:
            path=fixture.root/'package_identity.py';path.write_bytes(path.read_bytes()+b'\n# Different code\n')
            with self.assertRaisesRegex(ValueError,'root_recovery_current_provenance_required'):
                fixture.device_module.LocalDevice().validate_root_driver()

    def system_publication(self, fixture):
        """Real signed cache, own-package proof and current disk inventory."""
        import importlib, os, shutil, subprocess, sys
        from pathlib import Path
        from unittest.mock import patch
        from cytv import package
        project=Path(__file__).resolve().parents[2]
        sys.path.insert(0,str(fixture.payload/'root-updater'))
        fixture.stack.callback(lambda:sys.path.remove(str(fixture.payload/'root-updater')))
        fixture.stack.enter_context(patch.dict(sys.modules))
        system=importlib.import_module('system_updater.device')
        state=fixture.lib/'clean-your-tv-system-updater';state.mkdir();(state/'cache').mkdir();(state/'code').mkdir()
        store=fixture.device_module.Store(state,uid=os.getuid())
        # The trusted inspector is bundled in each computer installer.
        fixture.stack.enter_context(patch.object(fixture.device_module,'__file__',str(fixture.payload/'root-updater/install_device.py')))
        fixture.stack.enter_context(patch.object(system,'safe_bytes',fixture.device_module.safe_bytes))
        fixture.stack.enter_context(patch.object(importlib.import_module('system_updater.support.package'),'safe_bytes',fixture.device_module.safe_bytes))
        fixture.stack.enter_context(patch.object(importlib.import_module('system_updater.support.store'),'Store',fixture.device_module.Store))
        fixture.stack.enter_context(patch.object(system,'STATE',state))
        # The actual policy runs in Node; only the platform executable path differs.
        def fetch(device,method,payload=None,binary=False):
            result=subprocess.run(['node',str(state/'code/system_updater/policy.js'),method],input=json.dumps(payload or {}).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
            return result.stdout if binary else json.loads(result.stdout)
        fixture.stack.enter_context(patch.object(system.Device,'fetch',fetch))
        build=fixture.base/'system-build'
        subprocess.run([sys.executable,str(project/'system-updater/build.py'),'--output',str(build)],check=True,capture_output=True)
        raw=(build/'system-updater.ipk').read_bytes();files=package.data_files(raw)
        for name,data in files.items():
            target=fixture.installed/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);target.chmod(0o755 if name.endswith('/startup.sh') else 0o644)
        descriptor={'version':json.loads(files['usr/palm/applications/com.cleanyourtv.system.updater/appinfo.json'])['version'],'size':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'local':True}
        (state/'cache'/(descriptor['sha256']+'.ipk')).write_bytes(raw)
        store.write('bootstrap-bundle',{'schema':1,'package':{k:descriptor[k] for k in ('sha256','size')}})
        store.write('installed-package',{'schema':1,'package':descriptor,'files':{n:hashlib.sha256(b).hexdigest() for n,b in files.items()}})
        app='com.cleanyourtv.system.updater'
        store.write('installed-terminal',{'completed':True,'event':{'id':app,'statusValue':30,'details':{'packageId':app,'client':'com.webos.lunasend-1','ipkFile':'/var/lib/clean-your-tv-installer/cytv-root-install-fixture/package.ipk'}}})
        store.write('bootstrap',{'phase':'complete'});store.write('legacy-lockdown',{'schema':1,'files':{}})
        self.alter(fixture,legacy=True)
        path=fixture.root/'runtime/cli.py';path.write_bytes(path.read_bytes()+b'\n# Signed OTA replacement\n')
        proof=fixture.root_store.read('recovery-provision');proof['files'][str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        support=fixture.root/'package_identity.py';support.write_bytes(support.read_bytes()+b'\n# Signed OTA support replacement\n')
        proof['files'][str(support)]=hashlib.sha256(support.read_bytes()).hexdigest();fixture.root_store.write('recovery-provision',proof)
        receipt=fixture.up_store.read('infrastructure');receipt['recovery_sha256']=hashlib.sha256((fixture.root/'recovery-provision.json').read_bytes()).hexdigest();fixture.up_store.write('infrastructure',receipt)
        infra={'runtime/'+p.name:p.read_bytes() for p in (fixture.root/'runtime').glob('*.py')}
        infra['support/package_identity.py']=support.read_bytes()
        infra_raw=package.tgz(infra,directories=False)
        components=[]
        for name,folder,filename in [('root','root',json.loads((fixture.payload/'root/bundle.json').read_text())['package']),('root-updater','root-updater','root-updater.ipk')]:
            raw=(fixture.payload/folder/filename).read_bytes();application='com.cleanyourtv.root.preview' if name=='root' else 'com.cleanyourtv.root.updater'
            components.append({'name':name,'kind':'ipk','application':application,'version':json.loads(package.data_files(raw)['usr/palm/applications/'+application+'/appinfo.json'])['version'],'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),'url':'https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/v1.5.0/'+name+'.ipk'})
            (state/'cache'/components[-1]['sha256']).write_bytes(raw)
        components.append({'name':'root-infrastructure','kind':'infrastructure','version':'0.5.0','size':len(infra_raw),'sha256':hashlib.sha256(infra_raw).hexdigest(),'url':'https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/v1.5.0/root-infrastructure.tar.gz'})
        (state/'cache'/components[-1]['sha256']).write_bytes(infra_raw)
        release={'schema':1,'edition':'root','release':'v1.5.0','supervisor':1,'notes':'Signed retained recovery regression','components':components}
        js="const c=require('crypto'),fs=require('fs'),m=fs.readFileSync(0),k=c.generateKeyPairSync('rsa',{modulusLength:2048});process.stdout.write(JSON.stringify({proof:{payload:m.toString('base64'),signature:c.sign('RSA-SHA256',m,k.privateKey).toString('base64')},key:k.publicKey.export({type:'spki',format:'pem'})}));"
        signed=json.loads(subprocess.run(['node','-e',js],input=json.dumps(release).encode(),stdout=subprocess.PIPE,check=True).stdout)
        release['proof']=signed['proof']
        (state/'code/system_updater').mkdir();shutil.copyfile(project/'system-updater/policy.js',state/'code/system_updater/policy.js');(state/'code/system_updater/release-public.pem').write_text(signed['key'])
        (state/'code/infrastructure-paths.json').write_text(json.dumps(sorted(infra)))
        store.write('infrastructure',{'schema':1,'code':{str(p.relative_to(state/'code')):hashlib.sha256(p.read_bytes()).hexdigest() for p in (state/'code').rglob('*') if p.is_file()}})
        baseline=json.loads(json.dumps(release));baseline.pop('proof')
        for c in baseline['components']:
            c.pop('url');c['local']=True
            if c['kind']=='infrastructure':c.update(files={n:hashlib.sha256(b).hexdigest() for n,b in infra.items()},absent=[])
        store.write('baseline',baseline);store.write('current-root',release)
        return store,system

    def test_signed_system_runtime_replaces_original_bootstrap_hashes(self):
        with CurrentInstallation() as fixture:
            self.system_publication(fixture)
            fixture.device_module.LocalDevice().validate_root_driver()
            fixture.assert_preserved(self)

    def test_system_proof_cannot_authorize_changed_or_missing_runtime(self):
        for change in ('tamper','missing','forged-proof','support-tamper','support-forged-proof','bad-signature','pending'):
            with self.subTest(change=change),CurrentInstallation() as fixture:
                store,system=self.system_publication(fixture)
                path=fixture.root/'runtime/cli.py'
                if change=='tamper':path.write_bytes(path.read_bytes()+b'# untrusted\n')
                elif change=='missing':path.unlink()
                elif change in ('forged-proof','support-forged-proof'):
                    if change=='support-forged-proof':path=fixture.root/'package_identity.py'
                    path.write_bytes(path.read_bytes()+b'# untrusted\n');proof=fixture.root_store.read('recovery-provision');proof['files'][str(path)]=hashlib.sha256(path.read_bytes()).hexdigest();fixture.root_store.write('recovery-provision',proof)
                    receipt=fixture.up_store.read('infrastructure');receipt['recovery_sha256']=hashlib.sha256((fixture.root/'recovery-provision.json').read_bytes()).hexdigest();fixture.up_store.write('infrastructure',receipt)
                elif change=='support-tamper':
                    path=fixture.root/'package_identity.py';path.write_bytes(path.read_bytes()+b'# untrusted\n')
                elif change=='bad-signature':
                    release=store.read('current-root');release['proof']['signature']='AAAA';store.write('current-root',release)
                else:store.write('transaction',{'phase':'installing'})
                with self.assertRaises((ValueError,OSError,subprocess.CalledProcessError)):
                    fixture.device_module.LocalDevice().validate_root_driver()
