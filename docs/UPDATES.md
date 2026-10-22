# In-app updates (development)

This implementation is not in the released v0.7.1. Do not replace a working installation with these development packages before isolated hardware validation.

## User flow

Home Settings → Software updates → Check for updates shows installed and signed available Home versions. Release tags and application versions are separate: a setup-only release does not require reinstalling Home.

An independent **Home Updater** application and service must be installed once. Without root it can check releases, but installation remains a computer-assisted task. Root installations use Homebrew Channel's installation service. Unknown root capability, missing signatures, missing recovery packages and incompatible helper versions disable installation.

Before updating, disable Developer Mode renewal Beta. The updater refuses an enabled or unavailable renewal status. Disabled renewal diagnostics are included in the portable profile; restoring them does not enable renewal or schedule checks. Helper code, stop markers, autostart configuration and system Home profiles are never modified.

The first upgrade to Home 1.2.0 requires a personalized package using the existing sync/build flow. Subsequent in-app updates require an installed Home version at least 1.2.0 and a signed previous package that supports portable profiles. Do not install an empty generic package over a pre-1.2.0 installation expecting automatic migration.

## Preserved data

Before installation, Home captures the app inventory, embedded icon bytes, input labels, configuration, tile order and disabled renewal history. It first saves the profile locally, then the independent updater persists a private copy outside Home's package. Missing/unreadable icons, invalid profiles or quota/write failures stop installation. Relative icon files are converted to embedded PNG/JPEG/WebP; remote arbitrary icon URLs are rejected.

On a generic upgrade, Home loads the local profile before rendering; if it is absent, it requests the updater's backup. The backup restores captured ordering; an existing live ordering takes precedence during ordinary launches. A damaged local snapshot is not silently replaced.

Current bounds: 200 apps, 100 inputs, 256 KiB per external icon, 4 MiB JSON profile. Service message size and web storage quota require hardware validation. A personalized rebuild is not an inventory-reset mechanism once a saved profile exists; inventory editing/reset UI is outside this change.

## Recovery

Home Updater is a separate package so Home installation cannot intentionally replace its process or journal. It stores the prior signed package descriptor and transaction before invoking Homebrew Channel. A definite rejected installation gets one attempt to install the prior package. A confirmed installed update waits for a populated Home grid on first launch; this is a startup signal, not a complete hardware test.

Open Home Updater to inspect the state or restore the previous Home after a confirmed installation. Recovery rechecks root and helper compatibility and verifies the stored manifest signature. The previous package must still be downloadable; this is not an offline recovery image or a full TV backup.

Timeouts, service interruption and interrupted rollback remain `recovery-required`. A version read alone is not evidence that an installer has stopped. The app does not start another install in that state. Inspect the installer and journal before manual recovery; there is deliberately no “clear lock and retry” button. Power-loss recovery and installation service lifetime remain hardware test gates.

## Trust and publishing

The client requests `https://github.com/Razdva122/clean-your-tv-lg-webos/releases/latest/download/update.json` only when asked. The bounded HTTPS metadata reader allows only this project's GitHub release paths and GitHub asset CDN redirects. Metadata has a fixed schema and an RSA-SHA256 signature pinned to `updater-service/release-public.pem`. The signed descriptor fixes the package URL, Home version, exact helper version and SHA-256. Homebrew Channel verifies the downloaded package hash.

The private signing key is maintained separately, never inside this repository or an IPK. Preserve a secure backup; key loss requires a manually installed trust update. Do not publish development signed manifests to the stable feed.

Manifest input example:

```json
{"schema":1,"release":"v0.8.0","home":"1.2.0","helper":"0.6.13","url":"https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/v0.8.0/com.gathin.tvhome_1.2.0_all.ipk","sha256":"<actual 64-character lowercase SHA-256>","notes":"Release notes"}
```

Sign a reviewed manifest using an explicitly supplied key:

```sh
node scripts/sign-update.cjs manifest.json /secure/path/private.pem update.json previous-update.json
```

The optional previous envelope must be signed by the same trusted key. Its Home version must match the user's installed version and its helper requirement must match the installed helper. With one previous descriptor, other older versions need a manual update. Every future stable release, including tooling-only releases, must carry a signed `update.json` to keep the feed usable.

## Local build and validation

```sh
scripts/test.sh
scripts/build.sh
scripts/build-updater.sh
```

The independent package is `com.cleanyourtv.updater_0.1.0_all.ipk`. Its state directory is created by the running service with mode 0700 and its actual runtime UID; journal/profile files use 0600. The app uses bus-provided application identity and rejects unknown callers rather than accepting an identity from a payload.

Before enabling real hardware updates, verify with a disposable test package: bus identity/permissions; root/no-root detection; profile size and restart persistence; actual installer completion/error responses; closed Home and updater service survival; power interruption; prior-package rollback; renewal off and history restore; arrows, Back and Home after update. The current tests use local mocks and do not establish these hardware results.

## TV validation status (2026-10-22)

An isolated test on OLED55C3RLA, firmware 43.21.71, found two integration blockers. The stock package installer assigns a per-service UID (5132 in this run), so a state directory owned by a hard-coded prisoner UID is incorrect. The build now leaves state creation to the running service, with mode 0700. Existing deployed prototype directories need explicit migration; this change alone does not repair them.

LS2 rejected `getAppInfo` from the installed updater service. Declaring additional groups in the test `services.json` did not grant them. Cross-package access to the updater, Homebrew and renewal service needs a supported installation/permission design and device validation. No end-to-end update or rollback has passed on TV yet. Do not publish this prototype as a working TV updater. The production Home and Helper packages were not replaced.

### Requested renewal UX

The intended replacement for manual Beta disabling is a transactional pause: wait for an in-flight renewal request, persist the previous enabled state, pause scheduling, update, then restore that state after verified success or rollback. A previously disabled feature must stay disabled. Crash recovery, cancellation failure and ambiguous installation outcomes must be tested before removing the current guard. The renewal manager now implements and locally tests a durable pause/resume primitive and updater-only bus endpoints. The updater journal now records pause intent before calling the renewal service, saves the receipt, and retries terminal restoration independently of package installation. Cross-package receipt migration is implemented and tested locally, including erased package state and a later manual disable. The current manual guard remains until that integration passes failure/restart tests and TV permission validation.

### Journal integration checks

Local tests cover pause intent persisted before the RPC, no installation on an unconfirmed/mismatched pause, no renewal resume after an ambiguous install, retrying renewal restoration after service restart without installing again, and a fresh pause before rollback of a completed update. A crash before installation is reconciled by restoring renewal and marking the attempt aborted, not by silently starting installation. Completed resume IDs are persisted so a lost response cannot override a later manual disable.

The existing manual-disabled guard remains for now. If replacement removes the renewal service's pause record, the updater imports its journal receipt through the updater-only endpoint before resuming. Conflicts, malformed receipts, persistence errors and unconfirmed cancellation stay in recovery. A completed receipt is idempotent and cannot undo a later manual disable. TV migration validation and LS2 permission activation remain release blockers.
