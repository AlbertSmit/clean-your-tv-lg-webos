"""Host pending changes only after a verified device cancellation disposition."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock
from cytv import state

SOURCE=Path(__file__).resolve().parents[2]/'scripts/root-install-recovery.py'

class HostCancellationTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('root_install_recovery_tool',SOURCE)
        self.tool=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.tool)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.store=state.Store(self.tmp.name);self.profile=state.target('fixture.local','root')
        self.identifier='a'*32;self.proof='b'*64
        self.store.begin(self.profile,'install',stage='coordinator-submitted',product_operation=self.identifier,product_payload='/tmp/fixture',requires_updater=True,migrate=False)
        self.original=self.store.pending(self.profile)
        self.disposition=dict(operation=self.identifier,state='cancelled-and-removed',lease_terminal=True,proof_sha256=self.proof,home_changed=False)
    def test_verified_cancel_retains_host_history_before_finishing_pending(self):
        inspect=Mock(return_value=self.disposition)
        result=self.tool.reconcile(self.store,self.profile,self.identifier,'c'*64,self.proof,inspect)
        self.assertEqual(result['state'],'cancelled-and-removed');self.assertIsNone(self.store.pending(self.profile))
        import json
        history=list(self.store.device_dir(self.profile).glob('recovery-*.json'));self.assertEqual(len(history),1)
        value=json.loads(history[0].read_text());self.assertEqual(value['previous'],self.original)
        self.assertEqual(value['disposition'],self.disposition)
        inspect.assert_called_once_with(self.identifier,'c'*64)
    def test_unknown_wrong_operation_or_proof_preserves_pending(self):
        for change in ({'lease_terminal':False},{'state':'remove-submitting'},{'operation':'d'*32},{'proof_sha256':'d'*64},{'home_changed':True}):
            with self.subTest(change=change),self.assertRaises(ValueError):
                self.tool.reconcile(self.store,self.profile,self.identifier,'c'*64,self.proof,lambda *args:{**self.disposition,**change})
            self.assertEqual(self.store.pending(self.profile),self.original)
    def test_internal_recovery_staging_keeps_tv_parents_posix_on_windows(self):
        import contextlib,hashlib,io,json,sys
        from pathlib import PureWindowsPath
        from unittest.mock import patch
        from tests.cytv.test_remote_directories import RemoteTree
        self.store.save(self.profile)
        folder=Path(self.tmp.name)/'code';files={'install_driver.py':b'driver','system_updater/support/core.py':b'core'}
        for name,raw in files.items():
            target=folder/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        manifest={'files':{n:hashlib.sha256(raw).hexdigest() for n,raw in files.items()}}
        (folder/'bundle.json').write_text(json.dumps(manifest))
        class Remote(RemoteTree):
            def run(remote,command,**kwargs):
                if 'cancel_install.py inspect' in command:return '{"state":"admissible"}'
                if command.startswith('rm -rf -- '):return ''
                return super().run(command,**kwargs)
            def close(remote):pass
        remote=Remote()
        def inventory(bundle):
            # argparse has already made a real LOCAL bundle Path; only later
            # remote parent conversions should see simulated Windows semantics.
            self.tool.Path=PureWindowsPath
            return manifest,b'recovery','c'*64
        argv=['recovery','inspect','--code-bundle',str(folder),'--operation',self.identifier,'--candidate','d'*64,'--code-sha256','c'*64]
        with patch.object(self.tool.state,'Store',return_value=self.store),patch.object(self.tool,'Path',Path), \
             patch.object(self.tool,'code_inventory',side_effect=inventory),patch.object(sys,'argv',argv), \
             patch('cytv.transport.SSH.connect',return_value=remote),patch('cytv.operations.Installer._python',return_value='/usr/bin/python3'),contextlib.redirect_stdout(io.StringIO()):
            self.tool.main()
        self.assertEqual(remote.uploads,{'install_driver.py','system_updater/support/core.py','bundle.json','cancel_install.py'})
        self.assertEqual(self.store.pending(self.profile),self.original)

    def test_other_host_operation_does_not_even_request_reconciliation(self):
        inspect=Mock();self.store.checkpoint(self.profile,product_operation='d'*32)
        with self.assertRaises(ValueError):self.tool.reconcile(self.store,self.profile,self.identifier,'c'*64,self.proof,inspect)
        inspect.assert_not_called();self.assertIsNotNone(self.store.pending(self.profile))

if __name__=='__main__':unittest.main()
