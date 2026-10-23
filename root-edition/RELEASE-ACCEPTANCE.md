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
| 3 | Failsafe recovery | RC7 automatic restoration passed; normal mode returned; physical controls confirmation pending |
| 4 | Input/lifecycle matrix | Cancel and in-app Back, held arrows, volume, pointer/wheel, quick standby and cold boot on final bundle |
| 5 | Permanent-mode escape | Validated exit restores routing without zoom, reactivation or dependence on a reachable host |
| 6 | Permanent activation | Implement and accept after recovery/escape gates; preserve exact original state |
| 7 | Public release | Attach accepted artifacts and hashes; document install, restore, uninstall and limitations |

The host `restore` command and bounded deadline are the candidate's current escape
routes. Long Home is not a promised Root-mode emergency exit. System-library
patches and boot animations are outside this release.

## Deferred observation

After software-reboot recovery, Live TV became foreground and the user reported a
black screen; Home returned to the working launcher. Investigate separately.
Do not describe this as fixed or as evidence of a launcher crash.

## Hardware records

Record bundle hash, installed payload differences, model/firmware, initial routing,
helper state, transaction, outcome, recovery readback and user-visible result.
Keep private logs and credentials out of the repository. An API success alone is
not acceptance.
