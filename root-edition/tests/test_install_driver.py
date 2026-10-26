import os
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from updater.store import Store
from installation import Ownership, Busy
import install_driver

class Device:
    def __init__(self, fail=None): self.calls=[]; self.fail=fail; self.installed=False
    def call(self, name):
        self.calls.append(name)
        if name == self.fail: raise RuntimeError('private diagnostic')
    def preflight(self, payload, options): self.call('preflight')
    def inspect(self):
        self.call('inspect')
        return {'state':'installed' if self.installed else 'fresh'}
    def deploy(self, payload, options): self.call('deploy')
    def updater(self, payload, options): self.call('updater'); self.installed=True
    def supervisor(self, payload, options): self.call('supervisor')
    def readback(self): self.call('readback'); return {'verified':True}
    def restore(self): self.call('restore')
    def remove(self, checkpoint):
        checkpoint('remove-submitting'); self.call('remove'); checkpoint('remove-terminal')
        return {'removed':True}

class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.store=Store(Path(self.tmp.name).resolve()/'state',uid=os.getuid())
        self.owner=Ownership(self.store); self.device=Device()
        self.driver=install_driver.Coordinator(self.device,self.owner,read=lambda path:None); self.identifier='a'*32
    def test_order_and_no_activation(self):
        result=self.driver.install(self.identifier,'/verified',prepare_supervisor=True)
        self.assertEqual(self.device.calls,['preflight','inspect','deploy','updater','supervisor','readback'])
        self.assertEqual(result['state'],'complete'); self.assertTrue(self.owner.status()['terminal'])
        self.assertFalse(result['home_changed'])
    def test_failure_at_every_boundary_retains_ownership_and_never_replays(self):
        for boundary in ('deploy','updater','supervisor','readback'):
            with self.subTest(boundary=boundary), tempfile.TemporaryDirectory() as tmp:
                owner=Ownership(Store(Path(tmp).resolve()/'state',uid=os.getuid()))
                device=Device(boundary); driver=install_driver.Coordinator(device,owner,read=lambda path:None)
                result=driver.install(self.identifier,'/verified',prepare_supervisor=True)
                self.assertEqual(result['state'],'recovery_required'); self.assertFalse(owner.status()['terminal'])
                calls=list(device.calls)
                self.assertEqual(driver.install(self.identifier,'/verified',prepare_supervisor=True),result)
                self.assertEqual(device.calls,calls)
                with self.assertRaises(Busy): driver.install('b'*32,'/verified')
                self.assertNotIn('private diagnostic',str(result))
    def test_same_contract_handoff_maintains_without_submission(self):
        self.device.installed=True
        self.assertEqual(self.driver.install(self.identifier,'/verified')['state'],'complete')
        self.assertEqual(self.device.calls,['preflight','inspect','readback'])
    def test_retained_state_is_never_overwritten(self):
        self.device.inspect=lambda:{'state':'recovery_required'}
        result=self.driver.install(self.identifier,'/verified')
        self.assertEqual(result['code'],'installation_requires_recovery')
        self.assertEqual(self.device.calls,['preflight']); self.assertFalse(self.owner.status()['terminal'])
    def test_removal_holds_lease_and_retains_uncertain_submission(self):
        def remove(checkpoint):
            checkpoint('remove-submitting')
            with self.assertRaises(Busy):
                with Ownership(self.store).operation('deploy','deploy.json'): pass
            raise RuntimeError('lost terminal')
        self.device.remove=remove
        result=self.driver.remove(self.identifier)
        self.assertEqual(result['state'],'recovery_required')
        self.assertEqual(self.owner.status()['stage'],'remove-submitting')
        self.assertEqual(self.driver.remove(self.identifier),result)
    def test_status_and_restore_remain_available(self):
        self.device.fail='deploy'; self.driver.install(self.identifier,'/verified')
        self.assertEqual(self.driver.status(self.identifier)['state'],'recovery_required')
        self.driver.restore(); self.assertEqual(self.device.calls[-1],'restore')
        self.assertFalse(self.owner.status()['terminal'])
    def test_invalid_identifier_and_options_do_not_mutate(self):
        for identifier in ('../operation','A'*32,'a'*31,None):
            with self.assertRaises(ValueError): self.driver.install(identifier,'/verified')
        with self.assertRaises(ValueError): self.driver.install(self.identifier,'/verified',migrate=1)
        self.assertEqual(self.device.calls,[]); self.assertIsNone(self.owner.status())

class ActivationTests(unittest.TestCase):
    def test_pending_product_blocks_direct_root_activation_but_terminal_allows(self):
        import importlib.util
        path=Path(__file__).resolve().parents[1]/'runtime/update_guard.py'
        spec=importlib.util.spec_from_file_location('product_update_guard',path)
        guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()/'root';root.mkdir(mode=0o700)
            ownership=Ownership(Store(root.parent/'clean-your-tv-installation',uid=os.getuid()))
            with ownership.operation('product','product.json') as record:
                with self.assertRaises(guard.ProductPending):
                    with guard.control(root,os.getuid()): pass
            with self.assertRaises(guard.ProductPending):
                with guard.control(root,os.getuid()): pass
            with ownership.operation('product','product.json',resume=record['id']) as record:
                ownership.stage(record,'complete',terminal=True)
            with guard.control(root,os.getuid()): pass

    def test_direct_activation_serializes_with_product_ownership(self):
        import importlib.util
        path=Path(__file__).resolve().parents[1]/'runtime/update_guard.py'
        spec=importlib.util.spec_from_file_location('product_update_guard_race',path)
        guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve()/'root';root.mkdir(mode=0o700)
            ownership=Ownership(Store(root.parent/'clean-your-tv-installation',uid=os.getuid()))
            with guard.control(root,os.getuid()):
                with self.assertRaises(Busy):
                    with ownership.operation('product','product.json'): pass

class LocalRemovalTests(unittest.TestCase):
    def run_device(self, fail=None, apps=None, busy=None):
        from unittest.mock import patch
        import install_device
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        base=Path(temp.name).resolve();root=base/'root';root.mkdir()
        owner=Ownership(Store(base/'ownership',uid=os.getuid()))
        calls=[];present=set(apps if apps is not None else (install_device.APP,'com.cleanyourtv.root.updater','com.cleanyourtv.updater','com.local.nativehome','com.gathin.tvhome','com.cleanyourtv.system.updater'))
        class Model(install_device.LocalDevice):
            def log(self,error): pass
            def validate_root_driver(self): self.boundary('validate-root-driver')
            def boundary(self,name):
                self.assert_lease()
                calls.append(name)
                if name==fail: raise RuntimeError('private boundary failure')
            def assert_lease(self):
                if owner.status()['terminal']: raise AssertionError('lease released early')
                try:
                    with Ownership(owner.store).operation('foreign','transaction.json'): pass
                except Busy: pass
                else: raise AssertionError('foreign mutation entered removal')
            def apps(self): return set(present)
            def rpc(self,method,payload):
                self.boundary(method)
                if method.endswith('/status'):
                    return {'returnValue':True,'status':{'apps':[]},'result':{'transaction':None}}
                if method.endswith('/getAllInputStatus'): return {'devices':[]}
                return {'returnValue':True}
            def cleanup(self,name,*args):
                self.boundary('cleanup-'+name+'-'+(args[0] if args else ''))
                if name=='root_archive':
                    value=busy.pop(0) if busy and len(busy)>1 else (busy[0] if busy else False)
                    if isinstance(value,Exception): raise value
                    return {'busy':value}
                return {'disabled':True,'removed':True,'archive':'saved-'+name}
            def absent(self,app,terminal=None):
                self.boundary('absent-'+app)
                if app in present: raise ValueError('package remains')
            def verify_removed(self):
                self.boundary('verify-removed')
                if present: raise ValueError('packages remain')
        device=Model()
        def root_remove():
            device.boundary('root-remove');present.discard(install_device.APP)
            return {'removed':install_device.APP,'state_retained':str(root)}
        def package_remove(app,timeout):
            device.boundary('remove-'+app);present.discard(app)
            return {'completed':True,'event':{'id':app,'statusValue':31,'details':{'packageId':app,'state':'removed'}}}
        elapsed=[0]
        def sleep(seconds):elapsed[0]+=seconds
        with patch.object(install_device,'ROOT',root),patch.object(install_device,'SUPERVISOR',base/'supervisor'),patch('deploy.uninstall',root_remove),patch('observed_install.remove',package_remove),patch('time.monotonic',lambda:elapsed[0]),patch('time.sleep',sleep):
            result=install_driver.Coordinator(device,owner,read=lambda p:None).remove('a'*32)
        return result,owner,calls,present,elapsed

    def test_complete_sequence_retains_exact_terminals_and_global_ownership(self):
        result,owner,calls,present,_=self.run_device()
        self.assertEqual(result['state'],'complete');self.assertFalse(present)
        self.assertTrue(owner.status()['terminal'])
        self.assertLess(calls.index('cleanup-system_updater-disable'),calls.index('root-remove'))
        self.assertLess(calls.index('cleanup-root_updater-disable'),calls.index('root-remove'))
        self.assertLess(calls.index('root-remove'),calls.index('remove-com.cleanyourtv.root.updater'))
        self.assertLess(calls.index('cleanup-app_permissions-'),calls.index('cleanup-root_updater-finalize'))
        record=owner.store.read('removal-'+owner.status()['id'])
        for app,value in record['removals'].items():
            self.assertEqual(value['state'],'terminal')
            self.assertEqual(value['evidence']['event']['details']['packageId'],app)

    def test_every_effect_boundary_failure_keeps_reservation(self):
        _,_,boundaries,_,_=self.run_device()
        for boundary in boundaries:
            with self.subTest(boundary=boundary):
                result,owner,calls,_,_=self.run_device(fail=boundary)
                self.assertEqual(result['state'],'recovery_required')
                self.assertFalse(owner.status()['terminal'])
                self.assertEqual(calls[-1],boundary)

    def test_leftover_updater_does_not_resubmit_absent_root(self):
        result,_,calls,_,_=self.run_device(apps={'com.cleanyourtv.root.updater'})
        self.assertEqual(result['state'],'complete');self.assertNotIn('root-remove',calls)
        self.assertEqual([c for c in calls if c.startswith('remove-')],['remove-com.cleanyourtv.root.updater'])

    def test_root_exit_wait_and_failure_keep_ownership(self):
        for busy,success in (([False],True),([True,True,False],True),([True],False),([RuntimeError('private')],False)):
            with self.subTest(busy=busy):
                result,owner,_,_,elapsed=self.run_device(apps=set(),busy=busy)
                self.assertEqual(result['state'],'complete' if success else 'recovery_required')
                self.assertEqual(owner.status()['terminal'],success)
                self.assertLessEqual(elapsed[0],60)

class CurrentByteReadbackTests(unittest.TestCase):
    def fixture(self):
        import hashlib,json
        from cytv import package
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        base=Path(temp.name).resolve();root=base/'root';root.mkdir()
        updater=base/'updater';store=Store(updater,uid=os.getuid());(updater/'cache').mkdir()
        app='com.cleanyourtv.root.preview';prefix='usr/palm/applications/'+app+'/'
        files={prefix+'appinfo.json':json.dumps({'id':app,'version':'1.0.0','type':'web','main':'index.html'}).encode(),
               prefix+'index.html':b'current UI',prefix+'apps.js':b'personalized inventory',prefix+'config.js':b'personalized preferences',
               prefix+'startup.sh':b'#!/bin/sh\nexit 0\n','usr/palm/packages/'+app+'/packageinfo.json':json.dumps({'id':app,'app':app,'version':'1.0.0','services':[]}).encode()}
        raw=package.ipk(app,'1.0.0',files,executable=(prefix+'startup.sh',))
        parts=package.read_ar(raw);parts['data.tar.gz']=package.tgz(files,executable=(prefix+'startup.sh',),directories=False)
        parts['control.tar.gz']=package.tgz({'control':('Package: '+app+'\nVersion: 1.0.0\n').encode()},directories=False)
        raw=package.ar(parts)
        descriptor={'local':True,'version':'1.0.0','size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
        (updater/'cache'/(descriptor['sha256']+'.ipk')).write_bytes(raw);store.write('current',descriptor)
        installed=base/'installed'
        for name,data in files.items():
            target=installed/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);target.chmod(0o755 if name.endswith('startup.sh') else 0o644)
        return root,updater,installed,store,files

    def test_both_entry_points_validate_exact_bytes_and_leave_profile_and_off_latch(self):
        from unittest.mock import patch
        import install_device
        root,updater,installed,store,files=self.fixture()
        marker=root/'emergency-off';marker.write_bytes(b'off')
        before={name:(installed/name).read_bytes() for name in files}
        with patch('updater.device.Device.integrity',return_value={}):
            for origin in ('cytv','homebrew'):
                with self.subTest(origin=origin):
                    result=install_device.current_root(root,updater,installed,uid=os.getuid())
                    self.assertTrue(result['local']);self.assertEqual(marker.read_bytes(),b'off')
                    self.assertEqual({n:(installed/n).read_bytes() for n in files},before)
        startup=next(n for n in files if n.endswith('startup.sh'))
        self.assertEqual((installed/startup).stat().st_mode & 0o777,0o755)

    def test_byte_or_executable_mode_drift_refuses_current_contract(self):
        from unittest.mock import patch
        import install_device
        for change in ('bytes','mode'):
            root,updater,installed,_,files=self.fixture()
            startup=installed/next(n for n in files if n.endswith('startup.sh'))
            if change=='bytes':startup.write_bytes(b'changed')
            else:startup.chmod(0o644)
            with self.subTest(change=change),patch('updater.device.Device.integrity',return_value={}),self.assertRaises(ValueError):
                install_device.current_root(root,updater,installed,uid=os.getuid())

    def test_invalid_saved_profile_is_recovery_and_never_rewritten(self):
        from unittest.mock import patch
        import install_device
        root,updater,installed,store,_=self.fixture()
        profile={'schema':2,'private':'retained'}
        store.write('profile-'+'a'*32,profile)
        tx={'phase':'complete','homeResumePhase':'complete','profile':'profile-'+'a'*32,'profileDigest':'0'*64}
        store.write('transaction',tx)
        with patch('updater.device.Device.integrity',return_value={}),self.assertRaises(ValueError):
            install_device.current_root(root,updater,installed,uid=os.getuid())
        self.assertEqual(store.read('profile-'+'a'*32),profile)

    def test_unknown_legacy_updater_receipt_requires_migration(self):
        import install_device
        _,updater,installed,_,_=self.fixture()
        with self.assertRaisesRegex(ValueError,'migration'):
            install_device.current_updater(updater,installed,uid=os.getuid())

class WorkerDurabilityTests(unittest.TestCase):
    def test_process_death_after_submission_returns_status_without_replay(self):
        import subprocess
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name).resolve();state=root/'ownership';marker=root/'submissions'
        code='''import os,sys
sys.path.insert(0,sys.argv[1])
from install_driver import Coordinator
from installation import Ownership
from updater.store import Store
class Device:
 def preflight(self,*args):pass
 def inspect(self):return {'state':'fresh'}
 def deploy(self,*args):
  with open(sys.argv[3],'a') as out:out.write('submitted\\n');out.flush();os.fsync(out.fileno())
  os._exit(23)
Coordinator(Device(),Ownership(Store(sys.argv[2],uid=os.getuid())),read=lambda p:None).install('a'*32,'/verified')
'''
        result=subprocess.run([sys.executable,'-c',code,str(Path(__file__).resolve().parents[1]),str(state),str(marker)])
        self.assertEqual(result.returncode,23)
        owner=Ownership(Store(state,uid=os.getuid()));device=Device()
        driver=install_driver.Coordinator(device,owner,read=lambda p:None)
        self.assertEqual(driver.status('a'*32)['state'],'pending')
        self.assertEqual(driver.install('a'*32,'/verified')['state'],'pending')
        self.assertEqual(device.calls,[]);self.assertEqual(marker.read_text(),'submitted\n')
        self.assertFalse(owner.status()['terminal'])

    def submission_fixture(self):
        import json
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name).resolve();payload=root/'payload';payload.mkdir()
        inventories={}
        for name in ('root','root-updater'):
            bundle=payload/name;bundle.mkdir();(bundle/'install_driver.py').write_bytes(b'verified worker v1')
            import hashlib
            manifest={'files':{'install_driver.py':hashlib.sha256(b'verified worker v1').hexdigest()}}
            (bundle/'bundle.json').write_text(json.dumps(manifest));inventories[name]=manifest
        owner=Ownership(Store(root/'ownership',uid=os.getuid()))
        return root,payload,inventories,owner

    def test_detached_snapshot_survives_package_replacement_and_lost_reply(self):
        from unittest.mock import patch
        import install_device
        root,payload,inventories,owner=self.submission_fixture()
        with patch('install_driver._verified_payload',return_value=inventories),patch.object(install_device.LocalDevice,'preflight'),patch('subprocess.Popen') as spawn:
            record=install_driver.submit('a'*32,payload,ownership=owner)
            self.assertEqual(record['state'],'pending');self.assertTrue(spawn.call_args.kwargs['start_new_session'])
            (payload/'root-updater/install_driver.py').write_bytes(b'replaced installer v2')
            snapshot=Path(owner.store.root)/('request-'+'a'*32)/'root-updater/install_driver.py'
            self.assertEqual(snapshot.read_bytes(),b'verified worker v1')
            self.assertEqual(install_driver.submit('a'*32,payload,ownership=owner)['state'],'pending')
            self.assertEqual(spawn.call_count,1)

    def test_failed_spawn_is_retained_and_cannot_be_resubmitted(self):
        from unittest.mock import patch
        import install_device
        _,payload,inventories,owner=self.submission_fixture()
        with patch('install_driver._verified_payload',return_value=inventories),patch.object(install_device.LocalDevice,'preflight'),patch('subprocess.Popen',side_effect=OSError('private')) as spawn:
            self.assertEqual(install_driver.submit('a'*32,payload,ownership=owner)['state'],'recovery_required')
            self.assertEqual(install_driver.submit('a'*32,payload,ownership=owner)['state'],'recovery_required')
            self.assertEqual(spawn.call_count,1)

    def test_changed_reviewed_candidate_never_stages_or_spawns(self):
        from unittest.mock import patch
        _,payload,inventories,owner=self.submission_fixture()
        with patch('install_driver._verified_payload',return_value=inventories),patch('subprocess.Popen') as spawn:
            with self.assertRaisesRegex(ValueError,'candidate_changed'):
                install_driver.submit('a'*32,payload,candidate='0'*64,ownership=owner)
            spawn.assert_not_called()
            self.assertIsNone(owner.store.read('submission-'+'a'*32))

class ReservationRaceTests(unittest.TestCase):
    def test_completed_concurrent_request_does_not_leave_new_reserved_lease(self):
        from contextlib import contextmanager
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        store=Store(Path(temp.name).resolve()/'ownership',uid=os.getuid());owner=Ownership(store)
        original=owner.operation
        completed={'operation':'a'*32,'action':'install','stage':'complete','state':'complete','code':'verified','home_changed':False,'result':{'verified':True}}
        @contextmanager
        def racing(*args,**kwargs):
            store.write('request-'+'a'*32,completed)
            with original(*args,**kwargs) as record: yield record
        owner.operation=racing
        result=install_driver.Coordinator(Device(),owner,read=lambda path:None).install('a'*32,'/verified')
        self.assertEqual(result,completed)
        self.assertIsNone(owner.status())
