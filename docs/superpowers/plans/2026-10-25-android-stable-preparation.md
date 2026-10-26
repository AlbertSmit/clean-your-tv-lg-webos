# Android stable preparation implementation plan

**Goal:** Prepare a production Android installer without changing Developer Mode auto-renewal or declaring untested hardware stable.

**Approved scope:** The maintainer approved production packaging, signature/update continuity, both edition checks, interruption/recovery checks, CI and documentation. Work stays in the project root on `codex/android-stable-preparation` and targets `release/next`.

**Architecture:** Keep the existing package ID, private data directories and pinned signing certificate. Publish a non-debuggable release build using the existing protected signing identity; never introduce an automatic reinstall or discard operation receipts. Preserve current versions until candidate freeze.

## Tasks

- [x] Add a failing regression rejecting `application-debuggable` APKs and require `debuggable: false` in trusted build reports. Implement the verifier and assembly checks; run Android and release tests.
- [x] Configure `assembleRelease` / `lintRelease`, retain the pinned signer and fail closed without the release keystore. Build locally with a disposable test signer and verify release/debug metadata separately; the test signer must never become a published identity.
- [x] Exercise native operation ownership, bounded replay, pending prompts and rejected stale answers on an Android emulator. Add a regression before changing any discovered lifecycle defect. Check UI replay/recovery using the existing suites. Record physical-device checks as outstanding rather than infer them from emulator results.
- [x] Record the v1.1.0 Android success from issue #24 with its exact evidence limits. Document preview-to-release update checks, production signing, interruption/device acceptance and the remaining release gate. Keep preview metadata until the gate is met; do not change auto-renewal.
- [x] Run `scripts/test.sh`, the Android UI suites, release build/lint and available native checks. Review the diff and record actual results. No publishing or compatibility claims from package installation alone.

## Device acceptance gate

The existing issue #24 Android success is valid No-root user evidence after PR #42, but lacks phone/Android/TV details. It does not resolve the original reporter's unfinished removal. Capture exact APK/version/certificate, phone/Android/WebView, TV/firmware and edition for subsequent results. Require physical No-root and Root install/status/recovery, update over the pinned preview without private-data loss, network-loss and process-death reconciliation, Home/navigation/recovery and standby separately from cold boot. Exclude Developer Mode auto-renewal from this work.
