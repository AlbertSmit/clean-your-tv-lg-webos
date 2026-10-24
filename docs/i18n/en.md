# Clean Your TV — user guide

No-root and Root are equal options for different TV setups. Choose No-root for LG Developer Mode or Root for existing root SSH access. Compatibility and test coverage remain specific to each edition.

## Before installation

This guide covers installation, daily use and recovery. Language selection and the macOS/Linux desktop app are included in [v0.10.3](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.3). Older v0.9.0 downloads do not include the desktop app. See the [shared installation guide](../INSTALL.md) for both editions.

Keep the TV on and the computer on the same trusted local network. No always-on computer is needed afterward. Compatibility depends on model, firmware and remote; Root has outstanding hardware checks.

- **No-root:** enable LG Developer Mode and Key Server. Enter the passphrase displayed on the TV and accept the separate TV pairing request. Developer Mode must remain active; expiry can remove sideloaded apps. Monitor its official timer even with Beta renewal enabled. Helper monitoring needs local networking.
- **Root:** existing root SSH access is required. The installer does not root the TV. Do not enable Developer Mode on an existing rooted setup. Keep root access and recovery services available.

## Install and select a language

- **Windows x64:** Download `cytv-windows-x64-desktop.zip`, choose **Extract All** in File Explorer, then open `cytv-desktop/cytv-desktop.exe`. Keep the `_internal` folder beside it. Windows publisher signing is not configured. The separate console is `cytv-windows-x64.exe`; rename it to `cytv.exe` and use `.\cytv.exe` in PowerShell for the commands below.
- **macOS 13+:** extract `cytv-macos-arm64.zip` (Apple Silicon) or `cytv-macos-x64.zip` (Intel), move `cytv.app` into Applications and open it. Allow Local Network access. If blocked, use Privacy & Security → Open Anyway only for a trusted project download; do not disable Gatekeeper. Older-system acceptance is not established.
- **Linux x64:** on Ubuntu 22.04+, Debian 12+ or Mint 21+, open `cytv-linux-x64.deb` in the graphical package installer, install, then open Clean Your TV from the applications menu. Desktop libraries may require Internet access. Linux ARM is not included. The standalone `cytv-linux-x64` executable is the CLI; use the `.deb` for the graphical app.

[Android installer](../../android/README.md): all ten interface languages are available. The top-right control shows the current language; tap it to choose another. Your selection is saved on the phone.

Android status and recovery keep the selected action visible during connection and show its own progress. Text uses the phone’s system font with larger labels and help text.

The desktop wizard selects your system language automatically; its language selector saves an explicit choice. On the TV, open **Settings → Language** and select a language, or the system/automatic option to follow the TV language. Installer and TV preferences are separate. The supported codes are listed in the [language index](../LANGUAGES.md).

For a separately downloaded CLI on macOS/Linux, open a terminal in its extracted directory:

```sh
chmod +x cytv
./cytv --language en install
```

Choose the TV (or enter its IP), choose the edition and review the summary. Approve first-use SSH trust only for your own TV on a trusted network; a changed saved key blocks access. Root credentials are distinct from the Developer Mode passphrase. Root installs recovery and activates Home immediately, without a trial or Keep step. Check arrows, OK, Home, Back/Cancel, volume, standby/wake and cold boot on your own TV.

## Everyday use and recovery

Arrows select tiles; OK opens them; hold OK to reorder. Short Back retains the app's navigation and exit confirmation. Short Home opens Clean Your TV while Home control is active. In new builds, hold Back for 1.2 seconds to open LG Home once. The Home-control switch and your settings remain unchanged.

**New builds: press Home three times within two seconds**, releasing between presses, to return to LG Home and stop Home control. This preserves preferences. Older No-root Helper versions through 0.6.13 instead use holding Home for about two seconds; holding Home is not the Root emergency gesture.

No-root: open **Home Helper** from LG Apps to resume; opening Home alone does not clear the stop. Root: turn **Change Home** on in Home settings to resume. **Open LG Home** opens LG Home once without changing routing. To restore LG Home as the persistent destination, turn **Change Home** off or run `cytv restore`. Do not run both controllers together. If a failure repeats, leave LG Home active.

```sh
./cytv --language en status
./cytv --language en doctor --report
./cytv --language en restore
./cytv --language en uninstall
```

After interruption, run `status` before retrying; retain journals and recovery files. `restore` returns LG Home without removing apps. `uninstall` restores before removal. Root recovery state is deliberately retained; never delete it to force reinstallation. Review diagnostic reports before sharing; do not publish keys or profile folders.

## Updates and removal

Keep known-working packages and private settings backups. Stop No-root Helper before replacing its packages; update from the computer without uninstalling first, since removal may erase settings. The combined cytv Root installation includes an updater for compatible releases under Settings → Software updates; the manual Root bundle has different limitations. Do not replace a live Root runtime with a standalone IPK. Reinstall only through the explicit cytv recovery/reinstallation flow. Removing the desktop app does not remove TV apps.

Technical details in English: [desktop setup](../DESKTOP_INSTALL.md), [CLI](../CLI.md), [Installation of both editions](../INSTALL.md), [manual installation](../MANUAL_INSTALL.md), [recovery](../RECOVERY.md), [edition comparison](../EDITIONS.md).

After connecting, cytv reads the installed TV versions and shows current → bundled version for Home and Home Helper (No-root), or Root and Root Updater. Review and confirm before installation. First installs, reinstalls and downgrades are labeled separately; `--yes` skips confirmation but still prints the versions.

Software updates shows release details only for the installed version or newer. Open Recovery to see the saved rollback version or why rollback is unavailable; Back returns to updates.

No-root checks the TV shell ABI, so a 64-bit kernel with verified ARM32 userspace is accepted. If verification fails, attach the generated diagnostic JSON; do not share keys or passphrases.

Home updates require confirmation before installation; startup verification is automatic afterward. Background status refresh keeps the selected remote-control button in place.

In Root and No-root, startup health is confirmed automatically after installation; you do not need to confirm that everything works. Recovery remains available after confirmation, without a time limit, until the next update. Rollback returns the previous Home version and its saved pre-update settings; later settings changes may be lost. A warning appears before you start rollback. On-device No-root updates and rollback still require root and Homebrew Channel; otherwise use the computer installer.

The update screen now separates versions, status and readable release notes. Up/Down reads the notes; Left/Right selects the fixed actions below. After automatic startup checks, Root restores previously enabled Home control; No-root preserves the separate Helper state. Disabled preferences and explicit or emergency off remain off.

Opening Home settings checks for updates in the background. An orange dot on Software updates means a newer version is available, including releases that require computer setup. Settings stay usable during the check.

No-root: open Home settings → Developer Mode for auto-renewal, session checks and diagnostics. The main screen keeps a brief status and any renewal errors visible. Back returns to Home settings. Both editions place Language, Software updates and TV settings in the same row; an arrow opens each item.

Opening Home Helper shows its purpose and current state. Starting a stopped Helper requires confirmation. Home Updater and Root Updater explain recovery; regular updates are in Home settings. Restore is shown only when a saved version is available and asks for confirmation before replacing Home and its settings.
