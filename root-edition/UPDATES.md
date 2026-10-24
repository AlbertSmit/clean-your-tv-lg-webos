# Root software updates and recovery

Root Settings → Software updates checks the separate signed `root-update.json`
release feed. Ordinary Home's updater cannot install Root Edition. This
implementation has local automated coverage and an isolated TV validation of
Settings update, automatic timeout rollback and profile preservation on an LG C3.
See the [hardware record](../docs/development/ROOT-UPDATES-TV-VALIDATION.md) for
the tested commit, isolation and remaining release gates.

## One-time setup

The `cytv` installer now performs this setup automatically before enabling Root
Home, including rollback verification and a service check. The commands below
are for manual installations that do not use `cytv`.

Root Updater is independent of Root Home. A computer is needed once to install
its service, seed the rollback package and register its boot recovery worker.
After setup, compatible Root application releases update from Settings.

First install an updater-compatible Root bundle using [ROLLOUT](ROLLOUT.md),
with Root mode disabled. Keep that exact bundle as the rollback baseline:

```sh
python3 root-edition/build.py --version 0.1.6 --output build/root-candidate
python3 root-edition/build_updater.py --output build/root-updater
python3 root-edition/setup_updater.py --bundle build/root-updater --baseline build/root-candidate
```

The last command only prints the setup plan. After installing the matching Root
bundle and verifying root SSH access, apply it explicitly:

```sh
python3 root-edition/setup_updater.py --bundle build/root-updater --baseline build/root-candidate --ssh my-tv --apply
```

The distributed equivalent is `build/root-updater/setup-updater.py` with the
same arguments. Keep the entire updater directory together. SSH uses strict
host-key checking. Setup refuses existing updater state, foreign permission
files, an active Root route, or a baseline that differs from the installed
version. It does not replace a live recovery runtime.

Legacy Root installations without `runtime/update_guard.py` need a supervised
host migration to the new Root infrastructure first. Setup deliberately stops
there. Restore LG routing, retain the existing Root data and recovery evidence,
and follow the removal/replacement review in ROLLOUT; do not overwrite an active
runtime or delete retained state to bypass checks. This is not an unattended
upgrade path for legacy preview infrastructure. Installation from the ordinary
Home profile only migrates its validated packaged data, not arbitrary browser
storage from a legacy Root installation.

Private updater code and state live in `/var/lib/clean-your-tv-root-updater`.
The scoped LS2 registration points to that independent root-owned code; replacing
Root Home does not replace the updater. `51-clean-your-tv-root-updater` starts
journal reconciliation at normal boot. Setup retains evidence after an unknown
result; never rerun it blindly.

## Update on the TV

1. Open Root Home → Settings → Software updates. The check runs automatically.
   The available version and notes appear only for the installed version or newer.
2. Review the version and notes, then select Update → Install update.
3. The updater saves apps, embedded icons, inputs, configuration and tile order.
   It caches and verifies both new and previous packages before replacing Home.
4. LG Home is selected while the independent worker installs. Keep the TV on.
5. The new Root Home restores the profile before rendering and checks the visible
   application tiles. It acknowledges successful startup automatically; no
   post-install confirmation button is required. Failed readiness still rolls back.
6. To enable Root routing again, use **Home settings → Change Home** (turn it on).
   This enables persistent Home control after the recovery checks; no trial or
   Keep confirmation is required. Successful update verification itself does not enable routing.

Bounds: 200 apps, 100 inputs, 4 MiB UTF-8 profile JSON, 256 KiB embedded icon URI
per app, 32 MiB IPK and 64 MiB expanded payload. An unreadable saved profile,
missing icon, malformed order, failed disk write or missing rollback package
stops replacement. Third-party applications are not installed or removed.

Saved data belongs to Root, independently of ordinary Home. Completed transaction
snapshots apply once per transaction and restored version; subsequent local tile
order changes are retained. Browser storage erased later can recover the last
transaction snapshot, which does not include edits made after that snapshot.

## Failure and recovery

A verified completed installation followed by a payload or launch-confirmation
failure permits one rollback to the verified cached prior package. Restored Home must also
acknowledge profile restoration and tile rendering before `rolled-back` is
reported. Failed rollback or absent readiness keeps recovery evidence and LG
Home; it does not start a retry loop.

The current TV adapter recognizes only the independently matched successful
installer event (`statusValue=30` without errors). It does not yet have a
hardware-validated classifier for terminal installation failure events. Raw
installer errors therefore stay blocked as an unknown outcome, even if an error
message says installation failed. The core's definite-failure rollback branch
is tested, but must not be advertised as a firmware failure classifier. Add
that classifier only after capturing and validating terminal failure evidence
on the isolated target; never guess status codes from an error envelope.

Open the separate **Root Updater** application even if Root Home is broken.
In Root Home, **Software updates → Recovery** opens a separate recovery screen.
It shows the saved transaction’s rollback version, or explains why rollback is
unavailable. **Refresh status** restarts reconciliation; opening the screen alone
only reads status. Back returns to Software updates and restores remote focus.
The rollback confirmation names the exact saved version. Confirmed updates cannot
be rolled back through this recovery flow.

Roll back is offered only when the
original install has durable terminal evidence and rollback has not started.
An interrupted installer with unknown outcome remains blocked. Reading the
installed version or seeing an idle installer is not proof of completion;
the current worker cannot reconstruct lost historical terminal events. Such
cases require maintainer inspection through root SSH, not a clear-lock action.

Root enable/trial/confirmation is blocked while an update owns routing. Explicit
exit and emergency recovery remain available. The ordinary Home helper and
Developer Mode renewal are not enabled by this updater.

## Release preparation

Root releases use separate metadata, even when they share a repository release
tag with ordinary Home. Build, inspect and test the exact artifacts first:

```sh
bash scripts/test.sh
python3 root-edition/build.py --version 0.1.6 --output build/root-0.1.6
python3 root-edition/update_manifest.py --bundle build/root-0.1.6 --release v0.10.5 --notes 'Root application improvements' --output build/root-update.manifest.json
node scripts/sign-root-update.cjs build/root-update.manifest.json /absolute/path/to/release-private.pem build/root-update.json
```

The signing command requires an explicitly supplied private key and checks the
result against the repository's existing release public key. It creates a new
file and never publishes. No private key is included in either bundle. Publish
only after approval and isolated hardware acceptance. Root metadata pins exact
application identity, version, runtime/updater/profile contracts, IPK size and
SHA-256. Unknown contracts require a computer-assisted infrastructure upgrade.

Recovery runtime and updater infrastructure remain pinned. Ordinary updates
replace only the Root application package; the worker verifies/reasserts the
previously owned recovery service registration after package installation.
Registration drift is a recovery error, not permission to overwrite foreign
files. LS2 role/API configuration follows the existing Root provisioner and
[webOS LS2 security configuration](https://www.webosose.org/docs/guides/development/configuration-files/security-guide/);
OSE documentation alone does not establish TV firmware compatibility.

## Isolated TV acceptance

Before a public release, test on a separate controlled Root installation:

- First setup and effective root service identity; reject an unrelated caller.
- Upgrade between two signed versioned packages with a populated app/input
  inventory, custom config and reordered tiles; verify after restart.
- Withhold first-launch readiness and verify exactly one rollback, restored
  data readiness, LG routing and no old helper activation.
- Kill the web UI and worker separately around submission, terminal receipt,
  verification and rollback. Confirm no overlapping installation.
- Reboot with a pending transaction. Unknown install outcomes must stay blocked;
  known completed install/rollback must resume launch verification.
- Verify boot hooks, LS2 permissions, emergency recovery and updater availability
  after package replacement on the actual supported firmware.

Automated tests and deterministic offline builds are not TV acceptance evidence.

## Publish without a stale Root feed

CI builds installer binaries; it does not sign the Root update feed. A release
is not OTA-ready merely because its installer builds passed.

For a new Root application version, generate `root-update.json` from the exact
verified release bundle with `root-edition/update_manifest.py` and
`scripts/sign-root-update.cjs`. Keep the signing key local. Upload the standalone
IPK before the feed, and include the changed assets in `BUILD-INFO.json` and
`SHA256SUMS`. A later installer-only release may carry forward the signed feed
only while its Root version still matches. Recovery infrastructure is not
updated by an application-only package.

Publish a prepared draft through the checked entry point:

```sh
node scripts/publish-release.cjs vX.Y.Z --check-only
node scripts/publish-release.cjs vX.Y.Z
```

This downloads both edition feeds and build metadata, checks Root/Home versions
and the Helper requirement, verifies signatures, and downloads the referenced
Root, Home and No-root rollback IPKs to check their hashes. It
refuses to publish on a stale feed, invalid signature or missing/wrong package.
The `Release update feed` GitHub workflow repeats this check after publication
or a release edit; it can also be dispatched manually. Publishing directly with
`gh release edit` bypasses the pre-publication guard, so use the command above.
Fully unattended signing would additionally require securely provisioning the
private signing key to a protected CI environment; it has not been uploaded.
