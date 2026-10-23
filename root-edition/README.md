# Root Edition

**Native Home and Back routing, with an on-TV emergency exit.** Root Edition
uses the same launcher interface as No-root Edition, but registers a separate
application as the system Home. No router script, USB drive or always-on computer
is needed after setup. A computer is needed for installation and recovery tools.

**Root Preview:** permanent mode and software-reboot startup have been tested on
**LG OLED55C3RLA / firmware 43.21.71**. This is not a cross-model compatibility
claim or a stable release certification. Keep the working No-root installation.
Final-artifact cold-power, quick-standby and failsafe acceptance remains open.

[Install and activate](ROLLOUT.md) · [Compare editions](../docs/EDITIONS.md) ·
[Acceptance](RELEASE-ACCEPTANCE.md) · [Recovery design](RECOVERY.md)

## What works on the tested setup

- Short **Home** selects our launcher through system routing, without the old
  interception helper running.
- Confirmed **Back** exit returns to our launcher without an observed LG flash.
  In-app navigation and exit confirmation remain under the application's control.
- **Turn on Home control** enables permanent intent after automatic input and recovery checks.
- Normal software reboot restores routing safely, then reactivates after the
  normal-boot checks and fresh input/guardian health checks pass.
- **Three short Home presses within two seconds** request emergency restoration
  independently of the web interface. Release Home between presses; do not hold it.
- **Home settings → Return to LG Home → Confirm return** restores the original Home routing.
- Two independent health checks and recovery state protect the system route.
  Failed startup or a later health failure automatically restores LG Home.

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
