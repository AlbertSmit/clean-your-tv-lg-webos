import hashlib
import importlib.util, os, tempfile, unittest, json, stat
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('hook_under_test',Path(__file__).parents[1]/'startup_hook.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)

class HookTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.a=patch.object(h,'STATE',self.root);self.b=patch.object(h,'HOOK',self.root/'hook')
        self.a.start();self.b.start();self.c=patch.object(h,'trusted_directory');self.c.start();self.d=patch.object(h,'EXPECTED_UID',os.getuid());self.d.start()
    def tearDown(self):
        self.a.stop();self.b.stop();self.c.stop();self.d.stop();self.tmp.cleanup()
    def test_collision_is_not_adopted_or_removed(self):
        h.HOOK.write_bytes(h.CONTENT)
        with self.assertRaises((ValueError,OSError)):h.install(Path.read_bytes,lambda *a:None)
        h.remove(Path.read_bytes);self.assertTrue(h.HOOK.exists())
    def test_owned_drift_is_not_removed(self):
        import json
        (h.STATE/'startup-hook.json').write_text(json.dumps({'version':1,'path':str(h.HOOK),'content':h.CONTENT.decode()}))
        h.HOOK.write_bytes(b'other')
        with self.assertRaises(ValueError):h.remove(Path.read_bytes)
        self.assertEqual(h.HOOK.read_bytes(),b'other')
    def test_owned_remove_is_idempotent(self):
        import json
        (h.STATE/'startup-hook.json').write_text(json.dumps({'version':1,'path':str(h.HOOK),'content':h.CONTENT.decode()}))
        h.HOOK.write_bytes(h.CONTENT);h.HOOK.chmod(0o700)
        h.remove(Path.read_bytes);h.remove(Path.read_bytes)
        self.assertFalse(h.HOOK.exists());self.assertTrue((h.STATE/'startup-hook.json').exists())

class LinkTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name).resolve()
        self.state=self.root/'state';self.state.mkdir(mode=0o700)
        self.installed=self.root/'apps';self.installed.mkdir(mode=0o755)
        self.hook=self.root/'hook';self.app='com.cleanyourtv.root.preview'
        self.target=self.installed/'usr/palm/applications'/self.app/'startup.sh'
        self.target.parent.mkdir(parents=True)
        self.target.write_bytes(h.packaged_content(self.app));self.target.chmod(0o755)
        (self.target.parent/'appinfo.json').write_text(json.dumps({'id':self.app}))
        self.patches=[patch.object(h,'INSTALLED',self.installed),patch.object(h,'EXPECTED_UID',os.getuid()),
                      patch.object(h,'trusted_directory',side_effect=self.trust)]
        for p in self.patches:p.start()
    def trust(self,path):
        # Platform fixture /private/tmp is sticky and not a TV trust root.
        for parent in (path,*path.parents):
            if parent==self.root.parent:break
            info=parent.lstat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid!=os.getuid() or info.st_mode&0o022:raise ValueError('Unsafe directory')
    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        self.tmp.cleanup()
    def write(self,path,raw,mode=0o600):
        if isinstance(raw,str):raw=raw.encode()
        path.write_bytes(raw);path.chmod(mode)
    def install(self):h.install_link(Path.read_bytes,self.write,self.state,self.hook,self.app,(h.CONTENT,),sha256=hashlib.sha256((h.target_path(self.app).parent/'appinfo.json').read_bytes()).hexdigest())
    def remove(self):h.remove_link(Path.read_bytes,self.state,self.hook,self.app,(h.CONTENT,))
    def test_install_private_wrapper_and_repeat_remove_after_package_disappears(self):
        self.install();self.assertFalse(self.hook.is_symlink());self.assertEqual(self.hook.read_bytes(),h.private_content(self.app));self.assertEqual(stat.S_IMODE(self.hook.stat().st_mode),0o700)
        value=json.loads((self.state/'startup-hook.json').read_bytes())
        self.assertEqual(set(value),{'version','path','sha256','owner_app'});self.assertEqual(value['version'],3)
        self.target.unlink();self.remove();self.remove();self.assertFalse(os.path.lexists(self.hook))
        self.assertTrue((self.state/'startup-hook.json').exists())
    def test_packaged_startup_is_never_required_or_executed(self):
        self.target.write_bytes(b'#!/bin/sh\ntouch /SHOULD_NEVER_RUN\n');self.target.chmod(0o777)
        self.install();self.assertEqual(self.hook.read_bytes(),h.private_content(self.app))
        self.assertNotIn(str(self.installed).encode(),self.hook.read_bytes())
    def test_foreign_link_and_writable_parent_are_rejected(self):
        self.hook.symlink_to(self.root/'foreign')
        with self.assertRaises(ValueError):self.install()
        self.hook.unlink();self.root.chmod(0o777)
        with self.assertRaises(ValueError):self.install()
    def test_migration_retains_previous_receipt_and_resumes_after_receipt_write(self):
        prior={'version':1,'path':str(self.hook),'content':h.CONTENT.decode()}
        self.write(self.state/'startup-hook.json',json.dumps(prior));self.write(self.hook,h.CONTENT,0o700)
        original=os.replace
        with patch.object(h.os,'replace',side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):self.install()
        self.assertEqual(json.loads((self.state/'startup-hook.previous.json').read_bytes()),prior)
        self.assertEqual(self.hook.read_bytes(),h.CONTENT)
        self.install();self.assertFalse(self.hook.is_symlink());self.remove()
    def test_replaced_package_does_not_change_removal_authority(self):
        prior=h.target_receipt(None,self.hook,self.app,missing=True)
        self.write(self.state/'startup-hook.json',json.dumps(prior));self.hook.symlink_to(self.target)
        self.target.write_bytes(b'changed');self.target.parent.chmod(0o777)
        self.remove();self.remove();self.assertFalse(os.path.lexists(self.hook))
    def test_v2_migration_interruption_retains_exact_link_proof(self):
        prior=h.target_receipt(None,self.hook,self.app,missing=True)
        self.write(self.state/'startup-hook.json',json.dumps(prior));self.hook.symlink_to(self.target)
        with patch.object(h.os,'replace',side_effect=OSError('interrupted')):
            with self.assertRaises(OSError):self.install()
        self.assertEqual(json.loads((self.state/'startup-hook.previous.json').read_bytes()),prior)
        self.assertTrue(self.hook.is_symlink());self.install();self.assertEqual(self.hook.read_bytes(),h.private_content(self.app));self.remove();self.remove()
    def test_foreign_link_receipt_cannot_be_adopted_or_removed(self):
        prior=h.target_receipt(None,self.hook,self.app,missing=True)
        self.write(self.state/'startup-hook.json',json.dumps(prior));self.hook.symlink_to(self.root/'foreign')
        with self.assertRaises(ValueError):self.install()
        with self.assertRaises(ValueError):self.remove()
    def test_interrupted_v1_to_v2_receipt_migrates_without_losing_regular_proof(self):
        previous={'version':1,'path':str(self.hook),'content':h.CONTENT.decode()}
        self.write(self.state/'startup-hook.previous.json',json.dumps(previous))
        self.write(self.state/'startup-hook.json',json.dumps(h.target_receipt(None,self.hook,self.app)))
        self.write(self.hook,h.CONTENT,0o700)
        self.install();self.assertEqual(self.hook.read_bytes(),h.private_content(self.app));self.remove();self.remove()
    def test_unknown_previous_receipt_blocks_new_hook(self):
        self.write(self.state/'startup-hook.previous.json','{"version":99}')
        with self.assertRaises(ValueError):self.install()
        self.assertFalse(os.path.lexists(self.hook))
    def test_updater_owners_migrate_exact_v1_system_and_bound_python_wrappers(self):
        for owner in ('com.cleanyourtv.root.updater','com.cleanyourtv.system.updater'):
            app=self.installed/'usr/palm/applications'/owner;app.mkdir()
            (app/'appinfo.json').write_text(json.dumps({'id':owner,'type':'web'}))
            for content in h.owned_legacy(owner,self.state):
                for receipt in ('startup-hook.json','startup-hook.previous.json'):
                    path=self.state/receipt
                    if path.exists():path.unlink()
                self.write(self.state/'startup-hook.json',json.dumps(dict(version=1,path=str(self.hook),content=content.decode())))
                self.write(self.hook,content,0o700)
                h.install_link(Path.read_bytes,self.write,self.state,self.hook,owner,sha256=hashlib.sha256((h.target_path(owner).parent/'appinfo.json').read_bytes()).hexdigest())
                self.assertEqual(self.hook.read_bytes(),h.private_content(owner))
                h.remove_link(Path.read_bytes,self.state,self.hook,owner);h.remove_link(Path.read_bytes,self.state,self.hook,owner)
                self.assertFalse(os.path.lexists(self.hook))

    def test_wrong_unix_owner_is_not_accepted(self):
        with patch.object(h,'EXPECTED_UID',os.getuid()+1):
            with self.assertRaises(ValueError):self.install()
        self.assertFalse(os.path.lexists(self.hook))
    def test_copied_legacy_without_receipt_is_not_adopted(self):
        self.write(self.hook,h.CONTENT,0o700)
        with self.assertRaises(ValueError):self.install()
