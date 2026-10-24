# Changelog

## v0.10.3 — Redesigned desktop setup and source installation fixes

- Release cytv 0.2.6 with visible setup stages, Root/No-root cards, keyboard focus and collapsible maintenance actions.
- Include the localized setup, Root recovery/removal and Home startup fixes from the v0.10.2 source tag.
- Repair permissions in the current Helper package instead of a hardcoded old IPK.
- Honor Zig from ZIG/PATH in Termux without requesting the unavailable Android Python distribution.
- Components: cytv 0.2.6, Home 1.3.2, Helper 0.6.16, Root 0.1.4 and No-root Updater 0.1.4. C5/webOS 26 remains under investigation.

## v0.10.2 — Localized setup and complete project removal

- Complete cytv translations for interrupted setup, reinstallation, removal and recovery messages across all supported languages.
- Reconcile interrupted Root setup in the installer and verify the updater connection before activation.
- Remove Root Updater, its service, startup hook and retained app permissions through cytv; preserve inactive recovery records.
- Include the Home startup and bounded standby recovery fixes described in issue #10, plus ten-language TV and installer localization. QNED80T feedback is still pending.
- Versions: cytv 0.2.5, Home 1.3.2, Helper 0.6.16, Root 0.1.4 and No-root Updater 0.1.4.

## Unreleased — C4 helper follow-up

- Restore and verify known state permissions at runtime; avoid SSAP use if permission repair fails.
- Wait up to five seconds for held startup keys without grabbing the remote or losing heartbeat/stop handling.
- Preserve intentional LG Home after long Back while retaining short Home and normal app-exit returns.
- Distinguish EIM rejection, command failure, empty reply and confirmed registration.
- Add permission, startup relay, Back/controller and setup regressions. C3/C4 hardware verification remains pending.

## v0.8.2 — Root Edition 0.1.1 updates and recovery

- Add Root Settings → Software updates with an independent Root Updater and signed, edition-specific metadata.
- Preserve applications, embedded icons, inputs, configuration and tile order across compatible application updates.
- Add a durable one-attempt rollback after verified installation and failed launch confirmation; unknown installer outcomes remain blocked.
- Keep recovery/updater infrastructure pinned and require one-time computer setup; legacy Root Stable 0.1.0 needs supervised infrastructure migration.
- Validate a real Settings update and automatic timeout rollback on OLED55C3RLA / 43.21.71 using isolated lab identities; retain the exact-artifact and power-loss limitations.
- Retain No-root v0.8.1 packages and signed update metadata unchanged in the shared latest release.

## Root Stable 0.1.0 — OLED55C3RLA / 43.21.71

- Add a separate Root launcher, installer and recovery service without changing the stable No-root launcher, helper or updater implementation.
- Route short Home and confirmed Back exits through system Home; no LG flash observed on the tested OLED55C3RLA / 43.21.71.
- Add protected 60-second trials, explicit Keep Root mode, persistent intent and normal software-reboot reactivation.
- Add Settings exit and independent triple-short-Home emergency restoration, with reciprocal health checks, bounded recovery and owned startup registration.
- Import existing validated profile data into the candidate without changing the production profile.
- Fix atomic heartbeat read races and serialize boot callbacks; retain strict freshness and file-safety checks.
- Document both editions, installation, recovery, removal and hardware evidence. The fixed bundle passed quick standby, failsafe, clean removal/reinstall and fault recovery checks. Cold-power testing is deferred; an isolated first-attempt emergency-gesture miss remains unexplained. See the scoped Root Stable release notes.

## v0.8.1 — signed Home updates and recovery

- Add a separate signed-update and recovery package, portable Home profiles, and Software updates in Settings.
- Pause renewal Beta automatically and restore its prior preference after verified installation or rollback; Home Helper remains unchanged.
- Recheck signed offers after service restarts, subscribe to terminal installer responses, and keep ambiguous bus failures in recovery without starting another install.
- Add scoped permission setup/removal and fix remote navigation across disabled controls.
- Verify published signed Home update and rollback on OLED55C3RLA / 43.21.71, preserving apps, remote controls and disabled renewal.
- Grant the renewal service only canonical Activity Manager create/cancel methods; recover safely from a denied pause before installation.
- Refresh Recovery when reopened and reset restore confirmation.

## Unreleased — one-script installation

- Add `./install.sh <TV IP>` for macOS/Linux: local tool setup, Developer Mode SSH pairing, app sync, package build/install, verified helper configuration and helper launch.
- Install Zig 0.14.1 and webOS CLI 3.2.6 locally without sudo or global tool installation.
- Stop on setup errors, reject empty app inventories and protect existing CLI profiles from accidental retargeting. TV pairing approvals and hardware checks remain manual.

## v0.7.1 — macOS build and verified setup transfers

- Build on macOS: `fix-package-data.py` rewrites the ipk in Python; BSD `ar r` reduced the helper package to a 96-byte symbol-table archive.
- `configure-tv.sh` works with `@webos-tools/cli` 3.x, which offers `ares-push` only for the ose/apollo profiles: files are staged over `ares-novacom`, checked by SHA-256 and actual permissions, and atomically replaced; CLI errors are reported without echoing the key.
- `configure-tv.sh` checks the EIM response and warns when early input restoration is not registered.
- Compatibility: community test on LG OLED55C46LA (C4), webOS 24.

## v0.7.0 — Home 1.1.0, Home Helper 0.6.13

- Add opt-in Developer Mode session auto-renewal **Beta**, disabled by default.
- Add Home settings with session status, confirmed-renewal timestamp, disable control and sanitized diagnostics. LG TV settings remain accessible.
- Include a separate on-TV renewal service with direct LG HTTPS, bounded retries, persisted cooldown and a persistent hourly task.
- Home Helper, native key interception, emergency exit and watchdog are unchanged.
- Real renewal on stock unrooted TVs is awaiting feedback. Monitor the official timer; see [Beta guide](docs/DEVELOPER-MODE-BETA.md).


## v0.6.12 — first public release

Launcher 1.0.11; native helper 0.6.12.

- Skip the standby recovery launch when webOS already reports the launcher in front.
  Two quick power cycles passed with arrows, OK and short Home working.
- Include the tested network shortcut, system splash image and removal of the
  redundant internal loader.
- Preserve the native Home relay, watchdog and persistent long-Home emergency stop.
- Supply English setup, recovery and build instructions.
- Load watched application IDs from locally generated configuration instead of a
  developer-specific list.

Known issues: early cold-boot black interval; LG Home flash after Back exit;
unverified compatibility outside the listed C3 setup. The draft recovery-dialog
UI is not included in this release.
