import os
import runpy
import tempfile
import unittest
from pathlib import Path


@unittest.skipIf(os.name == 'nt', 'Debian package tree requires POSIX symlinks and permissions')
class DesktopPackageTests(unittest.TestCase):
    def test_installed_launcher_uses_packaged_executable_without_terminal(self):
        root = Path(__file__).resolve().parents[2]
        packaging = runpy.run_path(str(root / 'scripts/desktop_packaging.py'))
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            frozen = directory / 'frozen'
            frozen.mkdir()
            (frozen / 'cytv-desktop').write_bytes(b'fake executable')
            (frozen / 'libQt.so').write_bytes(b'fake library')
            (frozen / 'libQt.so.6').symlink_to('libQt.so')
            tree = packaging['deb_tree'](root, frozen, '0.2.0', directory / 'deb')
            desktop = (tree / 'usr/share/applications/cytv.desktop').read_text()
            self.assertIn('Terminal=false\n', desktop)
            command = next(line[5:] for line in desktop.splitlines() if line.startswith('Exec='))
            executable = tree / command.lstrip('/')
            self.assertTrue(executable.is_file())
            self.assertTrue(executable.stat().st_mode & 0o111)
            self.assertTrue((tree / 'opt/clean-your-tv/libQt.so.6').is_symlink())
            control = (tree / 'DEBIAN/control').read_text()
            self.assertIn('Architecture: amd64', control)
            self.assertIn('libxcb-cursor0', control)
            self.assertFalse((tree / 'DEBIAN/postinst').exists())
