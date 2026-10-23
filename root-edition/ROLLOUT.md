# Install and activate Root Edition

This is a separate Root Edition package for an already rooted TV. Tested device:
**OLED55C3RLA / 43.21.71**. See [acceptance and remaining gates](RELEASE-ACCEPTANCE.md).
The ordinary launcher and Home Helper remain installed. Keep a working backup
and root SSH connection before changing routing.

## 1. Download or build, then verify

For the published Root Edition archive, extract it and open a terminal in its top
folder. It includes source instructions and the tested bundle at `build/root-candidate`.
Skip the build commands below and continue with checksum verification. Do not
replace the bundled runtime with an untested build while following this release.

To build from source instead:

On your computer, use Python 3.9+, Node.js and OpenSSH. From the repository root:

```sh
bash scripts/test.sh
mkdir -p build
python3 root-edition/build.py --version 0.1.1 --output build/root-candidate
```

The output directory must be new. Keep the whole directory, including `setup.py`,
`bundle.json`, runtime, IPK and `SHA256SUMS`; the IPK alone does not provision
recovery. Verify its IPK checksum with `sha256sum -c SHA256SUMS` (macOS:
`shasum -a 256 -c SHA256SUMS`) from inside that directory. Installation also checks
all bundle files against `bundle.json`. Checksums do not replace source trust.

Public builds contain an empty inventory. They exclude the ordinary Home updater,
renewal and helper-control scripts. Root's separate update UI requires the
[one-time Root Updater setup](UPDATES.md). This build does not contact the TV.

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

## 2a. Install the independent updater once

For 0.1.1, install Root Updater before activating Home control. The distribution
contains `build/root-updater`; use the exact newly installed Root bundle as its
rollback baseline:

```sh
python3 build/root-updater/setup-updater.py --bundle build/root-updater --baseline build/root-candidate --ssh my-tv --apply
```

Keep LG Home selected during setup. See [Root updates and recovery](UPDATES.md).
Existing Root Stable 0.1.0 uses package version 0.0.1 and older recovery
infrastructure: it needs supervised computer migration, not an IPK-only update.
The setup refuses live or retained state rather than overwriting it. Restore LG
Home, retain private backups and have a maintainer inspect existing recovery
state; do not delete that state to bypass the check.

## 3. Turn on Home control

If Home Helper is active, hold Home for about two seconds to stop it, then release
all buttons. This is the **old helper's** exit action. Root activation refuses to
run while that helper is present and never clears its safety latch.

Open **Home Root Preview** from LG Apps, then **Home settings → Turn on Home control**.
Alternatively:

```sh
python3 build/root-candidate/setup.py enable --ssh my-tv
```

Activation checks input, the recovery guardian and effective Home routing
before recording permanent intent. No countdown or second confirmation is needed.
If startup fails, it restores LG Home. Check arrows/OK, short Home and Back.
Use **Return to LG Home**, three short Home presses, or the restore command below
to turn it off whenever needed.

## 4. Persistent operation

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
| Home settings → Return to LG Home → Confirm return | Normal restore; disables Root autostart |

Release Home between taps. Long Home is **not** the Root emergency action and can
trigger LG behavior such as zoom. Exiting Root mode does not remove root or resume
the old helper. To use No-root again, open Home Helper.

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
blocks reinstallation. Compatible Root application updates can use the separate
[Root Updater](UPDATES.md); infrastructure replacement remains host-assisted.
Archive and resolve that state only after verified removal and restoration,
following maintainer review.
An unknown removal result is not permission to resubmit or delete directories.

## Release scope

System libraries, early boot artwork and faster cold-start display are outside
this release. See [release scope and limitations](ROOT-STABLE-0.1.0.md). Evidence is model- and build-specific.
