"""The SSH client consumes the same durable records as the TV entry point."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock
from cytv.operations import Installer
from cytv import state


class SharedRootInstallTests(unittest.TestCase):
    def fixture(self, event):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        root=Path(temp.name);store=state.Store(root/'host');profile=state.target('tv.local','root')
        remote=MagicMock();remote.run.return_value=json.dumps(event)
        installer=Installer(remote,store,profile,root,{},lambda *_:None)
        installer._selected_python='/usr/bin/python3';installer._coordinator_code='/tmp/trusted-current-code'
        return installer,remote,store,profile

    def test_tv_origin_is_inspected_with_current_code_without_reinstall_or_profile_reset(self):
        event={'operation':None,'stage':'inspect','state':'installed','code':'inspected',
               'installation':{'state':'installed','reason':'verified_components','can_install':False,'can_maintain':True}}
        installer,remote,store,profile=self.fixture(event)
        self.assertTrue(installer.root_installation()['can_maintain'])
        command=remote.run.call_args.args[0]
        self.assertIn('/tmp/trusted-current-code/install_driver.py inspect',command)
        self.assertNotIn('/var/lib/clean-your-tv-root/deploy.py',command)
        self.assertIsNone(store.pending(profile));remote.luna.assert_not_called();remote.upload.assert_not_called()

    def test_pending_device_operation_stays_status_only_when_packages_are_absent(self):
        identifier='a'*32
        event={'operation':identifier,'stage':'package-remove-submitting','state':'pending','code':'operation_pending'}
        installer,remote,store,profile=self.fixture(event)
        store.begin(profile,'uninstall',full_project=True,product_operation=identifier)
        installer.installed_apps=MagicMock(return_value=[])
        installer.verify_absent=MagicMock()
        result=installer.status()
        self.assertEqual(result['device']['product'],event);self.assertIsNotNone(result['pending'])
        self.assertIn(' status --operation '+identifier,remote.run.call_args.args[0])
        remote.luna.assert_not_called();installer.verify_absent.assert_not_called()

    def test_verified_setup_offers_separate_explicit_activation(self):
        identifier='a'*32
        event={'operation':identifier,'stage':'complete','state':'complete','code':'verified','result':{'verified':True,'home_changed':False}}
        installer,remote,store,profile=self.fixture(event)
        store.begin(profile,'install',product_operation=identifier,requires_updater=True)
        result=installer.status()
        self.assertTrue(result['can_resume_root_setup']);self.assertIsNotNone(store.pending(profile))
        remote.luna.assert_not_called()
        self.assertFalse(any(' enable' in call.args[0] for call in remote.run.call_args_list))

    def test_desktop_import_does_not_load_device_only_posix_modules(self):
        project=Path(__file__).resolve().parents[2]
        code="""import builtins,sys
sys.path.insert(0,sys.argv[1])
original=builtins.__import__
def importing(name,*args,**kwargs):
 if name in ('fcntl','termios'):raise ImportError('device-only module is unavailable')
 return original(name,*args,**kwargs)
builtins.__import__=importing
import cytv.operations
"""
        result=subprocess.run([sys.executable,'-I','-B','-c',code,str(project)],cwd='/private/tmp',capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
