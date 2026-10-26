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
    def test_owner_absence_and_foreign_metadata_are_not_presence(self):
        from system_updater.device import Device
        with tempfile.TemporaryDirectory() as temp:
            from test_core import Store
            root=Path(temp).resolve();state=root/'state';state.mkdir();installed=root/'installed';installed.mkdir()
            device=Device(Store(state,uid=os.getuid()),installed=installed,uid=os.getuid())
            self.assertFalse(device.components_present())
            app=installed/'usr/palm/applications/com.cleanyourtv.system.updater';app.mkdir(parents=True)
            (app/'appinfo.json').write_text(json.dumps({'id':'foreign'}))
            self.assertFalse(device.components_present())
            (app/'appinfo.json').write_text(json.dumps({'id':'com.cleanyourtv.system.updater'}))
            self.assertTrue(device.components_present())
            (app/'appinfo.json').unlink();(app/'appinfo.json').symlink_to(root/'foreign')
            self.assertFalse(device.components_present())
