# Android stable readiness

Status: **preparation, not a stable Android release announcement**. Keep the
`-preview` component version and current published-download descriptions until
the acceptance gate below is completed. Choose the next version and increment
`versionCode` at candidate freeze through `docs/RELEASE-FLOW.md`.

Developer Mode auto-renewal is outside this work. No automatic discovery,
uninstall UI, extra phone architectures or Google Play publication is required
for the first stable installer. Those remain documented limits.

## Existing physical evidence

In [issue #24, comment 6400650506](https://github.com/Razdva122/clean-your-tv-lg-webos/issues/24#issuecomment-6400650506),
`gargaroff` confirmed successful use of v1.1.0 after the Android operation-receipt
fix in [PR #42](https://github.com/Razdva122/clean-your-tv-lg-webos/pull/42). This
is positive Android/No-root setup evidence, not merely an emulator result.

The comment does not give the phone model, Android/WebView version, TV model or
firmware, or a complete controls/recovery test. The TV in the original issue
body belongs to a different reporter. Do not assign that configuration to this
Android success, infer Root acceptance, or close the original unfinished-removal
report. Its `status:needs-info` remains appropriate for the outstanding original
reporter response.

No physical Android phone is available to the maintainer for this preparation.
Device checks remain an explicit release gate, to be supplied by maintainers or
community testers; the existing success must not be discarded or overextended.

## Production package and update identity

- Keep `com.cleanyourtv.android`, the existing app-private storage layout and
  `android/preview-certificate.sha256` unchanged.
- Build `assembleRelease` / `lintRelease`. `BuildConfig.DEBUG` is false, which
  also disables the WebView debugging API used by debug-only smoke scripts.
- Supply the persistent signing identity from the existing protected
  `CYTV_ANDROID_PREVIEW_KEYSTORE_B64` secret. The historical name/alias is retained
  for installed APK compatibility. Never export the key or print its contents.
- Packaging without `CYTV_ANDROID_KEYSTORE` fails. The APK verifier independently
  rejects `application-debuggable`, checks the pinned signer, SDK/ABI/version,
  source provenance and embedded TV payload. The trusted report explicitly
  records `debuggable: false`; final assembly requires that boolean.
- CI compiles `OperationChecks` but does not run it on physical hardware or claim
  device acceptance. The instrumentation APK is not a public release asset.
- A disposable local signer is suitable for emulator checks only. Such APKs must
  fail the pinned public-signer verifier. Do not change the pin to make them pass.

Before publication, verify the final protected-CI APK and its update over a
published preview with the **original** certificate. Local re-signing checks the
same-signer update mechanism but cannot replace this final artifact check.
Never instruct users to uninstall the Android app to bypass a signature error:
that deletes private keys, profiles and durable recovery receipts.

## Native emulator fixtures

Build the debug app and instrumentation APK:

```sh
android/gradlew -p android :app:assembleDebug :app:assembleDebugAndroidTest
adb -s emulator-5554 install -r android/app/build/outputs/apk/debug/app-debug.apk
adb -s emulator-5554 install -r android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk
python3 android/tests/native.py --serial emulator-5554
```

The runner uses the real Android `Operation` and JSON implementation. It checks
both edition contexts, refuses a second operation, bounds replay to 450 events,
retains the started event and outstanding prompt across 500 background log
events, rejects stale prompt answers and keeps secret values out of replay.
Detaching the Activity listener models the missed-live-event boundary; this is
not a physical rotation/standby acceptance claim.

The regression failed before the fix with `Pending prompt lost during Activity
replay`. FIFO trimming used to discard the outstanding question; trimming now
protects the started event and current prompt, allowing a recreated Activity to
rebuild the dialog. Answered questions become ordinary evictable events again.

### Preview-to-release and process-death fixture

Use an isolated emulator containing no real TV profiles or keys. The wrapper
requires an explicit `emulator-N` serial and treats a missing success marker as
failure, because `adb shell am instrument` can exit zero after a test failure.

1. Download the v1.1.0 `cytv-android-arm64.apk` into a private test directory and
   verify its original certificate with `apksigner verify --print-certs`; its
   SHA-256 must equal `android/preview-certificate.sha256`.
2. Create a disposable local keystore. For local checks only, re-sign a **copy**
   of that preview APK with it, build the new release APK with the same keystore,
   and re-sign the instrumentation APK with that key as well. Keep the originals
   and never use or publish these test-signed APKs as release assets.
3. Install the test-signed preview and instrumentation APK on the emulator.
4. Run `python3 android/tests/native.py --serial emulator-5554 --upgrade seed`.
   This uses the real Python `Store` in the preview to save a synthetic profile
   and unfinished installation receipt, plus a dummy imported-key file and
   private preference. It performs no TV commands.
5. Force-stop the target app, then use `adb -s emulator-5554 install -r` with the
   new test-signed release APK. Do **not** uninstall between seed and verification.
6. Run `python3 android/tests/native.py --serial emulator-5554 --upgrade verify`.
   It requires a non-debuggable target, retained files/preferences, the canonical
   saved identity path and unchanged pending receipt. A second `Store.begin`
   must refuse the unresolved operation. A fresh process must not replay an
   installation automatically. Only its reserved synthetic fixtures are removed
   after success.
7. Run `python3 android/tests/native.py --serial emulator-5554` against the same
   release target to verify native operation behavior without debug mode.

Android canonicalizes `/data/user/0` and `/data/data` aliases; compare the saved
identity to the key's canonical path rather than interpreting alias spelling as
lost user data. These fixtures do not test actual SSH credentials, network loss
to a TV or a whole-edition TV rollback.

## Physical acceptance before removing preview

Record the exact APK hash, signer, source/build and component versions for every
result, with phone model, Android/WebView version, TV model/firmware and edition.
Separate Android installer results from TV runtime compatibility.

| Required scenario | Current evidence | Remaining work |
| --- | --- | --- |
| No-root installation from phone | v1.1.0 user success in #24 | Record device details and verify final candidate |
| Root installation from phone | Not established by #24 | Physical install, status and recovery |
| Published preview update without data loss | Same-signer emulator fixture | Final CI APK with original public signer; physical update |
| Activity recreation and prompt replay | Native bounded-replay regression and browser replay suites | Real rotation, backgrounding and return to the same operation |
| Phone lock and denied notification permission | Foreground service and bounded wake lock in code | Verify operation continuation / clear outcome on actual Android devices |
| Network loss / TV unavailable | Existing negative connection fixtures and recovery UI | Interrupt real transfer; status/restore must reconcile before retry |
| OS process termination | Emulator force-stop and durable pending-receipt fixture | Interrupt physical install; no automatic retry or receipt deletion |
| Supported Android/WebView floor | API 35 emulator and WebView feature gate | Oldest supported Android 7 / WebView 108 and an additional current phone |
| TV controls after installation | Historical edition-specific TV evidence | Final installed candidate: Home, arrows/OK, Back, volume, triple-Home and explicit resume |
| TV power / recovery | Not established by successful package installation | Standby/wake and cold boot separately; status/restore and rollback within supported scope |

Close the gate only with recorded results or an explicitly narrowed supported
scope. Emulator checks, CI success and one successful setup do not establish
universal phone/TV compatibility.

## Automated verification record for this preparation

- `npm ci` completed.
- `scripts/test.sh` passed: 984 Python tests across the suites (23 skipped for
  unavailable optional/platform coverage), plus the included JS/native checks.
  On macOS the POSIX upload fixtures used the system `shasum -a 256` through a
  local `sha256sum` adapter; product code was unchanged for that environment.
- Android `ui.cjs`, `localization.cjs`, `maintenance.cjs` and
  `connection-first.cjs` passed.
- `assembleRelease`, `lintRelease` and `assembleDebugAndroidTest` built locally
  using JDK 17, SDK 35 and Gradle 8.13. The local release used a disposable key;
  the pinned-certificate verifier rejected it as expected.
- Release packaging without a signer failed with the required-keystore error.
- The pending-prompt native regression failed before the fix and passed after
  it on Android 15 / API 35 ARM64 emulator, for both edition contexts.
- The published v1.1.0 preview certificate matched the pin. A test-signed copy
  updated from versionCode 9 to the test-signed release versionCode 10 without
  uninstalling; synthetic profile, key file, preference and pending receipt were
  retained after force-stop. Reinstall was refused while that receipt was pending.
  Native operation checks also passed on the non-debuggable release target.

These are development checks, not publication evidence. The final PR records
the tested revision and final native upgrade results. Stable metadata and
physical acceptance remain pending.
