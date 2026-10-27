import subprocess,sys,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
import transport

class DeadlineTests(unittest.TestCase):
 def test_optional_rpc_deadline_terminates_a_stalled_child(self):
  spawn=subprocess.Popen;children=[]
  def stalled(*args,**kwargs):
   child=spawn([sys.executable,'-c','import time;time.sleep(30)'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   children.append(child);return child
  started=time.monotonic()
  with patch.object(transport.subprocess,'Popen',side_effect=stalled):
   with self.assertRaises(TimeoutError):transport.call('luna://test/stall',{},timeout=.05)
  self.assertLess(time.monotonic()-started,2)
  self.assertIsNotNone(children[0].poll())
