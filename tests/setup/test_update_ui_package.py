"""The independent recovery app must ship the stylesheet its HTML loads."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class UpdateUiPackageTests(unittest.TestCase):
    def test_standalone_recovery_build_includes_shared_dialog_styles(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ('scripts/lib', 'launcher/fonts', 'root-edition/ui', 'docs', 'updater-service'):
                (root/folder).mkdir(parents=True)
            shutil.copytree(ROOT/'updater-app', root/'updater-app')
            shutil.copy(ROOT/'scripts/build-updater.sh', root/'scripts/build-updater.sh')
            for name in ('renewal-panel.css', 'i18n.js', 'i18n.css', 'catalogs.js', 'user-data.js'):
                shutil.copy(ROOT/'launcher'/name, root/'launcher'/name)
            for name in ('service.js', 'permissions.js', 'services.json', 'release-public.pem'):
                (root/'updater-service'/name).write_text('fixture')
            for name in ('scripts/update-permissions.cjs', 'scripts/lib/update-permissions.cjs',
                         'root-edition/ui/root-locales.js', 'launcher/fonts/NotoSans.ttf', 'docs/UPDATES.md'):
                (root/name).write_text('fixture')
            packager = root/'packager'
            packager.write_text('#!/bin/sh\ntest -s "$1/renewal-panel.css"\n')
            packager.chmod(0o755)
            result = subprocess.run(['bash', 'scripts/build-updater.sh'], cwd=root,
                                    env=dict(os.environ, ARES_PACKAGE=str(packager)), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
            self.assertEqual((root/'build/updater-app/renewal-panel.css').read_bytes(),
                             (ROOT/'launcher/renewal-panel.css').read_bytes())
