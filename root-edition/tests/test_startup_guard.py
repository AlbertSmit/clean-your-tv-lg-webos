import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import package_data
import startup_guard as guard

class PrivateGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve();self.installed=self.root/'apps'
        self.owner='com.cleanyourtv.root.preview';self.app=self.installed/'usr/palm/applications'/self.owner
        self.app.mkdir(parents=True)
        for path in (self.installed,self.installed/'usr',self.installed/'usr/palm',self.app.parent):path.chmod(0o777)
        self.meta=self.app/'appinfo.json';self.meta.write_text(json.dumps({'id':self.owner,'type':'web'}));self.meta.chmod(0o644)
        self.patches=[patch.object(guard,'INSTALLED',self.installed),patch.object(guard,'read',side_effect=lambda path,**kw:package_data.read(path,installed=self.installed,uid=os.getuid()))]
        for p in self.patches:p.start()
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def test_shared_startup_bytes_cannot_be_executed_by_private_guard(self):
        (self.app/'startup.sh').write_text('#!/bin/sh\ntouch /SHOULD_NEVER_RUN\n')
        with patch.object(guard.subprocess,'run') as run:
            self.assertTrue(guard.start(self.owner));command=run.call_args.args[0]
        self.assertEqual(command,['/bin/sh','/var/lib/clean-your-tv-root/service/boot-recover.sh','mark'])
        self.assertNotIn(str(self.installed),' '.join(command))
    def test_replacement_deletion_or_unsafe_identity_stops_rearming(self):
        for mode in ('foreign','writable','missing','symlink','replaced'):
            original=self.meta.read_bytes()
            with self.subTest(mode=mode),patch.object(guard.subprocess,'run') as run,patch.object(guard.subprocess,'Popen') as spawn:
                if mode=='foreign':self.meta.write_text('{"id":"foreign","type":"web"}')
                elif mode=='writable':self.app.chmod(0o777)
                elif mode=='missing':self.meta.unlink()
                elif mode=='symlink':self.meta.rename(self.app/'other');self.meta.symlink_to('other')
                else:
                    old=self.app.with_name('old');self.app.rename(old);self.app.mkdir();self.meta.write_text('{"id":"foreign"}')
                self.assertFalse(guard.start(self.owner));run.assert_not_called();spawn.assert_not_called()
                if self.meta.is_symlink():self.meta.unlink();(self.app/'other').unlink()
                self.app.chmod(0o755);self.meta.write_bytes(original)
    def test_updater_workers_start_only_from_their_private_code(self):
        for owner in ('com.cleanyourtv.root.updater','com.cleanyourtv.system.updater'):
            app=self.app.with_name(owner);app.mkdir();(app/'appinfo.json').write_text(json.dumps({'id':owner,'type':'web'}))
            with patch.object(guard.subprocess,'Popen') as spawn:
                self.assertTrue(guard.start(owner));command=spawn.call_args.args[0]
                state=guard.OWNERS[owner]
                self.assertEqual(command[:3],['/usr/bin/node',str(state/'code/python_boot.js'),str(state)])
                self.assertEqual(command[-1],'worker');self.assertNotIn(str(self.installed),' '.join(command))
            (app/'appinfo.json').unlink()
            with patch.object(guard.subprocess,'Popen') as spawn:
                self.assertFalse(guard.start(owner));spawn.assert_not_called()

    def test_private_reader_still_rejects_shared_writable_ancestors(self):
        import python_binding
        with patch.object(python_binding,'EXPECTED_UID',os.getuid()):
            with self.assertRaises(ValueError):python_binding._read(self.meta)
