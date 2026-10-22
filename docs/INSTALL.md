# Installation

This experimental release targets a setup tested on LG OLED55C3RLA, firmware 43.21.71.
The public setup is experimental; recovery behavior is documented in RECOVERY.md. For another model,
start with the standalone launcher; native input compatibility is not guaranteed.

## 1. Prepare your TV

Install LG's **Developer Mode** app, sign in to your LG Developer account and enable
Developer Mode. Keep the session active. LG can remove sideloaded applications when
Developer Mode expires or becomes disabled.

Follow [LG's Developer Mode guide](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)
for account setup, network access and session renewal. TV and computer need to be
reachable on the same trusted local network.

## 2. Prepare your computer

The scripts use Bash, Python 3, Node.js, the webOS CLI and Zig 0.14.1. macOS/Linux are
the intended script environments; Windows users need a compatible shell/toolchain.
Windows installation has not been tested.

Install the CLI following [LG's CLI documentation](https://webostv.developer.lge.com/develop/tools/cli-dev-guide).
Check that `ares-package`, `ares-install`, `ares-launch`, `ares-novacom` and `ares-push`
are on PATH. Install Zig 0.14.1 separately or set `ZIG` to its executable.

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

- `dist/com.gathin.tvhome_1.0.11_all.ipk`
- `dist/com.local.nativehome_0.6.12_arm.ipk`
- `dist/SHA256SUMS`

For launcher-only use, run `ares-package launcher -o dist`; Zig and the native
helper are not needed. Short Home interception requires the optional helper.

## 6. Install and configure

```sh
ares-install -d lgtv dist/com.local.nativehome_0.6.12_arm.ipk
ares-install -d lgtv dist/com.gathin.tvhome_1.0.11_all.ipk
TV_HOST="$TV_HOST" DEVICE=lgtv scripts/configure-tv.sh
```

The setup script transfers your local SSAP key and app IDs to the helper's state
directory, then requests input-source registration. Check that the printed EIM
response contains `returnValue: true`. An error here means early input restoration
has not been enabled; do not treat completion of the script alone as confirmation.

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
- Hold Home for two seconds: LG Home should appear and navigation should work.
- Open Native Home Prototype manually to resume interception.
- Test standby/wake separately from a cold boot. Record what happens without pressing Home.

If any check fails, use [Recovery](RECOVERY.md). Report the failure before treating
this release candidate as validated on your TV.
