"""Real public 1.3 supervisor update/rollback on local files, without a TV."""
import os
from pathlib import Path
import subprocess
import sys
import unittest

class LegacyOTALifecycleTests(unittest.TestCase):
    def run_fixture(self,commands):
        helper=Path(__file__).with_name('legacy_ota_fixture.py')
        program="from legacy_ota_fixture import LegacyOTA\nwith LegacyOTA() as fixture:\n"+commands+" print('public 1.3 Device/Manager passed')\n"
        result=subprocess.run([sys.executable,'-c',program],cwd=helper.parents[2],env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONPATH':str(helper.parent)},stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=180)
        self.assertEqual(result.returncode,0,result.stdout)
        self.assertIn('Device/Manager passed',result.stdout)

    def test_public_13_supervisor_completes_update_with_real_registration_repair(self):
        self.run_fixture(' fixture.complete_update()\n')

    def test_public_13_supervisor_rolls_back_before_completion(self):
        self.run_fixture(' fixture.complete_update(finish=False)\n fixture.rollback()\n')

    def test_public_13_retained_rollback_after_publication(self):
        self.run_fixture(' fixture.complete_update()\n fixture.rollback()\n')

if __name__=='__main__':unittest.main()
