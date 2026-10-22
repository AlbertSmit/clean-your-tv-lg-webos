# Root Edition status and evidence

Updated 2026-10-22. Test device: **LG OLED55C3RLA / firmware 43.21.71**.
This is a record of bounded tests on one device, not a compatibility promise.

## What passed

- Native short Home opened a diagnostic Home while the normal helper was stopped.
- A paired override of `defaultApps.categories.home` and `idleApp.appId`, together
  with SAM's explicit default Home setting, routed a confirmed Kinopoisk Back exit
  to the diagnostic screen. The user observed no LG Home flash.
- SAM logs identified `closeByAppId` from system UI and `LAUNCH_LASTAPP` selecting
  the diagnostic destination. No key-interception helper was active.
- A real, temporary paired-profile override was automatically removed and all
  three original Home values read back correctly. The normal helper resumed.
- Earlier recovery-service boot tests ran in normal mode and Homebrew failsafe,
  including when ordinary `init.d` startup was unavailable. Those tests did not
  contain the final real-manifest change.
- Local file-publication tests terminated child processes at each staging
  boundary. Recovery preserved conflicting files instead of overwriting them.

## What failed, and why it matters

The production Home 1.1.0 manifest does not declare `appCategory: ["home"]`.
System profile and settings readback accepted its ID, but pressing Home caused
SAM `launchDefaultApp` to return **“no default app is set for the category”**.
The diagnostic candidate did declare the category. This is a prerequisite to
investigate, not proof that adding the field alone completes integration.

The production test was rolled back. The user confirmed normal Home and controls
worked. Production launcher metadata and startup configuration were not changed.
Native Back without a flash is **not yet established for the production launcher**.

An early test also revealed repeated boot callbacks while already running.
The lab recovery hook now defers such a callback only for a matching live,
time-bounded guardian process; failsafe still requests recovery immediately.
This corrected adapter needs real changed-manifest reboot/failsafe tests before
shipping.

## What remains before a release

- Preserve exact original manifest bytes and ownership; publish only the category
  change and verify the registered app information, not just the file contents.
- Establish a bounded cache-refresh method and its inverse without restarting
  broad system services or disturbing the existing launcher state.
- Recover manifest, registration cache, paired profiles and SAM setting together.
- Repeat short Home, confirmed Back, Cancel, in-app navigation and long-button
  behavior with the real launcher.
- Test normal reboot, fast standby/resume, cold boot, failsafe and interrupted
  installation with the real candidate.
- Provide a documented emergency escape and uninstall route that also restores
  root-mode routing; the No-root long-Home action alone is not that guarantee.

## Scope of public tools

The public doctor is read-only. The metadata planner and tests are local-only.
The device-specific lab activator is intentionally not shipped as an installer:
it depends on the test device's recovery service and contains unresolved release
gates. No Root Edition IPK is produced by the standard build.
