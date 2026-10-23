# Root Edition

**Native system Home integration, under development.** Root Edition targets TVs
with existing root access. It shares the Home interface with No-root Edition,
but aims to let webOS select Home directly instead of redirecting app exits.

**An installable hardware-test candidate is available locally; a supported permanent release is not yet available.**
Use [No-root Edition](../docs/INSTALL.md) for the released setup, or compare both
paths in [Choose your edition](../docs/EDITIONS.md). Do not replace a working
setup with the lab findings below.

## Why a separate edition?

The released helper already handles short Home and automatic startup on the
validated setup. Its Back-exit watcher can briefly expose LG Home. Root Edition
investigates system routing through both the default Home and idle-app profiles,
with a recovery mechanism that also works outside ordinary `init.d` startup.

A bounded diagnostic test on **OLED55C3RLA / 43.21.71** returned after a confirmed
Back exit without an observed LG flash while the helper was stopped. A later bounded test also passed with the real launcher UI under a separate ID.
Permanent integration still needs complete recovery and clean emergency-exit
validation.
See [test results and open gates](STATUS.md).

## Available now

| Tool / document | Purpose | Changes the TV? |
| --- | --- | --- |
| [Doctor](DOCTOR.md) | Read-only environment report; optional inspection of captured app registration | No |
| [Candidate build](ROLLOUT.md#build-and-verify-locally) | Isolated IPK, installer and recovery runtime | Build: no; explicit install/trial: yes |
| `metadata.py` | Prepare exact original/candidate manifest snapshots locally | No |
| [Recovery contract](RECOVERY.md) | Recovery requirements and rollback design | No |
| [Test plan](TESTING.md) | Local verification and hardware acceptance gates | No |

```sh
python3 root-edition/doctor.py --ssh my-tv --output doctor-report.json
python3 -m unittest discover -s root-edition/tests
```

`my-tv` is your existing OpenSSH alias with a verified host key. Neither command
obtains root or installs an application. For saved captures and metadata plans,
follow the linked guides.

## Root access and compatibility

Root availability is separate from Root Edition compatibility. The doctor does
not select an exploit or predict whether a firmware is rootable. Consult the
[webOS Homebrew rooting overview](https://www.webosbrew.org/rooting/) and the
upstream instructions for the exact method/model/firmware you are evaluating.
Do not infer support for another TV from the C3 test result, or change Developer
Mode, firmware, update settings or Homebrew configuration just to run this doctor.

[Registration investigation and next test](REGISTRATION-NOTES.md) explains why
changing the manifest alone is not enough.

## Goals still requiring validation

- Repeat native Home and confirmed Back acceptance on the final clean-installed bundle.
- Persistent startup with one clear emergency exit and complete uninstall/rollback.
- Final-bundle interrupted-install, failsafe and uninstall acceptance; software-reboot recovery passed on the corrected installed candidate.

Earlier boot graphics and elimination of the initial black interval are research
questions, not features delivered by this edition.

Follow the [ordered rollout plan](ROLLOUT.md) for release scope and remaining gates.
