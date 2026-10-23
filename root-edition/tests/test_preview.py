"""Offline staging tests: no device, installer, or root access."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'root-edition' / 'preview.py'

class PreviewTests(unittest.TestCase):
    def run_stage(self, destination):
        return subprocess.run([sys.executable, str(SCRIPT), '--output', str(destination)], capture_output=True, text=True)

    def test_isolated_sanitized_stage_and_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'preview'
            result = self.run_stage(out)
            self.assertEqual(result.returncode, 0, result.stderr)
            app = out / 'app'
            info = json.loads((app / 'appinfo.json').read_text())
            self.assertEqual(info['id'], 'com.cleanyourtv.root.preview')
            self.assertEqual(info['appCategory'], ['home'])
            self.assertFalse(info['needNetworkToLaunchOnBoot'])
            self.assertEqual((app / 'apps.js').read_text(), 'window.TV_APPS = {apps: [], inputs: []};\n')
            html = (app / 'index.html').read_text()
            for name in ('native-bootstrap.js', 'helper-control.js', 'renewal-panel.js', 'renewal-panel.css', 'user-data.js', 'update-panel.js', 'profile-bootstrap.js'):
                self.assertNotIn(name, html)
                self.assertFalse((app / name).exists())
            self.assertIn('root-settings.js', html)
            self.assertNotIn('<script src="app.js"></script>', html)
            self.assertIn('root-profile.js', html)
            self.assertIn('root-updates.js', html)
            self.assertIn('root-profile-data.js', html)
            self.assertIn('com.cleanyourtv.root.preview', (app / 'config.js').read_text())
            self.assertEqual((app / 'app.js').read_bytes(), (ROOT / 'launcher/app.js').read_bytes())
            inventory = json.loads((out / 'inventory.json').read_text())
            actual = {str(p.relative_to(app)): hashlib.sha256(p.read_bytes()).hexdigest() for p in app.rglob('*') if p.is_file()}
            self.assertEqual(inventory['files'], actual)
            self.assertFalse(inventory['activates_system_home'])
            self.assertFalse(inventory['public_release_ready'])

    def test_refuses_existing_destination_without_touching_it(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'preview'; out.mkdir()
            marker = out / 'keep'; marker.write_text('preserve')
            result = self.run_stage(out)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(list(out.iterdir()), [marker])
            self.assertEqual(marker.read_text(), 'preserve')

    def test_repeat_build_has_identical_content(self):
        with tempfile.TemporaryDirectory() as temp:
            a, b = Path(temp) / 'a', Path(temp) / 'b'
            self.assertEqual(self.run_stage(a).returncode, 0)
            self.assertEqual(self.run_stage(b).returncode, 0)
            self.assertEqual((a / 'inventory.json').read_bytes(), (b / 'inventory.json').read_bytes())

class SourceIsolationTests(unittest.TestCase):
    def test_private_inventory_and_extra_files_are_not_copied(self):
        import shutil
        from unittest.mock import patch
        sys.path.insert(0, str(SCRIPT.parent))
        import preview
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'launcher'
            shutil.copytree(ROOT / 'launcher', source)
            for name in ('apps.js', 'config.js', 'secret.key', 'state.json'):
                (source / name).write_text('PRIVATE_SENTINEL')
            with patch.object(preview, 'SOURCE', source):
                result = preview.prepare()
            self.assertNotIn('secret.key', result)
            self.assertNotIn('state.json', result)
            self.assertFalse(any(b'PRIVATE_SENTINEL' in value for value in result.values()))

    def test_indirect_source_rejected_before_output_created(self):
        import shutil
        from unittest.mock import patch
        sys.path.insert(0, str(SCRIPT.parent))
        import preview
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / 'launcher'
            shutil.copytree(ROOT / 'launcher', source)
            (source / 'app.js').unlink()
            (source / 'app.js').symlink_to(ROOT / 'launcher/app.js')
            out = Path(temp) / 'out'
            with patch.object(preview, 'SOURCE', source), self.assertRaises(ValueError):
                preview.stage(out)
            self.assertFalse(out.exists())
