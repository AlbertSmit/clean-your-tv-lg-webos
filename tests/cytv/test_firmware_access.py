"""Real registration changes preserve published updater and removal contracts."""
import ast
import hashlib
import json
import os
from pathlib import Path
import tarfile
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from cytv import firmware_access

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'root-edition'))
LEGACY=types.ModuleType('legacy_firmware_provision')
archive=ROOT/'tests/system_updates/fixtures/public-1.3.0-supervisor.tar.gz'
provenance=json.loads(archive.with_suffix('.provenance.json').read_bytes())
assert hashlib.sha256(archive.read_bytes()).hexdigest()==provenance['sha256']
with tarfile.open(archive) as stream:
    frozen=stream.extractfile('infrastructure/updater/provision.py').read()
assert hashlib.sha256(frozen).hexdigest()==provenance['files']['infrastructure/updater/provision.py']
exec(frozen.decode(),LEGACY.__dict__)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def encode(value):return (json.dumps(value,sort_keys=True,indent=2)+'\n').encode()
APP='com.cleanyourtv.root.preview';SERVICE=APP+'.service';GROUP=SERVICE+'.control'

class Tests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(dir=ROOT);self.addCleanup(self.tmp.cleanup)
        self.base=Path(self.tmp.name);self.root=self.base/'root';self.bus=self.base/'bus';self.apps=self.base/'apps';self.install=self.base/'installation';self.bundle=self.base/'bundle'
        for p in (self.root,self.bus,self.apps,self.install,self.bundle):p.mkdir(mode=0o700)
        (self.bundle/'runtime').mkdir();source=(ROOT/'root-edition/runtime/cli.py').read_bytes();(self.bundle/'runtime/cli.py').write_bytes(source)
        (self.bundle/'bundle.json').write_bytes(encode({'files':{'runtime/cli.py':sha(source)}}))
        code=firmware_access.program(self.bundle);tree=ast.parse(code);ns={};exec(ast.get_source_segment(code,tree.body[0]),ns);self.function=ns['firmware_access']
        self.paths={key:self.bus/folder/(SERVICE+suffix) for key,folder,suffix in [('service','services.d','.service'),('role','roles.d','.service.json'),('client','client-permissions.d','.service.json'),('api','api-permissions.d','.api.json')]}
        self.original={'service':'[D-BUS Service]\nName='+SERVICE+'\nExec=/usr/bin/run-js-service -n '+str(LEGACY.SERVICE)+'\n','role':json.dumps({'appId':SERVICE,'allowedNames':['*'],'permissions':[{'outbound':['*']}]}),'client':'{}','api':'{}'}
        raw=LEGACY.plan(self.original);files={}
        for key,path in self.paths.items():
            path.parent.mkdir(mode=0o700,exist_ok=True);path.write_bytes(raw[key]);path.chmod(0o600)
            files[str(path)]={'original':self.original[key],'original_sha256':sha(self.original[key].encode()),'installed_sha256':sha(raw[key]),'mode':0o600,'uid':os.getuid(),'gid':os.getgid()}
        self.snapshot=self.root/'ls2-provision-snapshot.json';self.snapshot.write_bytes(encode({'version':1,'service':SERVICE,'files':files}));self.snapshot.chmod(0o600)
        code=self.root/'runtime/cli.py';code.parent.mkdir(mode=0o700);code.write_bytes(b'trusted old runtime');code.chmod(0o600)
        self.proof=self.root/'recovery-provision.json';self.proof.write_bytes(encode({'version':1,'mode':'recovery-only','files':{str(code):sha(code.read_bytes())}}));self.proof.chmod(0o600)
        (self.root/'deploy.json').write_bytes(encode({'stage':'installed-recovery-only'}));(self.root/'deploy.json').chmod(0o600)
        info=self.apps/'applications'/APP/'appinfo.json';info.parent.mkdir(parents=True);info.write_bytes(encode({'id':APP,'version':'0.4.0'}));info.chmod(0o600)
        self.manifest=self.bus/'manifests.d'/(APP+'.json');self.manifest.parent.mkdir(mode=0o700)
        self.normal={'version':'0.4.0','id':APP,'serviceFiles':[str(self.paths['service'])],'apiPermissionFiles':[str(self.paths['api'])],'roleFiles':[str(self.paths['role']),str(self.bus/'roles.d'/(APP+'.app.json'))],'clientPermissionFiles':[str(self.paths['client']),str(self.bus/'client-permissions.d'/(APP+'.app.json'))]}
        self.manifest.write_bytes(encode(self.normal));self.manifest.chmod(0o640)
        self.api=self.root/'permissions/homebrew-configuration.api.json';self.receipt=self.root/'firmware-permissions.json';self.events=[]
    def grant(self,enable=True,lock_product=True):
        return self.function(self.root,self.bus,self.apps,self.install,enable=enable,lock_product=lock_product,refresh=lambda:self.events.append('scan'),uid=os.getuid())
    def test_only_configuration_api_and_legacy_updater_bytes_unchanged(self):
        before={p:p.read_bytes() for p in [self.snapshot,self.proof,*self.paths.values()]}
        self.grant();self.grant()
        self.assertEqual(json.loads(self.api.read_bytes()),{GROUP:['org.webosbrew.hbchannel.service/getConfiguration','org.webosbrew.hbchannel.service/setConfiguration']})
        self.assertEqual(json.loads(self.manifest.read_bytes())['apiPermissionFiles'],[str(self.paths['api']),str(self.api)])
        for p,raw in before.items():self.assertEqual(p.read_bytes(),raw)
        # This is the exact computation used by the retained updater's
        # repair_registration; changing snapshot hashes alone is unsafe.
        planned=LEGACY.plan(self.original);entries=json.loads(self.snapshot.read_bytes())['files']
        for key,path in self.paths.items():self.assertEqual(sha(planned[key]),entries[str(path)]['installed_sha256'])
    def test_revoke_restores_manifest_and_original_rollback_revokes_clients(self):
        original=self.manifest.read_bytes();self.grant();self.grant(False)
        self.assertEqual(self.manifest.read_bytes(),original);self.assertFalse(self.api.exists());self.assertEqual(json.loads(self.receipt.read_bytes())['phase'],'disabled')
        self.grant()
        original_clients=json.loads(json.loads(self.snapshot.read_bytes())['files'][str(self.paths['client'])]['original'])
        self.assertFalse(any(GROUP in groups for groups in original_clients.values()),'old provision.rollback removes the grant from every Home client')
    def test_drift_pending_and_poisoned_code_prevent_registration(self):
        for bad in ('drift','link','lease','transaction','proof','manifest'):
            with self.subTest(bad=bad):
                target=self.paths['client'];old=target.read_bytes();normal=self.manifest.read_bytes()
                if bad=='drift':target.write_bytes(b'foreign')
                if bad=='link':target.unlink();target.symlink_to(self.paths['api'])
                if bad=='lease':(self.install/'operation.json').write_bytes(encode({'schema':1,'terminal':False}))
                if bad=='transaction':(self.root.parent/'clean-your-tv-root-updater').mkdir(exist_ok=True);(self.root.parent/'clean-your-tv-root-updater/transaction.json').write_bytes(b'{')
                if bad=='proof':(self.root/'runtime/cli.py').write_bytes(b'tampered')
                if bad=='manifest':self.manifest.write_bytes(encode(dict(self.normal,apiPermissionFiles=['foreign'])))
                with self.assertRaises((ValueError,OSError)):self.grant()
                self.assertFalse(self.api.exists());self.assertFalse(self.receipt.exists())
                if target.is_symlink():target.unlink()
                target.write_bytes(old);target.chmod(0o600);self.manifest.write_bytes(normal)
                (self.install/'operation.json').unlink(missing_ok=True);(self.root.parent/'clean-your-tv-root-updater/transaction.json').unlink(missing_ok=True)
                (self.root/'runtime/cli.py').write_bytes(b'trusted old runtime')
    def test_each_interrupted_write_resumes(self):
        baseline=self.manifest.read_bytes();replace=os.replace
        for cut in range(1,5):
            with self.subTest(cut=cut):
                counter=0
                def crash(src,dst):
                    nonlocal counter
                    replace(src,dst);counter+=1
                    if counter==cut:raise OSError('power loss')
                with patch('os.replace',side_effect=crash),self.assertRaises(OSError):self.grant()
                self.grant();self.assertEqual(json.loads(self.receipt.read_bytes())['phase'],'enabled')
                self.grant(False);self.assertEqual(self.manifest.read_bytes(),baseline)
    def test_new_sdk_version_reconciles_without_changing_retained_snapshot(self):
        self.grant();before=self.snapshot.read_bytes()
        next_manifest=dict(self.normal,version='0.4.1');self.manifest.write_bytes(encode(next_manifest))
        info=self.apps/'applications'/APP/'appinfo.json';info.write_bytes(encode({'id':APP,'version':'0.4.1'}))
        self.grant(lock_product=False)
        self.assertIn(str(self.api),json.loads(self.manifest.read_bytes())['apiPermissionFiles'])
        self.assertEqual(self.snapshot.read_bytes(),before)
        self.grant(False);self.assertEqual(json.loads(self.manifest.read_bytes()),next_manifest)
    def test_scan_failure_is_resumable_and_manifest_metadata_is_preserved(self):
        metadata=self.manifest.stat();self.assertEqual(self.grant()['permissions_installed'],True)
        self.assertEqual((self.manifest.stat().st_uid,self.manifest.stat().st_gid,self.manifest.stat().st_mode),(metadata.st_uid,metadata.st_gid,metadata.st_mode))
        self.grant(False)
        def fail():raise OSError('scan failed')
        with self.assertRaises(OSError):self.function(self.root,self.bus,self.apps,self.install,refresh=fail,uid=os.getuid())
        self.grant();self.assertEqual(json.loads(self.receipt.read_bytes())['phase'],'enabled')
    def test_explicit_revoke_stays_off_during_automatic_registration(self):
        self.grant();self.grant(False)
        self.function(self.root,self.bus,self.apps,self.install,automatic=True,lock_product=False,refresh=lambda:self.events.append('scan'),uid=os.getuid())
        self.assertFalse(self.api.exists());self.assertEqual(json.loads(self.manifest.read_bytes()),self.normal)
        self.grant();self.assertTrue(self.api.exists())
    def test_runtime_registration_failure_never_blocks_home_or_update_finish(self):
        raw=(ROOT/'root-edition/runtime/cli.py').read_text();tree=ast.parse(raw)
        selected=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('execute','reconcile_firmware_access')]
        calls=[]
        def failure(**kwargs):calls.append(kwargs);raise ValueError('permission conflict')
        d=types.SimpleNamespace(STATE=self.root,EXPECTED_UID=os.getuid(),main=lambda mode:{'home':'safe'})
        ns={'d':d,'os':os,'firmware_access':failure}
        for node in selected:exec(ast.get_source_segment(raw,node),ns)
        intent=types.SimpleNamespace(boot=lambda:None)
        updates=types.SimpleNamespace(finish=lambda *args:{'finished':True},suspend=lambda *args:None,abort=lambda *args:None)
        with patch.dict(sys.modules,{'intent_runtime':intent,'update_guard':updates}):
            self.assertEqual(ns['execute']('boot'),{'home':'safe'})
            self.assertEqual(ns['execute']('finish-update','tx'),{'finished':True})
        self.assertEqual(calls,[{'lock_product':False,'automatic':True}]*2)

    def test_host_streams_verified_source_instead_of_a_long_ssh_command(self):
        from cytv.operations import Installer
        from unittest.mock import MagicMock
        calls=[]
        class Remote:
            root=True
            def run(remote,command,data=None,timeout=30):
                calls.append((command,data,timeout));return json.dumps({'returnValue':True,'permissions_installed':True})
        store=MagicMock();store.pending.return_value=None
        import shutil
        payload=self.base/'payload';payload.mkdir();shutil.copytree(self.bundle,payload/'root')
        installer=Installer(Remote(),store,{'edition':'root'},payload,{},lambda *_:None)
        with patch.object(installer,'_python',return_value='/usr/bin/python3'):
            installer.configure_firmware_access(True)
        self.assertLess(len(calls[0][0]),512,'TV SSH servers limit the exec request size')
        self.assertIn('-I -',calls[0][0]);self.assertIn(b'def firmware_access(',calls[0][1])

    def test_sdk_world_writable_containers_are_read_only_and_exactly_scoped(self):
        virtual=self.base/'virtual-media';app=virtual/'developer/apps/usr/palm/applications'/APP
        app.mkdir(parents=True);info=app/'appinfo.json';info.write_bytes(encode({'id':APP,'version':'0.4.0'}));info.chmod(0o600)
        for parent in (app.parent,*list(app.parents)[1:6]):parent.chmod(0o777)
        app.chmod(0o755);virtual.chmod(0o755)
        real_lstat,real_stat,real_open=Path.lstat,Path.stat,os.open
        def translate(path):
            value=str(path)
            return virtual/value[len('/media/'):] if value.startswith('/media/') else virtual if value=='/media' else path
        def mapped_stat(path,*args,**kwargs):return real_stat(translate(path),*args,**kwargs)
        def mapped_open(path,*args,**kwargs):return real_open(translate(path),*args,**kwargs)
        for mode in ('normal','unsafe-app','symlink-container'):
            with self.subTest(mode=mode):
                def mapped_lstat(path):
                    value=real_lstat(translate(path))
                    if mode=='symlink-container' and str(path)=='/media/developer/apps':
                        fields=list(value);fields[0]=0o120777;return os.stat_result(fields)
                    return value
                if mode=='unsafe-app':app.chmod(0o777)
                with patch.object(Path,'lstat',mapped_lstat),patch.object(Path,'stat',mapped_stat),patch('os.open',side_effect=mapped_open):
                    call=lambda enabled:self.function(self.root,self.bus,Path('/media/developer/apps/usr/palm'),self.install,enable=enabled,refresh=lambda:None,uid=os.getuid())
                    if mode=='normal':call(True);self.assertTrue(self.api.exists());call(False)
                    else:
                        with self.assertRaises(ValueError):call(True)
                        self.assertFalse(self.api.exists())
                app.chmod(0o755)

    def test_nondefault_sdk_manifest_gid_is_preserved(self):
        gids=[gid for gid in os.getgroups() if gid!=os.getegid()]
        if not gids:self.skipTest('No alternate permitted group on this host')
        os.chown(self.manifest,-1,gids[0]);before=self.manifest.stat()
        self.grant();self.grant(False)
        after=self.manifest.stat()
        self.assertEqual((after.st_uid,after.st_gid,after.st_mode),(before.st_uid,before.st_gid,before.st_mode))

    def test_completed_registration_does_not_rescan_or_rewrite_on_boot(self):
        self.grant();count=len(self.events);before=self.receipt.stat().st_mtime_ns
        self.function(self.root,self.bus,self.apps,self.install,automatic=True,lock_product=False,refresh=lambda:self.events.append('scan'),uid=os.getuid())
        self.assertEqual(len(self.events),count);self.assertEqual(self.receipt.stat().st_mtime_ns,before)

    def test_executable_program_requires_verified_bundle(self):
        (self.bundle/'runtime/cli.py').write_bytes(b'poisoned')
        with self.assertRaises(ValueError):firmware_access.program(self.bundle)
