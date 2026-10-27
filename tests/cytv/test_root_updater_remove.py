import json
import os
from pathlib import Path
import tempfile
import unittest
from cytv.root_updater_remove import SCRIPT

if os.name != 'posix':
    raise unittest.SkipTest('TV cleanup script requires POSIX locks and filesystem semantics')

namespace={'__name__':'cleanup_test'}
exec(SCRIPT,namespace)

class UpdaterRemovalTests(unittest.TestCase):
    def fixture(self, root):
        state=root/'state';state.mkdir(mode=0o700)
        base=root/'ls2';base.mkdir();installed=root/'apps';installed.mkdir()
        hook=root/'boot';registration={}
        for folder,suffix in (('services.d','.service'),('roles.d','.service.json'),('client-permissions.d','.service.json'),('api-permissions.d','.api.json')):
            (base/folder).mkdir();p=base/folder/('com.cleanyourtv.root.updater.service'+suffix)
            p.write_text(folder);registration[str(p)]={'installed':folder,'original':'old'}
        (state/'registration.json').write_text(json.dumps({'files':registration}))
        (base/'manifests.d').mkdir()
        service='com.cleanyourtv.root.updater.service';app='com.cleanyourtv.root.updater'
        manifest={'id':app,'version':'0.1.0','serviceFiles':[str(base/'services.d'/(service+'.service'))],
                  'apiPermissionFiles':[str(base/'api-permissions.d'/(service+'.api.json'))],
                  'roleFiles':[str(base/'roles.d'/(service+'.service.json')),str(base/'roles.d'/(app+'.app.json'))],
                  'clientPermissionFiles':[str(base/'client-permissions.d'/(service+'.service.json')),str(base/'client-permissions.d'/(app+'.app.json'))]}
        (base/'manifests.d'/(app+'.json')).write_text(json.dumps(manifest))
        hook.write_text('#!/bin/sh\n/usr/bin/python3 '+str(state/'code/run-updater.py')+' worker </dev/null >/dev/null 2>&1 &\n')
        return state,base,hook,installed,str(state)+'.archive-'+'a'*32


    def link_fixture(self,root):
        import hashlib
        import importlib.util
        spec=importlib.util.spec_from_file_location('hook_build',Path(__file__).parents[2]/'root-edition/startup_hook.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        args=self.fixture(root);state,base,hook,installed,_=args
        app='com.cleanyourtv.root.updater';target=installed/'applications'/app/'startup.sh';target.parent.mkdir(parents=True)
        target.write_bytes(module.packaged_content(app));(target.parent/'appinfo.json').write_text(json.dumps({'id':app}))
        hook.unlink();hook.symlink_to(target)
        (state/'startup-hook.json').write_text(json.dumps(dict(version=2,path=str(hook),target=str(target),owner_app=app,target_sha256=hashlib.sha256(target.read_bytes()).hexdigest())))
        return args,target

    def test_owned_link_archives_without_following_after_target_deletion(self):
        with tempfile.TemporaryDirectory() as tmp:
            args,target=self.link_fixture(Path(tmp).resolve())
            run=lambda action:namespace['operate'](action,*args,lambda:None,lambda _:None)
            self.assertTrue(run('inspect')['ownership_verified'])
            target.unlink();(target.parent/'appinfo.json').unlink();target.parent.rmdir()
            self.assertTrue(run('disable')['disabled']);self.assertTrue(run('disable')['disabled'])
            self.assertTrue((args[0]/'removed-registration/hook').is_symlink())
            self.assertTrue(run('finalize')['removed'])
            self.assertTrue((Path(args[4])/'startup-hook.json').exists())

    def test_foreign_link_or_changed_package_is_never_archived(self):
        for case in ('foreign','receipt'):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as tmp:
                args,target=self.link_fixture(Path(tmp).resolve());state,_,hook,_,_=args
                if case=='foreign':hook.unlink();hook.symlink_to(state/'registration.json')
                elif case=='changed':target.write_bytes(b'changed')
                else:(state/'startup-hook.json').unlink()
                with self.assertRaises((ValueError,OSError)):namespace['operate']('disable',*args,lambda:self.fail('refresh'),lambda _:None)
                self.assertTrue(hook.is_symlink());self.assertFalse((state/'cytv-removal.json').exists())

    def test_replaced_target_cannot_block_exact_owned_link_cleanup(self):
        with tempfile.TemporaryDirectory() as tmp:
            args,target=self.link_fixture(Path(tmp).resolve());target.write_bytes(b'foreign executable bytes');target.parent.chmod(0o777)
            self.assertTrue(namespace['operate']('disable',*args,lambda:None,lambda _:None)['disabled'])
    def test_private_wrapper_receipt_is_owned_and_removal_is_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve());state,_,hook,_,_=args
            raw=('#!/bin/sh\nunset NODE_OPTIONS NODE_PATH PYTHONHOME PYTHONPATH\nexec /usr/bin/node '+str(state/'code/python_boot.js')+' '+str(state)+' '+str(state/'code/startup_guard.py')+' com.cleanyourtv.root.updater\n')
            hook.write_text(raw);hook.chmod(0o700)
            (state/'startup-hook.json').write_text(json.dumps(dict(version=3,path=str(hook),owner_app='com.cleanyourtv.root.updater',sha256=__import__('hashlib').sha256(raw.encode()).hexdigest())))
            run=lambda action:namespace['operate'](action,*args,lambda:None,lambda _:None)
            self.assertTrue(run('inspect')['ownership_verified']);self.assertTrue(run('disable')['disabled']);self.assertTrue(run('disable')['disabled'])

    def test_interrupted_private_wrapper_publication_removes_exact_prior_link(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            args,target=self.link_fixture(Path(tmp).resolve());state,_,hook,_,_=args
            prior=(state/'startup-hook.json').read_bytes();(state/'startup-hook.previous.json').write_bytes(prior)
            raw=('#!/bin/sh\nunset NODE_OPTIONS NODE_PATH PYTHONHOME PYTHONPATH\nexec /usr/bin/node '+str(state/'code/python_boot.js')+' '+str(state)+' '+str(state/'code/startup_guard.py')+' com.cleanyourtv.root.updater\n').encode()
            (state/'startup-hook.json').write_text(json.dumps(dict(version=3,path=str(hook),owner_app='com.cleanyourtv.root.updater',sha256=hashlib.sha256(raw).hexdigest())))
            target.write_bytes(b'foreign script')
            self.assertTrue(namespace['operate']('disable',*args,lambda:None,lambda _:None)['disabled'])

    def test_managed_hook_requires_literal_owned_binding(self):
        managed='/var/lib/clean-your-tv-python/4a71641c8d5536175e404a961624e8656eba30e97b5026f6bd7dc31e4bbeaaea/bin/python3.13'
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve())
            state,base,hook,_,_=args
            launcher=state/'python-launcher'
            launcher.write_text('#!/bin/sh\nunset PYTHONHOME PYTHONPATH\nexport PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1\nexec '+managed+' "$@"\n');launcher.chmod(0o700)
            (state/'python-runtime.json').write_text(json.dumps({'schema':1,'executable':managed,'archive_sha256':managed.split('/')[-3],'inventory_sha256':'a'*64}))
            hook.write_text('#!/bin/sh\nunset NODE_OPTIONS NODE_PATH\n/usr/bin/node '+str(state/'code/python_boot.js')+' '+str(state)+' '+str(state/'code/run-updater.py')+' worker </dev/null >/dev/null 2>&1 &\n')
            self.assertTrue(namespace['operate']('inspect',*args,lambda:None,lambda _:None))
            launcher.write_text('#!/bin/sh\nexec /tmp/evil "$@"\n')
            with self.assertRaises(ValueError):namespace['operate']('inspect',*args,lambda:None,lambda _:None)

    def test_disable_is_repeatable_then_archives_only_after_package_absence(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve());calls=[]
            run=lambda action:namespace['operate'](action,*args,lambda:calls.append('refresh'),lambda code:calls.append('stop'))
            self.assertTrue(run('disable')['disabled']);self.assertTrue(run('disable')['disabled'])
            package=args[3]/'applications/com.cleanyourtv.root.updater';package.mkdir(parents=True)
            with self.assertRaisesRegex(ValueError,'remains'):run('finalize')
            package.rmdir()
            self.assertTrue(run('finalize')['removed']);self.assertFalse(args[0].exists())
            self.assertTrue(Path(args[4]).exists());self.assertTrue(run('finalize')['removed'])

    def test_conflict_and_pending_transaction_change_nothing(self):
        for case in ('changed','foreign','transaction','symlink'):
            with self.subTest(case=case),tempfile.TemporaryDirectory() as tmp:
                args=self.fixture(Path(tmp).resolve());state,base,hook,_,_=args
                if case=='changed':hook.write_text('someone else')
                if case=='transaction':(state/'transaction.json').write_text('{"schema":1,"phase":"installing"}')
                if case=='foreign':(state/'registration.json').write_text('{"files":{"/foreign":{"installed":"x"}}}')
                if case=='symlink':
                    hook.unlink();hook.symlink_to(state/'registration.json')
                with self.assertRaises((ValueError,OSError)):
                    namespace['operate']('disable',*args,lambda:self.fail('refresh'),lambda _:self.fail('stop'))
                self.assertTrue(os.path.lexists(hook))
                self.assertTrue(next((base/'services.d').iterdir()).exists())

    def test_empty_backup_directory_from_interrupted_prepare_can_resume(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve())
            (args[0]/'removed-registration').mkdir(mode=0o700)
            self.assertTrue(namespace['operate']('disable',*args,lambda:None,lambda _:None)['disabled'])

    def test_inspect_does_not_create_locks_journal_or_change_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            args=self.fixture(Path(tmp).resolve())
            before={str(p):p.read_bytes() for p in Path(tmp).rglob('*') if p.is_file()}
            self.assertTrue(namespace['operate']('inspect',*args,lambda:self.fail('refresh'),lambda _:self.fail('stop'))['ownership_verified'])
            after={str(p):p.read_bytes() for p in Path(tmp).rglob('*') if p.is_file()}
            self.assertEqual(before,after)

    def test_owned_legacy_permissions_are_removed_but_conflicts_are_kept(self):
        import hashlib
        from cytv.legacy_permissions_remove import SCRIPT as legacy
        ns={'__name__':'test'};exec(legacy,ns)
        for conflict in (False,True):
            with self.subTest(conflict=conflict),tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp).resolve();files=[]
                for folder in ('api-permissions.d','client-permissions.d','manifests.d'):
                    (root/folder).mkdir();p=root/folder/'com.cleanyourtv.updater.permissions.json';p.write_text('{}')
                    files.append({'path':str(p),'content':'{}','sha256':hashlib.sha256(b'{}').hexdigest()})
                receipt=root/'com.cleanyourtv.updater.permissions.receipt.json';receipt.write_text(json.dumps({'schema':1,'files':files}))
                if conflict:
                    Path(files[0]['path']).write_text('changed')
                    with self.assertRaises(ValueError):ns['operate'](root,lambda:self.fail('refresh'),os.geteuid())
                    self.assertTrue(all(Path(f['path']).exists() for f in files))
                else:
                    self.assertTrue(ns['operate'](root,lambda:None,os.geteuid()))
                    self.assertFalse(receipt.exists());self.assertFalse(any(Path(f['path']).exists() for f in files))

    def test_device_command_fits_webos_ssh_limit_and_preserves_script(self):
        import shlex
        from cytv.root_updater_remove import COMMAND
        self.assertLess(len(shlex.join(['/usr/bin/python3','-c',COMMAND,'finalize','/var/lib/clean-your-tv-root-updater.archive-'+'a'*32])),8000)
        ns={'__name__':'test'};exec(COMMAND,ns)
        self.assertIn('operate',ns)
