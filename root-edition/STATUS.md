# Root Edition status and evidence

Updated 2026-10-23. Test device: **LG OLED55C3RLA / firmware 43.21.71**.
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

## Earlier registration failure and subsequent isolated success

The production Home 1.1.0 manifest does not declare `appCategory: ["home"]`.
System profile and settings readback accepted its ID, but pressing Home caused
SAM `launchDefaultApp` to return **“no default app is set for the category”**.
The diagnostic candidate did declare the category. This is a prerequisite to
investigate, not proof that adding the field alone completes integration.

The production test was rolled back. The user confirmed normal Home and controls
worked. Production launcher metadata and startup configuration were not changed.
Native Back without a flash is **not yet established for an in-place production upgrade**.

A subsequent 60-second trial used the real launcher UI under an isolated diagnostic
ID with the Home category declared. The user confirmed short Home, arrows/OK and
confirmed Back return without an observed LG flash while the helper was stopped.
The independent timer restored routing, the helper resumed and the original
diagnostic package was restored. This does not validate persistent installation
or migration of the production app’s browser storage.

A physical long-Home test triggered emergency recovery and restored the working
setup, but also activated LG screen magnification. The user dismissed it with
Back. A clean long-Home escape is therefore still a release blocker. The local
library callback experiment is not installed and is not part of the preview.

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
The separate candidate builder includes an installer and recovery runtime for
supervised hardware tests. It does not enable permanent routing. No Root Edition
IPK is produced by the standard No-root build.

## Release preparation

The [rollout plan](ROLLOUT.md) separates verified isolated routing from remaining
persistent-installation gates. `preview.py` stages a sanitized UI under a new ID
from public source files, with per-file hashes and no services or activation hooks.
Five offline tests cover isolation, private-file exclusion, indirect-source
rejection, reproducibility and refusing to overwrite existing output.

## Current installable candidate

The separate `com.cleanyourtv.root.preview` package now includes a recovery-only
service, host installer, persisted installation journal and bounded routing runtime.
Local tests cover these components. An installed candidate with audited recovery corrections has passed bounded routing
and software-reboot recovery on the test TV. A clean install of the final bundle
still requires acceptance. Persistent enable/confirm are deliberately blocked.

Unlike earlier lab trials, this candidate does not automatically resume the legacy
helper: stopping it sets the same latch as the user's emergency exit. The user must
stop it explicitly before a trial and explicitly resume it after rollback. No
production helper protocol or system library is modified. See [rollout](ROLLOUT.md).

## Integrated recovery preparation — 2026-10-23

Merged main `b182393` (v0.8.1 signed-update fixes). On the C3, the initial candidate
failed closed before Home activation because packaged data and the Homebrew runner
had desktop/world-writable permissions. The recovery service now executes from
private root-owned state using the firmware's Node bootstrap. Homebrew is unchanged.

Activity registration is performed by the root installer with a fixed sender,
not by granting the web service broad management rights. This firmware requires
the compatible ActivityManager URI and explicit list flags; `current:false`
is essential to inspect the stored definition rather than live trigger results.
The owned task and recovery integrity passed readback. All three Home destinations
remained LG; no routing trial ran during this preparation. Boot/failsafe delivery
of the final candidate remains a separate hardware acceptance gate.

## Integrated routing and reboot recovery — 2026-10-23

With the legacy helper explicitly stopped, the isolated real-UI candidate passed
short Home, arrows/OK and confirmed Kinopoisk Back exit without an observed LG
flash. The independent 60-second guardian restored all three original routing
values. The user explicitly resumed the production helper and confirmed controls.

A second trial was interrupted by an acknowledged software reboot. At post-boot
uptime 36 seconds, its journal was already restored, all three Home destinations
were stock, and recovery integrity verified. No manual restore was invoked.
The persistent recovery activity retained its expected creator, callback, trigger
and type. The old guardian's monotonic deadline was still over 3,100 seconds;
this was boot recovery, not expiry of the old timer.

The kernel boot ID did not change on this device despite the uptime reset. Do not
use boot ID alone to classify restarts on this firmware.

After recovery, the user reported a black screen and then returned to production
Home with the Home button. Logs showed Live TV foreground before that press;
production Home and the legacy helper were active afterward. This visual transition
is deferred, not fixed, and does not invalidate the routing restoration readback.

These results apply to the installed candidate with audited corrections through
RC5, not a pristine RC5 installation. They do not establish permanent startup,
power-loss recovery or failsafe delivery for this exact deployment. Persistent
activation remains locked. See [release acceptance](RELEASE-ACCEPTANCE.md).
