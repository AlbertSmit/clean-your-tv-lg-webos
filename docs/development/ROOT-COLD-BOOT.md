# Root cold-start identity and initial screen

This is unpublished source work for issue #104. It is separate from issue #90's
intermittent standby input-readiness failure and PR #103's diagnostic reader.

## Observed existing-source behavior

The maintainer supervised two C3 AC-off tests on 2026-10-27. Existing Root 0.4.0
was active and recovery/guardian readback passed before each test. In the first,
Live TV's unconfigured-channels screen appeared, Root became disabled with stock
routing, and short Home opened LG Home. The kernel UUID was reused, while btime
later differed from the prior active intent. An earlier fault had already
revoked intent before the last recorded boot callback. The available records do
not uniquely identify dispatch versus independent guardian as the first writer.

After explicit user re-enable, the second test waited ten seconds after remote
off, disconnected AC for thirty seconds, reconnected and switched on. Live TV
again appeared first, but Root intent, guardian, routing and recovery were healthy;
short Home opened Clean. The user confirmed LG's Power On Screen was already Home;
read-only queries reported `general.homeAutoLaunch=on`,
`general.powerOnScreen=todays`, `option.quickStartMode=off`. An inert private `/tmp`
probe created before this cycle was absent afterward. The probe did not change
routing or runtime code. Device diagnostics and connection details remain private.

These are two separate outcomes: loss of Home control, and missing initial Clean
presentation despite working Home. Successful standby tests do not validate either
cold-start path. These observations are on the existing runtime, not acceptance
of the new source. Historical first-screen failures remain valid evidence.

## Source correction

`intent_runtime.boot_identity` centrally replaces UUID:btime with UUID plus a
random session nonce. A private `session.json` and `session.lock` share the
existing `/tmp/clean-your-tv-root-boot` directory with the normal-start marker.
The JSON schema is version 1 with `kernel` and a 32-character hexadecimal `token`.
The directory is created mode 0700 and records/lock mode 0600. Root ownership,
regular file/link checks, bounded lock acquisition, exact schema and atomic
publication protect concurrent consumers. Existing malformed records are retained
and rejected. Nothing writes this nonce to flash; existing durable intent stores
the resulting session identifier in its existing `boot` field. No new permissions
or network destinations are introduced.

All existing health, shutdown, update/audio and boot-gate callers share this
identity. Clock correction within a session cannot revoke it. A new kernel UUID
or a cleared volatile store creates a new identity. Old normal-start markers,
health and shutdown evidence cannot authorize that identity. Legacy UUID:btime
intent remains schema-valid and takes the existing restore-before-gate path;
only previously confirmed enabled intent can request rearm. Explicit/emergency
off, input faults and failsafe never become enabled through the new identity.

The nonce-store lifetime was checked on one C3 snapshot/AC-off path. A firmware
that restores this private volatile store can replay the nonce; verify that
path before claiming compatibility. Do not infer a new session solely from an
absent guardian, and never clear session state while Root is running.

After protected startup, one optional presentation request handles remaining
Live TV/stock Home foreground. It requires the native Home auto-launch preference,
normal active hardware startup, first-app launch evidence, fresh bound input
health, unchanged active intent and no failsafe. Foreground is read after health
validation. Other/unknown apps and an already visible Clean are preserved.
Failures are optional and do not revoke healthy Root. Each optional RPC uses a
0.5-second reply deadline plus at most 0.5 second for termination cleanup. No
operation lock spans launch; explicit off can finish while a request is in
flight. A changed intent returns `superseded`, and duplicate callbacks do not
retry presentation. The platform exposes separate foreground-read and launch
calls: an app switch after the final read can still race the single request.
No repeating watcher or automatic emergency-stop reset is added.

## Delivery and acceptance

Deliver the coherent retained runtime through supported checked setup/update.
An app-only update or new host installer does not replace it. Do not edit installed
runtime code or integrity receipts by hand. Keep original recovery/updater archives
and user data before a fresh setup; ordinary reinstallation can reset Root
preferences. Candidate builds and source tests do not establish device acceptance.

Remaining supervised tests on the actual corrected runtime:

- Remote-off/standby and AC-off cold boot separately: first screen without Home,
  then Emby to short Home, active intent, guardian and verified recovery.
- Repeated AC-off cycles, including early clock correction; verify the new
  session differs while its identity stays stable during the same startup.
- Open Emby early and retain it through startup readiness; no late relaunch.
- Triple-Home and explicit off, then cold boot: stay off and retain LG routing.
- Failures/unknown optional APIs, duplicate callbacks and in-flight explicit off.

New-code physical acceptance remains pending until recorded here with exact
installed source/bundle identities. No new firmware compatibility is claimed.
