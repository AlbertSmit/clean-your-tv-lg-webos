"""Retained runtime closure belongs to the installed version, not the new bundle."""
import hashlib
import json
import unittest
from install_fixture import CurrentInstallation


class RetainedRuntimeTests(unittest.TestCase):
    def alter(self, fixture, *, legacy=False, omit=()):
        root = fixture.root
        manifest = json.loads((root / 'bundle.json').read_text())
        proof = fixture.root_store.read('recovery-provision')
        if legacy:
            release = json.loads((root / 'release.json').read_text())
            release['version'] = '0.4.0'
            raw = json.dumps(release).encode()
            (root / 'release.json').write_bytes(raw)
            manifest['files']['release.json'] = hashlib.sha256(raw).hexdigest()
            old_package = manifest['package']
            manifest['package'] = 'com.cleanyourtv.root.preview_0.4.0_all.ipk'
            manifest['files'][manifest['package']] = manifest['files'].pop(old_package)
            omit = ('audio_recovery.py', *omit)
        for name in omit:
            (root / 'runtime' / name).unlink(missing_ok=True)
            manifest['files'].pop('runtime/' + name, None)
            proof['files'].pop(str(root / 'runtime' / name), None)
        (root / 'bundle.json').write_text(json.dumps(manifest))
        fixture.root_store.write('recovery-provision', proof)

    def test_complete_published_040_closure_does_not_require_new_audio_module(self):
        with CurrentInstallation() as fixture:
            self.alter(fixture, legacy=True)
            fixture.device_module.LocalDevice().validate_root_driver()

    def test_current_complete_closure_is_accepted(self):
        with CurrentInstallation() as fixture:
            fixture.device_module.LocalDevice().validate_root_driver()

    def test_legacy_tamper_or_other_missing_member_is_rejected(self):
        for omission in ((), ('intent_runtime.py',)):
            with self.subTest(omission=omission), CurrentInstallation() as fixture:
                self.alter(fixture, legacy=True, omit=omission)
                if not omission:
                    (fixture.root / 'runtime/cli.py').write_text('changed')
                with self.assertRaises((ValueError, OSError)):
                    fixture.device_module.LocalDevice().validate_root_driver()

    def test_current_version_cannot_claim_legacy_closure(self):
        with CurrentInstallation() as fixture:
            self.alter(fixture, omit=('audio_recovery.py',))
            with self.assertRaises((ValueError, OSError)):
                fixture.device_module.LocalDevice().validate_root_driver()

    def test_unbound_or_foreign_release_metadata_cannot_select_legacy_runtime(self):
        for change in ('unbound', 'foreign-app', 'package-version'):
            with self.subTest(change=change), CurrentInstallation() as fixture:
                self.alter(fixture, legacy=True)
                root = fixture.root
                release = json.loads((root / 'release.json').read_text())
                manifest = json.loads((root / 'bundle.json').read_text())
                if change == 'package-version':
                    manifest['package'] = 'com.cleanyourtv.root.preview_0.5.0_all.ipk'
                else:
                    release['application_id'] = 'foreign.application'
                    raw = json.dumps(release).encode()
                    (root / 'release.json').write_bytes(raw)
                    if change != 'unbound':
                        manifest['files']['release.json'] = hashlib.sha256(raw).hexdigest()
                (root / 'bundle.json').write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    fixture.device_module.LocalDevice().validate_root_driver()
