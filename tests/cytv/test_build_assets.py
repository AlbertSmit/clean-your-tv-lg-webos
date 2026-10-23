"""All runtime modules must be included even before their first Git commit."""
from pathlib import Path
import runpy
import unittest


class BuildAssetsTests(unittest.TestCase):
    def test_new_public_runtime_modules_are_packaged(self):
        build = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'scripts/build-cytv.py'))
        self.assertIn('state-permissions.js', list(build['tracked_files']('native/app')))
        self.assertIn('app-library.js', list(build['tracked_files']('launcher')))
        self.assertIn('app-inventory.js', list(build['tracked_files']('native/service')))

    def test_release_metadata_rejects_old_embedded_versions(self):
        import json
        import tempfile
        from cytv import package, __version__
        build = runpy.run_path(str(Path(__file__).resolve().parents[2] / 'scripts/build-cytv.py'))
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); (root/'root').mkdir()
            versions={'cytv':__version__,'home':'1.3.0','helper':'0.6.14','root':'0.1.2'}
            for filename,app,service,version in [('launcher.ipk','com.gathin.tvhome','com.gathin.tvhome.renewal',versions['home']),('helper.ipk','com.local.nativehome','com.local.nativehome.service',versions['helper']),('root/root.ipk',package.ROOT_APP,package.ROOT_APP+'.service',versions['root'])]:
                files={f'usr/palm/applications/{app}/appinfo.json':json.dumps({'id':app,'version':version}).encode(),f'usr/palm/services/{service}/package.json':json.dumps({'version':version}).encode()}
                (root/filename).write_bytes(package.ipk(app,version,files))
            (root/'root/bundle.json').write_text('{"package":"root.ipk"}')
            (root/'root/release.json').write_text('{"version":"0.1.2"}')
            build['verify_release_versions'](root,versions)
            versions['root']='0.0.1'
            with self.assertRaisesRegex(ValueError,'version'):
                build['verify_release_versions'](root,versions)
