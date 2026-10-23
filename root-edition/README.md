# Root Edition

**Native Home and Back routing, with an on-TV emergency exit.** Root Edition
uses the same launcher interface as No-root Edition, but registers a separate
application as the system Home. No router script, USB drive or always-on computer
is needed after setup. A computer is needed for installation and recovery tools.

**Root Stable 0.1.0** is scoped to **LG OLED55C3RLA / firmware 43.21.71**.
Other models and firmware are unvalidated. Cold-power testing of this exact bundle
is deferred; one initial second-attempt emergency-gesture report remains unexplained,
although instrumented repeats passed. Read the [release scope](ROOT-STABLE-0.1.0.md).
Keep the working No-root installation and recovery backups.

[Install and activate](ROLLOUT.md) · [Compare editions](../docs/EDITIONS.md) ·
[Acceptance](RELEASE-ACCEPTANCE.md) · [Recovery design](RECOVERY.md)

## What works on the tested setup

- Short **Home** selects our launcher through system routing, without the old
  interception helper running.
- Confirmed **Back** exit returns to our launcher without an observed LG flash.
  In-app navigation and exit confirmation remain under the application's control.
- **Keep Root mode** promotes a protected 60-second trial to permanent intent.
- Normal software reboot restores routing safely, then reactivates after the
  normal-boot checks and fresh input/guardian health checks pass.
- **Three short Home presses within two seconds** request emergency restoration
  independently of the web interface. Release Home between presses; do not hold it.
- **Settings → Exit Root mode → Confirm exit** restores the original Home routing.
- Two independent health checks and recovery state protect the system route.
  An unconfirmed trial automatically restores it after 60 seconds.

The original launcher, helper and their data are separate. Root exit disables
Root autostart; it does not remove root, uninstall apps or resume the old helper.
To return to No-root, restore first and then explicitly resume Home Helper from
the ordinary launcher. Never run both modes' input handling together.

## Requirements and limits

An already rooted TV, working root SSH access with a verified host key, Python 3
on the TV, Homebrew services and the supported ARM32 Magic Remote input interface
are required. Installation checks fail closed for unexpected state. A doctor
report alone does not establish compatibility.

The installer does not root your TV, change Developer Mode or flash firmware.
See the [upstream rooting overview](https://www.webosbrew.org/rooting/) separately.
Do not install Developer Mode over an existing root setup for this guide.

The public bundle contains no personal app list. Installation can copy validated
profile data from an existing Home installation without modifying it. It does not
migrate arbitrary browser storage. The Root candidate excludes the production
updater and Developer Mode renewal UI; use its separate installation procedure.

Early boot black screens, faster boot artwork, system-library patches and
removing system advertisements are **not** delivered by this edition. Long Home
is not its emergency gesture and can invoke LG behavior such as magnification.

For exact evidence and outstanding tests, read [release acceptance](RELEASE-ACCEPTANCE.md).
Historical research is retained in [STATUS.md](STATUS.md); older RC limitations
are not the current usage instructions.
