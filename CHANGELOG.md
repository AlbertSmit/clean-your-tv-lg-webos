# Changelog

## Unreleased — Root Edition preparation

- Add an edition comparison while keeping No-root as the released path.
- Add a read-only root doctor with optional launcher-category inspection.
- Add a local-only Home-category metadata plan and conflict-aware rollback decisions.
- Document bounded diagnostic successes, the production Home category failure, and remaining hardware/recovery gates.
- Include Root Edition Python checks in CI. No production launcher/helper behavior changes and no Root Edition installer in this update.

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
