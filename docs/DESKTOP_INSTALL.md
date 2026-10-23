# Install cytv without a terminal

The desktop wizard opens in its own window. It includes Python and the TV packages;
you do not need developer tools or terminal commands.

Download the desktop package for your computer from the
[v0.10.0 release](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.0).
The older v0.9.0 macOS/Linux files are console programs, not the desktop app.

## macOS

1. Download `cytv-macos-arm64.zip` for an Apple Silicon Mac (M1 or later), or
   `cytv-macos-x64.zip` for an Intel Mac.
2. Double-click the ZIP to extract `cytv.app`.
3. Drag `cytv.app` into **Applications**, then double-click it.
4. Allow **Local Network** access if macOS asks. Click **Set up my TV**.

The app currently has an ad-hoc signature, not an Apple Developer ID signature or
notarization. If macOS blocks it, open **System Settings → Privacy & Security**,
find the message about cytv and choose **Open Anyway**, then confirm. Only approve
a download you obtained from this project's release or build. Do not disable
Gatekeeper or run terminal commands to remove quarantine.

Desktop dependencies require macOS 13 or newer; native CI builds run on macOS 15.
Older-system acceptance has not been established.

## Ubuntu, Debian and Linux Mint

Use an **x64** computer with Ubuntu 22.04 or newer, Debian 12 or newer, or Linux
Mint 21 or newer. ARM Linux packages are not included.

1. Download `cytv-linux-x64.deb`.
2. Double-click the file. In your graphical package installer, click **Install**
   and enter your computer's administrator password if requested.
3. Open **Clean Your TV** from the applications menu.
4. Click **Set up my TV**.

The package installer may download desktop libraries, so keep the computer online.
If double-clicking opens an archive viewer, use **Open With** and select your
software/package installer. Minimal Linux installations without a graphical
package installer need one supplied by their distribution; the `.deb` itself
cannot provide that first installation UI.

After installation, cytv runs as your normal user. It does not ask for your Linux
administrator password when connecting to the TV. Uninstall cytv using your
software manager; this does not uninstall TV apps or delete saved recovery data.

## In the wizard

- Turn on the TV and connect it to the same home network as your computer.
- Select a discovered TV, or use the address field and **Help finding my TV**.
- Choose **No-root** for LG Developer Mode, or **Root** for an already rooted TV.
  Connection detection recommends an edition; root privileges are verified after sign-in.
- Review the TV and edition, then click **Continue**. Approve pairing on the TV.
- Root activates Home control and opens Clean Your TV Home immediately. There is
  no trial countdown or Keep confirmation.

Passwords are masked. SSH identity changes still block the connection. While TV
changes are in progress, the window waits for the step to finish instead of
terminating the installer halfway through an operation.

On failure, read the explanation, click **Save diagnostic report…**, then
**Open an issue**. Include your steps, expected/actual results, TV model and firmware.
Review the JSON report before attaching it. Do not attach your profile folder or keys.

The start page also offers status, diagnostics, return to LG Home and uninstall.
Existing console commands remain available in the separately distributed CLI.

## Build and validation

Install `cytv/build-requirements.txt`, then run:

```sh
python scripts/build-cytv.py --desktop
```

Build natively on each target. macOS creates `dist/desktop/cytv.app` and an
architecture-specific ZIP. Linux x64 creates `dist/cytv-linux-x64.deb` with a
`Terminal=false` application-menu entry. Windows retains its existing console build.

Every desktop build verifies its embedded payload and launches the frozen window
with an offline `--smoke-test`; this does not contact a TV. Widget tests cover
selection, secret entry, safe cancellation and destructive confirmation defaults.
The Qt libraries remain separate dynamic files in the app/package.
