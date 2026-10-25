import fcntl
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from cytv.system_updater_remove import SCRIPT, COMMAND

namespace={'__name__':'system_remove_test'}
exec(SCRIPT,namespace)
APP='com.cleanyourtv.system.updater';SERVICE=APP+'.service'

def digest(raw):return hashlib.sha256(raw).hexdigest()

class RemovalTests(unittest.TestCase):
    def fixture(self,root):
        state=root/'state';state.mkdir(mode=0o700);code=state/'code';code.mkdir();(state/'cache').mkdir()
        (code/'run-system-updater.py').write_bytes(b'fixed supervisor')
        (state/'bootstrap.json').write_text('{"phase":"complete","edition":"no-root"}')
        (state/'infrastructure.json').write_text(json.dumps({'schema':1,'code':{'run-system-updater.py':digest(b'fixed supervisor')}}))
        components=[]
        for name in ('home','helper','updater'):
            raw=name.encode();sha=digest(raw);(state/'cache'/sha).write_bytes(raw)
            components.append({'name':name,'size':len(raw),'sha256':sha,'local':True})
        (state/'legacy-lockdown.json').write_text('{"schema":1,"files":{}}')
        (state/'baseline.json').write_text(json.dumps({'schema':1,'edition':'no-root','supervisor':1,'components':components}))
        base=root/'bus';base.mkdir();installed=root/'apps';installed.mkdir();proc=root/'proc';proc.mkdir()
        registration={}
        for folder,suffix in (('services.d','.service'),('roles.d','.service.json'),('client-permissions.d','.service.json'),('api-permissions.d','.api.json')):
            (base/folder).mkdir();path=base/folder/(SERVICE+suffix)
            path.write_text(folder);registration[str(path)]={'installed':folder,'original':'original'}
        (state/'registration.json').write_text(json.dumps({'files':registration}))
        (base/'manifests.d').mkdir()
        manifest={'id':APP,'version':'1.0.0','serviceFiles':[str(base/'services.d'/(SERVICE+'.service'))], 'apiPermissionFiles':[str(base/'api-permissions.d'/(SERVICE+'.api.json'))], 'roleFiles':[str(base/'roles.d'/(SERVICE+'.service.json')),str(base/'roles.d'/(APP+'.app.json'))], 'clientPermissionFiles':[str(base/'client-permissions.d'/(SERVICE+'.service.json')),str(base/'client-permissions.d'/(APP+'.app.json'))]}
        (base/'manifests.d'/(APP+'.json')).write_text(json.dumps(manifest))
        role={'appId':APP,'type':'regular','allowedNames':[APP+'-*'],'trustLevel':'public','permissions':[{'service':APP+'-*','outbound':['*']}]}
        (base/'roles.d'/(APP+'.app.json')).write_text(json.dumps(role));(base/'client-permissions.d'/(APP+'.app.json')).write_text(json.dumps({APP+'-*':[]}))
        hook=root/'boot';hook.write_text('#!/bin/sh\n/usr/bin/python3 '+str(state/'code/run-system-updater.py')+' worker </dev/null >/dev/null 2>&1 &\n')
        return dict(state=state,base=base,hook=hook,installed=installed,proc=proc,refresh=lambda:None,stop_processes=lambda _:None)

    def test_status_is_read_only_and_proves_bootstrap_code_and_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve());root=Path(tmp)
            before={str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()}
            value=namespace['operate']('status',**args)
            self.assertTrue(value['present']);self.assertTrue(value['bootstrap_complete'])
            self.assertEqual(before,{str(p):p.read_bytes() for p in root.rglob('*') if p.is_file()})
            (args['state']/'code/run-system-updater.py').write_bytes(b'tampered')
            with self.assertRaisesRegex(ValueError,'integrity'):namespace['operate']('status',**args)

    def test_disable_retry_and_archive_retain_cache_and_owned_registrations(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve());state=args['state']
            archive=str(state)+'.archive-'+'a'*32
            first=namespace['operate']('disable',destination=archive,**args)
            self.assertTrue(first['disabled']);self.assertFalse(args['hook'].exists())
            self.assertTrue(namespace['operate']('disable',destination=archive,**args)['disabled'])
            package=args['installed']/'applications'/APP;package.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError,'package'):namespace['operate']('archive',destination=archive,**args)
            package.rmdir();value=namespace['operate']('archive',destination=archive,**args)
            self.assertFalse(state.exists());self.assertTrue(value['removed'])
            self.assertTrue((Path(archive)/'cache').is_dir());self.assertTrue((Path(archive)/'removed-registration/hook').exists())
            self.assertFalse(namespace['operate']('status',**args)['present'])

    def test_conflicts_partial_setup_and_unknown_outcome_never_change_files(self):
        for case in ('hook','receipt','transaction','cache','bootstrap','symlink'):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as tmp:
                args=self.fixture(Path(tmp).resolve());state=args['state']
                if case=='hook':args['hook'].write_text('someone else')
                if case=='receipt':(state/'registration.json').write_text('{"files":{"/foreign":{"installed":"x"}}}')
                if case=='transaction':(state/'transaction.json').write_text('{"schema":1,"phase":"installing"}')
                if case=='cache':next((state/'cache').iterdir()).write_bytes(b'bad')
                if case=='bootstrap':(state/'bootstrap.json').write_text('{"phase":"submitting-supervisor"}')
                if case=='symlink':args['hook'].unlink();args['hook'].symlink_to(state/'bootstrap.json')
                before={str(p):p.read_bytes() for p in Path(tmp).rglob('*') if p.is_file()}
                with self.assertRaises((ValueError,OSError)):namespace['operate']('disable',**args)
                self.assertEqual(before,{str(p):p.read_bytes() for p in Path(tmp).rglob('*') if p.is_file()})

    def test_locked_worker_and_exact_running_worker_block_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve());lock=args['state']/'daemon.lock'
            with lock.open('w') as stream:
                fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with self.assertRaisesRegex(ValueError,'worker'):namespace['operate']('status',**args)
            proc=args['proc']/'123';proc.mkdir();(proc/'cmdline').write_bytes(b'/usr/bin/python3\0'+str(args['state']/'code/run-system-updater.py').encode()+b'\0worker\0')
            (proc/'stat').write_text('123 (python) '+ ' '.join(['0']*19+['1234']))
            with self.assertRaisesRegex(ValueError,'worker'):namespace['operate']('status',**args)

    def test_absent_is_noop_but_orphan_artifacts_refuse(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve())
            namespace['operate']('disable',**args);namespace['operate']('archive',**args)
            self.assertEqual(namespace['operate']('status',**args),{'present':False})
            args['hook'].write_text('orphan')
            with self.assertRaisesRegex(ValueError,'ownership'):namespace['operate']('status',**args)

    def test_command_fits_ssh_limit_and_is_self_contained(self):
        import shlex
        self.assertLess(len(shlex.join(['/usr/bin/python3','-c',COMMAND,'status'])),8000)
        self.assertIn('operate',namespace)

    def test_process_matching_is_exact_and_includes_service_wrapper(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp).resolve();code=root/'state/code';proc=root/'proc';proc.mkdir()
            for pid,args in ((101,['/bin/sh',str(code.parent/'run-service')]),(102,['/usr/bin/node','unrelated.js',str(code)]),(103,['/usr/bin/python3',str(code/'run-system-updater.py'),'worker'])):
                path=proc/str(pid);path.mkdir();(path/'cmdline').write_bytes(b'\0'.join(a.encode() for a in args)+b'\0');(path/'stat').write_text(str(pid)+' (process) '+ ' '.join(['0']*19+['1234']))
            matches=namespace['processes'](code,proc)
            self.assertEqual({p[0] for p in matches},{101,103})
            self.assertEqual([p[2] for p in matches if p[0]==103],[True])

    def test_disable_restores_only_receipted_legacy_grants(self):
        for conflict in (False,True):
            with self.subTest(conflict=conflict),tempfile.TemporaryDirectory() as tmp:
                args=self.fixture(Path(tmp).resolve());state=args['state'];api=args['base']/'api-permissions.d/com.cleanyourtv.updater.permissions.json'
                original='{ "ui": ["legacy/install"] }';disabled='{ "ui": [] }';api.write_text(disabled)
                record={'schema':1,'files':{str(api):{'original':original,'disabled':disabled,'mode':0o600}}}
                (state/'legacy-lockdown.json').write_text(json.dumps(record))
                if conflict:api.write_text('other owner')
                if conflict:
                    with self.assertRaisesRegex(ValueError,'lockdown'):namespace['operate']('disable',**args)
                    self.assertTrue(args['hook'].exists());self.assertEqual(api.read_text(),'other owner')
                else:
                    namespace['operate']('disable',**args);self.assertEqual(api.read_text(),original)
                    self.assertTrue(namespace['operate']('disable',**args)['disabled'])

    def test_archive_allows_owned_legacy_cleanup_after_confirmed_restore(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve());api=args['base']/'api-permissions.d/com.cleanyourtv.updater.permissions.json';api.write_text('disabled')
            (args['state']/'legacy-lockdown.json').write_text(json.dumps({'schema':1,'files':{str(api):{'original':'original','disabled':'disabled','mode':0o600}}}))
            namespace['operate']('disable',**args);self.assertEqual(api.read_text(),'original')
            api.unlink()
            self.assertTrue(namespace['operate']('archive',**args)['removed'])
