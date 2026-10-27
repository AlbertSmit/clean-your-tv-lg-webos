# 1.4.0 maintainer acceptance — 2026-10-27

The maintainer accepted release 1.4.0 after supervised testing of source
`99997e47a3bde15da88b881800b3c1629cb86e7e`, trusted artifact run
[40498700100](https://github.com/Razdva122/clean-your-tv-lg-webos/actions/runs/40498700100).
TV: OLED55C3RLA, firmware 43.21.71, SDK 11.2.0. Final freeze changes only
release metadata and documentation; product sources remain the tested revision.
Fresh builds of the frozen commit are required before merging #98.
Raw device records, credentials and backups remain private.

| Check | Observed result |
| --- | --- |
| Checked replacement and fresh setup | Supported full-product removal/setup completed; all 25 installed runtime hashes matched the exact candidate bundle and recovery proof; active intent, guardian, recovery and System Updater verified. |
| Enabled AC-off startup | Three ordinary enabled cycles passed automatic Clean presentation without Home/app launch. First showed Live TV then Clean at about 20 seconds; second showed Clean immediately; third changed from Live TV to Clean with delay unspecified. New session per cycle and stable session through readback verified. No immediate-first-screen guarantee. |
| Standby/wake | Remote off at least 30 seconds with AC connected, wake without Home; Clean visible after one minute, Emby → short Home returned Clean; active routing/guardian/recovery and System Updater passed. |
| Triple-Home | Immediate LG routing and disabled intent verified; separate 30-second AC removal preserved off state for one minute with no Clean launch. |
| Explicit settings off | Immediate LG routing and disabled intent verified; separate AC removal preserved off state, Live TV remained and short Home opened LG Home. |
| Early app focus | One accepted Emby launch before Root startup completion; later boot decision preserved foreground. Emby remained for one minute; short Home then opened Clean. No installed helper/runtime patch. |
| Basic controls | Basic Clean/Emby playback/login and arrows/hold, OK, Back and volume passed on prior candidate9194. On corrected99997, short Home and emergency/off were repeated; other basic controls were deliberately not repeated at the maintainer request. Prior results are not relabeled as exact99997 results. |
| Manual physical rollback | Candidate installer removed the candidate through the checked path; checksum-verified published v1.3.0 installer restored Root 0.4.0 / Root Updater 0.3.0 and exact 24-file historical runtime/proof. Old System baseline/bootstrap, active intent, guardian/recovery and cleared pending operation verified. Owner confirmed Emby → short Home opened Clean. TV was deliberately left on v1.3.0; no return-to-candidate or old-version power-cycle result is claimed. |

The maintainer explicitly requested closing #90 after confirming normal operation
and no reproduction in these tests. This accepts the reported C3 case; it does
not establish that observer diagnostics alone corrected its historical cause.
#104 and #111 are accepted in the scope above. Public delivery remains pending
until signed publication and package/feed verification complete.

Limits: manual whole-product rollback is distinct from an automatic signed
System Updater downgrade, which was not exercised. Additional firmware/models,
C2/C5/NANO reporter results, eARC audible behavior/timing and physical Android
phone-to-TV operations remain unverified. eARC automation remains experimental
and off by default. Android acceptance retains the documented emulator scope
and original signing identity; frozen APK metadata/payload/signer and upgrade
verification remain required. Homebrew promotion remains disabled.
