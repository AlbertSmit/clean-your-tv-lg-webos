import hashlib
import importlib.util
import json
from pathlib import Path
import unittest
from cytv.package import ipk

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('assemble_release', ROOT / 'scripts/assemble-release.py')
release = importlib.util.module_from_spec(spec)
spec.loader.exec_module(release)
VERSIONS = {'release': '0.10.9', 'cytv': '0.2.12', 'home': '1.3.5', 'helper': '0.6.16', 'root': '0.1.9', 'updater': '0.1.5'}
SHA = 'a' * 40


class AutomaticRelease(unittest.TestCase):
    def test_new_version_starts_release(self):
        self.assertTrue(release.plan_release(VERSIONS, SHA, [], False))

    def test_published_release_is_not_overwritten(self):
        existing = [{'tag_name': 'v0.10.9', 'draft': False, 'prerelease': False, 'target_commitish': 'b' * 40}]
        self.assertFalse(release.plan_release(VERSIONS, SHA, existing, False))
        self.assertTrue(release.plan_release(VERSIONS, SHA, existing, True))

    def test_retry_requires_same_draft_commit(self):
        existing = [{'tag_name': 'v0.10.9', 'draft': True, 'prerelease': False, 'target_commitish': SHA}]
        self.assertTrue(release.plan_release(VERSIONS, SHA, existing, False))
        with self.assertRaisesRegex(ValueError, 'different commit'):
            release.plan_release(VERSIONS, 'b' * 40, existing, False)

    def test_older_release_and_invalid_versions_stop(self):
        existing = [{'tag_name': 'v0.10.10', 'draft': False, 'prerelease': False}]
        with self.assertRaisesRegex(ValueError, 'newer'):
            release.plan_release(VERSIONS, SHA, existing, False)
        with self.assertRaisesRegex(ValueError, 'version'):
            release.plan_release({**VERSIONS, 'release': '../bad'}, SHA, [], False)

    def test_payload_hashes_and_actual_versions_are_verified(self):
        files = {}
        for name, app, version in [('launcher.ipk', 'com.gathin.tvhome', VERSIONS['home']), ('helper.ipk', 'com.local.nativehome', VERSIONS['helper']), ('root/root.ipk', 'com.cleanyourtv.root.preview', VERSIONS['root'])]:
            files[name] = ipk(app, version, {'usr/palm/applications/' + app + '/appinfo.json': json.dumps({'id': app, 'version': version}).encode()})
        files['root/bundle.json'] = json.dumps({'package': 'root.ipk'}).encode()
        files['root/release.json'] = json.dumps({'version': VERSIONS['root']}).encode()
        files['payload.json'] = json.dumps({'home_version': VERSIONS['home'], 'helper_version': VERSIONS['helper'], 'files': {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}}).encode()
        self.assertGreater(release.verify_embedded(files.__getitem__, VERSIONS), 0)
        with self.assertRaisesRegex(ValueError, 'version'):
            release.verify_embedded(files.__getitem__, {**VERSIONS, 'root': '0.1.10'})
        files['launcher.ipk'] = b'corrupted'
        with self.assertRaisesRegex(ValueError, 'hash'):
            release.verify_embedded(files.__getitem__, VERSIONS)

    def test_artifacts_require_successful_trusted_main_builds(self):
        run = {'conclusion': 'success', 'status': 'completed', 'head_sha': SHA, 'head_branch': 'main', 'event': 'push', 'path': '.github/workflows/cytv.yml', 'head_repository': {'full_name': 'Razdva122/clean-your-tv-lg-webos'}}
        release.validate_build_run(run, SHA)
        for field, value in [('conclusion', 'failure'), ('head_sha', 'b' * 40), ('event', 'pull_request'), ('head_branch', 'feature'), ('path', '.github/workflows/other.yml'), ('head_repository', {'full_name': 'someone/fork'})]:
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'trusted main'):
                release.validate_build_run({**run, field: value}, SHA)
