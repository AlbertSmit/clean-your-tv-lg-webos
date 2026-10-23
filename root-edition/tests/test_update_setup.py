import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
import subprocess

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from updater.bootstrap import permission_plan, verify_bundle


class SetupTests(unittest.TestCase):
    def test_permissions_pin_service_methods_and_callers(self):
        files=permission_plan()
        text=json.dumps(files)
        self.assertNotIn('"all"',text);self.assertNotIn('"public"',text)
        client=files['client.json'];self.assertIn('com.cleanyourtv.root.preview',client)
        self.assertNotIn('org.other',client)
        role=files['role.json'];self.assertEqual(role['allowedNames'],['com.cleanyourtv.root.updater.service'])
        self.assertEqual(role['type'],'regular')

    def test_standalone_build_is_verified_and_private_files_excluded(self):
        spec=importlib.util.spec_from_file_location('updater_build',ROOT/'build_updater.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp).resolve()/'bundle';module.build(out)
            manifest=verify_bundle(out)
            self.assertIn('updater/core.py',manifest['files'])
            self.assertIn('root-updater.ipk',manifest['files'])
            self.assertFalse(any('state/' in name or 'private' in name for name in manifest['files']))
            (out/'updater/core.py').write_text('changed')
            with self.assertRaises(ValueError):verify_bundle(out)

    def test_distributed_setup_runs_readonly_plan_without_source_checkout(self):
        def load(name):
            spec=importlib.util.spec_from_file_location('bundle_test_'+name,ROOT/(name+'.py'))
            module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();updater=root/'updater';baseline=root/'baseline'
            load('build').build(baseline);load('build_updater').build(updater)
            result=subprocess.run([sys.executable,str(updater/'setup-updater.py'),'--bundle',str(updater),'--baseline',str(baseline)],cwd=root,capture_output=True,text=True)
            self.assertEqual(0,result.returncode,result.stderr)
            plan=json.loads(result.stdout)
            self.assertFalse(plan['replaces_root_runtime'])
            self.assertTrue(plan['requires_root_mode_disabled'])

    def test_fixed_cli_rejects_untrusted_fields(self):
        from updater.cli import validate_request
        for method,payload in (('shell',{}),('install',{'version':'0.2.0','profile':{},'url':'bad'}),('ready',{'transaction':'../escape','version':'0.2.0'}),('check',{'caller':'com.cleanyourtv.root.preview'})):
            with self.assertRaises(ValueError):validate_request(method,payload)


if __name__=='__main__':unittest.main()
