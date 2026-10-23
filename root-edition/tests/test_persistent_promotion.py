import sys,time,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
from test_persistent_recovery import IntegrationTests
import device_adapter as d

class PromotionTests(IntegrationTests):
 def setUp(self):
  super().setUp()
  for name in ('provision.verify','helper_bridge.require_idle','persistent_health.require_guardian'):
   p=patch(name);p.start();self.addCleanup(p.stop)
 def trial(self):
  self.c.exit(self.intent);s=self.store.read()
  s,_=self.c.event(s,'enable',boot='boot-a',token='new')
  self.create_route('new-route')
  j=d.safe_json(self.root/'profile-trial.json');j['deadline']=time.monotonic()+60;d.save(j)
  self.c.bind(s,'new-route');return s
 def test_confirmation_requires_verified_live_guard_and_lease(self):
  s=self.trial()
  with patch('persistent_health.require_fresh',side_effect=ValueError('expired')):
   with self.assertRaises(ValueError):self.c.confirm(s)
  self.assertFalse(self.store.read()['enabled'])
 def test_confirmed_trial_becomes_active(self):
  s=self.trial()
  with patch('persistent_health.require_fresh'),patch.object(d,'active_guardian',return_value=True):
   result=self.c.confirm(s)
  self.assertTrue(result['intent']['enabled']);self.assertEqual(self.store.read()['phase'],'active')
 def test_wrong_home_cannot_be_confirmed(self):
  s=self.trial();self.home='wrong'
  with patch('persistent_health.require_fresh'),patch.object(d,'active_guardian',return_value=True):
   with self.assertRaises(ValueError):self.c.confirm(s)
  self.assertFalse(self.store.read()['enabled'])
 def test_dead_guardian_cannot_be_confirmed(self):
  s=self.trial()
  with patch('persistent_health.require_fresh'),patch.object(d,'active_guardian',return_value=False):
   with self.assertRaises(ValueError):self.c.confirm(s)
  self.assertFalse(self.store.read()['enabled'])

 def test_confirmation_near_deadline_is_rejected(self):
  s=self.trial();j=d.safe_json(self.root/'profile-trial.json');j['deadline']=time.monotonic()+1;d.save(j)
  with patch('persistent_health.require_fresh'),patch.object(d,'active_guardian',return_value=True):
   with self.assertRaisesRegex(ValueError,'deadline'):self.c.confirm(s)
  self.assertFalse(self.store.read()['enabled'])
