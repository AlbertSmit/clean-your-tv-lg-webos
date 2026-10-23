import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock
spec = importlib.util.spec_from_file_location('root_provision',Path(__file__).parents[1]/'provision.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

class ProvisionTests(unittest.TestCase):
    def original(self):
        return {'service':'[D-BUS Service]\nName='+p.NAME+'\nExec=/usr/bin/run-js-service -n '+str(p.SERVICE)+'\n',
                'role':json.dumps({'appId':p.NAME,'allowedNames':['*'],'permissions':[{'outbound':['*']}]}),
                'client':'{}','api':'{}'}
    def test_narrow_rules(self):
        result=p.plan(self.original())
        self.assertIn(str(p.RUNNER).encode(),result['service'])
        role=json.loads(result['role'])
        self.assertEqual(role['allowedNames'],[p.NAME])
        self.assertNotIn('*',role['permissions'][0]['outbound'])
        api=json.loads(result['api'])
        self.assertEqual(api['activities.callbacks'],[p.NAME+'/boot'])
        self.assertNotIn(p.NAME+'/trial',str(api))
    def test_unexpected_launcher_and_app_refused(self):
        original=self.original();original['service']=original['service'].replace('/usr/bin/run-js-service','/bin/sh')
        with self.assertRaises(ValueError):p.plan(original)
        original=self.original();original['role']='{"appId":"other"}'
        with self.assertRaises(ValueError):p.plan(original)
    def test_no_manifest_before_registration(self):
        data={'version':1}
        with patch.object(p,'secure',return_value=json.dumps(data).encode()),patch.object(p,'manifest',return_value=data),patch.object(p,'rpc',return_value={'returnValue':True,'root':False}),patch.object(p,'write') as write:
            with self.assertRaises(ValueError):p.finalize()
            write.assert_not_called()
    def test_finalize_owned_registration(self):
        data={'version':1}
        with patch.object(p,'secure',return_value=json.dumps(data).encode()),patch.object(p,'manifest',return_value=data),patch.object(p,'rpc',return_value={'root':True,'registered':True,'activityName':p.NAME+'.recovery'}),patch.object(p,'write') as write:
            p.finalize()
            self.assertEqual(write.call_args[0][0],p.STATE/'recovery-provision.json')
    def test_runtime_drift_refuses_registration(self):
        with patch.object(p,'secure',return_value=b'{}'),patch.object(p,'manifest',return_value={'changed':True}),patch.object(p,'rpc') as rpc:
            with self.assertRaises(ValueError):p.finalize()
            rpc.assert_not_called()
    def test_rollback_drift_before_mutation(self):
        entries={str(path):{'original':'x','original_sha256':p.sha(b'x'),'installed_sha256':p.sha(b'y')} for path in p.FILES.values()}
        saved={'version':1,'service':p.NAME,'files':entries}
        with patch.object(p,'secure',side_effect=[json.dumps(saved).encode(),b'drift']),patch.object(p,'rpc') as rpc,patch.object(p,'write') as write:
            with self.assertRaises(ValueError):p.rollback()
            rpc.assert_not_called();write.assert_not_called()

    def test_restore_pending_keeps_activity(self):
        entries={str(path):{'original':'x','original_sha256':p.sha(b'x'),'installed_sha256':p.sha(b'y')} for path in p.FILES.values()}
        saved={'version':1,'service':p.NAME,'files':entries}
        for state in ('recovering','conflict','superseded'):
            with patch.object(p,'disable_trials'),patch.object(p,'secure',side_effect=[json.dumps(saved).encode()]+[b'y']*4),patch.object(p,'rpc',return_value={'returnValue':True,'result':{'returnValue':True,'result':state}}) as rpc,patch.object(p,'write') as write:
                with self.assertRaises(ValueError):p.rollback()
                rpc.assert_called_once_with('restore');write.assert_not_called()
    def test_rpc_keeps_stdin_open_until_reply(self):
        child=MagicMock(); child.poll.return_value=None
        with patch.object(p.subprocess,'Popen',return_value=child) as popen,patch.object(p.select,'select',return_value=([child.stdout],[],[])),patch.object(p.os,'read',return_value=b'{"returnValue":true}'):
            self.assertTrue(p.rpc('status')['returnValue'])
            self.assertIs(popen.call_args.kwargs['stdin'],p.subprocess.PIPE)
            child.stdin.close.assert_not_called()
            child.terminate.assert_called_once()
            child.communicate.assert_called_once_with(timeout=1)
    def test_refresh_fixed_scan(self):
        with patch.object(p.Path,'is_file',return_value=True),patch.object(p.subprocess,'run') as run:
            self.assertTrue(p.refresh()['returnValue'])
            self.assertEqual(run.call_args.args[0],['/usr/bin/ls-control','scan-services'])

    def test_repeated_rollback_checks_restored_hashes_without_rpc(self):
        entries={str(path):{'original':'x','original_sha256':p.sha(b'x'),'installed_sha256':p.sha(b'y'),'mode':0o644,'uid':0,'gid':0} for path in p.FILES.values()}
        saved={'version':1,'service':p.NAME,'phase':'rolled-back','files':entries}
        info=MagicMock(st_mode=0o100644,st_uid=0,st_gid=0)
        with patch.object(p,'secure',side_effect=[json.dumps(saved).encode()]+[b'x']*4),patch.object(p.Path,'stat',return_value=info),patch.object(p.os.path,'lexists',return_value=False),patch.object(p,'rpc') as rpc,patch.object(p,'write') as write:
            self.assertTrue(p.rollback()['already_rolled_back'])
            rpc.assert_not_called();write.assert_not_called()
        with patch.object(p,'secure',side_effect=[json.dumps(saved).encode(),b'drift']),patch.object(p.os.path,'lexists',return_value=False),patch.object(p,'rpc') as rpc:
            with self.assertRaises(ValueError):p.rollback()
            rpc.assert_not_called()

    def test_partial_restoration_resumes_without_service(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            paths={name:root/name for name in ('service','role','client','api')}
            entries={}
            for path in paths.values():
                path.write_bytes(b'installed');path.chmod(0o644)
                info=path.stat()
                entries[str(path)]={'original':'original','original_sha256':p.sha(b'original'),'installed_sha256':p.sha(b'installed'),'mode':0o644,'uid':info.st_uid,'gid':info.st_gid}
            snapshot=root/'ls2-provision-snapshot.json'
            snapshot.write_text(json.dumps({'version':1,'service':p.NAME,'files':entries}))
            real_write=p.write
            def interrupted(path,data,mode=0o600):
                if path == paths['role']:raise OSError('simulated power loss')
                real_write(path,data,mode)
            with patch.object(p,'STATE',root),patch.object(p,'FILES',paths),patch.object(p,'secure',side_effect=lambda path:path.read_bytes()),patch.object(p,'disable_trials'),patch.object(p.os,'chown'),patch.object(p,'rpc',side_effect=[{'result':{'returnValue':True,'result':'restored'}},{'returnValue':True}]) as rpc,patch.object(p,'write',side_effect=interrupted):
                with self.assertRaises(OSError):p.rollback()
                self.assertEqual(json.loads(snapshot.read_text())['phase'],'restoring')
                self.assertEqual(rpc.call_count,2)
            with patch.object(p,'STATE',root),patch.object(p,'FILES',paths),patch.object(p,'secure',side_effect=lambda path:path.read_bytes()),patch.object(p.os,'chown'),patch.object(p,'rpc') as rpc:
                self.assertTrue(p.rollback()['returnValue'])
                rpc.assert_not_called()
                self.assertTrue(p.rollback()['already_rolled_back'])
                self.assertTrue(all(path.read_bytes()==b'original' for path in paths.values()))

if __name__=='__main__':unittest.main()
