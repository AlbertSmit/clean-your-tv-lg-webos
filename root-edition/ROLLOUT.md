# Install and activate Root Stable

This is a separate Root Stable package for an already rooted TV. Tested device:
**OLED55C3RLA / 43.21.71**. See [acceptance and remaining gates](RELEASE-ACCEPTANCE.md).
The ordinary launcher and Home Helper remain installed. Keep a working backup
and root SSH connection before changing routing.

## 1. Build and verify

On your computer, use Python 3.9+, Node.js and OpenSSH. From the repository root:

```sh
bash scripts/test.sh
mkdir -p build
python3 root-edition/build.py --output build/root-candidate
```

The output directory must be new. Keep the whole directory, including `setup.py`,
`bundle.json`, runtime, IPK and `SHA256SUMS`; the IPK alone does not provision
recovery. Verify its IPK checksum with `sha256sum -c SHA256SUMS` (macOS:
`shasum -a 256 -c SHA256SUMS`) from inside that directory. Installation also checks
all bundle files against `bundle.json`. Checksums do not replace source trust.

Public builds contain an empty inventory. They exclude production updater,
renewal and helper-control scripts. This build does not contact the TV.

## 2. Check access and install without activating

Configure an OpenSSH alias `my-tv` for your existing root login. Verify its host
key through your existing trusted setup; do not disable host-key checking.
The TV needs Python 3, luna-send and Homebrew services. The doctor is read-only:

```sh
python3 root-edition/doctor.py --ssh my-tv --output doctor-report.json
python3 build/root-candidate/setup.py install --ssh my-tv --bundle build/root-candidate --migrate-packaged-home
python3 build/root-candidate/setup.py status --ssh my-tv
```

`--migrate-packaged-home` reads the existing updater's validated profile JSON when
available, otherwise copies the ordinary launcher's packaged inventory/config and
icons. It does not write to the original profile or migrate arbitrary localStorage.
Omit the flag only if you intend to configure the empty candidate yourself.
Resulting private hashes are recorded in `personalization.json` on the TV.

Installation provisions recovery but **does not switch system Home**. It refuses
an existing candidate or state directory. If installation has an unknown outcome,
retain its journal and inspect it; never blindly retry or delete recovery state.
Do not overwrite a live runtime with a newer bundle.

## 3. Start a protected trial

If Home Helper is active, hold Home for about two seconds to stop it, then release
all buttons. This is the **old helper's** exit action. Root activation refuses to
run while that helper is present and never clears its safety latch.

Open **Home Root Preview** from LG Apps, then **Settings → Try Root mode**.
Alternatively:

```sh
python3 build/root-candidate/setup.py enable --ssh my-tv
```

The trial lasts **60 seconds**. Check arrows/OK and short Home from an ordinary
app screen. Check Back navigation, Cancel in the exit dialog, then confirmed exit.
If the result is wrong, do not confirm: automatic recovery restores the original
Home. You can also select Exit Root mode or run the restore command below.

## 4. Keep Root mode

Before the trial expires, select **Settings → Keep Root mode**. Leave at least
five seconds for verification. The panel should report **Root mode active**.
This records permanent intent only after fresh input/guardian and routing checks.
An expired or unhealthy trial cannot be promoted.

The mode runs on the TV without a computer. On a normal software reboot it first
restores the previous route, then reactivates only after normal-boot checks and
fresh protections. A fault or explicit exit disables intent rather than looping
through automatic reactivation. Other lifecycle cases remain final release gates.

## Controls and recovery

| Action | Result |
| --- | --- |
| Short Home | Opens our system Home |
| Back inside an app | App handles navigation and its exit confirmation |
| Confirmed Back exit | Returns to our Home on the tested setup |
| Three short Home presses in two seconds | Emergency restore to LG, independent of the web interface |
| Settings → Exit Root mode → Confirm exit | Normal restore; disables Root autostart |

Release Home between taps. Long Home is **not** the Root emergency action and can
trigger LG behavior such as zoom. Exiting Root mode does not remove root or resume
the old helper. To use No-root again, open the ordinary Home and explicitly choose
its Resume Home / Enable Home control action, or open Home Helper.

Host recovery and readback:

```sh
python3 build/root-candidate/setup.py restore --ssh my-tv
python3 build/root-candidate/setup.py status --ssh my-tv
```

If restoration reports an error or conflict, keep its evidence and root access.
Do not remove state files or repeatedly activate. Recovery will not overwrite an
unrecognized foreign profile. [Recovery contract](RECOVERY.md).

## Remove or replace Root Edition

```sh
python3 build/root-candidate/setup.py restore --ssh my-tv
python3 build/root-candidate/setup.py status --ssh my-tv
python3 build/root-candidate/setup.py uninstall --ssh my-tv
```

Uninstall restores first, removes owned recovery registration/startup hook, then
removes the isolated package. It intentionally retains state and evidence. It
does not touch the original launcher or start its helper. A retained state directory
blocks reinstallation; there is no unattended Root updater yet. Archive and resolve
that state only after verified removal and restoration, following maintainer review.
An unknown removal result is not permission to resubmit or delete directories.

## Release scope

System libraries, early boot artwork and faster cold-start display are outside
this release. See [release scope and limitations](ROOT-STABLE-0.1.0.md). Evidence is model- and build-specific.
