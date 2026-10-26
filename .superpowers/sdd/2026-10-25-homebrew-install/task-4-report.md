# Task 4 — shared device coordinator

Status: implemented and ready for independent review. No TV calls, publication,
version selection, or issue changes were performed. Physical acceptance remains
outstanding; the automated models do not establish TV compatibility.

## Delivered contract

`root-edition/install_driver.py` owns the product orchestration;
`root-edition/install_device.py` provides bounded local effects. cytv keeps its SSH,
connection, inventory and UI adapters on the host. Its normal Root setup and full
product removal now consume the same device records as the upcoming TV bridge.
The original No-root flow and existing legacy status/doctor/restore interfaces
remain. The existing component setup scripts remain guarded low-level tools;
the shared coordinator invokes their local functions directly, without nested
component CLI leases.

Normal setup installs Root Home and Root Updater. System Updater is optional and
requires `--prepare-supervisor`. Home activation is never a coordinator side
effect; cytv still performs its existing explicit, verified activation phase.
Setup does not clear emergency/off state. Current Root maintenance verifies
current cached package descriptors, actual installed bytes, executable bits,
recognized final lifecycle receipts and saved mutable profiles separately. It
never resets the profile or submits the packages again merely to switch clients.
An absent optional supervisor is distinct from a broken/present supervisor.

Root Updater now records its actual installed package inventory and executable
files. The coordinator accepts the supervisor's verified current updater
component after a complete-product update instead of relying on an obsolete
bootstrap inventory. Exact install terminal events are retained by Root,
Root Updater and System Updater, and final Root removal retains its terminal
receipt. No package-absence readback is converted into a terminal installer event.

The TV path reuses the existing fixed local `dev/listApps` inventory module and
`cytv.package` personalization code, shipped as verified worker data. Host
personalized bytes remain unchanged. Rollback baselines match actual personalized
or explicitly migrated package bytes. Optional supervisor setup captures the
installed matching set; capture now preserves actual executable bits, including
0755 startup scripts.

Full removal holds the product lease across disabling services/startup,
restoring Root/Home, observed package removals, permission cleanup, archival,
registration/routing readback and waiting for old Root processes. Trusted existing
cleanup SCRIPTs are materialized by the builder; the desktop Installer class is
not copied to the TV. Exact per-package terminal events remain in the durable
removal journal. The separately installed `com.cleanyourtv.installer` is retained;
its own removal through LG/HBC is separate. Worker material is snapshotted before
product effects, so removing/replacing the installer cannot change the worker.

Public Root activation uses the same ownership mutex and strictly checks pending
receipts without creating another activation reservation. This serializes
activation against product mutations. Pending boot takes the restore path.
Status/emergency restore remain available, and the updater's separately verified
internal Home-resume `_enable` path is preserved.

## Fixed CLI / Task 5 interface

Invoke the emitted `root-updater/install_driver.py` using the interpreter already
prepared by Task 3. No network or runtime provisioning occurs here. The complete
offline payload uses `root/`, `root-updater/`, and optional `supervisor/`.
cytv uploads only the component payload and never the 50 MB offline runtime.

- `inspect [--payload FIXED_PAYLOAD] [--prepare-supervisor]`: read-only component
  classification. With payload, also verify it and return `candidate_sha256`.
- `install --operation ID --payload FIXED_PAYLOAD [--candidate SHA256]
  [--migrate-packaged-home] [--prepare-supervisor]`: verify and privately snapshot
  the selected component inventories, durably record the request, detach once.
- `status --operation ID`: read durable request/submission state. It never repeats
  package submission, repairs state, prepares a runtime, or acquires a mutation
  reservation.
- `restore`: bounded explicit existing Root recovery. Retained executable support
  and runtime bytes are checked before spawning retained recovery helpers.
- `remove --operation ID --payload FIXED_PAYLOAD [--candidate SHA256]`: same durable
  detached mechanism, then the complete device-owned removal sequence.

`ID` is exactly 32 lowercase hexadecimal UUID digits. Browser/UI input must never
supply paths, commands, URLs, or `--worker`; the bridge selects a fixed verified
payload and fixed actions. `--worker` is an internal subprocess entry, not a UI
operation. The bridge must pass the candidate returned by the review inspection.

`candidate_sha256` is SHA256 of canonical JSON (`sort_keys=True`, separators
`,`, `:`) mapping each selected component name to SHA256 of its exact
`bundle.json` bytes: Root + Root Updater, plus supervisor when explicitly selected.
Submission repeats authoritative inventory verification, checks a supplied
candidate before staging/spawn, checks copied worker bytes against those
inventories, and checks the completed snapshot binding again before execution.
Changed candidates fail safely. cytv also binds its staged bytes with this digest.

Events contain `operation`, `stage`, `state`, `code`. Inspection additionally has
`installation` (`state`, `reason`, `can_install`, `can_maintain`). Submission and
worker events also include `action`, `home_changed: false`, and the candidate
binding when available. Successful worker records include `result`; successful
setup includes `installed`, `verified`, `baseline_sha`, `home_changed: false`.
Successful removal includes `removed`,
`applications_services_startup_removed`, and retained recovery/archive paths.
Actual diagnostic exceptions stay in a mode-0600 worker log, not public events.

Request state is `pending`, `complete`, `recovery_required`, or `unknown` for an
unknown ID. Repeated IDs are status-only, including lost replies/failed spawns.
Changing an ID's action is refused. A duplicate-client reservation race is checked
under the mutex before a new durable lease can be created.

Private records live under `/var/lib/clean-your-tv-installation`: global
`operation.json`, `submission-ID.json`, `request-ID.json`, private
`request-ID/` payload+worker log, and `removal-LEASE_ID.json`. Component journals
and installer receipts retain their own authority. Inspection uses checked
read-only stores and does not create absent component state.

## Conservative recovery / compatibility limits

`--migrate-packaged-home` is the pre-existing explicit packaged-preference import
on a fresh setup. It is not a legacy infrastructure migration. No arbitrary old
retained installation is automatically converted or advertised as installed.
Missing/unknown updater inventories and incompatible journals remain recovery;
existing cytv status/doctor/restore are retained. Unsupported old pending host
full-removal records are not upgraded by package absence or replayed blindly.

Failed/uncertain shared requests remain inspection/restoration only. This commit
does not implement automatic package continuation or automatic release of a
nonterminal product reservation after a crash; absence, elapsed time or a dead
worker is never enough. A future explicitly proved reconcile/continuation path
must preserve the original request and exact terminal/lifecycle evidence. The UI
must display recovery, not offer the same submitted ID as a fresh install.
This is a material conservative limit for independent review, not a claim that
all interrupted-device scenarios are fully resolved.

Physical testing still needs fresh TV setup, both client handoff directions,
optional supervisor preparation, direct/external component and installer removal,
triple-Home, standby, and separately cold boot. No compatibility or issue-fix
claim follows from these tests. The ordinary IPK parsing size limit was not
weakened; Task 5's installer runtime archive needs its own existing offline payload
contract rather than the ordinary component-IPK parser.

## Verification and TDD evidence

Observed red→green cases include missing coordinator/kernel, pending activation
and route-mutex contention, a duplicate-client lease race, and captured startup
scripts losing 0755 (420 versus 493) in the supervisor baseline. Device adapter
integration fixtures additionally exercise every removal effect boundary and
assert ownership remains held. They preserve terminal receipts and verify no
submission occurs on a repeated request.

Final green evidence (earlier `*-red.log`, `task4-driver.log`, and
`task4-cytv-ops.log` are intermediate failures, not final results):

- `/private/tmp/task4-driver-green.log`: 22 coordinator tests, OK. Includes real
  process death after submission, snapshot replacement/lost reply, failed spawn,
  candidate mismatch, package bytes/modes, profile/off preservation, and removal
  boundary failures under the actual local orchestrator.
- `/private/tmp/task4-root-focused-green.log`: 139 tests, OK, via
  `PYTHONPATH=root-edition:root-edition/tests python3 -m unittest
  test_install_driver test_setup_deploy test_installation test_update_setup
  test_update_guard test_update_home_resume test_update_core test_update_device`.
- `/private/tmp/task4-cytv-green.log`: `python3 -m unittest discover -s tests/cytv`,
  318 tests, OK (23 existing environment-dependent skips). The new shared-client
  tests include desktop import without `fcntl`/`termios`.
- `/private/tmp/task4-system-green.log`: `python3 -m unittest discover -s
  tests/system_updates`, 92 tests, OK.
- `/private/tmp/task4-system-build-green.log`: 10 build/setup tests, OK, including
  actual captured startup executable bits.
- `/private/tmp/task4-payload-green.log`: actual emitted Root, Root Updater and
  supervisor builds plus the complete offline payload from the parent's verified
  pinned runtime cache. Authoritative inventories: Root 40, Root Updater 48,
  supervisor 26 files. Shared/infrastructure inventory consistency passed.
  An isolated subprocess outside the repository imported emitted
  `install_driver`, `install_device`, `system_setup`, `root_package` and verified
  the exact updater inventory without repository imports. The emitted optional
  supervisor verifier also passes; emitted `inspect` returns an unsupported
  event on this non-TV host.

The full Root suite had also passed 551 tests before the final focused additions;
`/private/tmp/task4-root.log` records that earlier broader run. Parent owns the
final combined `scripts/test.sh tv installer` gate after subsequent tasks; no
redundant final broad run was performed here. Test PATH was
`/private/tmp/clean-your-tv-pr16-venv/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`.
`git diff --check` passed.

Temporary `/private/tmp/task4-{root,updater,supervisor,payload}` outputs and Task 4
logs are review artifacts and may be removed after preserving this report. The
parent-owned pinned runtime cache was only read and must not be removed by this
task. Parent owns final managed-worktree archival and cleanup.
