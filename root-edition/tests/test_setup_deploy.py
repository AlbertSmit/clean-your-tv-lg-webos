import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load(name):
    path = ROOT / (name + '.py')
    if not path.exists():
        raise AssertionError('Missing deployment component: ' + name)
    spec = importlib.util.spec_from_file_location('root_' + name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SetupTests(unittest.TestCase):
    def test_host_rejects_shell_fragments_and_option_aliases(self):
        setup = load('setup')
        for alias in ('-ProxyCommand=bad', 'tv;id', 'tv user', 'root@tv', ''):
            with self.subTest(alias=alias), self.assertRaises(ValueError):
                setup.ssh_options(alias)
        args = setup.ssh_options('living-room')
        self.assertIn('StrictHostKeyChecking=yes', args)
        self.assertIn('BatchMode=yes', args)
        self.assertEqual(args[-1], 'living-room')

    def test_install_uploads_only_verified_bundle_files(self):
        setup = load('setup')
        import deploy
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            (source / 'bundle.json').write_text('{}')
            (source / 'safe').write_text('safe')
            (source / 'private-key').write_text('secret')
            uploads = []
            def run(args, **kwargs):
                if args[0] == 'scp':
                    sources = args[args.index('-r') + 1:-1]
                    self.assertTrue(sources)
                    for source_name in sources:
                        self.assertFalse(source_name.endswith('/.'))
                        uploads.append(Path(source_name).name)
            with patch.object(deploy, 'verify_bundle', return_value={'files': {'safe': 'unused'}}):
                setup.execute('install', 'living-room', source, run=run)
            self.assertEqual(set(uploads), {'safe', 'bundle.json'})

    def test_non_install_has_fixed_remote_command_and_no_upload(self):
        setup = load('setup')
        calls = []
        setup.execute('status', 'living-room', run=lambda args, **kwargs: calls.append(args))
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][-1], '/usr/bin/python3 /var/lib/clean-your-tv-root/deploy.py status')
        self.assertEqual(calls[0][0], 'ssh')


class DeployTests(unittest.TestCase):
    def test_recovery_commands_allow_the_bounded_recovery_deadline(self):
        deploy = load('deploy')
        from types import SimpleNamespace
        calls = []
        def run(args, **kwargs):
            calls.append(kwargs['timeout'])
            return SimpleNamespace(stdout=b'{"returnValue":true}')
        with patch.object(deploy.subprocess, 'run', side_effect=run):
            for mode in ('restore', 'rollback', 'status'):
                deploy.command(['/usr/bin/python3', '/fixed/driver.py', mode])
        self.assertEqual(calls, [700, 700, 100])

    def test_wrong_device_fails_before_mutation(self):
        deploy = load('deploy')
        with patch.object(deploy.os, 'geteuid', return_value=1000):
            with self.assertRaises(PermissionError):
                deploy.require_device()

    def test_existing_install_is_never_overwritten(self):
        deploy = load('deploy')
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state'
            state.mkdir()
            (state / 'keep').write_text('owned')
            with patch.object(deploy, 'STATE', state):
                with self.assertRaises(FileExistsError):
                    deploy.install(Path(tmp))
            self.assertEqual((state / 'keep').read_text(), 'owned')

    def test_payload_hash_drift_is_rejected(self):
        deploy = load('deploy')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            path = root / 'usr/palm/applications/com.cleanyourtv.root.preview/app.js'
            path.parent.mkdir(parents=True)
            path.write_bytes(b'changed')
            with patch.object(deploy, 'INSTALLED', root):
                with self.assertRaises(ValueError):
                    deploy.verify_payload({'files': {'usr/palm/applications/com.cleanyourtv.root.preview/app.js': '0' * 64}})

    def test_unknown_install_keeps_journal_and_never_provisions(self):
        deploy = load('deploy')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            builder = load('build')
            bundle = root / 'bundle'
            builder.build(bundle)
            events = []
            def observe(app, path, **kwargs):
                kwargs['on_ready']()
                raise deploy.OutcomeUnknown('No terminal evidence')
            with patch.object(deploy, 'STATE', root / 'state'), patch.object(deploy, 'INSTALLED', root / 'installed'):
                with self.assertRaises(deploy.OutcomeUnknown):
                    deploy.install(bundle, run=lambda args: events.append(args), observe=observe)
            self.assertTrue((root / 'state/deploy.py').is_file())
            self.assertTrue((root / 'state/runtime/helper_bridge.py').is_file())
            self.assertEqual(events, [])
            self.assertEqual(json.loads((root / 'state/deploy.json').read_text())['stage'], 'install-submitting')

    def test_explicit_migration_preserves_source_and_records_destination_hashes(self):
        deploy = load('deploy')
        self.assertTrue(hasattr(deploy, 'migrate_packaged_home'), 'Explicit packaged migration is missing')
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            state = root / 'state'; state.mkdir()
            installed = root / 'installed'
            source = installed / 'usr/palm/applications/com.gathin.tvhome'
            source.mkdir(parents=True)
            (source / 'apps.js').write_text('window.TV_APPS = {apps: [], inputs: []};')
            (source / 'config.js').write_text('window.CONFIG = {columns: 7};')
            original = {p.name:p.read_bytes() for p in source.iterdir()}
            target = installed / ('usr/palm/applications/' + deploy.APP)
            target.mkdir()
            (target / 'config.js').write_text('window.CONFIG = {};')
            with patch.object(deploy, 'STATE', state), patch.object(deploy, 'INSTALLED', installed):
                deploy.migrate_packaged_home()
            self.assertEqual({p.name:p.read_bytes() for p in source.iterdir()}, original)
            self.assertIn(b'columns: 7', (target / 'config.js').read_bytes())
            record = json.loads((state / 'personalization.json').read_text())
            import hashlib
            self.assertEqual(record['files']['config.js'], hashlib.sha256((target / 'config.js').read_bytes()).hexdigest())

    def test_install_success_requires_payload_then_orders_provision(self):
        deploy = load('deploy')
        builder = load('build')
        from test_build_root import ar_members
        import io, tarfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            bundle = root / 'bundle'
            package = builder.build(bundle)
            installed = root / 'installed'
            calls = []
            def observe(app, path, **kwargs):
                kwargs['on_ready']()
                with tarfile.open(fileobj=io.BytesIO(ar_members(package.read_bytes())['data.tar.gz'])) as archive:
                    for member in archive:
                        target = installed / member.name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(archive.extractfile(member).read())
                return {'completed':True}
            with patch.object(deploy, 'STATE', root / 'state'), patch.object(deploy, 'INSTALLED', installed):
                result = deploy.install(bundle, run=lambda args: calls.append(args[-1]), observe=observe)
            self.assertTrue(result['returnValue'])
            self.assertFalse(result['home_changed'])
            self.assertEqual(calls, ['apply', 'refresh', 'finalize'])
            self.assertEqual(json.loads((root / 'state/deploy.json').read_text())['stage'], 'installed-recovery-only')

    def test_remove_terminal_without_absence_keeps_state(self):
        deploy = load('deploy')
        import observed_install
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp).resolve()
            state = root / 'state'; state.mkdir()
            installed = root / 'installed'
            app = installed / ('usr/palm/applications/' + deploy.APP)
            app.mkdir(parents=True)
            with patch.object(deploy, 'STATE', state), patch.object(deploy, 'INSTALLED', installed), patch.object(observed_install, 'remove', return_value={'completed':True}):
                with self.assertRaises(deploy.OutcomeUnknown):
                    deploy.uninstall(run=lambda args: {'returnValue':True,'result':'restored'})
            self.assertTrue(state.exists())
            self.assertEqual(json.loads((state / 'deploy.json').read_text())['stage'], 'remove-observed')

    def test_uncertain_removal_is_not_resubmitted(self):
        deploy = load('deploy')
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp).resolve()
            (state / 'deploy.json').write_text(json.dumps({'stage':'remove-submitting'}))
            calls = []
            with patch.object(deploy, 'STATE', state):
                with self.assertRaises(deploy.OutcomeUnknown):
                    deploy.uninstall(run=lambda args: calls.append(args))
            self.assertEqual(calls, [])

    def test_restore_conflict_prevents_uninstall(self):
        deploy = load('deploy')
        calls = []
        def run(args):
            calls.append(args)
            return {'returnValue': True, 'result': 'conflict'}
        with self.assertRaises(ValueError):
            deploy.uninstall(run=run)
        self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main()
