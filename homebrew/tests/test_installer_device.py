"""TV adapter additions, with physical services replaced at their boundary."""
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'root-edition'))
import install_device

class InstallerDeviceTests(unittest.TestCase):
    def test_current_versions_are_installed_evidence_and_drift_is_recovery(self):
        values=dict(supported=True,packages_match=False,receipts_match=False,pending=False,retained=False,complete=False,migration_supported=False)
        with tempfile.TemporaryDirectory() as tmp:
            installed=Path(tmp)/'installed';root=Path(tmp)/'root';updater=Path(tmp)/'updater';root.mkdir();updater.mkdir()
            app=installed/'usr/palm/applications/com.cleanyourtv.root.updater/appinfo.json';app.parent.mkdir(parents=True);app.write_text(json.dumps({'id':'com.cleanyourtv.root.updater','version':'2.3.4'}))
            elf=bytearray(40);elf[:6]=b'\x7fELF\x01\x01';elf[18]=40;elf[39]=5
            with patch.object(install_device.sys,'platform','linux'),patch.object(install_device.platform,'machine',return_value='armv7l'),patch('deploy.require_device'),patch('deploy.require_node'),patch.object(install_device,'device_snapshot',return_value=values),patch.object(install_device,'ROOT',root),patch.object(install_device,'UPDATER',updater),patch.object(install_device,'SUPERVISOR',Path(tmp)/'absent'),patch.object(install_device,'INSTALLED',installed),patch('package_identity.identity',return_value={'id':'com.cleanyourtv.root.updater','version':'2.3.4'}),patch.object(install_device,'current_updater'),patch.object(install_device,'current_root',return_value={'version':'1.2.3'}),patch.object(install_device,'safe_bytes',side_effect=lambda p,**kwargs:bytes(elf) if p==Path('/bin/sh').resolve() else p.read_bytes()):
                result=install_device.LocalDevice().inspect()
                self.assertEqual(result.get('versions'),{'root':'1.2.3','root-updater':'2.3.4'})
                with patch.object(install_device,'current_root',side_effect=ValueError('drift')):
                    result=install_device.LocalDevice().inspect();self.assertEqual(result['state'],'recovery_required');self.assertNotIn('versions',result)
    def test_activation_requires_current_inspection_and_checked_retained_driver(self):
        device=install_device.LocalDevice()
        with patch.object(device,'inspect',return_value={'state':'fresh'}),patch.object(device,'validate_root_driver') as validated,patch('deploy.runtime') as runtime:
            with self.assertRaises(ValueError):device.activate()
            validated.assert_not_called();runtime.assert_not_called()
        with patch.object(device,'inspect',return_value={'state':'installed'}),patch.object(device,'validate_root_driver') as validated,patch('deploy.runtime',return_value={'returnValue':True}) as runtime:
            self.assertTrue(device.activate()['returnValue']);validated.assert_called_once();runtime.assert_called_once_with('enable')
        with patch.object(device,'inspect',return_value={'state':'installed'}),patch.object(device,'validate_root_driver',side_effect=ValueError('changed')),patch('deploy.runtime') as runtime:
            with self.assertRaises(ValueError):device.activate()
            runtime.assert_not_called()

if __name__=='__main__':unittest.main()
