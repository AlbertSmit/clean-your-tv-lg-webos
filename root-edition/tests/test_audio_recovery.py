"""Audio state effects are checked through a fake Luna boundary and real private files."""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'runtime'))

class AudioTests(unittest.TestCase):
    def setUp(self):
        path=ROOT/'runtime/cli.py'
        self.assertTrue(path.exists(), 'eARC runtime is missing')
        spec=importlib.util.spec_from_file_location('audio_recovery', path)
        self.a=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.a)
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.uid=patch.object(self.a.d,'EXPECTED_UID',__import__('os').getuid());self.uid.start();self.addCleanup(self.uid.stop)
        self.store=self.a.Store(Path(self.tmp.name))
        self.now=0.;self.writes=[];self.output='external_arc';self.configured='external_arc';self.earc='on';self.power='Active';self.after_sleep=None;self.fail_write=False
        self.engine=self.a.Engine(self.store,self.call,self.sleep,lambda:self.now,lambda:False)
    def call(self,uri,payload):
        if uri.endswith('/getPowerState'):return dict(returnValue=True,state=self.power,subscribed=True)
        if uri.endswith('/getSoundOutput'):return dict(returnValue=True,soundOutput=self.output,settingsSoundOutputs=[self.configured])
        if uri.endswith('/getSystemSettings'):return dict(returnValue=True,settings=dict(eArcSupport=self.earc,soundOutput=self.configured))
        if uri.endswith('/setSystemSettings'):
            self.earc=payload['settings']['eArcSupport'];self.writes.append(self.earc)
            if self.fail_write:raise TimeoutError('uncertain')
            return dict(returnValue=True)
        if uri.endswith('/setSoundOutput'):
            self.output=payload['soundOutput'];self.writes.append(self.output);return dict(returnValue=True)
        raise AssertionError(uri)
    def sleep(self,seconds):
        self.now+=seconds
        if self.after_sleep:
            action,self.after_sleep=self.after_sleep,None;action()
    def test_manual_reset_restores_setting_without_touching_other_system_settings(self):
        result=self.engine.perform('restart-earc')
        self.assertEqual(self.writes,['off','on']);self.assertEqual(result,'settings-restored')
        self.assertIsNone(self.store.read('pending'));self.assertEqual(self.store.read('last')['result'],'settings-restored')
    def test_unknown_arc_and_combined_outputs_are_never_toggled(self):
        for output,earc in [('external_arc','off'),('external_arc',''),('external_arc',True),('tv_speaker_external_arc_harmony','on'),('tv_speaker','on')]:
            self.output=self.configured=output;self.earc=earc
            self.assertEqual(self.engine.perform('restart-earc'),'unsupported')
        self.assertEqual(self.writes,[])
    def test_unknown_configured_route_never_defaults_to_hdmi(self):
        self.configured='';self.output='tv_speaker'
        self.assertEqual(self.engine.perform('restore-hdmi'),'unsupported');self.assertEqual(self.writes,[])
    def test_manual_route_restore_only_uses_confirmed_pure_hdmi_preference(self):
        self.output='tv_speaker'
        self.assertEqual(self.engine.perform('restore-hdmi'),'route-restored');self.assertEqual(self.writes,['external_arc'])
    def test_standby_cannot_start_reset(self):
        self.power='Active Standby';self.assertEqual(self.engine.perform('restart-earc'),'unsupported');self.assertFalse(self.writes)
    def test_disable_during_off_interval_still_restores_owned_setting(self):
        self.store.configure(True)
        self.after_sleep=lambda:self.store.configure(False)
        self.assertEqual(self.engine.perform('restart-earc'),'settings-restored');self.assertEqual(self.earc,'on')
        self.assertFalse(self.store.policy()['enabled'])
    def test_user_route_change_retains_journal_instead_of_overwriting_choice(self):
        self.after_sleep=lambda:setattr(self,'output','tv_speaker')
        self.assertEqual(self.engine.perform('restart-earc'),'needs-restore');self.assertEqual(self.writes,['off'])
        self.assertIsNotNone(self.store.read('pending'))
        self.assertEqual(self.engine.perform('restart-earc'),'needs-restore')
    def test_existing_pending_transaction_requires_explicit_restore(self):
        self.store.save('pending',dict(schema=1,original='on'))
        self.earc='off'
        self.assertEqual(self.engine.perform('restart-earc'),'needs-restore');self.assertFalse(self.writes)
        self.assertEqual(self.engine.perform('restore-setting'),'settings-restored');self.assertEqual(self.writes,['on'])
    def test_uncertain_write_never_announces_completion(self):
        self.fail_write=True
        self.assertEqual(self.engine.perform('restart-earc'),'needs-restore')
        self.assertIsNotNone(self.store.read('pending'))
    def test_stale_auto_generation_and_emergency_cannot_start_reset(self):
        policy=self.store.configure(True);self.store.configure(False)
        self.assertEqual(self.engine.perform('restart-earc',generation=policy['generation']),'canceled');self.assertFalse(self.writes)
        self.engine.blocked=lambda:True
        self.assertEqual(self.engine.perform('restart-earc'),'canceled')
    def test_operation_lock_serializes_distinct_process_requests(self):
        with self.store.lock('operation'):
            self.assertEqual(self.engine.perform('restart-earc'),'busy')
        self.assertFalse(self.writes)
    def test_power_snapshots_and_duplicate_active_events_do_not_reset_working_audio(self):
        wake=self.a.WakeWindow(lambda:self.now)
        wake.event('Active');self.now=12;self.assertFalse(wake.due())
        wake.event('Active Standby');wake.event('Active');wake.event('Active')
        self.now=23;self.assertTrue(wake.due());self.assertFalse(wake.due())
        wake.event('Active');self.now=100;self.assertFalse(wake.due())
    def test_late_or_canceled_wake_window_is_not_replayed(self):
        wake=self.a.WakeWindow(lambda:self.now,boot=True)
        wake.event('Active');self.now=31;self.assertFalse(wake.due())
        wake.event('Active Standby');wake.event('Active');wake.event('Active Standby')
        self.now=45;self.assertFalse(wake.due())
    def test_policy_and_pending_file_validation_refuse_unsafe_data(self):
        with self.assertRaises(ValueError):self.store.configure('true')
        self.store.save('pending',{'original':'off'})
        with self.assertRaises(ValueError):self.engine.perform('restore-setting')
    def test_persisted_settings_fallback_supports_older_audio_service_without_guessing(self):
        old=self.call
        def legacy(uri,payload):
            reply=old(uri,payload)
            if uri.endswith('/getSoundOutput'):reply.pop('settingsSoundOutputs')
            return reply
        self.engine.call=legacy
        self.assertEqual(self.engine.perform('restart-earc'),'settings-restored')
        self.assertEqual(self.writes,['off','on'])
    def test_conflicting_configured_sources_are_not_overwritten(self):
        old=self.call
        def conflict(uri,payload):
            reply=old(uri,payload)
            if uri.endswith('/getSystemSettings'):reply['settings']['soundOutput']='tv_speaker'
            return reply
        self.engine.call=conflict
        self.assertEqual(self.engine.perform('restart-earc'),'unsupported');self.assertFalse(self.writes)
    def test_manual_status_survives_unsupported_power_subscription(self):
        old=self.call
        def unsupported(uri,payload):
            if uri.endswith('/getPowerState') and payload.get('subscribe'):raise RuntimeError('subscription unavailable')
            return old(uri,payload)
        self.engine.call=unsupported
        reply=self.engine.status()
        self.assertTrue(reply['canRestart']);self.assertFalse(reply['autoSupported'])
    def test_worker_consumes_subscription_once_per_genuine_wake_and_exits_when_disabled(self):
        import contextlib,json
        from unittest.mock import MagicMock
        import update_guard,intent_runtime
        self.store.configure(True)
        child=MagicMock();child.poll.return_value=None
        messages=iter(['Active','Active Standby','Active','Active'])
        def select_event(*args):
            self.now+=1
            if self.now<5:return ([child.stdout],[],[])
            if self.now>17:self.store.configure(False)
            return ([],[],[])
        def read(*args):
            state=next(messages)
            return json.dumps(dict(returnValue=True,subscribed=True,state=state)).encode()
        with patch.object(self.a,'Engine',return_value=self.engine),patch.object(self.a,'blocked',return_value=False),patch.object(self.a.subprocess,'Popen',return_value=child),patch.object(self.a.select,'select',side_effect=select_event),patch.object(self.a.os,'read',side_effect=read),patch.object(self.a.time,'monotonic',side_effect=lambda:self.now),patch.object(self.a.d,'process_start',return_value='start'),patch.object(intent_runtime,'boot_identity',return_value='boot'),patch.object(update_guard,'control',side_effect=lambda *a:contextlib.nullcontext()):
            self.a.worker(self.store)
        self.assertEqual(self.writes,['off','on']);self.assertFalse(self.store.policy()['enabled'])
        self.assertIsNone(self.store.read('observer'))
        child.terminate.assert_called_once()
    def test_disable_or_emergency_during_initial_reads_prevents_first_write(self):
        old=self.call
        for emergency in (False,True):
            policy=self.store.configure(True)
            self.engine.blocked=lambda:False
            def canceled(uri,payload):
                reply=old(uri,payload)
                if uri.endswith('/getSystemSettings'):
                    if emergency:self.engine.blocked=lambda:True
                    else:self.store.configure(False)
                return reply
            self.engine.call=canceled
            self.assertEqual(self.engine.perform('restart-earc',generation=policy['generation']),'canceled')
            self.assertEqual(self.writes,[])
        self.engine.call=old
    def test_optional_audio_failure_cannot_block_explicit_home_restore(self):
        import cli,intent_runtime,update_guard
        with patch.object(cli,'inhibit',side_effect=ValueError('unsafe optional policy')),patch.object(update_guard,'cancel'),patch.object(intent_runtime,'restore',return_value='restored'):
            self.assertEqual(cli.execute('restore'),'restored')
    def test_repeated_or_late_boot_launch_does_not_rearm_cold_reset(self):
        import intent_runtime
        from unittest.mock import MagicMock
        self.store.configure(True)
        with patch.object(self.a,'observer_live',return_value=False),patch.object(self.a,'pending_live',return_value=False),patch.object(intent_runtime,'boot_identity',return_value='boot-a'),patch.object(self.a.time,'monotonic',return_value=20),patch.object(self.a.d,'process_start',return_value='start'),patch.object(self.a.subprocess,'Popen',return_value=MagicMock(pid=123)) as spawn:
            self.a.launch(self.store,boot=True)
            self.assertEqual(spawn.call_args.args[0][-1],'boot')
            self.a.launch(self.store,boot=True)
            self.assertEqual(spawn.call_args.args[0][-1],'watch')
        with patch.object(self.a,'observer_live',return_value=False),patch.object(self.a,'pending_live',return_value=False),patch.object(intent_runtime,'boot_identity',return_value='boot-b'),patch.object(self.a.time,'monotonic',return_value=200),patch.object(self.a.d,'process_start',return_value='start'),patch.object(self.a.subprocess,'Popen',return_value=MagicMock(pid=123)) as spawn:
            self.a.launch(self.store,boot=True)
            self.assertEqual(spawn.call_args.args[0][-1],'watch')
    def test_duplicate_launch_preserves_pending_cold_worker(self):
        import intent_runtime
        from unittest.mock import MagicMock
        self.store.configure(True)
        with patch.object(self.a,'observer_live',return_value=False),patch.object(self.a,'pending_live',side_effect=[False,True]),patch.object(intent_runtime,'boot_identity',return_value='boot-a'),patch.object(self.a.time,'monotonic',return_value=20),patch.object(self.a.d,'process_start',return_value='start'),patch.object(self.a.subprocess,'Popen',return_value=MagicMock(pid=123)) as spawn:
            self.a.launch(self.store,boot=True)
            self.a.launch(self.store,boot=True)
            self.assertEqual(spawn.call_count,1)
            self.assertEqual(spawn.call_args.args[0][-1],'boot')
    def test_enable_never_acknowledges_an_emergency_published_after_it_started(self):
        self.store.configure(True)
        save=self.store.save
        fired=[]
        def emergency(name,value):
            save(name,value)
            if name=='policy' and value['enabled'] and not fired:
                fired.append(True)
                self.a.inhibit(Path(self.tmp.name))
        with patch.object(self.store,'save',side_effect=emergency):
            self.assertFalse(self.store.configure(True)['enabled'])
        self.assertFalse(self.store.policy()['enabled'])
        self.assertIsNotNone(self.store.read('stop'))
    def test_emergency_stop_survives_policy_lock_contention_and_requires_explicit_enable(self):
        policy=self.store.configure(True)
        with self.store.lock('policy'):
            self.a.inhibit(Path(self.tmp.name))
            self.assertFalse(self.store.policy()['enabled'])
            self.assertEqual(self.engine.perform('restart-earc',generation=policy['generation']),'canceled')
        self.assertFalse(self.store.policy()['enabled']);self.assertFalse(self.writes)
        self.assertTrue(self.store.configure(True)['enabled'])
        self.assertIsNotNone(self.store.read('stop'))
    def test_cancellation_during_reads_prevents_other_audio_writes_too(self):
        old=self.call
        for operation in ('restore-hdmi','restore-setting'):
            self.engine.blocked=lambda:False
            self.output='tv_speaker' if operation=='restore-hdmi' else 'external_arc'
            self.earc='off'
            if operation=='restore-setting':self.store.save('pending',dict(schema=1,original='on'))
            def cancel(uri,payload):
                reply=old(uri,payload)
                if uri.endswith('/getSystemSettings'):self.engine.blocked=lambda:True
                return reply
            self.engine.call=cancel
            self.assertEqual(self.engine.perform(operation),'canceled')
            self.assertFalse(self.writes)
        self.engine.call=old
    def test_receipt_is_durable_before_first_write_and_failed_restoration_keeps_it(self):
        old=self.call
        def no_restore(uri,payload):
            if uri.endswith('/setSystemSettings'):
                self.assertEqual(self.store.pending(),dict(schema=1,original='on'))
                if payload['settings']['eArcSupport']=='on':return dict(returnValue=True)
            return old(uri,payload)
        self.engine.call=no_restore
        self.assertEqual(self.engine.perform('restart-earc'),'needs-restore')
        self.assertIsNotNone(self.a.Store(Path(self.tmp.name)).pending())
        self.assertEqual(self.earc,'off')
    def test_emergency_during_enable_eligibility_is_not_acknowledged(self):
        import contextlib,update_guard
        old=self.call
        def cancel(uri,payload):
            reply=old(uri,payload)
            if uri.endswith('/getSystemSettings'):self.a.inhibit(Path(self.tmp.name))
            return reply
        self.engine.call=cancel
        with patch.object(self.a.os,'geteuid',return_value=0),patch.object(self.a,'blocked',return_value=False),patch.object(self.a,'Store',return_value=self.store),patch.object(self.a,'Engine',return_value=self.engine),patch.object(update_guard,'control',side_effect=lambda *a:contextlib.nullcontext()),patch.object(self.a,'launch') as launch:
            self.assertFalse(self.a.audio_main('enable')['returnValue'])
            launch.assert_not_called()
        self.assertFalse(self.store.policy()['enabled'])
    def test_old_worker_cannot_disable_newer_explicit_policy(self):
        old=self.store.configure(True)
        current=self.store.configure(True)
        self.store.configure(False,expected=old)
        self.assertEqual(self.store.policy(),current)
    def test_disable_during_enable_eligibility_cancels_older_request(self):
        import contextlib,update_guard
        old=self.call
        def disable(uri,payload):
            reply=old(uri,payload)
            if uri.endswith('/getSystemSettings'):self.store.configure(False)
            return reply
        self.engine.call=disable
        with patch.object(self.a.os,'geteuid',return_value=0),patch.object(self.a,'blocked',return_value=False),patch.object(self.a,'Store',return_value=self.store),patch.object(self.a,'Engine',return_value=self.engine),patch.object(update_guard,'control',side_effect=lambda *a:contextlib.nullcontext()),patch.object(self.a,'launch') as launch:
            self.assertFalse(self.a.audio_main('enable')['returnValue']);launch.assert_not_called()
        self.assertFalse(self.store.policy()['enabled'])
    def test_policy_file_symlink_is_rejected(self):
        self.store.root.joinpath('policy.json').symlink_to(Path(self.tmp.name)/'foreign')
        with self.assertRaises((ValueError,OSError)):self.store.policy()

if __name__=='__main__':unittest.main()
