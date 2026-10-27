# Testing the unpublished 1.4.0 candidate

Use only the artifacts from the **cytv standalone builds** Actions run linked in
[release candidate #98](https://github.com/Razdva122/clean-your-tv-lg-webos/pull/98).
Verify its source SHA against the PR and record each downloaded artifact's SHA-256.
The latest release/download links still deliver v1.3.0. Candidate artifacts expire
according to Actions retention; they are not public release/update feeds.

Expected versions: cytv 0.5.0; Home 1.5.0; Helper 0.6.19; Root 0.5.0;
both independent Updaters 0.3.1; Android 0.4.0 / code 13.
System supervisor wrapper remains 1.1.0 / protocol 1; Root/System private inventories
must come from this candidate. Homebrew public promotion remains disabled.
Android 0.4.0 removes preview after maintainer-approved emulator acceptance.
Keep the existing signing/application/private-data identity. Tested scope is
Android 15 / API 35 ARM64, WebView 124; physical phones and live phone-to-TV
installation/recovery remain community follow-up, not established compatibility.
See [Android acceptance and limits](../android/STABLE-READINESS.md).

## Host checks before contacting a TV

1. Use the console artifact for the computer architecture. Run `cytv --version`,
   `cytv --check-runtime` and `cytv --check-payload` (prefix `./` on macOS/Linux).
   Expect 0.5.0 and successful exit for both checks. On Intel macOS, run the same
   runtime probe through the extracted GUI bundle's `Contents/MacOS/cytv`
   executable as well; it must not require a TV or open Qt for this probe.
2. Extract desktop archives fully; test first launch from outside the build tree.
   Verify focused preparation Back/Continue, credential-specific help, Details,
   enlarged LG example screens and cancellation. Example pictures must work offline.
   Preparation Continue must never answer the separate connection confirmation.
3. Android: install the signed release-mode candidate as an update to the existing
   preview without clearing data. Verify saved TV/ports, profiles, keys and recovery
   receipts survive; check small portrait/landscape setup and pending prompts.
   Run Done → Tools → Home button diagnostics for No-root and verify port 9922.

## Recorded C3 cache experiment and owner checks

On OLED55C3RLA / firmware 43.21.71 / SDK 11.2.0, the separately authorized native
WAM cache/codecache request recovered about 98.4 MiB with unchanged protected-data
fingerprints and WAM remaining active. The owner confirmed normal app launch,
playback, retained sign-ins and return to LG Home. Clean was the initial page,
consistent with the configured Home choice. The source CLI inspection and default-No
cancel with --yes also passed without sending a cleanup request.

These results apply to the direct cache API experiment on the existing C3 setup.
They do not accept a newly built installer, the changed Root startup runtime,
AC-off cold boot, emergency-off persistence, rollback, or the reporter's C2.
See [recorded measurements and limits](research/2026-10-27-wam-storage-cleanup.md).

## Device matrix — exact-candidate acceptance pending

| Path / target | Required result and evidence |
| --- | --- |
| No-root C5, #12 | On reporter's exact model/firmware, Home works; unknown status stays distinct from off. Open Settings → Developer Mode → Show diagnostics; scroll/focus/Back work; safe Home RPC/storage categories and actual renewal version appear. Recording connection result is separate from settings transport. |
| No-root C2 OLED48C24LA / 43.21.74, #59 | Triple-Home stops; opening Helper settings alone preserves stop; confirmed Start resumes. Failed service status does not trigger reinstall or automatic start. Preserve results for standby and true cold boot separately. |
| Root 43NANO90A6B / 33.31.61, #82 | Review retained operation before any setup. On an eligible absent-key stock baseline, explicit setup journals before SAM write and independently reads explicit LG Home with unchanged other defaults/profiles. Setup, guarded activation and removal then pass. A read-only status/doctor must never initialize the key. |
| Intel macOS / reporter NANO86SNA, #93 | Both frozen entrypoints pass runtime probe without libssl import error; then confirm connection/setup separately. Record firmware, which was not supplied in the original report. |
| Root OLED65C2AUA / 04.40.90, #95 | Low-space preflight reports available/required MiB and failed check, preserves state and performs no cleanup. Advisory WAM measurement is not permission to delete it. Optional console/desktop WAM cache cleanup (#100) requests only cache/codecache through the native API; Session Storage is manual. Verify warnings/manual alternatives, No/cancel, --yes/noninteractive refusal, failed/unknown API replies without retry/fallback, actual space and excluded app data. C3 direct API evidence is limited to the measured cache test; exact installer and C2 acceptance remain pending. Storage was freed and the reporter confirmed cytv 0.4.0 passes Python preflight (#94); the later deployment is blocked by #101. Successful setup remains unconfirmed. |
| No-root 55NANO81ANA / 04.64.00, #21 | Check TV status offers Recover and reinstall for interrupted installation. No/cancel preserves original receipt; Yes checks TV installer idle, restores LG Home and verifies removal before version review/new install. Failed recovery exports that attempt report; no automatic retry. Original package refusal remains unresolved. |
| Root OLED65C2AUA / 04.40.90, #101 | Fresh candidate private readers accept UID 1001 only at exact shared packages/services containers for independently pinned DATA. Preserve strict own-code ownership, hashes and links. Existing stopped operations keep their original drivers and require separately reviewed recovery before any fresh setup; do not overwrite or replay them. |
| Root eARC LG 55NANO956NA / webOS 5.6.2 / 04.64.00 / HW-Q950A | Automatic recovery starts off. Verify manual reconnect and confirmed route fallback, restore readback and audible sound separately. Compare off/on over at least five repetitions per condition; separate standby/cold boot, Quick Start+ and warm/cold receiver. Measure start-time spread and needless interruptions. |
| Root eARC fault/recovery | Check ARC-only/off, combined/WOW, unknown route, delayed/disconnected receiver, working audio, disable during wait/write, interrupted process, timeout/status and explicit saved-setting restore. Confirm emergency Home restore stops automation and never clears persistent Home off. Only supervised recoverable tests; retain uncertain receipts. |
| Controls and lifecycle | Home/arrows/OK/Back/volume/unrelated buttons and key-up delivery; triple-Home persistent-off and explicit re-enable; standby and AC-off cold boot separately; new setup/update/removal and rollback with candidate private inventories. Known #90 standby failure is still open. |

Record each row as pass/fail/not tested with exact source/artifact, model/firmware,
expected/actual behavior and reviewed redacted evidence. A package install, RPC
success or settings restoration does not establish input compatibility or sound.
Do not transplant old acceptance into this candidate's `acceptance` field.

## Root 0.4.0 transition regression (#111)

Supervised C3 preparation on source `3eef546b` stopped before Root removal:
the coordinator required the new `audio_recovery.py` in the complete published
0.4.0 runtime. System/Root Updaters had already been disabled. The original
request and private off-TV backup were retained; supported restore returned LG
Home, confirmed by the owner with arrows/OK/volume. At the restored pre-removal checkpoint, Root intent was disabled, recovery
integrity verified, and all application versions were unchanged.
A complete separately verified coordinator from `cc7051aa` subsequently continued
the same original operation/lease with its immutable snapshot. All 51 new code
files, original request identity, completed disable receipts and absence of
uncertain submissions/live workers were checked before continuation. Removal
completed; independent installer status confirmed `current: true` and reconciled
the local receipt. Old Root state remains retained and updater states are archived.
This proves the checked transition recovery, not new-runtime acceptance. Do not use that older
candidate to replace Root 0.4.0.

PR #112 integrates the corrected coordinator. It must bind the installed release metadata and verify
its exact version-specific runtime inventory against both bundle and recovery
proof, before disabling updaters and again before invoking the old driver. A
current-version missing file, altered digest, foreign app/package or unsupported
historical closure must fail closed.

An already retained original request requires reviewed continuation with the
same operation/lease and immutable request payload. Prove there is no live
worker, no uncertain package submission and no Root removal submission. Use the
complete separately verified trusted coordinator closure; never patch installed
runtime, the old worker snapshot or completion receipts. Record old request and
new recovery-code identities separately. Fresh exact-source installers and all
remaining hardware checks are still required before publication.

## Exact 9194 Root 0.5.0 first AC result (#104)

On the maintainer's OLED55C3RLA / 43.21.71, exact source
`9194c16a1a38e136823624fd5c9bce1b373fc92c` / CI40489987476 completed checked
fresh Root0.5 setup after the supported #111 recovery. Runtime integrity,
active intent, independent guardian and recovery passed before the test.
Owner-confirmed Clean, Emby launch/playback/retained login, short Home→Clean,
arrows/hold/OK/Back/volume passed as basic controls.

**First AC cold boot failed:** remote off10s, AC off30s, reconnect/on and no Home
for1minute left LiveTV/unconfigured channels. Input ENODEV revoked intent and
restored stock routing; subsequent Home opened LG Home with working controls.
Original logging cannot place that input loss before versus after restart.
A separate passive Root-disabled diagnostic cycle confirmed Active Standby before
ENODEV and systemd stopping afterward. This is investigation only, not standby
acceptance. The diagnostic observer was removed; Root remains disabled.

Do not reuse these artifacts to accept the new shutdown correction. Deliver any
new source through fresh exact artifacts and supported checked transition, only
when the owner is ready. Cold boot, standby, emergency/off persistence and actual
physical rollback remain pending. #104 is under further implementation; #90's
original standby report remains separate. Keep raw evidence private and release
acceptance empty. See [technical evidence](development/ROOT-COLD-BOOT.md).

## Existing Root installations and rollback

Read [Root Home initialization](development/ROOT-HOME-READBACK.md) and
[audio recovery](development/ROOT-AUDIO-RECOVERY.md) before testing.
An app-only update cannot replace retained private runtime/service drivers.
Continue only through the supported coordinator when exact private hashes and
operation evidence permit it; otherwise retain state for reviewed recovery.
Do not delete journals or overwrite recovery files to force this candidate.
The explicit stock LG Home override remains after rollback/removal; audio receipts
can remain with retained recovery evidence. Restore saved eARC only by explicit
choice when that saved setting is still desired.

Retain verified v1.3.0 rollback packages and feeds before device changes. Record
actual whole-edition rollback separately from package/feed integrity checks;
physical signed rollback is not claimed tested. Do not clear emergency stop
implicitly. No diagnostics, credentials or private state belong in release assets.

## Maintainer finish

Run the complete suite and payload/package verification on the combined source.
Dispatch `cytv.yml` on `release/next` with `test_build=true`. Keep #98 draft and
acceptance empty while collecting feedback. After any source change, use fresh
artifacts and repeat affected device checks. Before making #98 ready, complete the
documentation pass, hardware/rollback record and exact final-head Linux/macOS,
Android and all four desktop builds. Then follow [release flow](RELEASE-FLOW.md).

## Required before publication: Root cold boot and first screen (#104)

Source fixes and observer diagnostics are being integrated separately. Existing
Root 0.4.0 observations do not accept the corrected candidate. Use the exact
candidate's coherent retained runtime through supported checked setup/update;
record source/bundle hashes and the TV model/firmware. Keep raw records private.

- [ ] Verify active intent, independent guardian and recovery before power-off.
- [ ] With LG Power On Screen set to Home, remote off, wait ten seconds, remove AC
  for thirty seconds, reconnect and turn on. Do not press Home or open an app
  until recording the first screen. **Expected: Clean appears automatically**;
  unconfigured channels/Live TV remaining foreground is a failure even if Home works.
- [ ] After the first-screen observation, open Emby and press short Home.
  **Expected: Clean**, with active intent, fresh guardian and verified recovery.
- [ ] Repeat at least three AC-off cycles; retain every failure. Verify a new
  session identity per cycle and stable identity through early clock correction.
  Record standby/wake separately; issue #90 remains unresolved by diagnostics alone.
- [ ] Open Emby as soon as startup permits and leave it visible through the first
  minute. No delayed Clean relaunch should replace that app. Foreground read and
  optional launch are separate platform calls; record any concurrent-switch race.
- [ ] Triple-Home, then cold boot: Root stays off, short Home uses LG routing and
  Clean does not automatically reactivate. Repeat after explicit settings off.
- [ ] Confirm arrows/key-up, OK, Back, volume and unrelated controls; no repeated
  launch loop or late retry after an unavailable/uncertain optional API result.

All boxes remain pending for the new candidate. Keep release acceptance empty
until genuine results are recorded; do not copy successful stable standby or
old-source cold-boot results into this matrix. See
[cold-start evidence and source policy](development/ROOT-COLD-BOOT.md).
