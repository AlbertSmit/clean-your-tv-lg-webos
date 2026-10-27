# Clean Your TV — user guide


No-root and Root are equal options for different TV setups. Choose No-root for LG Developer Mode or Root for existing root SSH access. Compatibility and test coverage remain specific to each edition.

## Before installation

This guide covers **[v1.3.0 stable](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.3.0)**. Latest-download links follow the published stable release. See the [installation guide](../INSTALL.md) and [release notes](../RELEASE-1.3.0.md).

The release contains cytv **0.4.0**, Home **1.4.2**, Home Helper **0.6.19**, Root Edition **0.4.0**, Home Updater and Root Updater **0.3.0**, Android **0.3.0-preview** (version code **11**) and System Updater supervisor **1.1.0** (protocol **1**). These are the v1.3.0 release components.

The unpublished 1.4.0 candidate selects Android 0.4.0 (code 13), without preview, after maintainer-approved emulator checks. Tested: Android 15 ARM64 / WebView 124. Physical phones and live phone-to-TV recovery remain unverified; Android 7 / WebView 108 is a minimum requirement, not a tested phone. Update without uninstalling or clearing data. Published downloads still provide 0.3.0-preview. Report problems with phone, Android/WebView, TV/firmware, edition and failed step; exclude credentials.

Known issue in 1.3.0: Root Home control can turn off after standby and return Home presses to LG. Turn Home control on again explicitly in Clean Your TV settings; if activation fails, keep LG Home and save diagnostics. See [issue #90](https://github.com/Razdva122/clean-your-tv-lg-webos/issues/90) and the [current acceptance record](../RELEASE-1.3.0-ACCEPTANCE.md).

Keep the TV on and the computer on the same trusted local network. No always-on computer is needed afterward. Compatibility depends on model, firmware and remote; Root has outstanding hardware checks.

- **No-root:** enable LG Developer Mode and Key Server. Enter the passphrase displayed on the TV and accept the separate TV pairing request. Developer Mode must remain active; expiry can remove sideloaded apps. Monitor its official timer even with Beta renewal enabled. Helper monitoring needs local networking.

The updated No-root Helper requires TV Node.js 0.12.2 or newer. The installer checks the TV runtime before installation. Older published packages do not gain this compatibility automatically; input-device access and standby/cold boot still need testing on each model.

- **Root:** existing root SSH access is required. The installer does not root the TV. Do not enable Developer Mode on an existing rooted setup. Keep root access and recovery services available.


## Developer Mode setup (No-root)

Developer Mode lets CYTV install apps on a TV without root.

1. On the TV, open LG Apps, search for Developer Mode and install it.
2. Open Developer Mode and sign in with your LG Developer account. Create an account at webostv.developer.lge.com if needed.
3. Turn on Dev Mode Status. The TV restarts. Open Developer Mode again.
4. Turn on Key Server and leave Developer Mode open. Its IP Address is the TV address to enter in CYTV.
5. Enter Passphrase: the six characters shown in Developer Mode on the TV. Match uppercase and lowercase letters.

Use the code from the TV, not your LG account password. If no code is visible, turn on Key Server.

Pairing is a separate step: when the TV asks, approve CYTV with your remote.

Keep Developer Mode active: open it before the timer runs out and press EXTEND while the TV is online. If it expires, LG can remove these apps.

Home is your app screen. Home Helper makes the Home button open it.

After installation, press Home to try it. If LG Home opens, open Home Helper from the TV's apps. Three short Home presses within two seconds return to LG Home. To restart Home control, open Home Helper, choose Start Helper and confirm. Your saved Home screen choice is kept.

Desktop CYTV shows preparation one step at a time. Details opens the operation log. LG example images can be enlarged; use the code from your own TV.

[LG Developer Mode](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)

## Optional Python for Root in v1.1.0

Root needs a working Python **3.9+** on the TV. The installer checks the required modules (including `json` and `fcntl`), locking, filesystem and subprocess operations; the version number alone is insufficient. A suitable existing interpreter avoids the extra download. Otherwise setup downloads verified **CPython 3.13.17 for ARMv7 soft-float** on the computer or Android device, then transfers it over trusted SSH; the TV does not need Internet access. This optional archive is not bundled in ordinary installers: about **26.3 MB** downloaded, **51.5 MB** for normalized SSH transfer and **119.3 MB** installed, with **320 MiB** free required for initial staging. The private runtime does not replace system Python, libc or global PATH.

The runtime still needs a compatible loader and libraries. Root SSH, Node.js **8+**, `luna-send` and the webOS application/service directories remain required; No-root Helper needs Node.js **0.12.2+**. LG UK6540PTD / firmware 05.50.70 / ARM32 (issue #37, Python 2.7.12 with no Python 3) has **not** passed hardware acceptance with this runtime. QEMU tests do not establish TV, cold-boot, remote-input or rollback compatibility. Historical hardware results apply only to their recorded model, firmware and artifacts.

To prepare a verified cache on an Internet-connected computer **without contacting a TV**:

```sh
./cytv --language en --prepare-python-runtime
```

Use the same private data directory for setup; when moving a cache, prepare a fresh dedicated directory with `--data-dir /path/to/private-data` and use that option for both commands. Do not copy normal SSH keys or profiles into a shared cache. Status, diagnostics, restore and removal do not download Python automatically. Retain runtime slots referenced by installed updaters or recovery. See [Python details](../OPTIONAL-PYTHON.md).

## Install and select a language

- **Windows x64:** Download `cytv-windows-x64-desktop.zip`, choose **Extract All** in File Explorer, then open `cytv-desktop/cytv-desktop.exe`. Keep the `_internal` folder beside it. Windows publisher signing is not configured. The separate console is `cytv-windows-x64.exe`; rename it to `cytv.exe` and use `.\cytv.exe` in PowerShell for the commands below.
- **macOS 13+:** extract `cytv-macos-arm64.zip` (Apple Silicon) or `cytv-macos-x64.zip` (Intel), move `cytv.app` into Applications and open it. Allow Local Network access. If blocked, use Privacy & Security → Open Anyway only for a trusted project download; do not disable Gatekeeper. Older-system acceptance is not established.
- **Linux x64:** on Ubuntu 22.04+, Debian 12+ or Mint 21+, open `cytv-linux-x64.deb` in the graphical package installer, install, then open Clean Your TV from the applications menu. Desktop libraries may require Internet access. Linux ARM is not included. The standalone `cytv-linux-x64` executable is the CLI; use the `.deb` for the graphical app.

[Android installer](../../android/README.md): all twelve interface languages are available. The top-right control shows the current language; tap it to choose another. Your selection is saved on the phone.

Android status and recovery keep the selected action visible during connection and show its own progress. Text uses the phone’s system font with larger labels and help text.

The desktop wizard selects your system language automatically; its language selector saves an explicit choice. On the TV, open **Settings → Language** and select a language, or the system/automatic option to follow the TV language. Installer and TV preferences are separate. The supported codes are listed in the [language index](../LANGUAGES.md).

For a separately downloaded CLI on macOS/Linux, open a terminal in its extracted directory:

```sh
chmod +x cytv
./cytv --language en install
```

Choose the TV (or enter its IP), choose the edition and review the summary. Approve first-use SSH trust only for your own TV on a trusted network; a changed saved key blocks access. Root credentials are distinct from the Developer Mode passphrase. Root installs recovery and activates Home immediately, without a trial or Keep step. Check arrows, OK, Home, Back/Cancel, volume, standby/wake and cold boot on your own TV.

If Root removal is interrupted, choose Remove again in the app. It checks the retained TV journal and package state before continuing; completed removal is not submitted again. If the previous operation is still running, wait a minute. If its outcome cannot be verified, restart the TV and check again; retain the diagnostic report for support.

## Everyday use and recovery

Arrows select tiles; OK opens them; hold OK to reorder. Short Back retains the app's navigation and exit confirmation. Short Home opens Clean Your TV while Home control is active. In new builds, hold Back for 1.2 seconds to open LG Home once. The Home-control switch and your settings remain unchanged.

**New builds: press Home three times within two seconds**, releasing between presses, to return to LG Home and stop Home control. This preserves preferences. Older No-root Helper versions through 0.6.13 instead use holding Home for about two seconds; holding Home is not the Root emergency gesture.

No-root: Three short Home presses within two seconds return to LG Home. To restart Home control, open Home Helper, choose Start Helper and confirm. Your saved Home screen choice is kept. Root: turn **Change Home** on in Home settings to resume. **Open LG Home** opens LG Home once without changing routing. To restore LG Home as the persistent destination, turn **Change Home** off or run `cytv restore`. Do not run both controllers together. If a failure repeats, leave LG Home active.

```sh
./cytv --language en status
./cytv --language en doctor --report
./cytv --language en restore
./cytv --language en uninstall
```

After interruption, run `status` before retrying; retain journals and recovery files. `restore` returns LG Home without removing apps. `uninstall` restores before removal. Root recovery state is deliberately retained; never delete it to force reinstallation. Review diagnostic reports before sharing; do not publish keys or profile folders.

## Updates and removal

Keep known-working packages and private settings backups. For computer-assisted No-root package replacement, stop Helper first and update without uninstalling, which may erase settings. Removing the desktop app does not remove TV apps. Do not replace a live Root runtime with a standalone IPK; use cytv's explicit recovery/reinstallation flow.

In v1.1.0, **Update all** in Home Settings → Software updates uses a signed release set: Home, Helper and Home Updater for No-root on a rooted TV; Root Home, Root Updater and the routing/recovery runtime for Root. This requires root, Homebrew Channel, working webOS installer services, Python 3.9+ and Node.js 8+. An unrooted TV still uses the computer installer.

For a fresh setup, use the complete stable installer to install the matching transition Home and edition-specific recovery Updater. **An existing Root installation with a retained Root Updater may deliberately block generic reinstallation.** First inspect `status`, Recovery and the existing transaction through the matching legacy recovery flow; follow the [existing-TV checkpoint](../UPDATES.md#one-time-computer-preparation). Do not delete journals or bypass this check. A legacy Home-only OTA does not install the new infrastructure.

Only after the installed components and recovery state are ready, enable **updates for all TV components** in the desktop installer. For a saved root SSH connection and the Root edition:

```sh
./cytv --language en enable-system-updates --edition root --host TV_ADDRESS
```

This separate action provisions the fixed supervisor and captures the installed component set as a rollback baseline. It requires installed Home metadata with `systemUpdateProtocol = 1`; it does not reinstall Home or change routing. Ordinary No-root edition on a rooted TV needs root SSH and the matching computer-installed components; follow the [bootstrap procedure](../UPDATES.md#one-time-computer-preparation). A legacy Home-only OTA update does **not** provision the new supervisor, Python or updater infrastructure. Once the supervisor is installed, conflicting legacy installers are disabled; do not replace packages around it.

Root 0.2.0, Root Updater 0.2.0 and supervisor 1.0.0 passed controls, triple-Home emergency exit/resume, standby/wake with Emby open for 70 seconds, installed-version menus and friendly feed-unavailable handling on OLED55C3RLA / firmware 43.21.71 / webOS 11.2.0 (`d344d92`, product contents identical to `4b66951`). True cold boot, Helper 0.6.19 on a TV, UK6540PTD and a complete signed system upgrade/rollback remain untested. Stable publication accepts this limited evidence; other models are not validated.

Technical details in English: [desktop setup](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [Installation of both editions](../INSTALL.md), [manual installation](../MANUAL_INSTALL.md), [recovery](../RECOVERY.md), [edition comparison](../EDITIONS.md).

After connecting, cytv reads the installed TV versions and shows current → bundled version for Home and Home Helper (No-root), or Root and Root Updater. Review and confirm before installation. First installs, reinstalls and downgrades are labeled separately; `--yes` skips confirmation but still prints the versions.

Software updates shows release details only for the installed version or newer. Open Recovery to see the saved rollback version or why rollback is unavailable; Back returns to updates.

No-root checks the TV shell ABI, so a 64-bit kernel with verified ARM32 userspace is accepted. If verification fails, attach the generated diagnostic JSON; do not share keys or passphrases.

Home updates require confirmation before installation; startup verification is automatic afterward. Background status refresh keeps the selected remote-control button in place.

Startup health is checked automatically in both editions; no manual health-confirmation step is required. Legacy Home-only rollback restores the previous Home package and its saved profile; System Updater rollback restores the complete previous release set. Recovery remains available after confirmation, without a time limit, until the next update. Later settings changes may be lost; rollback asks for confirmation. On-TV No-root updates and rollback still need root and Homebrew Channel. After an interruption, run `status` and inspect Recovery before continuing. An uncertain installer outcome blocks reinstallation and rollback: retain logs, journals and runtime slots, and never delete state to force a retry. Resume an interrupted cytv operation only through its checked recovery flow.

The update screen now separates versions, status and readable release notes. Up/Down reads the notes; Left/Right selects the fixed actions below. After automatic startup checks, Root restores previously enabled Home control; No-root preserves the separate Helper state. Disabled preferences and explicit or emergency off remain off.

Opening Home settings checks for updates in the background. An orange dot on Software updates means a newer version is available, including releases that require computer setup. Settings stay usable during the check.

No-root: open Home settings → Developer Mode for auto-renewal, session checks and diagnostics. The main screen keeps a brief status and any renewal errors visible. Back returns to Home settings. Both editions place Language, Software updates and TV settings in the same row; an arrow opens each item.

Opening Home Helper shows its purpose and current state. Starting a stopped Helper requires confirmation. Home Updater and Root Updater explain recovery; regular updates are in Home settings. Restore is shown only when a saved version is available and asks for confirmation before replacing Home and its settings.

If Root shows `Denied methods call status` immediately after supervisor bootstrap, close and reopen Home Root once, then check updates again. If it persists, retain diagnostics and recovery state.

1.2.0 (#51): after a TV package rejection, the diagnostic JSON retains only the operation category, bounded numeric error/status codes, an allowlisted package state and a boolean result. It excludes raw TV error text, paths and app IDs. Review the report before sharing; installation is not automatically retried, and the UN70006LA installation failure is not yet confirmed fixed.

1.2.0 (#59): if Helper status cannot be checked, **Start Helper** remains available with confirmation. Opening the tile does not restart Helper or clear an emergency stop. Home button settings require a responding controller.

1.2.0 (#55): Root validates migration data before installing. Interrupted cleanup before provisioning can remove the package without a nonexistent LS2 snapshot, retaining a verified receipt for the normal cytv archive/reinstall flow. Later missing snapshots or conflicting evidence still stop cleanup. These changes require the new driver; the OLED Flex recovery-service startup failure remains unresolved.

## LG firmware blocking in 1.2.0

Root only: Home settings → LG firmware updates changes the existing Homebrew Channel preference. This includes firmware security updates; Clean Your TV updates remain separate. A real TV restart is needed in both directions; standby is not enough. The switch shows the saved preference, not verified active blocking. Some TVs check before blocking starts, so prompts may remain and router blocking may be needed. Homebrew keeps the preference after CYTV removal or rollback. If unavailable or unconfirmed, check Homebrew and refresh status. See the acceptance record for the scope of TV checks.

[LG firmware blocking](../LG-FIRMWARE-UPDATES.md) · [1.2.0](../RELEASE-1.2.0-ACCEPTANCE.md)

## New in 1.3.0: guided desktop recovery

New in 1.3.0. After Check TV status, connection diagnostics or Return to LG Home, an unfinished No-root removal offers **Recover and reinstall** for the same TV and connection. Review and explicitly confirm finishing removal (default: No), then review the bundled versions before installation. **Set up my TV** also offers this recovery directly. Returning to LG Home alone does not finish removal. On failure, use **Save diagnostic report…** to save the report from that failed attempt, then attach it to your issue; no terminal is needed. If no report could be created, include the visible error. Keep recovery files; failed or ambiguous operations are not retried automatically. This does not yet establish a fix for the reported G5/firmware 43.21.71 failure (#65).

## New in 1.3.0 — #12

Android Tools keeps the selected TV, edition and SSH port after returning to the start screen; No-root normally uses 9922. If Home settings cannot verify Home control, they show an unknown status and hide Change Home until a valid reply. This does not mean Helper stopped and does not restart it. These changes are not in the published v1.2.0 packages.

Root diagnostics in 1.3.0 (#55): after a failed setup, save the diagnostic report from that attempt. It can include categorized recovery-service startup failures; keep recovery state and retained drivers. This does not yet confirm a fix on OLED Flex.

## Unreleased candidate: Root setup through Homebrew

This source candidate adds the separate **CYTV Installer** app for **Root only**.
It is not yet published in the Homebrew catalog. cytv keeps No-root and Root on
Windows, macOS, Linux and Android; existing download links remain published cytv.

Installer requires existing root, Homebrew Channel with root exec, Node.js **8+**
and working Python **3.9+**. For supported ARMv7/`armv8l` 32-bit userspace it
embeds a pinned private Python offline. Opening/status is read-only: explicitly
prepare missing Python, inspect again, then review installation. Runtime setup
needs **320 MiB free after Installer installation**, plus TV package staging space
which has not been measured. No new model/firmware compatibility is established.

Setup installs Root Home and Root Updater; System Updater preparation is an
explicit optional choice. Enable Change Home separately after verification;
setup never clears emergency/off. Current verified installations share profiles
and recovery across cytv/TV without reinstall or reset. Unknown older infrastructure
needs diagnosis; packaged-preference import is only for fresh setup, not browser
storage or infrastructure migration.

After interruption inspect status first. Continue appears only with the original
snapshot/lease and proven final readback. Other stages need status, restore or
diagnosis; the source CLI can explicitly resume additional recognized stages.
cytv's Finish Root setup does not restart an incomplete worker. Never delete
journals or blindly retry. Homebrew updates Installer only; existing updaters own
product updates/signed complete sets. Deleting Installer leaves the product.
Explicit complete removal restores LG Home and cleans owned startup hooks while
retaining independent recovery/archive evidence and referenced Python slots.
All physical checks for this path remain pending; the historical Root 0.2.0 C3
results above do not validate Homebrew setup.

Startup uses receipt-owned private wrappers that check installed package identity as data. Packaged startup scripts are never executed. Missing or unsafe packages stop automatic rearming; independent recovery can still restore LG Home. Inspection may briefly stage verified files privately without changing Home or the product.

[Candidate setup and recovery (English)](../INSTALL.md#candidate-on-tv-root-installation) ·
[Pending physical acceptance (English)](../development/HOMEBREW-INSTALL-ACCEPTANCE.md)


For this source candidate, an existing Root installation needs checked recovery and fresh setup to receive the corrected private runtime. Updating Installer alone does not replace it. Keep recovery records and enable Home only through the normal setup/settings flow.

Next candidate only: No-root Settings → Developer Mode → Show diagnostics includes safe storage/Home RPC failure categories and the actual service version. Viewing diagnostics does not enable renewal or start Helper. A failed status check does not prove Helper stopped. This does not establish a C5 fix; see [diagnostics (English)](../SETTINGS-DIAGNOSTICS.md).

The report receives remote focus. Up/Down scrolls it; Left/Right or Enter returns to nearby actions, and Back returns to Home settings.

**Unreleased, #82:** when the Home setting is absent, explicit Root setup can initialize it to LG Home and verify the readback before enabling recovery. Status/doctor never writes it. An uncertain write is not repeated; keep recovery data. The explicit LG Home setting remains after removal. This firmware still needs device testing.

## Unreleased candidate: HDMI sound recovery (Root)

Home settings → HDMI sound offers Reconnect eARC and confirmed HDMI-route fallback
recovery. ARC-only, combined/WOW Orchestra and unknown modes are skipped.
Recover after power-on is experimental, off by default; it may interrupt healthy
audio after power-on/standby and requires a supported power subscription. Back can
close the panel during cleanup. After interruption, check status; restore the saved
setting only if you want eARC on. Home restoration/emergency stop disables automation
until explicit enable. Older private runtimes need checked fresh setup. TV compatibility
and faster audio acquisition remain unconfirmed.

[Device acceptance (English)](../development/ROOT-AUDIO-RECOVERY.md)

Unreleased: private Python preflight reports ABI, directory safety and free-space failures separately. Initial setup needs 320 MiB free in /var/lib. A large WAM Session Storage may explain low space; clearing it can lose app session state. See the [recovery guide](../RECOVERY.md#private-python-and-low-var-space).

In the unpublished 1.4.0 candidate, an interrupted No-root installation also offers **Recover and reinstall** after **Check TV status**. Confirm removal only if you want to remove the Clean Your TV apps, then review the versions before reinstalling. If recovery fails, save its diagnostic report and stop. This does not yet identify or fix the original TV package rejection (#21).


**Unreleased — WAM:** `cytv clean-wam-cache --edition root`. Only cache and codecache are requested. Session Storage, cookies, Local Storage, Service Worker and databases are excluded. Close TV apps first. Cached data will be downloaded or rebuilt; the next app launch may be slower. [WAM](../WAM-CLEANUP.md).

You can cancel and free space yourself. Use the manual cleanup guide and recheck /var/lib; removing apps may free a different partition. **Session Storage (SSH):** Close TV apps first. This deletes app session state and may sign you out or lose unsaved work. [WAM](../WAM-CLEANUP.md#free-space-yourself-instead).

Unreleased Root cold-start correction: with Home control enabled and LG Power On Screen set to Home, a healthy startup can request Clean once if Live TV or LG Home is still visible. An already visible app is preserved at the final screen check; automatic presentation is not retried. Explicit off and triple-Home stay off. The corrected retained runtime needs checked setup/update; an app-only update is insufficient. Device acceptance remains pending.

[Cold-start investigation and acceptance (English)](../development/ROOT-COLD-BOOT.md)
