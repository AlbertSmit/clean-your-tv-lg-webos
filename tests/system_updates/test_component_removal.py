"""Deletion never submits another install or promotes an unresolved transaction."""
import copy
import importlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from test_core import CoreBase, profile

class SystemRemovalTests(CoreBase):
    def test_disappearance_at_every_phase_stops_without_replay_and_retains_profile(self):
        phases=('preparing','downloading','backed-up','suspending','installing','verifying','rolling-back','verifying-rollback')
        for phase in phases:
            with self.subTest(phase=phase),tempfile.TemporaryDirectory() as temp:
                from test_core import IO, Store
                io=IO();store=Store(Path(temp).resolve(),uid=os.getuid());manager=self.Manager(store,io)
                manager.install('no-root','v1.1.0',profile())
                if phase=='verifying-rollback':
                    self._advance(manager,'verifying');manager.rollback();self._advance(manager,phase)
                elif phase=='rolling-back':
                    self._advance(manager,'verifying');manager.rollback()
                else:self._advance(manager,phase)
                prior=copy.deepcopy(store.read('transaction'));calls=list(io.calls)
                result=manager.component_removed()
                self.assertIn(result['phase'],('aborted','recovery-required'))
                self.assertEqual([c for c in io.calls if c.startswith('install:')],[c for c in calls if c.startswith('install:')])
                self.assertEqual(result['components'],prior['components'])
                self.assertEqual(store.read(prior['profile']),profile())
                self.assertEqual(manager.run()['phase'],result['phase'])
    def _advance(self,manager,phase):
        for _ in range(40):
            if manager.status()['phase']==phase:return
            manager.run()
        self.fail(manager.status())

class PackagePresenceTests(unittest.TestCase):
    def test_unproven_owner_is_never_learned_from_sdk_metadata(self):
        from system_updater.device import Device
        with tempfile.TemporaryDirectory() as temp:
            from test_core import Store
            root=Path(temp).resolve();installed=root/'installed';installed.mkdir()
            device=Device(Store(root/'state',uid=os.getuid()),installed=installed,uid=os.getuid())
            with self.assertRaisesRegex(ValueError,'own-package proof'):device.components_present()
            app=installed/'usr/palm/applications/com.cleanyourtv.system.updater';app.mkdir(parents=True)
            (app/'appinfo.json').write_text(json.dumps({'id':'com.cleanyourtv.system.updater','type':'web','version':'1.1.0'}))
            with self.assertRaisesRegex(ValueError,'own-package proof'):device.components_present()
            self.assertFalse((root/'state/installed-package.json').exists())

class CombinedOwnerPresenceTests(unittest.TestCase):
    def test_all_owners_checked_before_touched_transition_is_deferred(self):
        from contextlib import ExitStack,nullcontext
        from types import SimpleNamespace
        from unittest.mock import patch
        sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'root-edition/tests'))
        import test_package_identity as fixtures
        import package_identity as p
        from system_updater.device import Device
        from system_updater import cli
        from system_updater.support.store import encode
        for touched in (p.ROOT,p.UPDATER):
            for condition in ('absent','changed'):
                with self.subTest(touched=touched,condition=condition),ExitStack() as stack:
                    fixture=fixtures.IdentityTests();fixture.setUp();stack.callback(fixture.tearDown)
                    state=fixture.states[p.SYSTEM];store=fixture.stores[p.SYSTEM]
                    own=fixture.packages[p.SYSTEM];descriptor=own[0]
                    store.write('bootstrap-bundle',{'schema':1,'package':{k:descriptor[k] for k in ('sha256','size')}})
                    store.write('bootstrap',{'phase':'complete'})
                    store.write('installed-package',{'schema':1,'package':descriptor,'files':own[2]})
                    store.write('installed-terminal',{'completed':True,'event':{'id':p.SYSTEM,'statusValue':30,'details':{'packageId':p.SYSTEM,'client':'com.webos.lunasend-99','ipkFile':'/var/lib/clean-your-tv-installer/cytv-root-install-fixture/package.ipk'}}})
                    tx=fixture.system_tx('rolling-back');index=0 if touched==p.ROOT else 1
                    tx['components'][index]['installEvidence']={'intent':True,'submitted':{'original':'request'},'terminal':{'success':False}}
                    for key,version in (('prior','1.0.0'),('candidate','1.1.0')):tx[key].update(release='v'+version,supervisor=1,notes='Original fixture')
                    tx['release']='v1.1.0';snapshot=profile();tx['profileDigest']=p.digest(encode(snapshot));store.write(tx['profile'],snapshot);store.write('transaction',tx);store.write('baseline',tx['prior'])
                    untouched=p.UPDATER if touched==p.ROOT else p.ROOT
                    meta=fixture.installed/'usr/palm/applications'/untouched/'appinfo.json'
                    if condition=='absent':meta.unlink()
                    else:meta.write_bytes(meta.read_bytes().replace(b'1.0.0',b'9.0.0'))
                    device=Device(store,root_state=fixture.states[p.ROOT],root_updater=fixture.states[p.UPDATER],installed=fixture.installed,uid=fixture.uid)
                    checked=[];observe=device.owner_identity
                    def identity(owner,**kw):checked.append(owner);return observe(owner,**kw)
                    device.owner_identity=identity;device.integrity=lambda:None;device.suspend=lambda tx:None;device.routing_safe=lambda:True
                    device.snapshot_mutable=lambda:None;device.restore_mutable=lambda:None;device.repair_registrations=lambda:None
                    # Only the worker's root-uid lock and platform lease/transport
                    # are adapted. Actual private resolver, adapter/core remain.
                    original_fstat=os.fstat
                    def fstat(fd):
                        info=original_fstat(fd);lock=state/'daemon.lock'
                        if lock.exists() and info.st_ino==lock.stat().st_ino:
                            values={n:getattr(info,n) for n in dir(info) if n.startswith('st_')};values['st_uid']=0;return SimpleNamespace(**values)
                        return info
                    from itertools import permutations
                    for order in permutations((p.SYSTEM,p.ROOT,p.UPDATER)):
                        if condition=='absent':self.assertFalse(p.owners_present(order,device.owner_identity))
                        else:
                            with self.assertRaises(ValueError) as caught:p.owners_present(order,device.owner_identity)
                            self.assertNotIsInstance(caught.exception,p.TransitionUnknown)
                    checked.clear()
                    before=store.read('transaction')
                    with patch.object(cli.os,'fstat',side_effect=fstat),patch('installation.device_operation',return_value=nullcontext()),patch('observed_install.install',side_effect=AssertionError('external deletion must stop submission')) as install:
                        if condition=='absent':cli.worker(store,device)
                        else:
                            with self.assertRaises(ValueError):cli.worker(store,device)
                        self.assertEqual(install.call_count,0)
                    result=store.read('transaction')
                    self.assertFalse(result['rollbackAttempted'])
                    self.assertEqual(result['components'],before['components'])
                    self.assertEqual(store.read(tx['profile']),snapshot)
                    self.assertEqual(set(checked),{p.SYSTEM,p.ROOT,p.UPDATER})
                    if condition=='absent':self.assertEqual(result['phase'],'recovery-required')
                    else:self.assertEqual(result,before)
