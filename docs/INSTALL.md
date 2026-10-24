# No-root Edition installation

Looking for the other track? See [Choose your edition](EDITIONS.md).
Root Edition has no supported installer yet; do not use this guide to alter an
existing root setup.

This release targets a setup tested on LG OLED55C3RLA, firmware 43.21.71.
Recovery behavior is documented in RECOVERY.md. For another model,
start with the standalone launcher; native input compatibility is not guaranteed.

## What you need — and what you do not

- **No root access or replacement firmware** on the tested LG C3 setup.
- **No always-on external device:** both the launcher and helper run on the TV.
  You do not need a router script, Raspberry Pi, home server or USB drive.
- **A computer for setup and maintenance:** build, pairing, installation, app-list
  updates and software updates use the tools below. The computer can be off during use.
- **LG Developer Mode must remain active.** This is separate from rooting the TV.
- **A working local network:** initial pairing and the helper's power/foreground
  watcher use the TV's local control interface. Running on the TV does not make
  these monitoring features independent of network connectivity.

## 1. Prepare your TV

Install LG's **Developer Mode** app, sign in to your LG Developer account and enable
Developer Mode. Keep the session active. LG can remove sideloaded applications when
Developer Mode expires or becomes disabled.

Follow [LG's Developer Mode guide](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)
for account setup, network access and session renewal. TV and computer need to be
reachable on the same trusted local network.

## Recommended: one-script installation

On macOS or Linux, install **Node.js 20+ with npm**, **Python 3.9+** (with `venv`
and `pip` support), and **Git**. On some Linux distributions Python's `venv` support
is a separate OS package. Enable **Key Server** in the TV's Developer Mode app.
Then run:

```sh
git clone https://github.com/Razdva122/clean-your-tv-lg-webos.git
cd clean-your-tv-lg-webos
./install.sh 192.168.1.50
```

Use your TV's IP address; without an argument, the script asks for it.
It downloads Python dependencies into `.venv/`, uses **Zig 0.14.1** from `ZIG`
or `PATH` when available (otherwise installs it into `.venv/`), and installs the
official **webOS CLI 3.2.6** in `build/tools/`. No global installation or `sudo` is
needed. Internet access on the computer is required to download these tools.

### Termux / Android

Supply a working **Zig 0.14.1** executable before running the script. Android has
no compatible `ziglang==0.14.1` Python distribution; with an explicit compiler,
`install.sh` skips that distribution and still installs the Python dependencies.

```sh
export ZIG=/absolute/path/to/zig
"$ZIG" version  # must print 0.14.1
./install.sh 192.168.1.50
```

A `zig` executable on `PATH` is also accepted. If neither is available, setup
stops with instructions before pairing or installing anything on the TV. No
script edits are needed. The compiler must run in your actual Android/Termux
(or Linux container) environment; a Linux archive's CPU architecture alone does
not establish Android compatibility. The rest of the Node.js, Python and CLI
requirements above still apply. End-to-end Termux and C5/webOS 26 hardware
compatibility have not been verified by these build-tool fixes.

The script creates a separate CLI profile named `clean-your-tv-<IP-with-dashes>`
and asks the CLI to fetch its SSH key. **Enter the passphrase shown on the TV** when
prompted. Then accept the separate **remote-control pairing request on the TV**.
The CLI stores the SSH key/profile in its usual user configuration location;
the app-sync tool stores the local control key in the ignored `.lgtv-key.json`.
Do not share these files or run setup under shell tracing (`bash -x`).

The script then syncs your apps and icons, builds the launcher and native helper,
installs both packages, transfers the helper configuration with the existing
verified setup script, requests early input restoration, and launches Home Helper.
If EIM registration is unavailable, setup prints a warning and startup relies on
the guarded fallback; this is not reported as verified early restoration.

Afterwards, perform [the TV checks below](#7-verify-before-daily-use). A successful
script run confirms the commands completed, not hardware compatibility. You may
switch the computer off during everyday use; Developer Mode and local networking
requirements still apply.

**Run the same command again** to resync apps, rebuild and reinstall from your current
checkout. It preserves `launcher/config.js`; customize that file if desired. To update
from GitHub, first update the checkout, then rerun. A failed step stops setup;
fix the error and rerun. Packages already installed are not automatically rolled back;
see [Recovery](RECOVERY.md). The script will not retarget an existing CLI profile
that points to another TV. Set `DEVICE=another-name ./install.sh <IP>` to use a
separate profile. Native Windows is not supported by this Bash script; WSL and
Windows setup have not been tested.

## Manual installation

The steps below remain available for developers and launcher-only installation.
The one-script installation above already performs pairing, app sync, build,
installation and helper configuration; skip to the TV checks after it completes.

## 2. Prepare your computer

The scripts use Bash, Python 3, Node.js, the webOS CLI and Zig 0.14.1. macOS/Linux are
the intended script environments; Windows users need a compatible shell/toolchain.
Windows installation has not been tested.

Install the CLI following [LG's CLI documentation](https://webostv.developer.lge.com/develop/tools/cli-dev-guide).
Check that `ares-package`, `ares-install`, `ares-launch` and `ares-novacom`
are on PATH (`npm install -g @webos-tools/cli`). Install Zig 0.14.1 separately or set `ZIG` to its executable.

From the repository root:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## 3. Pair Developer Mode SSH

Run `ares-setup-device` interactively and add a device named `lgtv`:

- Host: your TV's local IP address.
- Port: `9922`.
- User: `prisoner`.
- No SSH password for the Developer Mode connection.

Enable **Key Server** in the TV's Developer Mode app, then run:

```sh
ares-novacom --device lgtv --getkey
ares-device --system-info --device lgtv
```

Enter the passphrase shown on your TV when prompted. Do not put it in scripts or
issue reports. This SSH pairing is separate from the on-screen remote-control
pairing in the next step.

## 4. Discover your apps

Replace the example address with your TV's address:

```sh
export TV_HOST=192.168.1.50
python3 sync-apps.py "$TV_HOST"
```

Accept the pairing request **on the TV**. The tool saves the key in the ignored
`.lgtv-key.json` file, then generates `launcher/apps.js` and app icons. These are
personal build inputs: do not publish them. The tool skips an app if its icon
cannot be downloaded; check the reported count and terminal warnings.

Edit `launcher/config.js` to choose `dockApps`, `hiddenApps` and the column count.
Find app IDs with `python3 sync-apps.py "$TV_HOST" --list`.
Hiding a tile does not uninstall an application.

## 5. Test and build

```sh
scripts/test.sh
scripts/build.sh
```

Output:

- `dist/com.gathin.tvhome_1.1.0_all.ipk`
- `dist/com.local.nativehome_0.6.13_arm.ipk`
- `dist/SHA256SUMS`

For launcher-only use, run `ares-package launcher renewal-service -o dist`; Zig and the native
helper are not needed. Short Home interception requires the optional helper.

## 6. Install and configure

```sh
ares-install -d lgtv dist/com.local.nativehome_0.6.13_arm.ipk
ares-install -d lgtv dist/com.gathin.tvhome_1.1.0_all.ipk
TV_HOST="$TV_HOST" DEVICE=lgtv scripts/configure-tv.sh
```

The setup script transfers your local SSAP key and app IDs to the helper's state
directory using a temporary file, verifies SHA-256 and file permissions (640 for the
key, 644 for app IDs), then atomically replaces each destination. A failed transfer
leaves that destination unchanged. The two files are verified individually, not as
a single transaction. Remote `mktemp`, `base64`, `sha256sum`, and `stat -c` are required.
Do not run setup with shell tracing (`bash -x`): the transfer command contains the
pairing key in Base64. The script then requests input-source registration. It checks the EIM response
for a top-level `returnValue: true`. Empty output means registration is unconfirmed,
not rejected: some firmware returns no bus replies from the Developer Mode shell.
An explicit rejection and a command failure have separate warnings. The guarded
startup fallback remains available. Runtime restores state permissions after startup;
see the C4 follow-up limits in COMPATIBILITY.md.

```sh
ares-launch -d lgtv com.local.nativehome
```

The helper opens the launcher and attempts remote interception. Pin the launcher
to a numbered Quick Access key as a recovery shortcut: open the launcher, then
assign it through your TV's Quick Access menu (hold **0** on supported LG remotes).
Existing assignments should be changed explicitly.

## 7. Verify before daily use

- Check arrows and held arrows, OK, Back, volume, pointer and wheel.
- Open an app and press short Home: the launcher should return.
- Press Home three times within two seconds: LG Home should appear and navigation should work.
- Open Home Helper manually to resume interception.
- Test standby/wake separately from a cold boot. Record what happens without pressing Home.

If any check fails, use [Recovery](RECOVERY.md). Report the failure before treating
this release as validated on your TV.

## Optional session auto-renewal (Beta)

After installation, open Settings → Enable Beta to opt in. It is disabled by default.
Read [the Beta guide](DEVELOPER-MODE-BETA.md) before relying on it. Monitor the official
Developer Mode timer and share feedback; real renewal is not yet validated.
