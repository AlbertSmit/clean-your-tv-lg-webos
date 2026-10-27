# Install cytv without a terminal

Unpublished 1.4.0 candidate: [test artifacts, device matrix and recovery gates](RC-1.4.0-TESTING.md). Stable download links below still refer to v1.3.0.

**[v1.3.0 stable](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v1.3.0)** contains cytv **0.4.0**, Home **1.4.2**, Helper **0.6.19**, Root **0.4.0**, both edition Updaters **0.3.0**, Android **0.3.0-preview / code 11** and System Updater **1.1.0 / protocol 1**. The latest-download links follow the published stable release. Hardware evidence is limited to the documented configuration and checks; see [release notes](RELEASE-1.3.0.md) and [compatibility](COMPATIBILITY.md).

No-root and Root are equal options for different TV setups. Choose No-root for LG Developer Mode or Root for existing root SSH access. Compatibility and test coverage remain specific to each edition.

The desktop wizard opens in its own window. The sidebar follows the four setup
steps; Root and No-root are shown with descriptions before you choose. Expand
**Maintenance action** on the start screen for status, diagnostics, restore and removal.
It includes the computer Python runtime and the TV packages; the optional
TV Python archive is a separate verified download during eligible Root setup;
you do not need developer tools or terminal commands.

Download the macOS, Windows or Linux desktop package from the
[latest release](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/latest).
The older v0.9.0 macOS/Linux files are console programs, not the desktop app.

## macOS

1. Download `cytv-macos-arm64.zip` for an Apple Silicon Mac (M1 or later), or
   `cytv-macos-x64.zip` for an Intel Mac.
2. Double-click the ZIP to extract `cytv.app`.
3. Drag `cytv.app` into **Applications**, then double-click it.
4. Allow **Local Network** access if macOS asks. Click **Set up my TV**.

### If macOS says “cytv was not opened”

Our current Mac builds are not Apple-notarized. macOS may say that Apple cannot
verify whether cytv contains malware. If you downloaded the app from this
project's GitHub release and want to open it:

1. Click **Done** to dismiss the warning; keep the app in **Applications**.
2. Open **Apple menu → System Settings → Privacy & Security**.
3. Scroll to **Security**, find the blocked cytv message and click **Open Anyway**.
4. Confirm with your Mac password or Touch ID if requested, then click **Open**.

After this approval, launch cytv normally by double-clicking it. If the button is
missing, try opening cytv once more, then return to these settings. A managed
work Mac may require your administrator's help.

These steps apply to the unverified-developer/notarization warning. If macOS
reports actual malware or a damaged app, stop and report the exact message.
Do not disable Gatekeeper or remove quarantine with terminal commands.
See [Apple's first-launch guidance](https://support.apple.com/en-mo/102445).

### If the app opens but cannot connect to the TV

1. Turn on the TV and connect it and your Mac to the same home network.
2. Open **System Settings → Privacy & Security → Local Network** and enable **cytv**
   if it is listed. Allow access when the app asks.
3. After changing permission, fully quit cytv and reopen it. Use **Check TV status**
   before retrying an interrupted installation.
4. If the connection still fails, save the diagnostic report and open an issue
   with the error, macOS version and TV model. Do not delete recovery files.

Desktop dependencies require macOS 13 or newer; native CI builds run on macOS 15.
Older-system acceptance has not been established.

## Windows x64

Download [cytv-windows-x64-desktop.zip](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/latest/download/cytv-windows-x64-desktop.zip):

1. Download the ZIP, right-click it in File Explorer and choose **Extract All**.
2. Open the extracted `cytv-desktop` folder and double-click `cytv-desktop.exe`.
3. Click **Set up my TV**. No terminal or separate Python installation is needed.

Keep the whole folder together, including `_internal`; do not run the executable
inside the ZIP or copy the executable out by itself. The app opens its own window
without a console. `cytv-windows-x64.exe` is the separate console wizard.
Windows publisher signing is not configured.

## Ubuntu, Debian and Linux Mint

Use an **x64** computer with Ubuntu 22.04 or newer, Debian 12 or newer, or Linux
Mint 21 or newer. ARM Linux packages are not included.

1. Download `cytv-linux-x64.deb`.
2. Double-click the file. In your graphical package installer, click **Install**
   and enter your computer's administrator password if requested.
3. Open **Clean Your TV** from the applications menu.
4. Click **Set up my TV**.

The `.deb` contains the graphical app. The standalone `cytv-linux-x64` executable
is the separate CLI and opens a terminal wizard.

The package installer may download desktop libraries, so keep the computer online.
If double-clicking opens an archive viewer, use **Open With** and select your
software/package installer. Minimal Linux installations without a graphical
package installer need one supplied by their distribution; the `.deb` itself
cannot provide that first installation UI.

After installation, cytv runs as your normal user. It does not ask for your Linux
administrator password when connecting to the TV. Uninstall cytv using your
software manager; this does not uninstall TV apps or delete saved recovery data.

## Language selection

The installer chooses the computer’s language automatically.
Use the language selector to save another language, or choose **Auto** to follow
system settings. On the TV, use **Settings → Language**; this is a separate preference.
These language controls are included in v0.10.3 and later downloads.
Version 1.3.0 adds Simplified and Traditional Chinese with script-specific
bundled fonts; earlier v1.2.0 downloads retain ten languages.
See the [twelve localized installation, use and recovery guides](LANGUAGES.md).

## In the wizard

- Turn on the TV and connect it to the same home network as your computer.
- Select a discovered TV, or use the address field and **Help finding my TV**.
- Choose **No-root** for LG Developer Mode, or **Root** for an already rooted TV.
  Connection detection sets the current choice to match the detected connection; you can select either edition. Root privileges are verified after sign-in.
- Review the TV and edition, then click **Continue**. Approve pairing on the TV.
- Root checks Python 3.9+, TV Node.js 8+, root/Homebrew services and input support.
  Eligible ARMv7 TVs without suitable Python can receive a separate pinned runtime
  over SSH; this does not certify older-TV compatibility. Root activates Home
  control and opens Clean Your TV Home immediately. There is
  no trial countdown or Keep confirmation.

Passwords are masked. SSH identity changes still block the connection. While TV
changes are in progress, the window waits for the step to finish instead of
terminating the installer halfway through an operation.

On failure, read the explanation, click **Save diagnostic report…**, then
**Open an issue**. Include your steps, expected/actual results, TV model and firmware.
Review the JSON report before attaching it. Do not attach your profile folder or keys.

When an earlier installation was interrupted, **Set up my TV** checks its state
before proceeding. If Root and Root Updater are already installed and verified,
choose **Finish Root setup** to activate Home without reinstalling the packages.
If the earlier attempt stopped before updater setup, the wizard verifies recovery
and offers reinstallation in the same flow. Unverified states remain blocked;
save the diagnostic report instead of deleting recovery files.

The start page also offers status, diagnostics, return to LG Home and uninstall.
Existing console commands remain available in the separately distributed CLI.

### Guided No-root recovery and reinstallation in 1.3.0

This recovery flow is included in 1.3.0; it is absent from earlier v1.2.0 downloads.
If a No-root removal remains unfinished after **Check TV status**, connection
diagnostics or **Return to LG Home**, click **Recover and reinstall**. The wizard
keeps the same TV, edition and SSH port, even when several connections are saved.
It reconnects, checks the current state and asks you to finish removal with a
separate, default-No confirmation. It restores LG Home, verifies removal, then
shows the bundled versions for review before installing. **Set up my TV** also
offers this recovery when it finds an unfinished removal. Returning to LG Home
alone does not complete removal.

If any step fails, **Save diagnostic report…** is the primary action. Save that
attempt's report with the normal file dialog and attach it to your issue; no
terminal or later `doctor` run is needed. Cancelling the file dialog or choosing
an unwritable destination keeps the original report available. If report creation
failed, the window says so; include the visible error instead. Unknown outcomes
still stop the process, with no automatic retry or deletion of recovery evidence.

This improves the desktop recovery journey for issue #65. It does not establish
the cause or resolution of the original OLED77G55LW / firmware 43.21.71 failure;
the requested reporter diagnostics and physical-TV acceptance are still needed.

## Remove the project from a rooted TV

Choose **Uninstall Clean Your TV** with the saved **Root** connection. The wizard
restores LG Home and removes Root, Root Updater, its service and boot hook, plus
any installed No-root Home, Helper and Home Updater packages. It also removes
owned updater bus permissions and the System Updater supervisor when present.
Other TV applications stay installed.

This also works if an older cytv already removed Root but left Root Updater behind.
The wizard checks that the updater is idle before stopping it and verifies that
project apps, service registrations and startup hooks are gone. If a removal was
interrupted, run the same action again; an ambiguous package removal is never
submitted twice automatically.

Root recovery records, archived updater state and referenced managed Python
runtime slots remain for diagnostics and recovery.
They have no active service or startup registration. The Mac application and its
local reports remain installed on your computer.

## Build and validation

Install `cytv/build-requirements.txt`, then run:

```sh
python scripts/build-cytv.py --desktop
```

Build natively on each target. macOS creates `dist/desktop/cytv.app` and an
architecture-specific ZIP. Linux x64 creates `dist/cytv-linux-x64.deb` with a
`Terminal=false` application-menu entry. Windows creates
`dist/cytv-windows-x64-desktop.zip`, containing `cytv-desktop/cytv-desktop.exe`
and its `_internal` runtime. It uses a native PyInstaller windowed directory build;
the console build remains separate. Windows CI extracts the ZIP and runs its
offline smoke check; release assembly includes the desktop ZIP.

Every desktop build verifies its embedded payload and launches the frozen window
with an offline `--smoke-test`; this does not contact a TV. Widget tests cover
selection, secret entry, safe cancellation and destructive confirmation defaults.
The Qt libraries remain separate dynamic files in the app/package.

### Offline interface previews

With desktop dependencies installed, `python scripts/preview-installer.py --language ru`
saves screenshots of the real Qt widgets to `build/installer-preview/`. These use
sample TV data and do not discover, connect to, or modify a TV. Add `--all-locales`
to capture every supported language at the minimum window size.

## Unreleased: optional WAM cache cleanup

A matching candidate adds **Maintenance → Clear WAM caches (root required)**.
Review the estimated Cache/Code Cache size, free space, slower-next-launch warning
and manual alternative before the default-No prompt. Only the native WAM API types
`cache` and `codecache` are requested. Session Storage and other app data are
excluded; no root filesystem deletion, service stop, reboot, retry or setup resume
is performed. Existing Root SSH is required; TV Python/Node are not. See
[WAM cache cleanup](WAM-CLEANUP.md) for manual Session Storage risks and the limited
C3 API evidence. Published downloads do not include this action yet.

### Interrupted No-root installation in the unpublished 1.4.0 candidate

In the unpublished 1.4.0 candidate, an interrupted No-root installation also offers **Recover and reinstall** after **Check TV status**. Confirm removal only if you want to remove the Clean Your TV apps, then review the versions before reinstalling. If recovery fails, save its diagnostic report and stop. This does not yet identify or fix the original TV package rejection (#21). Removing the apps may reset Home preferences. The default is No, including with `--yes`; noninteractive setup cannot approve this step. The existing TV-installer-idle, removal readback and unknown-outcome guards remain in force. Published v1.3.0 offers this button for unfinished removal only.
