from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock
from cytv.operations import Installer, UPDATER_APP
from cytv import state, package

class FullUninstallTests(unittest.TestCase):
    def test_removes_leftover_updater_without_resubmitting_root_removal(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=state.Store(tmp);profile=state.target('tv.local','root');remote=MagicMock()
            remote.luna.return_value={'returnValue':True,'status':{'apps':[]}}
            remote.run.return_value=''
            inst=Installer(remote,store,profile,Path(tmp),{},lambda *_:None)
            inst.installed_apps=MagicMock(side_effect=[[{'id':UPDATER_APP}],[]])
            inst.root_updater_cleanup=MagicMock(side_effect=[{'disabled':True},{'removed':True,'archive':'saved'}])
            inst.verify_project_removed=MagicMock();inst.verify_absent=MagicMock();inst.root_action=MagicMock();inst.cleanup_legacy_permissions=MagicMock()
            result=inst.uninstall(full_project=True)
            self.assertTrue(result['removed'])
            inst.root_action.assert_not_called()
            self.assertEqual([c.args[0] for c in inst.root_updater_cleanup.call_args_list],['disable','finalize'])
            removes=[c for c in remote.luna.call_args_list if c.args[0].endswith('/remove')]
            self.assertEqual([c.args[1]['id'] for c in removes],[UPDATER_APP])
            self.assertIsNone(store.pending(profile))

    def test_uncertain_updater_remove_is_not_submitted_again(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=state.Store(tmp);profile=state.target('tv.local','root');remote=MagicMock()
            remote.luna.return_value={'returnValue':True,'status':{'apps':[]}}
            remote.run.return_value=''
            inst=Installer(remote,store,profile,Path(tmp),{},lambda *_:None)
            inst.verify_absent=MagicMock();inst.cleanup_legacy_permissions=MagicMock()
            inst.installed_apps=MagicMock(return_value=[{'id':UPDATER_APP}]);inst.root_updater_cleanup=MagicMock(return_value={'disabled':True})
            store.begin(profile,'uninstall',full_project=True,removals={UPDATER_APP:'submitted'},updater_archive='/var/lib/clean-your-tv-root-updater.archive-'+'a'*32)
            with self.assertRaisesRegex(RuntimeError,'unknown'):inst.uninstall(full_project=True)
            self.assertFalse(any(c.args[0].endswith('/remove') for c in remote.luna.call_args_list))
            self.assertIsNotNone(store.pending(profile))

    def test_final_verification_checks_registrations_even_without_root_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            remote=MagicMock();remote.run.return_value=''
            inst=Installer(remote,state.Store(tmp),state.target('tv.local','root'),Path(tmp),{},lambda *_:None)
            with self.assertRaisesRegex(RuntimeError,'registrations remain'):inst.verify_project_removed()
            remote.luna.assert_not_called()
            command=remote.run.call_args.args[0]
            self.assertIn('50-clean-your-tv-root',command)
            self.assertIn('clean-your-tv-root.json',command)

    def test_status_never_finishes_partial_full_uninstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            store=state.Store(tmp);profile=state.target('tv.local','root');remote=MagicMock()
            remote.run.return_value='{"stage":"uninstalled-state-retained"}'
            inst=Installer(remote,store,profile,Path(tmp),{},lambda *_:None);inst.verify_absent=MagicMock()
            store.begin(profile,'uninstall',full_project=True)
            self.assertIsNotNone(inst.status()['pending'])
            self.assertIsNotNone(store.pending(profile))
