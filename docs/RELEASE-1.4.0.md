# v1.4.0 candidate — guided setup, diagnostics, native cache cleanup and Root startup

**Unpublished testing candidate.** PR #98 remains draft. These versions are
committed for artifact testing, not hardware acceptance or public delivery.
Published downloads remain v1.3.0. No new TV compatibility is established.

| Component | Published v1.3.0 | Candidate |
| --- | --- | --- |
| Overall release | 1.3.0 | 1.4.0 |
| cytv installer | 0.4.0 | 0.5.0 |
| Home / renewal service | 1.4.2 | 1.5.0 |
| Home Helper | 0.6.19 | 0.6.19, exact published package |
| Root Edition | 0.4.0 | 0.5.0 |
| Both independent edition Updaters | 0.3.0 | 0.3.1 |
| Android installer | 0.3.0-preview / code 11 | 0.4.0 / code 13 |
| System Updater supervisor | 1.1.0 / protocol 1 | 1.1.0 / protocol 1; enclosing infrastructure rebuilt |
| Homebrew Installer | Not published | Development only; no promotion record |

Android 0.4.0 removes the preview suffix by explicit maintainer decision after
scoped emulator acceptance. It keeps the application ID, private storage and
public signing identity. Android 15 / API 35 ARM64 with WebView 124 is the tested
configuration; physical phones, Android 7 / WebView 108 and live phone-to-TV
installation/recovery remain unverified. Community feedback will expand the
hardware evidence; this decision does not establish universal compatibility.
See [Android acceptance and limits](../android/STABLE-READINESS.md).

## Included scope

Candidate acceptance also found #111: replacing published Root 0.4.0 stopped at
runtime validation before Root removal, after updater preparation. The owner
confirmed the supported return to LG Home and working controls. PR #112
verifies a release-bound historical runtime inventory before updater effects.
Checked continuation of the original C3 request completed and independent status
verified removal; fresh setup and new-runtime hardware acceptance remain pending.
See the [transition record](RC-1.4.0-TESTING.md#root-040-transition-regression-111).


- #80 / issues #12 and #59: bounded Home/settings and renewal failure diagnostics,
  actual renewal-service version and remote-readable report. This is a partial
  diagnostic improvement; firmware service access and reporter acceptance remain
  unresolved. Helper control/emergency-stop behavior is preserved.
- #81: focused first-time desktop and Android setup, credential instructions and
  offline LG screen examples. Preparation navigation does not grant connection
  confirmation. Example codes are not the user's TV credentials.
- #87 / issue #82: explicit Root setup can initialize an absent Home setting to
  stock LG Home after durable intent, then require independent Settings Service
  readback and unchanged profiles/other defaults. Status/doctor stays read-only;
  uncertain writes are not replayed. The explicit stock override remains after
  removal. Original finalize failure/device acceptance is not yet confirmed.
- #89: experimental Root HDMI sound recovery, including manual eARC reconnect,
  confirmed HDMI-route fallback and automatic boot/wake recovery **off by
  default**. Unknown, ARC-only and combined/WOW modes are skipped. Success means
  settings/output restored, not proven audible sound or improved start time.
  Bluetooth and microphone controls from separate PR #27 are not included.
- #97 / issue #93: binary cryptography wheels and real frozen-entrypoint probes
  address the reproduced Intel macOS preconnection loader failure. Both GUI and
  console artifacts must pass `--check-runtime`; target-device result is pending.
- #99 / issue #95: private-Python preflight identifies ABI, ownership and storage
  checks, reports available/required space and advisory WAM size with bounded
  diagnostics. Diagnostics delete no app storage. Separate opt-in WAM cache cleanup
  (#100) requests only `cache` and `codecache` through the native WAM API, with
  default-No consent, a cache-rebuilding warning and manual Session Storage guidance.
  No root file deletion, reboot, automatic retry or setup resume occurs. A direct
  C3 API test recovered about 98.4 MiB with unchanged protected-data fingerprints;
  the C3 owner confirmed app launch/playback, retained sign-ins and LG Home return.
  Exact installer, changed Root runtime and C2 acceptance remain pending. The reporter has since
  confirmed #94 passes in published cytv 0.4.0; the later Root deployment fails in #101.

- Issues #101 and #21: accept observed C2 UID 1001 only for independently pinned
  DATA at the exact shared packages/services containers; keep strict private
  execution and own-file checks. Extend guided No-root recovery to interrupted
  installs, with separate default-No removal before version review/reinstallation.
  Existing failed Root operations retain their original drivers and need reviewed
  recovery. The original No-root package rejection and both device results remain
  unconfirmed; this is partial delivery for #21.

## Packaging and recovery

Rebuild desktop/console installers on Windows x64, Linux x64, macOS ARM64 and
macOS x64, plus signed non-debuggable Android. Rebuild Home, Root, both independent
Updaters and Root/System private inventories. Shared styles, catalogs and fonts
also affect updater packages; their version is bumped. The unchanged supervisor
wrapper keeps 1.1.0; its enclosing runtime/infrastructure hashes must be new.
Helper must equal the published 0.6.19 bytes, SHA-256
`52510c9115a518a05849f6618516b41886aea54b7f74ea4763ffeeaf63c03e7b`.

Existing retained Root recovery drivers do not change through an app-only update.
Use checked fresh setup or supported exact-code continuation after reviewing the
existing operation. Do not overwrite retained drivers, delete journals, manually
seed Home settings or blindly replay failed setup. Root stock-initialization and
audio-recovery receipts are persistent recovery state; retain uncertain records.
Homebrew remains unreleased (`homebrew/release.json` absent).

## Testing and release gates

Follow the [candidate test matrix](RC-1.4.0-TESTING.md). Record exact source SHA,
artifact hashes, model, firmware, expected/actual result, standby and true cold
boot separately. Historical v1.3.0 evidence is a baseline, not acceptance of this
candidate. Issue #90's known standby limitation remains unresolved.

`release-plan.json.acceptance` deliberately remains empty. Draft artifact builds
use the explicit `test_build=true` dispatch; they do not satisfy Release policy.
No main merge, tag, signed feed change or publication is part of preparation.
After hardware feedback, refresh documentation, commit acceptance honestly,
rebuild the exact final head on all platforms and finish the normal release gates.
Public rollback and signed feed verification remain required before shipping.

## Root cold-start correction (unpublished, #104)

The source correction replaces clock-dependent startup identity with a private
volatile session nonce and makes one optional Clean presentation request after
healthy hardware startup when native Home auto-launch is on and Live TV/LG Home
still occupies the foreground. Other visible apps are preserved at the final
check. Explicit/emergency off is not reset. Separate observer diagnostics retain
issue #90 as unresolved.

This requires rebuilding and deploying the coherent private runtime; an app-only
update is insufficient. Physical acceptance of the changed runtime is pending.
The [mandatory cold-boot matrix](RC-1.4.0-TESTING.md#required-before-publication-root-cold-boot-and-first-screen-104)
must pass before publication, including first screen without Home, Emby-to-Home,
repeated AC-off cycles and off/emergency preservation. Use fresh artifacts whose source SHA includes #103/#105 and #100; older
pre-integration installers cannot validate or deliver these changes. A successful
build does not satisfy the physical startup/rollback gates.
