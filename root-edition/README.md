# Root Edition

**Native Home and Back routing, with an on-TV emergency exit.** Root Edition
uses the same launcher interface as No-root Edition, but registers a separate
application as the system Home. No router script, USB drive or always-on computer
is needed after setup. Published setup uses a computer for installation and recovery tools.

[v1.3.0 stable](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.3.0) includes **Root Edition 0.4.0**, **Root Updater 0.3.0** and **System Updater supervisor 1.1.0**. Latest-download links follow the published release.

Historical Root **0.2.0**, Root Updater **0.2.0** and System Updater supervisor **1.0.0** were checked on **LG OLED55C3RLA / firmware 43.21.71 / webOS 11.2.0**, using `d344d92` (product contents identical to `4b66951`). Arrows, OK, app launch, Home, Back/Cancel/confirmed exit, volume/mute, triple-Home emergency exit and explicit resume passed. Standby/wake with Emby left open for 70 seconds and the installed-version menus passed; an unavailable update feed showed a friendly message. True cold boot, Helper **0.6.19** on a TV, UK6540PTD, and a complete signed system upgrade or rollback remain untested. Stable publication accepts this limited evidence; it does not validate every model or path.

See [current 1.3.0 acceptance and known issue #90](../docs/RELEASE-1.3.0-ACCEPTANCE.md). Historical [1.2.0 acceptance](../docs/RELEASE-1.2.0-ACCEPTANCE.md) remains scoped to its original artifacts. Earlier [0.1.1](ROOT-0.1.1.md) and [0.1.0](ROOT-STABLE-0.1.0.md) records retain their original artifact scope. Keep working installers and recovery backups.

[Install and activate](ROLLOUT.md) · [Compare editions](../docs/EDITIONS.md) ·
[Acceptance](RELEASE-ACCEPTANCE.md) · [Recovery design](RECOVERY.md)

**Since 1.2.0:** Home settings → LG firmware updates controls Homebrew
Channel's existing firmware-blocking preference. Changes need a real TV restart;
the saved switch is not proof of active blocking. This also blocks firmware
security updates, and Homebrew retains the preference after CYTV removal.
See [operation, limitations and TV acceptance scope](../docs/LG-FIRMWARE-UPDATES.md).

## Candidate: two setup clients, one installation

**Unpublished Homebrew Installer candidate:** CYTV Installer is a separate Root-only on-TV
application alongside cytv. It has no published Homebrew catalog listing yet.
cytv retains No-root and Root on all existing platforms. Root setup requires
existing root, Homebrew exec, Node.js 8+ and working Python 3.9+; supported ARMv7
or `armv8l` 32-bit userspace may explicitly prepare the bundled pinned offline
private runtime before reinspection/final review. No new hardware compatibility
is implied by packaging or the historical Root 0.2.0 checks above.

The shared coordinator installs Root Home and Root Updater, with explicit optional
System Updater preparation. Home activation is separate and off/emergency state
stays off. Verified installations share profiles and recovery across clients;
unknown older infrastructure is not migrated automatically. Fresh
`--migrate-packaged-home` imports packaged preferences only, never browser storage.

Homebrew updates Installer only; product updates remain with existing updaters.
Deleting Installer leaves Root and recovery installed. Complete removal restores
LG Home and removes owned packages, registrations and startup links, retaining
required recovery archives and Python slots. The UI offers continuation only for
proven final readback; other interrupted stages need status/recovery or the
[explicit source CLI](../docs/MANUAL_INSTALL.md#candidate-shared-product-continuation).
See [setup](../docs/INSTALL.md#candidate-on-tv-root-installation) and the
[pending hardware matrix/state inventory](../docs/development/HOMEBREW-INSTALL-ACCEPTANCE.md).

## What works on the tested setup

- Short **Home** selects our launcher through system routing, without the old
  interception helper running.
- Confirmed **Back** exit returns to our launcher without an observed LG flash.
  In-app navigation and exit confirmation remain under the application's control.
- Turning **Change Home** on enables permanent intent after automatic input and recovery checks.
- A confirmed normal shutdown retains our Home profile so bootManager selects
  our launcher as its first app on the next startup. Recovery then renews the
  routing transaction after normal-boot and fresh input/guardian checks pass.
- **Three short Home presses within two seconds** request emergency restoration
  independently of the web interface. Release Home between presses; do not hold it.
- Turning **Change Home** off in Home settings restores the original routing.
  **Open LG Home** only visits LG Home once and preserves the routing selection.
- Two independent health checks and recovery state protect the system route.
  Failed startup or a later health failure automatically restores LG Home.

The original launcher, helper and their data are separate. Root exit disables
Root autostart; it does not remove root, uninstall apps or resume the old helper.
To return to No-root, restore first and then explicitly resume Home Helper from
the ordinary launcher. Never run both modes' input handling together.

## Requirements and limits

An already rooted TV, working root SSH access with a verified host key, Python 3.9+
and Node.js 8+ on the TV, Homebrew services and the supported ARM32 Magic Remote input interface
are required. Installation checks fail closed for unexpected state. A doctor
report alone does not establish compatibility.

**Unreleased, issue #82:** if Settings Service has no Home override, explicit
setup can initialize it to verified LG Home and read it back before finalizing
recovery. Existing values are not replaced. Uncertain writes are not replayed;
retain recovery data. Status/doctor never writes this setting. The explicit stock
override remains after removal. See [readback design and acceptance limits](../docs/development/ROOT-HOME-READBACK.md).

The computer/Android installer can provision a private, verified ARMv7 Python
when system Python is missing or incompatible. Working system installations do
not download this component. See [automatic Python runtime](../docs/OPTIONAL-PYTHON.md)
for delivery, retained recovery dependencies and unverified older-TV limitations.

The installer does not root your TV, change Developer Mode or flash firmware.
See the [upstream rooting overview](https://www.webosbrew.org/rooting/) separately.
Do not install Developer Mode over an existing root setup for this guide.

The public bundle contains no personal app list. Installation can copy validated
profile data from an existing Home installation without modifying it. It does not
migrate arbitrary browser storage. Root excludes the ordinary Home updater and
Developer Mode renewal UI. Its own **Settings → Software updates** uses an
independent System Updater supervisor after explicit computer bootstrap, with
signed whole-edition release sets, saved profiles and bounded rollback. Startup
health confirmation is automatic. Rollback remains available after confirmation,
without a time limit, until the next update replaces the saved transaction. It
restores the previous package and pre-update settings; the rollback dialog warns
that later settings changes will be lost. After verified startup, previously
enabled Home control resumes automatically through its existing guarded activation
path. Explicit or emergency off during the update wins; disabled preferences,
failsafe and uncertain activation stay off. The runtime and independent updater
must be migrated together from the computer for this behavior. See
[Root updates and one-time setup](UPDATES.md) and the
[isolated update/rollback validation](../docs/development/ROOT-UPDATES-TV-VALIDATION.md). The RC can update compatible Root recovery infrastructure as part of the signed
set; first supervisor/runtime bootstrap and legacy migrations remain computer-assisted.

Early boot black screens, faster boot artwork, system-library patches and
removing system advertisements are **not** delivered by this edition. Long Home
is not its emergency gesture and can invoke LG behavior such as magnification.

For exact evidence and outstanding tests, read [release acceptance](RELEASE-ACCEPTANCE.md).
Historical research is retained in [STATUS.md](STATUS.md); older RC limitations
are not the current usage instructions.


## Recovery startup diagnostics (1.3.0, issue #55)

Version 1.3.0 preloads `service/startup-diagnostics.js` before the firmware's
Node bootstrap. The runner still execs Node with the same PID and bootstrap
arguments; registration formats and recovery behavior do not change. A private,
root-owned mode-0600 `recovery-service.json` under `/var/lib/clean-your-tv-root`
records the current startup and terminal exit code. On Node 12.17+/13.7+,
`uncaughtExceptionMonitor` also records a bounded exception name/code/stack
without handling the exception or preventing its normal fatal exit. Node 8 still
records exit codes but cannot capture the exception through that monitor.

The file is replaced on each start and remains below 32 KiB; the exception stack
is limited to 4096 characters. Unsafe paths, symlinks/hard links and diagnostic
I/O failures cannot redirect writes or stop the service. This is exception/exit
instrumentation, not an unbounded stderr log. SIGKILL, default signal termination,
native aborts and failures before the preload runs may leave only an incomplete
startup record or no record. No exit code is invented in those cases.

If `finalize` fails, `recovery-failure.json` retains the failed phase, bounded
numeric Luna/client codes, recognized service/method/permission categories and
safe startup observations. A previous unchanged startup record is marked stale.
Luna stdout and stderr are drained with a combined 64-KiB limit; raw RPC text is
not exported. No readiness proof, Home activation or automatic retry is added.

The cytv installer reads this data after a definite failed Root install and adds
allowlisted `root_recovery` fields to that failed attempt's saved diagnostic
report. A per-install `CYTV_ROOT_INSTALL_ATTEMPT` token must match the retained
report; earlier failures cannot be attached to a later attempt. The token is not
exported. Failed/malformed diagnostic reads preserve the original install error.
The manual SSH bundle retains the two private files on the TV; its nonzero exit
alone is not a diagnosis. Review private exception text locally before sharing;
never publish the full file without redaction. Preserve deployment journals,
LS2 snapshots and retained drivers; do not overwrite an older installed driver
to retrofit these diagnostics or rerun provisioning merely to collect a log.

The OLED Flex 42LX3Q9LA / webOS 11.2.0 startup failure is still unresolved. The
firmware bootstrap argument contract and effective LS2 registrations need device
evidence; this change does not implement the report's unconfirmed manifests.d
hypothesis. No hardware, standby or cold-boot acceptance is claimed.

Packaging at freeze: bump/rebuild Root and cytv, synchronize metadata and rebuild
all desktop/console/Android payloads. The new private service file also changes
the generated Root infrastructure and System Updater inventory. Version/rebuild
the supervisor/bootstrap and validate its migration or explicit computer
rebootstrap before shipping; an old pinned inventory cannot accept the new path.
Existing failed installations and rollback baselines must remain recoverable.
Component versions and the release candidate inventory are unchanged here.


Unreleased cold-boot correction: rooted SDK DATA may have ordinary `0777` modes.
The corrected private readers require independent original package hashes; they
do not repair shared permissions or execute shared source. Missing/conflicting
current, transaction or own-package proof keeps automatic Home rearm inhibited,
while independent private LG Home restoration remains available. Deliver the
changed helper closure through checked fresh setup/rebootstrap, preserving
existing recovery archives and unknown-operation records. Updating Installer
alone does not replace retained private product code. Root remains disabled until
an explicit activation through the normal setup/settings flow. See the
[candidate authority and acceptance record](../docs/development/HOMEBREW-INSTALL-ACCEPTANCE.md#cold-boot-data-authority-correction).

## Unreleased HDMI sound recovery

Root settings → HDMI sound provides manual eARC restart and confirmed HDMI-route
fallback recovery. Experimental boot/standby recovery is off by default and may
interrupt healthy audio. Unsupported/combined modes are skipped. Interrupted
transactions require explicit setting restoration. Home restoration/emergency
off inhibits automation until explicit enable. Existing private runtimes need
checked fresh setup. No physical compatibility or faster acquisition is claimed.
See [runtime and pending acceptance](../docs/development/ROOT-AUDIO-RECOVERY.md).
