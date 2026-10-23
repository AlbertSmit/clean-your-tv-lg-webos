import sys,subprocess,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
import shutdown_state as s
class Tests(unittest.TestCase):
 def test_only_manager_stopping_is_accepted(self):
  for state in ('stopping\n','running\n','degraded\n','offline\n','unknown\n',''):
   with patch.object(s.subprocess,'run',return_value=subprocess.CompletedProcess([],1,stdout=state,stderr='')):
    self.assertEqual(s.stopping(),state=='stopping\n')
 def test_unavailable_manager_is_not_shutdown_permission(self):
  with patch.object(s.subprocess,'run',side_effect=OSError()):self.assertFalse(s.stopping())
