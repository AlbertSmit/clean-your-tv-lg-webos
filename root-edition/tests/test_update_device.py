import copy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from updater.device import Device


class DeviceTests(unittest.TestCase):
    def status(self):
        return {'intent':{'phase':'disabled'},'effective':{'sam_home':'com.webos.app.home','profiles':{'defaultApps':{'categories':{'home':'com.webos.app.home'}},'idleApp':{'appId':'com.webos.app.home','support':True}}}}

    def test_route_readback_cannot_be_inferred_from_disabled_intent(self):
        status=self.status()
        self.assertEqual({'active':False,'safe':True,'intent':{'phase':'disabled'}},Device.route_state(status))
        status['effective']['sam_home']='com.cleanyourtv.root.preview'
        self.assertTrue(Device.route_state(status)['active']);self.assertFalse(Device.route_state(status)['safe'])
        status=self.status();status['effective']['profiles']['idleApp']['appId']='other'
        self.assertFalse(Device.route_state(status)['safe'])
        self.assertFalse(Device.route_state({'intent':{'phase':'disabled'}})['safe'])

    def test_active_and_legacy_trial_routing_is_recorded_for_post_update_choice(self):
        status=self.status();status['intent']={'phase':'active'}
        self.assertTrue(Device.route_state(status)['active'])
        status=self.status();status['intent']=None
        status['effective']['profiles']['defaultApps']['categories']['home']='com.cleanyourtv.root.preview'
        self.assertTrue(Device.route_state(status)['active'])


if __name__=='__main__':unittest.main()
