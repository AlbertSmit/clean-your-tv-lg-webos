import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import package_identity
import startup_guard as guard
import test_package_identity as fixtures

class PrivateGuardTests(unittest.TestCase):
    def setUp(self):
        self.fixture=fixtures.IdentityTests();self.fixture.setUp();self.addCleanup(self.fixture.tearDown)
        self.root=self.fixture.base;self.installed=self.fixture.installed;self.owner=package_identity.ROOT
        self.meta=self.installed/'usr/palm/applications'/self.owner/'appinfo.json'
        self.identity=patch.object(guard,'identity',side_effect=lambda owner,**kw:package_identity.identity(owner,states=self.fixture.states,installed=self.installed,uid=os.getuid(),purpose=kw.get('purpose','current'),full=kw.get('full',False)))
        self.identity.start();self.addCleanup(self.identity.stop)
        allowed=patch.object(guard,'worker_allowed',side_effect=lambda owner:package_identity.worker_allowed(owner,states=self.fixture.states,uid=os.getuid()))
        allowed.start();self.addCleanup(allowed.stop)
    def test_shared_startup_bytes_cannot_be_executed_by_private_guard(self):
        (self.meta.parent/'startup.sh').write_text('#!/bin/sh\ntouch /SHOULD_NEVER_RUN\n')
        with patch.object(guard.subprocess,'run') as run:
            self.assertTrue(guard.start(self.owner));command=run.call_args.args[0]
        self.assertEqual(command,['/bin/sh','/var/lib/clean-your-tv-root/service/boot-recover.sh','mark'])
        self.assertNotIn(str(self.installed),' '.join(command))
    def test_changed_or_deleted_metadata_never_marks_or_starts(self):
        original=self.meta.read_bytes()
        for mode in ('foreign','missing','symlink','same-length'):
            with self.subTest(mode=mode),patch.object(guard.subprocess,'run') as run,patch.object(guard.subprocess,'Popen') as spawn:
                if mode=='missing':self.meta.unlink()
                elif mode=='symlink':self.meta.rename(self.meta.with_name('other'));self.meta.symlink_to('other')
                else:self.meta.write_bytes(original.replace(b'1.0.0',b'9.0.0') if mode=='same-length' else b'{"id":"foreign"}')
                self.assertFalse(guard.start(self.owner));run.assert_not_called();spawn.assert_not_called()
                if self.meta.is_symlink():self.meta.unlink();self.meta.with_name('other').unlink()
                self.meta.write_bytes(original);self.meta.chmod(0o777)
    def test_missing_marker_with_transient_failsafe_admits_marks_and_returns(self):
        sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
        import boot_gate
        marker=self.root/'marker';failsafe=self.root/'failsafe';failsafe.touch()
        with patch.object(boot_gate,'ROOT',marker),patch.object(boot_gate.d,'EXPECTED_UID',os.getuid()),patch.object(boot_gate.d,'FAILSAFE',failsafe),patch('intent_runtime.boot_identity',return_value='boot-a'),patch.object(boot_gate,'wait',side_effect=AssertionError('init must never wait')),patch.object(guard.subprocess,'run',side_effect=lambda *a,**kw:boot_gate.mark()):
            self.assertFalse(marker.exists());self.assertTrue(guard.start(self.owner))
            self.assertEqual(boot_gate.observation(),(True,True))
            self.assertEqual(json.loads((marker/'normal.json').read_text()),{'version':1,'boot':'boot-a'})
            self.assertFalse(any(self.root.rglob('home-intent.json')))
    def test_updater_workers_start_only_from_private_code(self):
        with patch.object(guard.subprocess,'Popen') as spawn:
            self.assertTrue(guard.start(package_identity.UPDATER));command=spawn.call_args.args[0]
            state=guard.OWNERS[package_identity.UPDATER]
            self.assertEqual(command[:3],['/usr/bin/node',str(state/'code/python_boot.js'),str(state)])
            self.assertEqual(command[-1],'worker');self.assertNotIn(str(self.installed),' '.join(command))
        with patch.object(guard.subprocess,'Popen') as spawn:
            self.assertFalse(guard.start(package_identity.SYSTEM));spawn.assert_not_called()
    def test_private_reader_still_rejects_writable_sdk_path(self):
        import python_binding
        with patch.object(python_binding,'EXPECTED_UID',os.getuid()),self.assertRaises(ValueError):python_binding._read(self.meta)
