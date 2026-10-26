# Root software updates and recovery

**[v1.2.0 stable](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.2.0)** updates a complete signed edition release set through
an independent fixed **System Updater supervisor**. Root's set includes Root Home,
Root Updater and the compatible Root recovery infrastructure. No-root's separate
set includes Home, Helper and Home Updater. The editions are not interchangeable;
third-party apps and TV firmware are outside the set.

Current C3 checks covered supervisor bootstrap, installed-version menus and friendly feed-unavailable handling. A complete signed system upgrade and rollback remain untested. See [current acceptance](../docs/RELEASE-1.1.0-ACCEPTANCE.md); [earlier Root update evidence](../docs/development/ROOT-UPDATES-TV-VALIDATION.md) retains its original artifact and scenario scope.

## Candidate: Homebrew setup is separate from updates

**Unreleased source candidate:** CYTV Installer can install Root Home and Root
Updater on a compatible rooted TV, optionally preparing System Updater after
explicit selection. It does not obtain root or activate Home during setup.
Homebrew upgrades Installer only; the existing signed product update/recovery
contracts below remain authoritative. Installer's embedded versions may be older
than a later project release. Deleting Installer leaves the product installed;
complete-product removal restores LG and cleans owned startup/registration state,
retaining required recovery evidence and interpreter bindings.

Current verified installations share records/profiles with cytv without reinstall.
Unknown older infrastructure still needs matching diagnosis/migration review.
The [candidate setup guide](../docs/INSTALL.md#candidate-on-tv-root-installation)
and [physical acceptance record](../docs/development/HOMEBREW-INSTALL-ACCEPTANCE.md)
are separate from the historical C3 results above.

## Computer-assisted bootstrap

Existing root SSH, Homebrew services, TV Node.js 8+ and suitable Python 3.9+ are
required. Supplying Python does not supply root, Node.js or compatible webOS APIs.
Unrooted TVs use computer updates. A legacy Home-only OTA cannot install the new
supervisor or managed-runtime infrastructure.

For a fresh setup, install the complete matching Root edition with LG Home selected. The cytv
installation prepares Root Updater before enabling Home. Preparing the independent
System Updater is a separate explicit action from a trusted computer:

```sh
cytv enable-system-updates --edition root
```

Use the saved TV connection, or supply `--host` and the existing root credentials.
For an existing Root installation with a retained Root Updater, first inspect its
status, transaction and matching recovery flow. Generic cytv reinstallation is
deliberately refused while that updater remains; these fresh-setup commands do
not provide a migration shortcut. Follow the [existing-TV checkpoint](../docs/UPDATES.md#one-time-computer-preparation)
and review the infrastructure transition before replacing anything. A standalone launcher update does not install the supervisor.
For the No-root edition on an already rooted TV, use the manual supervisor
command below with `--edition no-root` and an existing root SSH alias. The cytv
No-root connection logs in as `prisoner`; changing its port does not grant root.
Developer Mode access alone is insufficient. This captures the actual
installed baseline and provisions the supervisor. Existing supervisor state,
conflicting legacy transactions, uncertain package outcomes and unsupported
infrastructure stop setup; retain their evidence rather than deleting it.

When suitable TV Python is missing, this setup can provision the separate pinned
ARMv7 runtime over SSH on an eligible TV. Working system interpreters skip it.
See [Python delivery and limits](../docs/OPTIONAL-PYTHON.md), including cache
preparation with `cytv --prepare-python-runtime`. Maintenance commands never
download another interpreter.

For a fresh manual Root installation, build fresh output directories. These
commands do not migrate an existing retained updater:

```sh
python3 root-edition/build.py --version 0.4.0 --output build/root-candidate
python3 root-edition/build_updater.py --output build/root-updater
export CYTV_OPERATION=$(python3 -c 'import uuid; print(uuid.uuid4().hex)')
python3 root-edition/setup_updater.py --bundle build/root-updater --baseline build/root-candidate --ssh my-tv --apply --operation "$CYTV_OPERATION"
# Repeat this read-only status command until state=complete AND current=true.
python3 build/root-candidate/setup.py status --ssh my-tv --bundle build/root-candidate --updater-bundle build/root-updater --operation "$CYTV_OPERATION"
# Only after that verified completion:
python3 system-updater/build.py --output build/system-updater
python3 system-updater/setup.py --bundle build/system-updater --edition root --ssh my-tv --apply
```

`--apply` returns after submitting a detached worker; successful shell exit is
not setup completion. Keep the original operation UUID and repeat only the shared
status command above. `pending` means wait and inspect again; `recovery_required`,
`conflict`, or `current: false` stops the sequence for diagnosis/recovery. Do not
run supervisor setup or enable Home until `state: complete` and `current: true`.
Never repeat installation automatically or generate a new UUID to escape a pending request.

These are **unreleased source** commands: normal `setup_updater.py --apply` now
submits the same shared Root + Root Updater request as `setup.py install` with
`--updater-bundle`; do not run both for a fresh installation. The baseline must
match the reviewed Root bundle exactly. `--component-only` is an advanced
component/recovery bootstrap (`--component-only --resume` explicitly continues
a known retained Root Updater bootstrap), not normal product setup or an old-infrastructure
migration shortcut. Published tagged bundles retain their own matching procedure.
Keep the whole bundles together; see [manual source setup](../docs/MANUAL_INSTALL.md#7-root-first-installation-checks-and-persistent-activation). The
manual supervisor command defaults to `/usr/bin/python3`; `--python` accepts only
approved system/managed interpreter paths. Use the verified installed binding
when managed Python is required. It does not download Python itself. Omitting
`--apply` prints a setup plan without changing the TV. OpenSSH uses strict host
checking and batch authentication with an explicit alias such as `my-tv`.

For a known interrupted standalone supervisor bootstrap, `system-updater/setup.py
--resume` explicitly uses the retained baseline and exact package evidence, for
either edition. Keep the same bundle and edition; an unknown submitted outcome
is refused. This is recovery, not a retry that submits packages blindly.

The supervisor's private state is `/var/lib/clean-your-tv-system-updater`; its
normal-boot worker uses `52-clean-your-tv-system-updater`. Root Updater retains
its independent recovery role and interpreter binding. Never replace private
code, cached baselines or state files to bypass a setup failure.

If Root immediately shows `Denied methods call status` after supervisor bootstrap, close and reopen **Home Root** once to restart the GUI, then check Software updates again. If it persists, retain diagnostics and recovery state.

## Update on the TV

Open **Home → Settings → Software updates**, review the offered release and
confirm installation. The supervisor verifies the complete signed set, compatible
contracts and all cached rollback components before replacing anything. It
preserves the profile and suspends Home routing while installation is in progress.
Keep the TV powered on.

Startup health and profile readiness are confirmed automatically. Previously
enabled Home control resumes only through guarded activation when its saved
preference and recovery state still permit it. Explicit/emergency off, failsafe,
a changed boot or uncertain activation keeps it off. There is no Keep countdown.
An update does not grant permission to enable a previously disabled preference.

Downgrades, incomplete sets, conflicting installers, missing rollback material
and unknown install outcomes are refused. A successful installer run does not
validate remote buttons, cold boot, firmware APIs or recovery on another model.

## Failure and recovery

Open the separate **Root Updater** application if Home cannot open, or use
**Software updates → Recovery**. The supervisor owns the transaction and its
complete rollback set. Confirming rollback restores the saved components and
pre-update profile; later settings changes can be lost. Availability depends on
verified retained transaction evidence. Do not substitute an app-only old IPK.

Run `cytv status` after an interruption. Unknown package outcomes remain blocked;
installed-version readback or an idle installer does not reconstruct a missing
terminal receipt. Automatic recovery is bounded; an uncertain activation is not
replayed. Preserve journals, baselines and interpreter slots for investigation.
Use `cytv doctor --report` for issue-ready diagnostics and `cytv restore` to
request routing recovery. These commands do not provision a missing runtime.
For removal, use cytv's verified uninstall flow; an ambiguous removal is not
submitted twice automatically. See [CLI recovery](../docs/CLI.md#interrupted-operations).

## Release preparation and validation

Follow [the release process](../docs/RELEASE-PROCESS.md) and the
[1.1.0 release scope](../docs/RELEASE-1.1.0.md). Legacy `root-update.json`
application metadata alone does not describe a complete system release set.
The fixed supervisor remains separate from the components it installs.

Remaining physical-hardware validation for the published release includes:
first bootstrap and caller permissions, complete upgrade and explicit rollback,
profile preservation, startup/remote input, normal and cold boot, failsafe and
interruptions around terminal installer evidence. Helper 0.6.19 needs its own
rollback approval; approval of 0.6.18 is insufficient. QEMU and automated tests
cannot establish TV acceptance. Issue #37's UK6540PTD / firmware 05.50.70 remains
unvalidated for the managed runtime; issue #24's unfinished removal is not claimed
resolved by the Android receipt fix.


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
