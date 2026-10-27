"""Prevent stale stable-download and component metadata at the release gate."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('readme_release_flow', ROOT / 'scripts/release-flow.py')
FLOW = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FLOW)
VERSIONS = dict(release='2.0.0', cytv='1.0.0', home='1.1.0', helper='0.6.19',
                root='0.8.0', updater='0.4.0', android='0.6.0', android_version_code=20)
README = '''<!-- release:downloads -->
Current stable release: **[v2.0.0](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v2.0.0)** — [release notes](docs/RELEASE-2.0.0.md).
<!-- /release:downloads -->
<!-- release:components -->
| Component | Stable version |
| --- | --- |
| cytv installer | 1.0.0 |
| Home | 1.1.0 |
| Home Helper | 0.6.19 |
| Root edition | 0.8.0 |
| Both edition Updaters | 0.4.0 |
| Android installer / versionCode | 0.6.0 / 20 |
<!-- /release:components -->
Historical evidence: [v1.3.0](docs/RELEASE-1.3.0.md).
'''


class ReadmeRelease(unittest.TestCase):
    def test_stale_download_notes_components_and_missing_sections_fail(self):
        self.assertTrue(hasattr(FLOW, 'validate_readme'), 'Release gate must validate README metadata')
        FLOW.validate_readme(README, VERSIONS)
        for before, after in [('v2.0.0', 'v1.3.0'), ('RELEASE-2.0.0.md', 'RELEASE-1.3.0.md'),
                              ('| 1.1.0 |', '| 1.0.0 |'), ('0.6.0 / 20', '0.6.0-preview / 19'),
                              ('<!-- release:downloads -->', ''),
                              ('<!-- /release:components -->', ''),
                              ('| Home Helper | 0.6.19 |', '')]:
            with self.subTest(before=before), self.assertRaisesRegex(ValueError, 'README'):
                FLOW.validate_readme(README.replace(before, after), VERSIONS)
        with self.assertRaisesRegex(ValueError, 'README'):
            FLOW.validate_readme(README + README, VERSIONS)

    def test_final_candidate_rejects_stale_readme_before_build_gate(self):
        from unittest.mock import patch
        import json
        plan = dict(schema=1, version='2.0.0', changes=[], excluded=[], acceptance='C3 checked')
        files = {'release-plan.json': json.dumps(plan), 'release-versions.json': json.dumps(VERSIONS),
                 'docs/RELEASE-2.0.0.md': 'Release notes', 'README.md': README.replace('v2.0.0', 'v1.3.0')}
        pr = {'base': {'sha': 'a' * 40}, 'head': {'sha': 'b' * 40, 'ref': 'release/next',
                                                     'repo': {'full_name': FLOW.REPO}}}
        def read(commit, path, root):
            if commit == 'a' * 40:
                return json.dumps({**VERSIONS, 'release': '1.9.0'})
            return files[path]
        with patch.object(FLOW, 'read_at', side_effect=read), \
             patch.object(FLOW, 'merged_scope', return_value=(set(), [])):
            with self.assertRaisesRegex(ValueError, 'README'):
                FLOW.validate_candidate(pr)
            files['README.md'] = README
            self.assertEqual(FLOW.validate_candidate(pr), plan)

    def test_repository_readme_matches_committed_versions(self):
        import json
        self.assertTrue(hasattr(FLOW, 'validate_readme'), 'Release gate must validate README metadata')
        FLOW.validate_readme((ROOT / 'README.md').read_text(),
                             json.loads((ROOT / 'release-versions.json').read_text()))
