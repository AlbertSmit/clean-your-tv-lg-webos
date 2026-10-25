"""Real bounded archive and fixed-path device effects, without a TV bus."""
import hashlib
import importlib
import io
import json
import os
from pathlib import Path
import tarfile
import tempfile
import unittest
from test_core import Store

def digest(raw):return hashlib.sha256(raw).hexdigest()
def tar(files):
    output=io.BytesIO()
    with tarfile.open(fileobj=output,mode='w:gz') as archive:
        for name,raw in files.items():
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o600;archive.addfile(info,io.BytesIO(raw))
    return output.getvalue()
def ipk(app='com.gathin.tvhome',foreign=False):
    prefix='usr/palm/applications/'+app+'/'
    files={prefix+'appinfo.json':json.dumps({'id':app,'version':'1.0.0','type':'web','main':'index.html','systemUpdateProtocol':1}).encode(),prefix+'index.html':b'Home','usr/palm/packages/'+app+'/packageinfo.json':json.dumps({'id':app,'app':app,'version':'1.0.0','services':[]}).encode()}
    if foreign:files['etc/passwd']=b'bad'
    parts={'debian-binary':b'2.0\n','control.tar.gz':tar({'control':('Package: '+app+'\nVersion: 1.0.0\n').encode()}),'data.tar.gz':tar(files)};out=b'!<arch>\n'
    for name,data in parts.items():out+=(name+'/').ljust(16).encode()+b'0           0     0     100644  '+str(len(data)).ljust(10).encode()+b'`\n'+data+(b'\n' if len(data)%2 else b'')
    return out

class DeviceBase(unittest.TestCase):
    def setUp(self):
        try:self.mod=importlib.import_module('system_updater.device')
        except ModuleNotFoundError:self.fail('fixed device adapter is missing')
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(os.path.realpath(self.tmp.name));self.store=Store(self.root/'state',uid=os.getuid());(self.root/'state/cache').mkdir();(self.root/'code').mkdir()
        self.store.write('legacy-lockdown',{'schema':1,'files':{}})
        self.device=self.mod.Device(self.store,code=self.root/'code',root_state=self.root/'root',root_updater=self.root/'root-updater',installed=self.root/'installed',uid=os.getuid())
    def tearDown(self):self.tmp.cleanup()

class Tests(DeviceBase):
    def test_package_foreign_paths_and_identity_rejected(self):
        raw=ipk();descriptor={'name':'home','application':'com.gathin.tvhome','version':'1.0.0','sha256':digest(raw),'size':len(raw),'kind':'ipk'};self.assertTrue(self.device.inspect(raw,descriptor))
        raw=ipk(foreign=True);descriptor.update(sha256=digest(raw),size=len(raw))
        with self.assertRaises(ValueError):self.device.inspect(raw,descriptor)
    def test_infrastructure_exact_baseline_allowlist_and_no_symlinks(self):
        raw=tar({'runtime/cli.py':b'new','updater/service.js':b'code'});c={'name':'root-infrastructure','version':'1.0.0','kind':'infrastructure','sha256':digest(raw),'size':len(raw),'files':{'runtime/cli.py':'a'*64,'updater/service.js':'b'*64},'local':True}
        self.store.write('baseline',{'edition':'root','components':[c]});self.assertEqual(set(self.device.inspect(raw,c)),set(c['files']))
        bad=tar({'runtime/cli.py':b'new','updater/service.js':b'code','runtime/../outside':b'bad'});c.update(sha256=digest(bad),size=len(bad))
        with self.assertRaises(ValueError):self.device.inspect(bad,c)
    def test_supervisor_integrity_detects_code_change(self):
        p=self.root/'code/fixed.py';p.write_bytes(b'trusted');self.store.write('infrastructure',{'schema':1,'code':{'fixed.py':digest(b'trusted')}});self.device.integrity();p.write_bytes(b'tampered')
        with self.assertRaises(ValueError):self.device.integrity()
    def test_cached_bytes_are_rechecked_before_mutation(self):
        raw=ipk();c={'name':'home','application':'com.gathin.tvhome','version':'1.0.0','kind':'ipk','sha256':digest(raw),'size':len(raw),'local':True};(self.root/'state/cache'/c['sha256']).write_bytes(b'tampered')
        with self.assertRaises(ValueError):self.device.inspect(self.device.cache_bytes(c),c)
    def test_unknown_legacy_transaction_blocks(self):
        self.device.legacy_states=[self.root/'legacy.json'];self.device.legacy_states[0].write_text('{"phase":"installing"}')
        with self.assertRaises(ValueError):self.device.check_legacy()
        self.device.legacy_states[0].write_text('{"phase":"complete"}');self.device.check_legacy()

if __name__=='__main__':unittest.main()

class ExistingPackageTests(DeviceBase):
    def test_public_ordinary_package_directory_entries_are_supported(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
        from cytv.package import ipk as build_ipk, data_files
        files=data_files(ipk());raw=build_ipk('com.gathin.tvhome','1.0.0',files)
        c={'name':'home','application':'com.gathin.tvhome','version':'1.0.0','kind':'ipk','sha256':digest(raw),'size':len(raw)}
        self.assertTrue(self.device.inspect(raw,c))
    def test_helper_empty_state_marker_is_compatible_but_preferences_are_forbidden(self):
        from cytv.package import ipk as build_ipk, data_files
        app='com.local.nativehome';files=data_files(ipk(app));files['usr/palm/applications/'+app+'/state/.keep']=b''
        raw=build_ipk(app,'1.0.0',files);c={'name':'helper','application':app,'version':'1.0.0','kind':'ipk','sha256':digest(raw),'size':len(raw)}
        self.assertTrue(self.device.inspect(raw,c));files['usr/palm/applications/'+app+'/state/blocked']=b'';raw=build_ipk(app,'1.0.0',files);c.update(sha256=digest(raw),size=len(raw))
        with self.assertRaises(ValueError):self.device.inspect(raw,c)

class PreferenceBase(DeviceBase):
    def setUp(self):
        super().setUp()
        self.events=[]
        self.device.boot=lambda:'boot-one'
        self.device._stop_renewal=lambda:self.events.append('stop')
        self.device._cancel_renewal=lambda:self.events.append('cancel')
        self.device.rpc=lambda uri,payload:self.events.append(uri) or {'returnValue':True,'state':{'enabled':True}}
        self.settings=self.root/'installed/usr/palm/services/com.gathin.tvhome.renewal/state/settings.json';self.settings.parent.mkdir(parents=True);self.settings.write_text('{"enabled":true,"preferenceTouched":true}')
        self.tx={'id':'a'*32,'edition':'no-root','phase':'complete'};self.store.write('transaction',self.tx)

class PreferenceTests(PreferenceBase):
    def test_renewal_is_durably_paused_before_replacement(self):
        self.device._pause_renewal(self.tx);state=json.loads(self.settings.read_bytes());self.assertFalse(state['enabled']);self.assertTrue(state['updatePause']['wasEnabled']);self.assertEqual(self.events,['stop','cancel']);self.assertTrue(self.store.read('renewal-pause-'+self.tx['id'])['confirmed'])
    def test_explicit_renewal_disable_during_update_wins(self):
        self.device._pause_renewal(self.tx);state=json.loads(self.settings.read_bytes());state['updatePause']['wasEnabled']=False;self.settings.write_text(json.dumps(state));result=self.device._finish_renewal(self.tx)
        self.assertEqual(result['status'],'skipped');self.assertFalse(json.loads(self.settings.read_bytes())['enabled']);self.assertNotIn('updatePause',json.loads(self.settings.read_bytes()));self.assertFalse(any(isinstance(e,str) and e.endswith('/enable') for e in self.events))
    def test_renewal_resume_is_attempted_once_and_bound_to_boot(self):
        self.device._pause_renewal(self.tx);self.assertEqual(self.device._finish_renewal(self.tx)['status'],'restored');self.device._finish_renewal(self.tx)
        self.assertEqual(sum(isinstance(e,str) and e.endswith('/enable') for e in self.events),1)
    def test_changed_boot_keeps_renewal_disabled(self):
        self.device._pause_renewal(self.tx);self.device.boot=lambda:'boot-two';self.assertEqual(self.device._finish_renewal(self.tx)['status'],'skipped');self.assertFalse(json.loads(self.settings.read_bytes())['enabled'])
    def test_mutable_restore_never_overwrites_newer_emergency_latch(self):
        latch=self.root/'installed/usr/palm/applications/com.local.nativehome/state/blocked';latch.parent.mkdir(parents=True);latch.write_bytes(b'older');self.device.snapshot_mutable();latch.write_bytes(b'new emergency');self.device.restore_mutable();self.assertEqual(latch.read_bytes(),b'new emergency')

class InfraTransitionTests(DeviceBase):
    def test_local_resume_accepts_only_prior_or_candidate_file_hashes(self):
        old=tar({'runtime/cli.py':b'old'});new=tar({'runtime/cli.py':b'new'})
        a={'name':'root-infrastructure','kind':'infrastructure','version':'1.0.0','size':len(old),'sha256':digest(old),'files':{'runtime/cli.py':digest(b'old')},'local':True};b={**a,'version':'1.1.0','size':len(new),'sha256':digest(new)}
        self.store.write('baseline',{'edition':'root','components':[a]});self.store.write('transaction',{'edition':'root','prior':{'components':[a]},'candidate':{'components':[b]}})
        (self.root/'state/cache'/a['sha256']).write_bytes(old);(self.root/'state/cache'/b['sha256']).write_bytes(new);runtime=self.root/'root/runtime';runtime.mkdir(parents=True);(runtime/'cli.py').write_bytes(b'old')
        self.device.validate_infrastructure_transition();(runtime/'cli.py').write_bytes(b'new');self.device.validate_infrastructure_transition();(runtime/'cli.py').write_bytes(b'foreign')
        with self.assertRaises(ValueError):self.device.validate_infrastructure_transition()

class LegacyBaselineTests(DeviceBase):
    def test_completed_root_release_seeds_legacy_recovery_cache(self):
        raw=ipk('com.cleanyourtv.root.preview');c={'name':'root','application':'com.cleanyourtv.root.preview','version':'1.0.0','kind':'ipk','sha256':digest(raw),'size':len(raw),'local':True};(self.root/'state/cache'/c['sha256']).write_bytes(raw)
        self.device.sync_root_baseline({'edition':'root','phase':'complete','candidate':{'components':[c]}})
        legacy=Store(self.root/'root-updater',uid=os.getuid());saved=legacy.read('current');self.assertEqual(saved['version'],'1.0.0');self.assertEqual((self.root/'root-updater/cache'/(c['sha256']+'.ipk')).read_bytes(),raw)
    def test_root_legacy_terminal_without_resume_cleanup_blocks(self):
        self.root.joinpath('root-updater').mkdir();self.root.joinpath('root-updater/transaction.json').write_text('{"phase":"complete"}')
        with self.assertRaises(ValueError):self.device.check_legacy()
        self.root.joinpath('root-updater/transaction.json').write_text('{"phase":"complete","homeResumePhase":"complete"}');self.device.check_legacy()

class ProcessSafetyTests(DeviceBase):
    def test_permission_error_while_enumerating_proc_never_means_idle(self):
        from unittest.mock import patch
        class Entry:
            name='123'
            def __truediv__(self,name):return self
            def read_bytes(self):raise PermissionError('proc is unreadable')
        with patch.object(self.mod.Path,'iterdir',return_value=iter([Entry()])):
            with self.assertRaises(PermissionError):self.device._helper_processes()
    def test_reused_process_id_is_never_signalled(self):
        from unittest.mock import patch
        self.device._process_start=lambda pid:'newer-start'
        with patch.object(self.mod.os,'kill') as kill:
            with self.assertRaises(ValueError):self.device._signal_checked(42,'original-start',self.mod.signal.SIGKILL)
            kill.assert_not_called()

class RetainedCycleTests(PreferenceBase):
    def test_retained_rollback_has_new_preference_pause_and_resume_cycle(self):
        self.device._pause_renewal(self.tx);self.device._finish_renewal(self.tx)
        self.settings.write_text('{"enabled":true,"preferenceTouched":true}')
        rollback={**self.tx,'phase':'rolled-back','resumeCycle':'rollback'};self.store.write('transaction',rollback)
        self.device._pause_renewal(rollback);state=json.loads(self.settings.read_bytes());self.assertEqual(state['updatePause']['id'],self.tx['id']+'-rollback')
        self.assertEqual(self.device._finish_renewal(rollback)['status'],'restored');self.assertNotIn('updatePause',json.loads(self.settings.read_bytes()));self.assertEqual(sum(isinstance(e,str) and e.endswith('/enable') for e in self.events),2)


class LockdownTests(DeviceBase):
    def test_legacy_lockdown_preflights_every_file_before_changes(self):
        first=self.root/'legacy-api.json';second=self.root/'legacy-receipt.json';first.write_text('original');second.write_text('foreign')
        self.store.write('legacy-lockdown',{'schema':1,'files':{str(p):{'original':'original','disabled':'disabled','mode':0o600} for p in (first,second)}})
        from unittest.mock import patch
        with patch.object(self.device,'_legacy_lockdown_paths',return_value={str(first),str(second)}):
            with self.assertRaises(ValueError):self.device.enforce_legacy_lockdown()
            self.assertEqual(first.read_text(),'original')
            second.write_text('original');scans=[];self.device.scan_services=lambda:scans.append(True);self.device.enforce_legacy_lockdown();self.assertEqual(first.read_text(),'disabled');self.assertEqual(second.read_text(),'disabled');self.assertEqual(scans,[True]);self.device.enforce_legacy_lockdown();self.assertEqual(scans,[True])
    def test_foreign_legacy_lockdown_path_is_rejected(self):
        self.store.write('legacy-lockdown',{'schema':1,'files':{'/etc/passwd':{'original':'before','disabled':'after','mode':0o600}}})
        with self.assertRaises(ValueError):self.device.enforce_legacy_lockdown()

class HelperBootPauseTests(DeviceBase):
    def setUp(self):
        super().setUp();self.device._helper_processes=lambda:[];self.device.boot=lambda:'boot-one';self.device.rpc=lambda uri,payload:{'returnValue':True}
        self.tx={'id':'b'*32,'edition':'no-root','phase':'complete'};self.store.write('transaction',self.tx)
        self.startup=self.root/'installed/usr/palm/services/com.local.nativehome.service/state/startup-state.json';self.startup.parent.mkdir(parents=True);self.original=b'{"enabled":true,"schema":3,"boot":"boot-one"}';self.startup.write_bytes(self.original)
    def test_helper_boot_is_paused_during_transaction_and_restored_on_same_boot(self):
        self.device._suspend_helper(self.tx);self.assertFalse(json.loads(self.startup.read_bytes())['enabled']);self.device.finish(self.tx);self.assertEqual(self.startup.read_bytes(),self.original)
    def test_explicit_disable_during_pause_wins(self):
        self.device._suspend_helper(self.tx);self.startup.write_bytes(b'{"enabled":false}');self.device.finish(self.tx);self.assertEqual(self.startup.read_bytes(),b'{"enabled":false}')
    def test_reboot_never_reenables_helper_boot_implicitly(self):
        self.device._suspend_helper(self.tx);self.device.boot=lambda:'boot-two';self.device.finish(self.tx);self.assertFalse(json.loads(self.startup.read_bytes())['enabled'])

class PrivateServiceTests(DeviceBase):
    def test_private_recovery_service_has_fixed_destination_and_receipts(self):
        files={'runtime/cli.py':b'runtime','service/service.js':b'new-service','updater/service.js':b'updater'}
        raw=tar(files);c={'name':'root-infrastructure','kind':'infrastructure','version':'1.1.0','sha256':digest(raw),'size':len(raw),'local':True,'files':{n:digest(v) for n,v in files.items()}}
        self.store.write('baseline',{'edition':'root','components':[c]})
        self.assertEqual(self.device.inspect(raw,c),c['files'])
        for name,data in files.items():
            path=self.device._infra_path(name);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
        proof={'mode':'recovery-only','files':{str(self.device._infra_path(n)):digest(b'old') for n in files if not n.startswith('updater/')}};proof_path=self.root/'root/recovery-provision.json';proof_path.write_text(json.dumps(proof))
        legacy=Store(self.root/'root-updater',uid=os.getuid());legacy.write('infrastructure',{'schema':1,'code':{'service.js':digest(b'old')},'recovery_sha256':digest(proof_path.read_bytes())})
        self.device._refresh_root_receipts(c['files']);updated=json.loads(proof_path.read_bytes());self.assertEqual(updated['files'][str(self.root/'root/service/service.js')],digest(b'new-service'));self.assertEqual(legacy.read('infrastructure')['recovery_sha256'],digest(proof_path.read_bytes()))
        old_hashes={n:digest(b'old') for n in files};self.device._refresh_root_receipts(old_hashes);self.assertEqual(json.loads(proof_path.read_bytes())['files'][str(self.root/'root/service/service.js')],digest(b'old'))

class StateDirectoryTests(DeviceBase):
    def test_missing_state_directory_restores_owned_writable_metadata(self):
        self.store.write('transaction',{'id':'c'*32,'edition':'no-root'})
        state=self.root/'installed/usr/palm/services/com.gathin.tvhome.renewal/state';state.mkdir(parents=True);os.chmod(state,0o700);settings=state/'settings.json';settings.write_bytes(b'{"enabled":false}')
        self.device.snapshot_mutable();settings.unlink();state.rmdir();self.device.restore_mutable()
        self.assertEqual(state.stat().st_mode&0o777,0o700);self.assertEqual(state.stat().st_uid,os.getuid());self.assertEqual(settings.read_bytes(),b'{"enabled":false}');(state/'write-check').write_bytes(b'writable')

class ProfileProtocolTests(DeviceBase):
    def test_launcher_releases_cannot_drop_profile_health_protocol(self):
        import sys
        sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
        from cytv.package import ipk as build_ipk, data_files
        files=data_files(ipk());name='usr/palm/applications/com.gathin.tvhome/appinfo.json';app=json.loads(files[name]);app.pop('systemUpdateProtocol',None);files[name]=json.dumps(app).encode();raw=build_ipk('com.gathin.tvhome','1.0.0',files)
        c={'name':'home','application':'com.gathin.tvhome','version':'1.0.0','kind':'ipk','sha256':digest(raw),'size':len(raw)}
        with self.assertRaises(ValueError):self.device.inspect(raw,c)

class SignedInfrastructureTests(DeviceBase):
    def test_signed_private_service_upgrade_and_rollback_update_real_bytes_and_receipts(self):
        import subprocess
        import shutil
        from test_core import ROOT
        old_files={'runtime/cli.py':b'old runtime','service/service.js':b'old service','updater/service.js':b'old updater'}
        new_files={name:value.replace(b'old',b'new') for name,value in old_files.items()};old=tar(old_files);new=tar(new_files)
        def infra(raw,version,local=False):
            c={'name':'root-infrastructure','kind':'infrastructure','version':version,'sha256':digest(raw),'size':len(raw)}
            if local:c.update(local=True,files={n:digest(b) for n,b in old_files.items()})
            else:c['url']='https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/v1.1.0/infrastructure.tar.gz'
            return c
        previous=infra(old,'1.0.0',True);candidate=infra(new,'1.1.0')
        components=[{'name':name,'application':app,'kind':'ipk','version':'1.1.0','sha256':'a'*64,'size':1,'url':'https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/v1.1.0/'+name+'.ipk'} for name,app in [('root','com.cleanyourtv.root.preview'),('root-updater','com.cleanyourtv.root.updater')]]+[candidate]
        release={'schema':1,'edition':'root','release':'v1.1.0','supervisor':1,'notes':'Signed infrastructure fixture','components':components}
        js="const c=require('crypto'),fs=require('fs'),m=fs.readFileSync(0),k=c.generateKeyPairSync('rsa',{modulusLength:2048});process.stdout.write(JSON.stringify({proof:{payload:m.toString('base64'),signature:c.sign('RSA-SHA256',m,k.privateKey).toString('base64')},key:k.publicKey.export({type:'spki',format:'pem'})}));"
        signed=json.loads(subprocess.run(['node','-e',js],input=json.dumps(release).encode(),stdout=subprocess.PIPE,check=True).stdout);release['proof']=signed['proof']
        baseline={**release,'release':'v1.0.0','components':[{k:v for k,v in c.items() if k!='url'} for c in components]};baseline.pop('proof');baseline['components'][-1]=previous
        for c in baseline['components'][:-1]:c.update(version='1.0.0',local=True)
        self.store.write('baseline',baseline);self.store.write('transaction',{'edition':'root','prior':baseline,'candidate':release})
        for c,raw in ((previous,old),(candidate,new)):(self.root/'state/cache'/c['sha256']).write_bytes(raw)
        code=self.root/'code/system_updater';code.mkdir();shutil.copyfile(ROOT/'system-updater/policy.js',code/'policy.js');(code/'release-public.pem').write_text(signed['key'])
        self.store.write('infrastructure',{'schema':1,'code':{str(p.relative_to(self.root/'code')):digest(p.read_bytes()) for p in code.iterdir()}})
        for name,data in old_files.items():
            p=self.device._infra_path(name);p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        proof=self.root/'root/recovery-provision.json';proof.write_text(json.dumps({'mode':'recovery-only','files':{str(self.device._infra_path(n)):digest(v) for n,v in old_files.items() if not n.startswith('updater/')}}))
        legacy=Store(self.root/'root-updater',uid=os.getuid());legacy.write('infrastructure',{'schema':1,'code':{'service.js':digest(old_files['updater/service.js'])},'recovery_sha256':digest(proof.read_bytes())})
        def local_verifier(method,payload=None,binary=False):
            result=subprocess.run(['node',str(code/'policy.js'),method],input=json.dumps(payload or {}).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
            return result.stdout if binary else json.loads(result.stdout)
        self.device.fetch=local_verifier
        self.device._stop_service_processes=lambda target:None;self.device.repair_registrations=lambda:None;self.device.rpc=lambda uri,payload:{'returnValue':True,'root':True}
        # Actual Node signature verification, bounded archive parsing, fixed-file
        # replacement and root-owned receipt writes run; only TV bus/process IO is substituted.
        for c,expected in ((candidate,new_files),(previous,old_files)):
            terminal=[];self.device.install(c,lambda value:None,terminal.append);self.assertTrue(terminal[0]['success'])
            for name,data in expected.items():self.assertEqual(self.device._infra_path(name).read_bytes(),data)
            self.assertEqual(json.loads(proof.read_bytes())['files'][str(self.root/'root/service/service.js')],digest(expected['service/service.js']));self.assertEqual(legacy.read('infrastructure')['recovery_sha256'],digest(proof.read_bytes()))

class RepeatedHelperPauseTests(HelperBootPauseTests):
    def test_automatic_rollback_respects_newer_explicit_disable(self):
        self.device._suspend_helper(self.tx);self.startup.write_bytes(b'{"enabled":false}');self.device._suspend_helper(self.tx);self.device.finish(self.tx);self.assertEqual(self.startup.read_bytes(),b'{"enabled":false}')
