"""Boot-only foreground fallback, with real intent, routing and health records."""
import sys,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
import intent_runtime as runtime
import persistent_health as health
from profile_plan import CANDIDATE,STOCK
import test_persistent_recovery as recovery_tests

class PresentationTests(unittest.TestCase):
 create_route=recovery_tests.IntegrationTests.create_route
 read=recovery_tests.IntegrationTests.read
 call=recovery_tests.IntegrationTests.call
 write=recovery_tests.IntegrationTests.write
 def tearDown(self):recovery_tests.IntegrationTests.tearDown(self)
 def setUp(self):
  recovery_tests.IntegrationTests.setUp(self)
  self.hp=patch.object(health,'ROOT',self.root/'health');self.hp.start();self.addCleanup(self.hp.stop)
  self.bp=patch.object(runtime,'boot_identity',return_value='boot-a');self.bp.start();self.addCleanup(self.bp.stop)
  health.publish('route-a',1)
  self.launches=[];self.foreground='com.webos.app.livetv';self.auto='on';self.stop_before_launch=False
  self.rpc=patch.object(self,'call',side_effect=self.rpc_call);self.rpc.start();self.addCleanup(self.rpc.stop)
  self.result={'intent':self.intent,'trial':{'transaction':'route-a'}}
 def rpc_call(self,uri,payload,timeout=5):
  self.assertLessEqual(timeout,.5)
  if uri.endswith('/getSystemSettings'):
   self.assertEqual(payload,{'category':'general','keys':['homeAutoLaunch']})
   return {'returnValue':True,'settings':{'homeAutoLaunch':self.auto}}
  if uri.endswith('/getBootStatus'):
   return {'returnValue':True,'powerStatus':'active','bootStatus':'normal','bootTarget':'hardware','firstAppLaunched':True,'firstAppId':'','signals':{'core-boot-done':True},'subscribed':False}
  if uri.endswith('/getForegroundAppInfo'):
   if self.stop_before_launch:self.c.exit(self.intent)
   return {'returnValue':True,'appId':self.foreground,'appCategory':[],'processId':'123','windowId':'window'}
  if uri.endswith('/launch'):
   self.assertEqual(payload,{'id':CANDIDATE});self.launches.append(payload['id'])
   return {'returnValue':True}
  self.fail('Unexpected RPC '+uri)
 def test_live_tv_startup_is_presented_only_after_confirmed_health(self):
  self.assertEqual(runtime.present_boot(self.c,self.result),'launch-requested')
  self.assertEqual(self.launches,[CANDIDATE]);self.assertTrue(self.store.read()['enabled'])
 def test_opened_user_app_or_already_visible_clean_is_preserved(self):
  for app in ('com.emby.app',CANDIDATE):
   with self.subTest(app=app):
    self.foreground=app
    self.assertEqual(runtime.present_boot(self.c,self.result),'preserved-foreground')
    self.assertEqual(self.launches,[])
 def test_last_input_preference_does_not_launch_clean(self):
  self.auto='off'
  self.assertEqual(runtime.present_boot(self.c,self.result),'preserved-startup-setting')
  self.assertEqual(self.launches,[])
 def test_concurrent_explicit_off_wins_before_launch(self):
  self.stop_before_launch=True
  self.assertEqual(runtime.present_boot(self.c,self.result),'unavailable')
  self.assertEqual(self.launches,[]);self.assertFalse(self.store.read()['enabled'])
 def test_missing_input_health_never_launches_or_disables_healthy_intent(self):
  health.path('route-a').unlink()
  self.assertEqual(runtime.present_boot(self.c,self.result),'unavailable')
  self.assertEqual(self.launches,[]);self.assertEqual(self.store.read(),self.intent)
 def test_unavailable_foreground_does_not_request_launch(self):
  self.foreground=None
  self.assertEqual(runtime.present_boot(self.c,self.result),'preserved-foreground')
  self.assertEqual(self.launches,[])
 def test_failed_launch_is_not_retried_or_converted_to_intent_fault(self):
  original=self.rpc_call
  def fail_launch(uri,payload,timeout=5):
   if uri.endswith('/launch'):raise TimeoutError('unknown launch outcome')
   return original(uri,payload,timeout)
  self.call.side_effect=fail_launch
  self.assertEqual(runtime.present_boot(self.c,self.result),'unavailable')
  self.assertEqual(self.store.read(),self.intent)
 def test_software_reboot_does_not_request_hardware_startup_fallback(self):
  original=self.rpc_call
  def software_boot(uri,payload,timeout=5):
   reply=original(uri,payload,timeout)
   if uri.endswith('/getBootStatus'):reply['bootTarget']='software'
   return reply
  self.call.side_effect=software_boot
  self.assertEqual(runtime.present_boot(self.c,self.result),'preserved-startup-setting')
  self.assertEqual(self.launches,[])
 def test_explicit_off_during_inflight_launch_completes_and_stays_off(self):
  original=self.rpc_call
  def stop_during_launch(uri,payload,timeout=5):
   if uri.endswith('/launch'):self.c.exit(self.intent)
   return original(uri,payload,timeout)
  self.call.side_effect=stop_during_launch
  self.assertEqual(runtime.present_boot(self.c,self.result),'superseded')
  self.assertFalse(self.store.read()['enabled']);self.assertEqual(self.read(),self.baseline)
 def test_app_opened_while_health_is_checked_is_preserved(self):
  original=health.require_fresh
  def opened_app(tx):
   self.foreground='com.emby.app';return original(tx)
  with patch.object(health,'require_fresh',side_effect=opened_app):
   self.assertEqual(runtime.present_boot(self.c,self.result),'preserved-foreground')
  self.assertEqual(self.launches,[])
