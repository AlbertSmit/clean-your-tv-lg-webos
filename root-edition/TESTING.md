# Root Edition test plan

## Local checks (no TV required)

```sh
python3 -m unittest discover -s root-edition/tests -v
scripts/test.sh
```

The Python suite checks doctor parsing and privacy filtering, manifest validation,
exact-byte rollback decisions, preservation of unrelated fields, tampered plans,
conflicts and refusing to overwrite output files. It does not emulate SAM,
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
