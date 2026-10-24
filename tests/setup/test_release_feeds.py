import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('prepare_release', ROOT / 'scripts/prepare-release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
from cytv.package import ipk
import json


def packages(home='1.3.5', root='0.1.9', helper='0.6.16'):
    result = {}
    for kind, app, version in [('home', 'com.gathin.tvhome', home), ('root', 'com.cleanyourtv.root.preview', root), ('helper', 'com.local.nativehome', helper)]:
        result[kind] = ipk(app, version, {'usr/palm/applications/' + app + '/appinfo.json': json.dumps({'id': app, 'version': version}).encode()})
    return result


def build(home='1.3.5', root='0.1.9', helper='0.6.16'):
    return {'tag': 'v0.10.9', 'versions': {'home': home, 'root': root, 'helper': helper}}


class ReleaseFeeds(unittest.TestCase):
    def prepare(self, current=None, prior=None, prior_build=None, rollback=None):
        return release.prepare_manifests('v0.10.9', current or build(), packages(), prior_build or build('1.3.4', '0.1.8'), prior or packages('1.3.4', '0.1.8'), rollback)

    def test_versions_and_hashes_come_from_actual_packages(self):
        manifests, files = self.prepare()
        self.assertEqual(manifests['root']['version'], '0.1.9')
        self.assertEqual(manifests['home']['home'], '1.3.5')
        self.assertEqual(manifests['previous']['home'], '1.3.4')
        self.assertEqual(files['com.gathin.tvhome_1.3.4_all.ipk'], packages('1.3.4', '0.1.8')['home'])
        self.assertEqual(manifests['home']['sha256'], release.digest(packages()['home']))

    def test_stale_package_cannot_be_signed_as_new_version(self):
        with self.assertRaisesRegex(ValueError, 'package version'):
            self.prepare(current=build('1.3.6'))

    def test_incompatible_helper_baseline_stops_release(self):
        with self.assertRaisesRegex(ValueError, 'Helper baseline'):
            self.prepare(prior=packages('1.3.4', '0.1.8', '0.6.15'), prior_build=build('1.3.4', '0.1.8', '0.6.15'))

    def test_changed_bytes_without_version_bump_stop_release(self):
        prior = packages()
        prior['home'] = ipk('com.gathin.tvhome', '1.3.5', {'usr/palm/applications/com.gathin.tvhome/appinfo.json': json.dumps({'id': 'com.gathin.tvhome', 'version': '1.3.5'}).encode(), 'extra.txt': b'changed'})
        with self.assertRaisesRegex(ValueError, 'without version bump'):
            self.prepare(prior=prior, prior_build=build())

    def test_installer_only_release_preserves_older_rollback(self):
        prior = packages()
        rollback = ({'home': '1.3.4', 'helper': '0.6.16'}, packages('1.3.4')['home'])
        manifests, _ = self.prepare(prior=prior, prior_build=build(), rollback=rollback)
        self.assertEqual(manifests['previous']['home'], '1.3.4')

    def test_version_regression_stops_release(self):
        with self.assertRaisesRegex(ValueError, 'regression'):
            self.prepare(prior=packages('1.3.6'), prior_build=build('1.3.6'))

    def test_changed_helper_bytes_without_version_bump_stop_release(self):
        prior = packages('1.3.4', '0.1.8')
        prior['helper'] = ipk('com.local.nativehome', '0.6.16', {'usr/palm/applications/com.local.nativehome/appinfo.json': json.dumps({'id': 'com.local.nativehome', 'version': '0.6.16'}).encode(), 'extra.txt': b'changed'})
        with self.assertRaisesRegex(ValueError, 'without version bump'):
            self.prepare(prior=prior)
