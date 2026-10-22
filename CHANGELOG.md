# Changelog

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
