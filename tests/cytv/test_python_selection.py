"""Interpreter selection at the SSH orchestration boundary."""
import json
import unittest
from unittest.mock import patch
from cytv.operations import Installer, ROOT_STATE
from cytv.errors import UserError

MANAGED='/var/lib/clean-your-tv-python/4a71641c8d5536175e404a961624e8656eba30e97b5026f6bd7dc31e4bbeaaea/bin/python3.13'

class Remote:
    def __init__(self, failed=(), bound=False):
        self.failed=failed; self.bound=bound; self.calls=[]
    def run(self, command, **kwargs):
        self.calls.append(command)
        if 'CYTV_PYTHON_BOUND' in command:
            return 'CYTV_PYTHON_BOUND' if self.bound else ''
        if 'CYTV_ROOT_READY' in command:
            missing=any(v in command for v in self.failed)
            if '/usr/bin/python3' in command: missing=True
            return 'CYTV_ROOT_MISSING' if missing else 'CYTV_ROOT_READY'
        if 'deploy.py' in command:return json.dumps({'returnValue':True})
        return ''

class SelectionTests(unittest.TestCase):
    def test_install_selects_managed_python_and_rechecks_requirements(self):
        remote=Remote();installer=Installer(remote,None,{'edition':'root'},'.',{})
        with patch.object(installer,'_select_python',return_value=MANAGED,create=True) as select:
            installer.preflight(install=True)
        select.assert_called_once_with(provision=True)
        self.assertTrue(all(v=='pass' for v in installer.tv_info['root_requirements'].values()))
        installer.root_action('status')
        self.assertTrue(MANAGED+' ' in remote.calls[-1])
    def test_missing_node_never_provisions_python(self):
        installer=Installer(Remote(('/usr/bin/node',)),None,{'edition':'root'},'.',{})
        with patch.object(installer,'_select_python',create=True) as select:
            with self.assertRaises(UserError):installer.preflight(install=True)
        select.assert_not_called()
    def test_maintenance_prefers_existing_binding_without_provisioning(self):
        remote=Remote(bound=True);installer=Installer(remote,None,{'edition':'root'},'.',{})
        with patch.object(installer,'_select_python',create=True) as select:
            installer.root_action('restore')
        select.assert_not_called()
        self.assertTrue(MANAGED+' ' in remote.calls[-1])
    def test_diagnostics_do_not_provision_missing_python(self):
        installer=Installer(Remote(),None,{'edition':'root'},'.',{})
        with patch.object(installer,'_select_python',create=True) as select:
            with self.assertRaises(UserError):installer.preflight()
        select.assert_not_called()

    def test_reconnected_removal_uses_its_archived_binding(self):
        from types import SimpleNamespace
        archive='/var/lib/clean-your-tv-system-updater.archive-'+'a'*32
        remote=Remote();original=remote.run
        def run(command,**kwargs):
            if 'CYTV_PYTHON_BOUND' in command and archive in command:return 'CYTV_PYTHON_BOUND'
            return original(command,**kwargs)
        remote.run=run
        store=SimpleNamespace(pending=lambda profile:{'action':'uninstall','system_updater_archive':archive})
        installer=Installer(remote,store,{'edition':'no-root'},'.',{})
        with patch.object(installer,'_select_python',create=True) as select:
            self.assertEqual(installer._python(),MANAGED)
        select.assert_not_called()

    def test_system_module_or_process_failure_triggers_install_fallback(self):
        remote=Remote();original=remote.run
        def run(command,**kwargs):
            if 'CYTV_ROOT_READY' in command:
                return 'CYTV_ROOT_MISSING' if 'cytv-child' in command and '/usr/bin/python3' in command else 'CYTV_ROOT_READY'
            return original(command,**kwargs)
        remote.run=run;installer=Installer(remote,None,{'edition':'root'},'.',{})
        with patch.object(installer,'_select_python',return_value=MANAGED) as select:
            installer.preflight(install=True)
        select.assert_called_once_with(provision=True)
