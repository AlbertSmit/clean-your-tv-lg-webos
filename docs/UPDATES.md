# In-app updates (development)

This draft adds signed Home updates and recovery. It is not in the released v0.7.1. The isolated update/rollback path passed on an LG OLED55C3RLA with firmware 43.21.71; production permission setup across reboot remains a release gate. Do not install these development packages over a working installation as a stable upgrade.

## What users get

Home Settings → Software updates → Check for updates shows installed and available Home versions. The separate **Home Updater** app owns the backup and recovery journal. Installation requires root, Homebrew Channel and the scoped LS2 permission setup below. The no-root launcher remains supported with computer-assisted updates; checking releases through this updater also depends on access to Homebrew's metadata API and is not promised on an unrooted TV.

Developer Mode renewal Beta is paused automatically before installation and its prior preference is restored after verified success or rollback. Users do not have to disable it manually. Helper code, emergency-stop markers, autostart configuration and system Home profiles are not changed.

The first upgrade to Home 1.2.0 requires a personalized package using the existing sync/build flow. Subsequent in-app updates require an installed Home version at least 1.2.0 and a signed matching previous package. Never install an empty generic package over a pre-1.2.0 installation expecting migration.

## Preserved data

Home captures the app inventory, embedded icons, input labels, configuration, tile order and renewal diagnostic history. It saves a local copy and then an independent updater backup before installation. The transaction's renewal receipt, not diagnostic history, controls restoration of the enabled preference. Missing icons, invalid profiles and storage failures stop installation.

The new Home loads its saved profile before rendering, or restores the independent backup when local data is absent. A damaged local profile is not silently replaced. Current bounds are 200 apps, 100 inputs, 256 KiB per icon and 4 MiB profile JSON; maximum-sized profiles have not been validated on hardware. A personalized rebuild is not an inventory reset once a saved profile exists.

## Recovery

Open Home Updater to inspect the transaction or restore the signed previous Home package. Recovery checks root, helper compatibility, manifest signature and package hash. The previous package must remain downloadable; this is not an offline recovery image or a full TV backup.

Homebrew does not distinguish transport failures from terminal installer failures in its error envelope. A failed installation call therefore stays in recovery; it does not automatically start another install. Timeouts and interrupted installation remain blocked in `recovery-required`; reading a version is not proof that an installer has stopped. There is no clear-lock-and-retry button. A confirmed install waits for the populated Home grid on launch before restoring renewal. This is a startup signal, not a complete UI health test.

The service fetches and verifies metadata again at confirmation so idle shutdown between Check and Confirm does not lose the offer. A changed offered version requires a new confirmation. Installation uses a subscription and waits for Homebrew's terminal `finished` reply; progress messages are not success.

## Scoped permission setup (maintainer procedure)

The package alone does not grant cross-package permissions. Build `scripts/build-updater.sh`; its `dist/updater-setup/` directory contains the CLI and its dependencies. Transfer that directory intact to a temporary directory on an already-rooted TV. From that directory, as root:

```sh
node scripts/update-permissions.cjs plan production
node scripts/update-permissions.cjs apply production
```

Review the plan before applying it. It creates only dedicated API/client permission files and a permission-only manifest under `/var/luna-service2-dev`, plus an ownership receipt. It does not edit Homebrew's manifest or grant `all`, `public`, shell access or system Home/profile permissions. Only named methods are exposed. Bus identity checks remain enforced by the updater and renewal service.

The CLI rejects filename collisions, symlink paths and changed owned files. Writes are staged, synchronized and installed without overwriting existing files; the manifest is last. A bounded `ls-control scan-services` refresh follows. `installed` means files were applied and scanning completed, **not** that every running provider has adopted the grants.

On the tested TV, an already-running Homebrew JS service needed re-registration before the new permissions worked. Do not kill processes by a broad name match or restart SSH/dropbear. Confirm the exact service identity and that no installer operation is active before a targeted service restart. This procedure is not yet an automated user-facing installer. A transient `Message not processed` was also observed on a first read; never turn that into automatic retries of installation.

Remove with the same LS2 root. This version also recognizes the previous exact-service client plan; it does not accept arbitrary paths from a receipt. To upgrade those permissions, remove the old plan first, then apply the new one:

```sh
node scripts/update-permissions.cjs remove production
```

Removal deletes only files matching the receipt, removes the manifest first and refreshes LS2. Changed files or stale lock/staging files require inspection, not deletion by guesswork. After removal verify that cross-package calls are denied; cached permissions may require provider re-registration. The lab's post-removal check was rejected.

`/var/luna-service2-dev` persistence through reboot and permission retention across all service lifecycles still need a defined production setup path. Do not silently add a boot hook, change the root to `/var/luna-service2`, or claim reboot-safe setup from this test. The alternative root is accepted by the CLI but was not tested here. These are release gates, not changes to the working no-root installation.

## Build, signing and release checklist

```sh
scripts/test.sh
scripts/build.sh
scripts/build-updater.sh
```

The updater package is `com.cleanyourtv.updater_0.1.0_all.ipk`. Its service creates private state with its actual runtime UID (directory 0700, files 0600); no fixed UID is packaged. Earlier prototypes with incorrectly owned state require explicit migration.

The feed is `https://github.com/Razdva122/clean-your-tv-lg-webos/releases/latest/download/update.json`. Requests are user-triggered. The HTTPS reader restricts redirects to this project's release assets and GitHub's asset CDN. RSA-SHA256 metadata is verified against the packaged `updater-service/release-public.pem`; it fixes the package URL, Home version, exact helper requirement and SHA-256. Homebrew checks the downloaded hash.

Example manifest input:

```json
{"schema":1,"release":"v0.8.0","home":"1.2.0","helper":"0.6.13","url":"https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/v0.8.0/com.gathin.tvhome_1.2.0_all.ipk","sha256":"<actual 64-character lowercase SHA-256>","notes":"Release notes"}
```

Sign reviewed metadata using an explicitly supplied private key kept outside the repository:

```sh
node scripts/sign-update.cjs manifest.json /secure/path/private.pem update.json previous-update.json
```

The signer validates the result against the pinned public key and validates the previous envelope. One previous descriptor supports only its exact installed version; other older versions need manual updates. Every future stable release, even tooling-only releases, must retain usable signed metadata.

Before publishing:

- Resolve production permission activation and reboot behavior; do not present the lab setup as a finished consumer installer.
- Build public packages from clean sources, never personalized/live-TV backups. Exclude lab identifiers, loopback URLs, fake LG adapters, test keys and runtime state.
- Compute hashes from the final IPKs; sign with the real pinned key. Verify the candidate and previous IPK version, helper requirement, URLs and hashes against both signed descriptors.
- Keep the previous package downloadable. Test the public asset URLs before making the release latest. Do not publish the lab's signed envelopes to the stable feed.
- Include updater setup files, install/removal instructions, bootstrap limitations and recovery instructions. Publishing metadata and changing the stable feed are separate from merging this PR.

## Validation and limits

On 2026-10-22, the corrected service completed a user-triggered isolated 1.2.0 → 1.2.1 update, restored the enabled renewal preference, and rolled back to 1.2.0 automatically. The user confirmed the preserved test tile, remote navigation and working production Home afterwards. Scoped permissions were removed and the temporary server stopped; production package metadata and helper processes matched the baseline.

An earlier attempt required manual journal recovery after the terminal installer reply was lost. It is not counted as unattended success. The subscription fix was then tested with a fresh transaction, without manual recovery. See [the detailed lab record](development/UPDATE-LAB-RUNBOOK.md).

The lab used fake LG responses/scheduling, an ephemeral signing key, loopback package delivery and a rooted TV. It does not prove real LG renewal, unrooted installation, maximum profile sizes, power-loss recovery, production permission persistence or public GitHub delivery. Local tests cover signature/policy checks, transaction failures, erased service state, manual preference overrides, service restart between UI actions and remote navigation. No new feature work is required for this PR.
