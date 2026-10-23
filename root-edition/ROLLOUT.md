# Root Edition candidate rollout

The deliverable is an isolated, installable hardware-test candidate. Permanent
activation remains disabled until the final package passes the checks below.
The production No-root application and helper are not upgraded by this installer.

## Priority and release gates

| Priority | Deliverable | Current evidence / remaining gate |
| --- | --- | --- |
| P0 | Isolated application, native Home and Back routing | Corrected installed candidate passed Home and Back; clean final bundle still needs acceptance |
| P0 | Independent 60-second rollback, exact profile restoration | Corrected candidate passed independent timer and software-reboot rollback |
| P0 | Recovery service, interrupted install handling, uninstall | Software-reboot delivery passed; final clean install, failsafe and uninstall remain |
| P0 | Preserve existing Home, preferences and helper latch | Installer refuses conflicts; never clears the helper's emergency stop |
| P1 | Reboot, fast standby, cold boot, failsafe acceptance | Test together on the final candidate |
| P1 | Persistent activation and clean emergency escape | Locked pending acceptance; not a supported feature of this candidate |
| P1 | Public prerelease | Only after the preceding gates; publish hashes and model-specific results |
| Later | Boot artwork, shorter black screen, system library patches | Outside this release scope |

Do not turn earlier lab evidence into a compatibility claim for this package.
Test device: LG OLED55C3RLA, firmware 43.21.71. Other models are unvalidated.

## Build and verify locally

From the repository root, using Python 3.9+ and Node.js:

```sh
bash scripts/test.sh
mkdir -p build
python3 root-edition/build.py --output build/root-candidate
```

The output directory must not already exist. It contains the IPK, host controller,
device driver, recovery runtime, release inventory and SHA-256 bundle manifest.
Public builds contain an empty application inventory, never personal backups.
Production updater, profile bootstrap and helper-control UI are omitted from this
separate application. Installation alone does not change system Home.

## Hardware session (run together)

Use an existing root OpenSSH alias `my-tv` with a verified host key. The host needs
Python and OpenSSH; the TV needs Python 3, luna-send and Homebrew root services.
The installer does not obtain root or alter Developer Mode.

```sh
python3 build/root-candidate/setup.py install --ssh my-tv --bundle build/root-candidate
python3 build/root-candidate/setup.py status --ssh my-tv
```

Installation registers a recovery-only service. It refuses an existing candidate
or state directory. An unknown installation result is not success: retain its
journal and inspect it; do not retry or delete the state directory blindly.

Before the first routing test, explicitly stop the existing No-root helper using
its long-Home action. The candidate refuses to activate while the helper appears
to be running. It never clears the emergency-stop latch or restarts that helper.

```sh
python3 build/root-candidate/setup.py trial --ssh my-tv
```

The independent guardian restores the previous routing after 60 seconds. Check
short Home, arrows/OK, Back within an application, Cancel in its exit dialog, then
confirmed exit. Record whether LG flashes. Long Home is not advertised as an
emergency exit in this candidate: use the deadline or the separate restore command.

```sh
python3 build/root-candidate/setup.py restore --ssh my-tv
python3 build/root-candidate/setup.py status --ssh my-tv
python3 build/root-candidate/setup.py uninstall --ssh my-tv
```

Uninstall restores routing first, removes only owned recovery registration, then
removes the isolated package. Conflict evidence and state are retained. It does
not delete or restart the production helper. After recovery, manually use the
production Home's **Enable Home control** action to resume your existing setup.

Next test the same candidate across restart, fast standby, cold boot and failsafe.
Only then decide permanent activation and its emergency escape. A working timer
or SSH command is not a substitute for a validated permanent-mode emergency exit.

### Optional packaged preference migration

Add `--migrate-packaged-home` only to the install command to copy the fixed
installed `com.gathin.tvhome` app's packaged `apps.js`, `config.js`, and referenced
icons into the isolated candidate after its original IPK hashes are verified.
The production source is read-only. Browser/localStorage-only preferences are
excluded. The offline bundle stays generic; the TV records resulting candidate
hashes in `/var/lib/clean-your-tv-root/personalization.json`. Without this flag,
the candidate uses its empty default inventory. This flag is rejected for other
commands.

Unknown removal is also fail-closed: a recorded `remove-submitting` or
`remove-observed` stage blocks automatic resubmission. Inspect the retained
terminal evidence and candidate directories before any manual recovery decision.

Track the remaining evidence in [release acceptance](RELEASE-ACCEPTANCE.md).
