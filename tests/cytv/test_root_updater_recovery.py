import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock
from cytv import operations,state


class UpdaterRecoveryTests(unittest.TestCase):
    def test_only_proven_unstarted_updater_allows_retry_and_retains_receipt(self):
        for failure in (None,'fresh','missing','bootstrap','updater','busy','files','integrity','routing','guardian','intent','phase','action','query'):
            with self.subTest(failure=failure), tempfile.TemporaryDirectory() as tmp:
                store=state.Store(tmp); profile=state.target('tv.local','root')
                remote=MagicMock()
                remote.run.return_value='CYTV_UPDATER_ABSENT' if failure!='updater' else 'CYTV_EXISTING_UPDATER'
                if failure=='query':remote.run.side_effect=RuntimeError('unavailable')
                remote.luna.return_value={'returnValue':True,'status':{'apps':[] if failure!='busy' else [{}]}}
                installer=operations.Installer(remote,store,profile,Path(tmp),{},lambda *_:None)
                installer.root_files_match=MagicMock(return_value=failure!='files')
                store.begin(profile,'setup-root-updater',stage='setup',requires_updater=True,release_sha='a'*64,bundle_sha='b'*64)
                pending=store.pending(profile)
                if failure=='phase':pending['stage']='verify'
                if failure=='action':pending['action']='install'
                result={'recovery':{'integrity_verified':failure!='integrity'},'guardian_active':failure=='guardian',
                        'intent':{'enabled':failure=='intent'},'effective':{'sam_home':'com.webos.app.home',
                        'profiles':{'defaultApps':{'categories':{'home':'com.webos.app.home'}},'idleApp':{'appId':'com.webos.app.home'}}}}
                if failure in ('fresh', 'missing'):
                    result.pop('guardian_active')
                    result['intent'] = None
                    if failure == 'fresh': result['journal_exists'] = False
                success = failure in (None, 'fresh')
                if failure=='routing':result['effective']['sam_home']='foreign.home'
                if failure in ('phase', 'action'):
                    store.checkpoint(profile, **{key: pending[key] for key in ('stage', 'action')})
                reply = remote.run.return_value
                if failure != 'query':
                    remote.run.side_effect = lambda command: ('{"stage":"installed-recovery-only"}' if 'deploy.json' in command else ('busy' if failure == 'bootstrap' else 'CYTV_BOOTSTRAP_IDLE') if 'CYTV_BOOTSTRAP_IDLE' in command else reply)
                    installer.root_action = MagicMock(return_value={'result': result})
                    status = installer.status()
                    self.assertEqual(status['reconciled'] is not None, success)
                else:
                    self.assertFalse(installer.recover_unstarted_root_updater(pending, result))
                if success:
                    self.assertIsNone(store.pending(profile))
                    saved=list(store.device_dir(profile).glob('recovery-*.json'))
                    self.assertEqual(len(saved),1)
                    self.assertEqual(json.loads(saved[0].read_text())['previous'],pending)
                else:self.assertIsNotNone(store.pending(profile))
                remote.upload.assert_not_called()
