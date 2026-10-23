"""All runtime modules must be included even before their first Git commit."""
from pathlib import Path
import runpy
import unittest


class BuildAssetsTests(unittest.TestCase):
    def test_new_public_runtime_modules_are_packaged(self):
        build = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'scripts/build-cytv.py'))
        self.assertIn('app-library.js', list(build['tracked_files']('launcher')))
        self.assertIn('app-inventory.js', list(build['tracked_files']('native/service')))
