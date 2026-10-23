# Root candidate validation — 2026-10-23

This is a development record, not a public release certification.

## Confirmed on the TV

On OLED55C3RLA / firmware 43.21.71, the user confirmed the actual Root launcher,
remote navigation, short Home, and confirmed application exit through Back.
The UI intentionally resembles the ordinary launcher; system Home registration,
not visual appearance, distinguishes the Root mode.

The isolated candidate now imports validated JSON from the updater profile when
available. It copies app selection into the candidate without running the
production bootstrap or modifying the production profile. This resolves the
empty candidate caused by importing empty packaged inventory from a newer UI.

## Unexpected recovery

The previous active run recovered to LG Home at approximately uptime 703 s.
The emergency log recorded `supervisor_error` from `require_guardian`:
`device_adapter.safe_json` raised `Unsafe state file`. Recovery disabled the
persistent intent and restored the original Home.

A deterministic local regression reproduces this exception when an atomic
publisher replaces a heartbeat after the reader opens it but before `fstat`.
The old inode then has zero links. The TV log does not record individual stat
fields, so the precise inode race on that run is inferred from the matching
failure and the publication code, not directly observed.

The reader now reopens the current path up to three times only for detached
inodes. It never accepts detached content. Owner, file type, write permissions,
size, no-follow, hard-link and heartbeat freshness checks remain enforced.
Continuous replacement fails closed. Local suite: 367 tests passed.

## Remaining release gates

- Observe the corrected active mode beyond the previous failure interval.
- Reboot-test the serialized boot dispatcher and current candidate together.
- Do not equate successful local tests with permanent hardware validation.
- Preserve independent rollback, emergency exit and the untouched ordinary launcher.
