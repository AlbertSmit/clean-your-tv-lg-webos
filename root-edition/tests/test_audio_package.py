import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from test_build_root import ar_members

class AudioPackageTests(unittest.TestCase):
 def test_audio_code_ships_in_real_ipk_and_verified_support_bundle(self):
  import tarfile,io
  spec=importlib.util.spec_from_file_location('audio_build',ROOT/'build.py')
  builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
  with tempfile.TemporaryDirectory() as folder:
   package=builder.build(Path(folder).resolve()/'bundle')
   manifest=json.loads((package.parent/'bundle.json').read_text())
   self.assertIn('runtime/audio_recovery.py',manifest['files'])
   with tarfile.open(fileobj=io.BytesIO(ar_members(package.read_bytes())['data.tar.gz']),mode='r:gz') as archive:
    names=archive.getnames()
    self.assertIn('usr/palm/services/com.cleanyourtv.root.preview.service/audio-recovery.js',names)
    self.assertIn('usr/palm/applications/com.cleanyourtv.root.preview/root-audio.js',names)
   spec=importlib.util.spec_from_file_location('audio_provision',ROOT/'provision.py')
   provision=importlib.util.module_from_spec(spec);spec.loader.exec_module(provision)
   original={'service':'Exec=/usr/bin/run-js-service -n '+str(provision.SERVICE),'role':json.dumps({'appId':provision.NAME})}
   permissions=json.loads(provision.plan(original)['api'])
   for method in ('audioRecoveryStatus','setAudioRecoveryEnabled','recoverAudio'):
    self.assertIn(provision.NAME+'/'+method,permissions[provision.NAME+'.control'])
