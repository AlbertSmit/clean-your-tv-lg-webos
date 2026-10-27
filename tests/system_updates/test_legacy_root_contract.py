"""Candidate packages must remain consumable by an untouched v1.3 supervisor."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[2]
CONTRACT=json.loads((Path(__file__).parent/'fixtures/root-contract-v1.3.0.json').read_text())

def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value

class LegacyRootContractTests(unittest.TestCase):
 def test_candidate_archive_fits_published_13_destinations(self):
  from cytv.package import data_files
  build=module('contract_system_build',ROOT/'system-updater/build.py')
  with tempfile.TemporaryDirectory() as tmp:
   payload=Path(tmp).resolve()
   for script,name in [('build.py','root'),('build_updater.py','root-updater')]:
    subprocess.run([sys.executable,str(ROOT/'root-edition'/script),'--output',str(payload/name)],check=True,capture_output=True)
   raw,hashes=build.infrastructure(payload)
   self.assertEqual(set(hashes),set(CONTRACT['infrastructure_paths']), 'untouched 1.3 supervisor rejects any added or missing destination')
   # Exercise the actual archive guard, not merely builder constants.
   import importlib,os
   from test_core import Store
   device=importlib.import_module('system_updater.device')
   store=Store(payload/'state',uid=os.getuid());code=payload/'code';code.mkdir();(code/'infrastructure-paths.json').write_text(json.dumps(CONTRACT['infrastructure_paths']))
   prior={'name':'root-infrastructure','kind':'infrastructure','version':'0.4.0','local':True,'files':hashes,'absent':[]}
   store.write('baseline',{'edition':'root','components':[prior]})
   inspector=device.Device(store,code=code,uid=os.getuid())
   target={'name':'root-infrastructure','kind':'infrastructure','version':'0.5.0','sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw)}
   self.assertEqual(inspector.inspect(raw,target),hashes)

 def test_candidate_registration_plan_preserves_original_installed_grants(self):
  sys.path.insert(0,str(ROOT/'root-edition'))
  provision=module('contract_root_provision',ROOT/'root-edition/provision.py')
  actual={k:hashlib.sha256(v).hexdigest() for k,v in provision.plan(CONTRACT['registration_original']).items()}
  self.assertEqual(actual,CONTRACT['registration_sha256'], 'old registration repair refuses a changed permission plan')
