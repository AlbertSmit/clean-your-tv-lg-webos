"""Original synchronous System submission with real private owner authority."""
import copy
from contextlib import contextmanager, nullcontext
import os
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from test_core import profile
from test_device import tar
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'root-edition/tests'))
import test_package_identity as fixture_support
import package_identity as p
from system_updater.core import Manager
from system_updater.device import Device
from system_updater.support.store import encode


class OriginalSubmissionTests(unittest.TestCase):
    @contextmanager
    def original(self,index=0):
        fixture=fixture_support.IdentityTests();fixture.setUp()
        try:
            store=fixture.stores[p.SYSTEM];own=fixture.packages[p.SYSTEM];descriptor=own[0]
            store.write('bootstrap-bundle',{'schema':1,'package':{k:descriptor[k] for k in ('sha256','size')}})
            store.write('bootstrap',{'phase':'complete'})
            store.write('installed-package',{'schema':1,'package':descriptor,'files':own[2]})
            store.write('installed-terminal',{'completed':True,'event':{'id':p.SYSTEM,'statusValue':30,'details':{'packageId':p.SYSTEM,'client':'com.webos.lunasend-99','ipkFile':'/var/lib/clean-your-tv-installer/cytv-root-install-fixture/package.ipk'}}})
            tx=fixture.system_tx('installing');tx['release']='v1.1.0'
            # An independently proved, already completed local leg keeps this
            # fixture focused on the two SDK legs. Its readback remains real.
            code=fixture.base/'code';code.mkdir();(code/'infrastructure-paths.json').write_text('["runtime/fixture.py"]')
            for key,version in (('prior','1.0.0'),('candidate','1.1.0')):
                tx[key].update(release='v'+version,supervisor=1,notes='Fixture')
                raw=tar({'runtime/fixture.py':version.encode()})
                tx[key]['components'][2].update(sha256=p.digest(raw),size=len(raw),files={'runtime/fixture.py':p.digest(version.encode())},absent=[])
                (Path(store.root)/'cache'/p.digest(raw)).write_bytes(raw)
            target=fixture.states[p.ROOT]/'runtime/fixture.py';target.parent.mkdir();target.write_bytes(b'1.1.0')
            tx['components'][2]['installEvidence']=dict(fixture.success(),intent=True)
            tx['candidate']['proof']={'original':'fixture-signature'}
            for previous in range(index):
                owner=(p.ROOT,p.UPDATER)[previous]
                fixture.install(owner,fixture.package(owner,'1.1.0'))
                tx['components'][previous]['installEvidence']=dict(fixture.success(),intent=True)
            snapshot=profile();store.write(tx['profile'],snapshot);tx['profileDigest']=p.digest(encode(snapshot))
            store.write('baseline',tx['prior']);store.write('transaction',tx)
            fixture.stores[p.ROOT].write('intent',{'enabled':False,'emergency':True})
            device=Device(store,code=code,root_state=fixture.states[p.ROOT],root_updater=fixture.states[p.UPDATER],installed=fixture.installed,uid=fixture.uid)
            device.check_legacy=lambda:None;device.routing_safe=lambda:True;device.now=lambda:1000
            # The signed-release verifier is external; original release matching,
            # cache parsing, owner selection and installed readback remain real.
            def verify(method,payload=None,binary=False):
                self.assertEqual(method,'verify');self.assertEqual(payload,{'proof':{'original':'fixture-signature'}})
                return {k:copy.deepcopy(v) for k,v in tx['candidate'].items() if k!='proof'}
            device.fetch=verify
            def effect():
                current=store.read('transaction')
                self.assertTrue(current['components'][index]['installEvidence']['intent'])
            device.integrity=lambda **kw:None;device.enforce_legacy_lockdown=effect;device.snapshot_mutable=effect
            device.restore_mutable=lambda:None;device.repair_registrations=lambda:None;device.launch=lambda edition:None
            yield fixture,store,device,tx
        finally:fixture.tearDown()

    def transport(self,fixture,store):
        def install(owner,path,**kw):
            index=(p.ROOT,p.UPDATER).index(owner);e=store.read('transaction')['components'][index]['installEvidence']
            self.assertTrue(e['intent']);self.assertIsNone(e['submitted']);self.assertIsNone(e['terminal'])
            selected=store.read('transaction')['candidate']['components'][index]
            self.assertEqual(Path(path).name,selected['sha256'])
            kw['on_ready']()
            fixture.install(owner,fixture.package(owner,'1.1.0'))
            return {'completed':True,'event':{'id':owner,'statusValue':30,'details':{'packageId':owner,'client':'com.webos.lunasend-99','ipkFile':'/var/lib/clean-your-tv-installer/cytv-root-install-fixture/package.ipk'}}}
        return install

    def test_original_root_and_updater_submit_once_then_reach_candidate_health(self):
        with self.original() as (fixture,store,device,tx):
            observed=[];observe=device.owner_identity
            device.owner_identity=lambda owner,**kw:observed.append(owner) or observe(owner,**kw)
            with patch('observed_install.install',side_effect=self.transport(fixture,store)) as submit:
                manager=Manager(store,device)
                for index in (0,1):
                    observed.clear();result=manager.run()
                    self.assertEqual(result['phase'],'installing',result.get('error'))
                    self.assertEqual(set(observed),{p.SYSTEM,p.ROOT,p.UPDATER})
                    evidence=result['components'][index]['installEvidence']
                    self.assertTrue(evidence['terminal']['success'])
                    self.assertEqual(evidence['terminal']['event']['statusValue'],30)
                    self.assertEqual(submit.call_count,index+1)
                    self.assertEqual(fixture.identity((p.ROOT,p.UPDATER)[index],purpose='worker')['version'],'1.1.0')
                self.assertEqual(manager.run()['phase'],'verifying')
                manager.healthy('root',tx['id'],'1.1.0');self.assertEqual(manager.run()['phase'],'complete')
                self.assertEqual(submit.call_count,2)
            self.assertEqual(fixture.stores[p.ROOT].read('intent'),{'enabled':False,'emergency':True})
            self.assertEqual(store.read(tx['profile']),profile())

    def test_original_preflight_refuses_missing_or_changed_untouched_owner(self):
        for index in (0,1):
            for owner in (p.SYSTEM,(p.UPDATER,p.ROOT)[index]):
                for condition in ('missing','changed'):
                    with self.subTest(index=index,owner=owner,condition=condition),self.original(index) as (fixture,store,device,tx):
                        path=fixture.installed/'usr/palm/applications'/owner/'appinfo.json'
                        if condition=='missing':path.unlink()
                        else:path.write_bytes(path.read_bytes().replace(b'1.',b'9.'))
                        with patch('observed_install.install',side_effect=AssertionError('owner refusal must precede transport')) as submit:
                            result=Manager(store,device).run()
                            self.assertEqual(submit.call_count,0)
                        self.assertFalse(result['components'][index]['installEvidence']['intent'])
                        self.assertEqual(result['components'],tx['components'])
                        self.assertEqual(store.read(tx['profile']),profile())
                        self.assertEqual(fixture.stores[p.ROOT].read('intent'),{'enabled':False,'emergency':True})

    def test_interrupted_original_before_or_after_transport_never_replays(self):
        from system_updater import cli
        for index in (0,1):
            for boundary in ('before-transport','after-transport'):
                with self.subTest(index=index,boundary=boundary),self.original(index) as (fixture,store,device,tx):
                    def interrupt(*args,**kw):
                        if kw:
                            kw['on_ready']()
                            fixture.install((p.ROOT,p.UPDATER)[index],fixture.package((p.ROOT,p.UPDATER)[index],'1.1.0'))
                        raise KeyboardInterrupt('power loss')
                    if boundary=='before-transport':device.snapshot_mutable=interrupt
                    with patch('observed_install.install',side_effect=interrupt) as submit:
                        with self.assertRaises(KeyboardInterrupt):Manager(store,device).run()
                        original=store.read('transaction')['components']
                        evidence=original[index]['installEvidence']
                        self.assertTrue(evidence['intent']);self.assertIsNone(evidence['terminal'])
                        self.assertEqual(evidence['submitted'] is not None,boundary=='after-transport')
                        for purpose in ('current','worker','admission','live'):
                            with self.assertRaises(p.TransitionUnknown):fixture.identity(p.ROOT if purpose=='live' else (p.ROOT,p.UPDATER)[index],purpose=purpose)
                        manager=Manager(store,device)
                        self.assertEqual(manager.run()['phase'],'recovery-required')
                        manager.rollback();self.assertEqual(store.read('transaction')['components'],original)
                        # Exercise the real fresh worker as well as fresh Manager.
                        actual_fstat=os.fstat
                        def fstat(fd):
                            info=actual_fstat(fd);lock=Path(store.root)/'daemon.lock'
                            if lock.exists() and info.st_ino==lock.stat().st_ino:
                                values={n:getattr(info,n) for n in dir(info) if n.startswith('st_')};values['st_uid']=0
                                return SimpleNamespace(**values)
                            return info
                        with patch.object(cli.os,'fstat',side_effect=fstat),patch('installation.device_operation',return_value=nullcontext()):cli.worker(store,device)
                        self.assertEqual(submit.call_count,0 if boundary=='before-transport' else 1)
                    self.assertEqual(store.read('transaction')['components'],original)
                    self.assertFalse(store.read('transaction')['rollbackAttempted'])
                    self.assertEqual(store.read(tx['profile']),profile())
                    self.assertEqual(fixture.stores[p.ROOT].read('intent'),{'enabled':False,'emergency':True})

    def test_corrupt_original_candidate_cache_cannot_record_intent_or_submit(self):
        for index in (0,1):
            with self.subTest(index=index),self.original(index) as (fixture,store,device,tx):
                descriptor=tx['candidate']['components'][index]
                (Path(store.root)/'cache'/descriptor['sha256']).write_bytes(b'x'*descriptor['size'])
                with patch('observed_install.install',side_effect=AssertionError('unverified cache submitted')) as submit:
                    result=Manager(store,device).run()
                    self.assertEqual(submit.call_count,0)
                self.assertFalse(result['components'][index]['installEvidence']['intent'])

    def test_direct_adapter_cannot_bypass_unknown_original_intent(self):
        for index in (0,1):
            with self.subTest(index=index),self.original(index) as (fixture,store,device,tx):
                tx['components'][index]['installEvidence']['intent']=True;store.write('transaction',tx)
                with patch('observed_install.install') as submit,patch.object(device,'integrity') as effects:
                    with self.assertRaises(p.TransitionUnknown):
                        device.install(tx['candidate']['components'][index],self.fail,self.fail,self.fail)
                    self.assertEqual(submit.call_count,0);self.assertEqual(effects.call_count,0)

    def test_post_intent_lockdown_failure_stays_unknown_without_submission(self):
        with self.original() as (fixture,store,device,tx):
            def failed_integrity():
                self.assertTrue(store.read('transaction')['components'][0]['installEvidence']['intent'])
                raise ValueError('private infrastructure changed')
            device.enforce_legacy_lockdown=failed_integrity
            with patch('observed_install.install') as submit:
                result=Manager(store,device).run()
                self.assertEqual(result['phase'],'recovery-required')
                self.assertTrue(result['components'][0]['installEvidence']['intent'])
                self.assertIsNone(result['components'][0]['installEvidence']['submitted'])
                self.assertEqual(Manager(store,device).run()['phase'],'recovery-required')
                self.assertEqual(submit.call_count,0)

    def test_interruption_before_durable_intent_has_no_effect_and_can_start_once(self):
        with self.original() as (fixture,store,device,tx):
            write=store.write
            def interrupted_write(name,value):
                if name=='transaction' and value['components'][0]['installEvidence']['intent']:
                    raise KeyboardInterrupt('power loss before durable intent')
                return write(name,value)
            with patch.object(store,'write',side_effect=interrupted_write),patch.object(device,'enforce_legacy_lockdown') as effects,patch('observed_install.install') as submit:
                with self.assertRaises(KeyboardInterrupt):Manager(store,device).run()
                self.assertEqual(effects.call_count,0);self.assertEqual(submit.call_count,0)
            self.assertEqual(store.read('transaction'),tx)
            self.assertEqual(fixture.identity(p.ROOT,purpose='worker')['version'],'1.0.0')
            with patch('observed_install.install',side_effect=self.transport(fixture,store)) as submit:
                result=Manager(store,device).run()
                self.assertTrue(result['components'][0]['installEvidence']['terminal']['success'])
                self.assertEqual(submit.call_count,1)

    def test_private_preflight_intent_and_effects_keep_their_required_order(self):
        with self.original() as (fixture,store,device,tx):
            order=[];verify=device.fetch;write=store.write;transport=self.transport(fixture,store)
            def integrity(*,enforce=True):
                self.assertFalse(enforce);self.assertFalse(store.read('transaction')['components'][0]['installEvidence']['intent'])
                order.append('private-integrity')
            def fetch(*args,**kw):order.append('release-verifier');return verify(*args,**kw)
            def save(name,value):
                if name=='transaction' and value['components'][0]['installEvidence']['intent'] and not store.read(name)['components'][0]['installEvidence']['intent']:
                    order.append('intent')
                return write(name,value)
            def lockdown():
                self.assertTrue(store.read('transaction')['components'][0]['installEvidence']['intent']);order.append('lockdown')
            def install(*args,**kw):order.append('transport');return transport(*args,**kw)
            device.integrity=integrity;device.fetch=fetch;device.enforce_legacy_lockdown=lockdown
            with patch.object(store,'write',side_effect=save),patch('observed_install.install',side_effect=install):
                result=Manager(store,device).run()
            self.assertTrue(result['components'][0]['installEvidence']['terminal']['success'])
            self.assertEqual(order,['private-integrity','release-verifier','intent','lockdown','transport'])
