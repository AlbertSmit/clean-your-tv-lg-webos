# v1.4.0 candidate — guided setup, safe diagnostics and opt-in eARC recovery

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
| Android installer | 0.3.0-preview / code 11 | 0.4.0-preview / code 12 |
| System Updater supervisor | 1.1.0 / protocol 1 | 1.1.0 / protocol 1; enclosing infrastructure rebuilt |
| Homebrew Installer | Not published | Development only; no promotion record |

## Included scope

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
  diagnostics. No app storage is deleted. Optional WAM cleanup and the separate
  architecture report are not delivered by this candidate. The reporter has since
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
