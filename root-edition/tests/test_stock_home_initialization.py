"""An absent override must become independently readable before recovery setup."""
import copy
import importlib.util
import json
import os
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parents[1]))
spec = importlib.util.spec_from_file_location('stock_home_provision', Path(__file__).parents[1]/'provision.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
STOCK = 'com.webos.app.home'


class StockHomeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.apps = {'MembershipApp':'com.webos.app.overlaymembership'}
        self.profiles = {'defaultApps':{'categories':{'home':STOCK}},
                         'idleApp':{'support':True,'appId':STOCK}}
        self.calls = []
        self.write_mode = 'ok'
        for name, value in [('STATE',self.root), ('rpc',self.bus),
                            ('secure',lambda path:path.read_bytes())]:
            context = patch.object(p,name,value)
            context.start(); self.addCleanup(context.stop)

    def bus(self, method):
        self.calls.append(method)
        if method == 'home-read':
            return {'returnValue':True,'settings':{'defaultApps':copy.deepcopy(self.apps)}}
        if method == 'home-profiles':
            return {'returnValue':True,'profiles':copy.deepcopy(self.profiles)}
        if method == 'home-stock':
            # Intent must already be durable before the side effect.
            receipt = json.loads((self.root/'stock-home-initialization.json').read_text())
            self.assertEqual(receipt['phase'],'submitted')
            self.assertNotIn('home',receipt['defaultApps'])
            self.assertEqual((self.root/'stock-home-initialization.json').stat().st_mode & 0o777,0o600)
            if self.write_mode != 'no-op': self.apps['home'] = STOCK
            if self.write_mode == 'lost': raise p.RecoveryRPCError('timeout')
            if self.write_mode == 'interrupted': raise KeyboardInterrupt()
            return {'returnValue':True}
        self.fail('Unexpected bus operation: '+method)

    def test_absent_home_is_initialized_and_independently_read_back(self):
        self.assertTrue(callable(getattr(p,'prepare_stock_home',None)), 'missing setup-only initialization')
        p.prepare_stock_home()
        self.assertEqual(self.apps,{'MembershipApp':'com.webos.app.overlaymembership','home':STOCK})
        self.assertEqual(self.calls,['home-read','home-profiles','home-stock','home-read','home-profiles'])
        receipt = json.loads((self.root/'stock-home-initialization.json').read_text())
        self.assertEqual(receipt['phase'],'verified')
        (self.root/'recovery-provision.json').write_text('{}')
        p.prepare_stock_home()
        self.assertEqual(self.calls.count('home-stock'),1)

    def test_existing_valid_setting_is_never_rewritten(self):
        for home in (STOCK,'other.home'):
            self.apps['home'] = home; self.calls.clear()
            p.prepare_stock_home()
            self.assertEqual(self.calls,['home-read'])
            self.assertFalse((self.root/'stock-home-initialization.json').exists())

    def test_explicit_malformed_home_is_not_treated_as_absence(self):
        for home in (None,'',False,[],{},' home '):
            self.apps['home'] = home; self.calls.clear()
            with self.subTest(home=home), self.assertRaises(ValueError): p.prepare_stock_home()
            self.assertEqual(self.calls,['home-read'])

    def test_nonstock_or_incomplete_profiles_prevent_any_write(self):
        for profiles in ({}, {'defaultApps':self.profiles['defaultApps']},
                         dict(self.profiles,idleApp={'support':False,'appId':STOCK}),
                         dict(self.profiles,idleApp={'support':True,'appId':'other.home'})):
            self.profiles = profiles
            with self.subTest(profiles=profiles), self.assertRaises(ValueError): p.prepare_stock_home()
            self.assertNotIn('home-stock',self.calls)
            self.assertFalse((self.root/'stock-home-initialization.json').exists())

    def test_prior_activation_or_profile_artifacts_prevent_initialization(self):
        for name in ('profile-trial.json','persistent-intent.json','persistent-binding.json','recovery-provision.json','profile-candidate.stage'):
            file = self.root/name
            file.symlink_to(self.root/'missing')
            with self.subTest(name=name), self.assertRaises(ValueError): p.prepare_stock_home()
            self.assertNotIn('home-stock',self.calls)
            file.unlink()
        with patch.object(p.os.path,'lexists',side_effect=lambda path: str(path)=='/var/webos-profile/override/clean-your-tv-root.json'):
            with self.assertRaises(ValueError): p.prepare_stock_home()
        self.assertNotIn('home-stock',self.calls)

    def test_lost_acknowledgement_is_reconciled_by_readback(self):
        self.write_mode = 'lost'
        p.prepare_stock_home()
        self.assertEqual(self.calls.count('home-stock'),1)
        self.assertEqual(json.loads((self.root/'stock-home-initialization.json').read_text())['phase'],'verified')

    def test_success_without_effect_stays_pending_and_is_never_replayed(self):
        self.write_mode = 'no-op'
        with self.assertRaises(ValueError): p.prepare_stock_home()
        self.assertEqual(json.loads((self.root/'stock-home-initialization.json').read_text())['phase'],'submitted')
        with self.assertRaises(ValueError): p.prepare_stock_home()
        self.assertEqual(self.calls.count('home-stock'),1)

    def test_interrupted_success_can_be_verified_without_another_write(self):
        self.write_mode = 'interrupted'
        with self.assertRaises(KeyboardInterrupt): p.prepare_stock_home()
        p.prepare_stock_home()
        self.assertEqual(self.calls.count('home-stock'),1)
        self.assertEqual(json.loads((self.root/'stock-home-initialization.json').read_text())['phase'],'verified')

    def test_present_malformed_receipt_never_becomes_a_fresh_submission(self):
        receipt = self.root/'stock-home-initialization.json'
        for value in ('null','false','[]','{}','{"schema":1}','broken'):
            receipt.write_text(value)
            with self.subTest(value=value), self.assertRaises(ValueError): p.prepare_stock_home()
            self.assertEqual(receipt.read_text(),value)
            self.assertNotIn('home-stock',self.calls)

    def test_changed_unrelated_setting_or_profile_refuses_completion(self):
        real = self.bus
        for change in ('setting','profile'):
            with self.subTest(change=change):
                self.apps.pop('home',None)
                (self.root/'stock-home-initialization.json').unlink(missing_ok=True)
                def bus(method):
                    result = real(method)
                    if method == 'home-stock':
                        if change == 'setting': self.apps['MembershipApp'] = 'changed'
                        else: self.profiles['idleApp']['support'] = False
                    return result
                with patch.object(p,'rpc',side_effect=bus), self.assertRaises(ValueError): p.prepare_stock_home()

    def test_finalize_normalizes_before_status_and_publishes_only_after_registration(self):
        (self.root/'recovery-provision.pending.json').write_text('{}')
        real = self.bus
        def bus(method):
            if method in ('status','register'):
                self.assertEqual(self.apps['home'],STOCK)
                self.assertFalse((self.root/'recovery-provision.json').exists())
                self.calls.append(method)
                return {'root':True,'registered':True,'activityName':p.NAME+'.recovery'}
            return real(method)
        def firmware():
            self.assertTrue((self.root/'recovery-provision.json').exists())
            self.calls.append('firmware')
        with patch.object(p,'rpc',side_effect=bus), patch.object(p,'manifest',return_value={}), patch('startup_hook.install'), patch.object(p,'register_firmware_access',side_effect=firmware):
            p.finalize()
        self.assertEqual(self.calls[-3:],['status','register','firmware'])
        self.assertTrue((self.root/'recovery-provision.json').exists())

    def test_failed_initialization_never_calls_service_or_publishes_readiness(self):
        (self.root/'recovery-provision.pending.json').write_text('{}')
        self.write_mode = 'no-op'
        with patch.object(p,'manifest',return_value={}), patch('startup_hook.install') as hook:
            with self.assertRaises(ValueError): p.finalize()
            hook.assert_not_called()
        self.assertNotIn('status',self.calls)
        self.assertFalse((self.root/'recovery-provision.json').exists())
        self.assertEqual(json.loads((self.root/'recovery-failure.json').read_text())['phase'],'stock-home')

    def test_runtime_status_does_not_initialize_an_absent_override(self):
        sys.path.insert(0,str(Path(__file__).parents[1]/'runtime'))
        import device_adapter as d
        import transport
        calls = []
        def bus(uri,payload):
            calls.append(uri)
            if uri.endswith('/getProfiles'): return {'returnValue':True,'profiles':self.profiles}
            if uri.endswith('/getSystemSettings'): return {'returnValue':True,'settings':{'defaultApps':self.apps}}
            self.fail('Runtime status attempted a mutation')
        with patch.object(d,'STATE',self.root), patch.object(d,'EXPECTED_UID',os.geteuid()), patch.object(transport,'call',side_effect=bus):
            with self.assertRaisesRegex(ValueError,'Missing or malformed routing destination'): d.main('status')
        self.assertEqual(len(calls),2)
        self.assertFalse((self.root/'stock-home-initialization.json').exists())


if __name__ == '__main__': unittest.main()
