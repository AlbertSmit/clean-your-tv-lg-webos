# Testing the unpublished 1.4.0 candidate

Use only the artifacts from the **cytv standalone builds** Actions run linked in
[release candidate #98](https://github.com/Razdva122/clean-your-tv-lg-webos/pull/98).
Verify its source SHA against the PR and record each downloaded artifact's SHA-256.
The latest release/download links still deliver v1.3.0. Candidate artifacts expire
according to Actions retention; they are not public release/update feeds.

Expected versions: cytv 0.5.0; Home 1.5.0; Helper 0.6.19; Root 0.5.0;
both independent Updaters 0.3.1; Android 0.4.0-preview / code 12.
System supervisor wrapper remains 1.1.0 / protocol 1; Root/System private inventories
must come from this candidate. Homebrew public promotion remains disabled.

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

## Device matrix — all new results pending

| Path / target | Required result and evidence |
| --- | --- |
| No-root C5, #12 | On reporter's exact model/firmware, Home works; unknown status stays distinct from off. Open Settings → Developer Mode → Show diagnostics; scroll/focus/Back work; safe Home RPC/storage categories and actual renewal version appear. Recording connection result is separate from settings transport. |
| No-root C2 OLED48C24LA / 43.21.74, #59 | Triple-Home stops; opening Helper settings alone preserves stop; confirmed Start resumes. Failed service status does not trigger reinstall or automatic start. Preserve results for standby and true cold boot separately. |
| Root 43NANO90A6B / 33.31.61, #82 | Review retained operation before any setup. On an eligible absent-key stock baseline, explicit setup journals before SAM write and independently reads explicit LG Home with unchanged other defaults/profiles. Setup, guarded activation and removal then pass. A read-only status/doctor must never initialize the key. |
| Intel macOS / reporter NANO86SNA, #93 | Both frozen entrypoints pass runtime probe without libssl import error; then confirm connection/setup separately. Record firmware, which was not supplied in the original report. |
| Root OLED65C2AUA / 04.40.90, #95 | Low-space preflight reports available/required MiB and failed check, preserves state and performs no cleanup. Advisory WAM measurement is not permission to delete it. Original successful setup and separate ABI report remain separate acceptance. |
| Root eARC LG 55NANO956NA / webOS 5.6.2 / 04.64.00 / HW-Q950A | Automatic recovery starts off. Verify manual reconnect and confirmed route fallback, restore readback and audible sound separately. Compare off/on over at least five repetitions per condition; separate standby/cold boot, Quick Start+ and warm/cold receiver. Measure start-time spread and needless interruptions. |
| Root eARC fault/recovery | Check ARC-only/off, combined/WOW, unknown route, delayed/disconnected receiver, working audio, disable during wait/write, interrupted process, timeout/status and explicit saved-setting restore. Confirm emergency Home restore stops automation and never clears persistent Home off. Only supervised recoverable tests; retain uncertain receipts. |
| Controls and lifecycle | Home/arrows/OK/Back/volume/unrelated buttons and key-up delivery; triple-Home persistent-off and explicit re-enable; standby and AC-off cold boot separately; new setup/update/removal and rollback with candidate private inventories. Known #90 standby failure is still open. |

Record each row as pass/fail/not tested with exact source/artifact, model/firmware,
expected/actual behavior and reviewed redacted evidence. A package install, RPC
success or settings restoration does not establish input compatibility or sound.
Do not transplant old acceptance into this candidate's `acceptance` field.

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
