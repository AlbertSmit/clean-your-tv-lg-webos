"""Failed Root setup must export safe recovery evidence without repeating setup."""
import json
import shlex
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
from types import SimpleNamespace
from cytv import diagnostics, operations, state
from cytv.errors import TVCommandError


class RootRecoveryDiagnosticsTests(unittest.TestCase):
    def test_failed_install_collects_only_allowlisted_evidence_and_keeps_original_error(self):
        for extra in ({'reason':'negative-reply','luna_error_code':-1},
                      {'reason':'timeout','startup_state':'exited','startup_exit_status':1,
                       'exception_name':'Error','exception_code':'MODULE_NOT_FOUND'}):
            with self.subTest(extra=extra), tempfile.TemporaryDirectory() as folder:
                error=TVCommandError(1)
                raw={'schema':1,'attempt':'a'*32,'phase':'status',**extra,'stack':'PRIVATE 192.0.2.1','pid':1234}
                remote=MagicMock()
                remote.run.side_effect=[error,json.dumps(raw)]
                installer=operations.Installer(remote,None,{},Path(folder),{})
                installer._python=lambda path:'/usr/bin/python3'
                with patch.object(operations.uuid,'uuid4',return_value=SimpleNamespace(hex='a'*32)):
                    with self.assertRaises(TVCommandError) as caught:
                        installer.root_action('install',bundle='/tmp/verified-bundle')
                self.assertIs(caught.exception,error)
                self.assertEqual(remote.run.call_count,2, 'one failed install and one read-only diagnostic collection')
                second=remote.run.call_args.args[0]
                self.assertIn('recovery-failure.json',second)
                self.assertNotIn('deploy.py',second)
                report=diagnostics.create_report(state.Store(folder),'install',None,'root-install',error)
                data=json.loads(report.read_text())
                self.assertEqual(data['root_recovery'],{'phase':'status',**extra})
                self.assertNotIn('PRIVATE',report.read_text())
                self.assertNotIn('192.0.2.1',report.read_text())
                self.assertNotIn('pid',data['root_recovery'])

    def test_unavailable_or_untrusted_diagnostics_never_replace_failure(self):
        for raw in (OSError('unavailable'), 'not JSON', '[]', '{"schema":99}',
                    '{"schema":1,"attempt":"old","phase":"status","reason":"negative-reply","luna_error_code":-1}',
                    '{"schema":1,"phase":"PRIVATE","reason":"PRIVATE","startup_exit_status":true}'):
            with self.subTest(raw=raw):
                error=TVCommandError(7); remote=MagicMock();remote.run.side_effect=[error,raw]
                installer=operations.Installer(remote,None,{},'.',{})
                installer._python=lambda path:'/usr/bin/python3'
                with self.assertRaises(TVCommandError) as caught:installer.root_action('install')
                self.assertIs(caught.exception,error)
                self.assertFalse(getattr(error,'root_recovery',{}))

    def test_attempt_identity_crosses_real_process_boundary(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/'deploy.py').write_text("import json,os,pathlib,sys\np=pathlib.Path(__file__).parent/'recovery-failure.json'\np.write_text(json.dumps({'schema':1,'attempt':os.environ.get('CYTV_ROOT_INSTALL_ATTEMPT'),'phase':'status','reason':'timeout'}))\np.chmod(0o600)\nsys.exit(1)\n")
            class Device:
                def run(self, command, timeout=30):
                    argv=shlex.split(command)
                    if '-c' in argv:
                        # Map only the TV path and root uid to this local device fixture.
                        argv[-1]=argv[-1].replace('/var/lib/clean-your-tv-root/recovery-failure.json',str(root/'recovery-failure.json')).replace('s.st_uid!=0','s.st_uid!=os.geteuid()')
                    result=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
                    if result.returncode:raise TVCommandError(result.returncode)
                    return result.stdout
            installer=operations.Installer(Device(),None,{},root,{})
            installer._python=lambda path:sys.executable
            with self.assertRaises(TVCommandError) as caught:installer.root_action('install',bundle=str(root))
            self.assertEqual(getattr(caught.exception,'root_recovery',None),{'phase':'status','reason':'timeout'})
            attempt=json.loads((root/'recovery-failure.json').read_text())['attempt']
            self.assertRegex(attempt,r'^[a-f0-9]{32}$')
