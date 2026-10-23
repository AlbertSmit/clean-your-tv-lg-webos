# Root Edition release acceptance

Updated 2026-10-23. Target: LG OLED55C3RLA, firmware 43.21.71.

## Release boundary

The current deliverable is an isolated 60-second hardware-test candidate, not a
permanent Home replacement. Keep the supported No-root release available.
Do not unlock `enable`/`confirm` based on successful timer tests alone.
Earlier lab tests do not establish acceptance of a different final bundle.

## Completed on the corrected installed candidate

- Native short Home and confirmed Back exit to the real launcher UI, without an
  observed LG flash, with the legacy interception helper stopped.
- Arrows and OK during the bounded routing test.
- Independent timer restoration of SAM Home and both system-profile destinations.
- Software reboot during an active trial: automatic restoration, no manual restore.
- Recovery activity persisted across reboot; recovery integrity passed.
- Explicit production helper resumption; Home returned to the production launcher.

The TV candidate received audited corrections through RC5. RC7 subsequently passed clean installation and normal uninstall; routing and
reboot evidence still applies to the earlier corrected deployment. No cross-model support is implied.

## Ordered remaining work

| Priority | Gate | Pass condition |
| --- | --- | --- |
| 1 | Final bundle identity | Reproducible build, passing local suite, retained hashes, no private inventory |
| 2 | Clean install and removal | Passed on RC7; production static hashes unchanged and helper active |
| 3 | Failsafe recovery | RC7 automatic restoration passed; normal mode and arrows/OK/short Home confirmed by the user |
| 4 | Input/lifecycle matrix | Cancel and in-app Back, held arrows, volume, pointer/wheel, quick standby and cold boot on final bundle |
| 5 | Permanent-mode escape | Validated exit restores routing without zoom, reactivation or dependence on a reachable host |
| 6 | Permanent activation | Implement and accept after recovery/escape gates; preserve exact original state |
| 7 | Public release | Attach accepted artifacts and hashes; document install, restore, uninstall and limitations |

The host `restore` command and bounded deadline are the candidate's current escape
routes. Long Home is not a promised Root-mode emergency exit. System-library
patches and boot animations are outside this release.

## Normal UI exit

RC10 passed Settings → Exit Root mode → Confirm exit on the C3. Readback and LG
Home foreground were confirmed before the independent deadline. The helper stop
latch remained set. A frozen-UI emergency path is still a separate gate.

## Deferred observation

After software-reboot recovery, Live TV became foreground and the user reported a
black screen; Home returned to the working launcher. Investigate separately.
Do not describe this as fixed or as evidence of a launcher crash.

## Hardware records

Record bundle hash, installed payload differences, model/firmware, initial routing,
helper state, transaction, outcome, recovery readback and user-visible result.
Keep private logs and credentials out of the repository. An API success alone is
not acceptance.

## RC13 bounded emergency exit accepted — 2026-10-23

On OLED55C3RLA / 43.21.71, three short Home presses restored LG Home on
the first attempt, without observed zoom, both normally and with the separate
candidate renderer stopped by SIGSTOP. The legacy helper was stopped throughout.
The observer does not grab, consume or reinject keys.

RC11 exposed an inactive input node returning ENXIO; discovery now skips only
ENXIO/ENODEV/ENOENT and still rejects ambiguous or inaccessible active channels.
RC12 required a second gesture attempt. A passive trace showed cursor-show 1198
cleared the first Home tap. RC13 excludes that notification from gesture resets;
physical buttons, repeats, long holds and the existing time limits remain unchanged.
The exact recorded failing sequence is now a regression test. Both corrected
passive sequences were recognized (approximately 599 and 522 ms).

Normal trial a477d2ff-0b36-40ec-a8d4-98e30ee8d341 restored all three stock
Home destinations by uptime 2246.19, before deadline 2269.64, with reason `escape`.
Frozen-renderer trial ee8889b2-0bc5-4943-b901-19558a774e51 recorded restoration
at uptime 2306.37 while the renderer was still `T (stopped)`. The separate
resumer then issued SIGCONT because the journal was restored, not because its
45-second timeout expired. The independent Home deadline was 2351.15. The user
confirmed first-attempt LG Home and no zoom in both trials. Subsequent readback
showed stock SAM/defaultApps/idleApp, no active guardian and verified integrity.

Full local suite passed (171 Python tests, 11 additional tests and remaining
script checks). RC13 bundle.json SHA-256: `f85fb75dc77cec7a867fdb927711ddb560e4d292161dcc53370e9e2edd9f5e56`.
The installed candidate includes locally migrated packaged preferences; private
inventory and raw device logs are not published. RC12 artifacts/state are retained
for rollback. Production launcher and helper files were not modified.

This closes the **bounded-trial** frozen-UI escape check on this model. Permanent
observer lifecycle, persistent activation and final-bundle lifecycle acceptance
remain separate gates; `hardware_validated` and permanent activation stay locked.
