# Root Edition test plan

## Local checks (no TV required)

```sh
python3 -m unittest discover -s root-edition/tests -v
scripts/test.sh
```

The Python suite checks doctor parsing and privacy filtering, manifest validation,
exact-byte rollback decisions, preservation of unrelated fields, tampered plans,
conflicts and refusing to overwrite output files. Preview tests also verify
separate identity, exclusion of personal inventory and helper scripts, rejection
of indirect source files and reproducible content hashes. It does not emulate SAM,
registration-cache updates, power loss or Homebrew failsafe.

Existing launcher/helper tests remain part of the normal suite. Root tooling is
not included in the production IPKs by `scripts/build.sh`.

## Hardware gates (user present)

Before each stage, verify the baseline, off-device backup and independent recovery.
Use one bounded change at a time. Do not count a successful API reply as a visible
or cached-state result.

| Stage | Required evidence |
| --- | --- |
| Manifest registration | Only Home category changed; getAppInfo and actual category-based launch both agree |
| Metadata rollback | Exact original bytes restored; SAM registration matches original; settings untouched |
| Short Home | From an ordinary application screen, returns to real Home while the interception helper is stopped |
| Back Cancel | Back still navigates in-app; Cancel leaves the app running |
| Back exit | Confirmed exit returns to real Home; observe any LG flash |
| Other controls | Arrows, held arrows, OK, volume, pointer, wheel and app launches work |
| Emergency behavior | A documented escape returns to LG and restores routing, with no automatic re-enable |
| Timer/crash recovery | Forced activation/worker failure returns all routing and metadata state to baseline |
| Startup | Normal reboot, quick standby and cold start preserve controls and intended startup |
| Failsafe | Recovery runs with ordinary init.d unavailable; normal operation resumes after leaving failsafe |

Repeat application-exit tests across multiple apps. A dialog intercepting Home is
not the same case as Home pressed from an ordinary app screen. Record the screen,
transaction timing and whether the helper was actually stopped.

## Report results

Use the Root Edition issue template. Include model, firmware, component versions,
which exact stage ran, expected/actual behavior and whether rollback succeeded.
Review/redact doctor output. Do not attach root credentials, pairing tokens,
SSH keys, private backups, firmware images or complete device logs.

## Integrated candidate acceptance record

For the new package, record its `bundle.json` SHA-256 before starting. Earlier
private tests do not count as acceptance of this build. Run these steps together:

1. Install recovery-only; confirm production Home and startup are unchanged.
2. Confirm candidate payload hashes, service root identity and owned activity.
3. Explicitly stop the legacy helper. Start the bounded trial; confirm native
   Home, Back Cancel, confirmed Back exit and other controls.
4. Let the deadline expire. Check all original Home destinations and user-visible
   control. Resume the legacy helper explicitly through its existing UI.
5. Repeat recovery after worker failure and reboot, then Homebrew failsafe.
6. Exercise interrupted installation and uninstall only on this isolated package;
   preserve conflicting/unknown state for inspection.

Local tests cover independent installer completion, unknown outcomes, exact
payload hashes, recovery provisioning and the helper stop latch. They cannot
prove delivery of a boot activity on this firmware. Permanent activation remains
unavailable until lifecycle tests and an emergency exit are accepted.
