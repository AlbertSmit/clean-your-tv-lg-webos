# Choose your edition

**Use No-root Edition for daily use today.** Root Edition is a separate development
track for TVs that already have root; there is no supported Root Edition installer
or release package yet. Both tracks use the same Home interface.

| | No-root Edition | Root Edition |
| --- | --- | --- |
| Availability | Released: Home 1.1.0 + Home Helper 0.6.13 | Development tools and test findings only |
| Root / replacement firmware | Neither required on the tested setup | Existing root required; this repository does not obtain it |
| Everyday external hardware | No always-on computer, router script, server or USB drive | Designed to run on the TV; no external runtime planned |
| Setup | Computer, LG Developer Mode, local pairing | Compatibility checks and verified recovery required before installation can be offered |
| Home destination | Helper intercepts short Home | System Home and idle-app routing under development |
| Confirmed Back exit | Helper returns to Home; LG can briefly flash | Diagnostic candidate returned without LG flash; production launcher not yet validated |
| Emergency exit | Hold Home ~2 seconds; Resume Home re-enables helper | Permanent root-mode escape behavior still needs implementation and hardware validation |
| Auto-start | Tested standby and cold-boot restoration on one C3 | Separate root-mode boot/recovery validation remains open |
| Developer Mode session | Must remain active; optional renewal Beta is unverified with real LG renewal | Root installation lifecycle will be documented with the eventual installer; do not change your current setup based on this roadmap |
| Early boot black screen | Known limitation | Not solved or promised by root access |

## No-root Edition

Start with [installation](INSTALL.md), read [recovery](RECOVERY.md), and keep the
[compatibility limits](COMPATIBILITY.md) in mind. Having a rooted TV does not
require you to switch to Root Edition. Do not install Developer Mode over an
existing root setup just to follow a different edition's guide.

## Root Edition

Read the [Root Edition overview](../root-edition/README.md) and
[hardware evidence](../root-edition/STATUS.md). You can run its read-only doctor
or local metadata planner now. Neither tool installs Root Edition or changes TV
routing. A successful doctor exit code does not mean the TV is supported.

## Shared limits

The hardware evidence is from **LG OLED55C3RLA, firmware 43.21.71**, with a Magic
Remote. Other models and firmware may have different services, input devices and
recovery behavior. Configuration and installed app lists remain personal to each
TV. No firmware image, credential or private backup belongs in this repository.
