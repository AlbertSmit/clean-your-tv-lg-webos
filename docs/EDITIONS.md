# Choose your edition

No-root and Root are equal options for different TV setups. Choose No-root for LG Developer Mode or Root for existing root SSH access. Compatibility and test coverage remain specific to each edition.

Both editions share the Home interface and run on the TV after setup. Root
Stable is separate from the stable No-root release; installing it does not
upgrade or remove your ordinary launcher.

| | No-root Edition | Root Stable |
| --- | --- | --- |
| 1.1.0 RC source (unreleased) | Home 1.4.0 + Helper 0.6.19 | Root 0.2.0; new candidate hardware acceptance pending |
| Root required | No | Existing root required; installer does not obtain it |
| Everyday external device | None | None |
| Setup | Computer, LG Developer Mode and local pairing | Computer, verified root SSH, compatibility and recovery checks |
| Short Home | On-TV helper redirects it | System Home routing; old helper must be stopped |
| Confirmed Back exit | Preserves navigation; LG can briefly flash | No LG flash observed in tested Kinopoisk exits |
| Emergency exit | Three short Home presses within two seconds | Three short Home presses within two seconds |
| Enable again | Home Helper | Turn Change Home on in Home settings; stays on until disabled |
| Normal exit | Turn Change Home off, or use the emergency gesture | Turn Change Home off; Open LG Home only visits once |
| Startup evidence | Standby and cold boot on tested setup | Software reboot, quick standby and failsafe have scoped evidence; cold-power testing deferred |
| Developer Mode | Session must remain active; auto-renewal is opt-in Beta | Not used by Root installer; do not install Developer Mode over root |
| Updates | Computer-assisted on unrooted TVs; the separate Home Updater requires root ([details](UPDATES.md)) | Signed whole-edition updates with independent supervisor, saved profile and rollback; one-time root/Homebrew computer bootstrap required ([guide](../root-edition/UPDATES.md)) |
| Early black screen | Known limitation | Not solved |

## Get started

The latest published download is 1.0.3 stable; the versions above describe the
unreleased [1.1.0 RC](RELEASE-1.1.0.md). Its [test artifacts](https://github.com/Razdva122/clean-your-tv-lg-webos/actions/runs/40178512948)
are from product commit `acf1acc`. For the current source
versions, use [`release-versions.json`](../release-versions.json); hardware evidence
remains specific to the artifacts and scenarios recorded in the compatibility guides.

- **Without cytv:** [Manual installation of No-root and Root](MANUAL_INSTALL.md), including requirements for each edition and recovery commands.

- **Both editions:** [Install with cytv](INSTALL.md).
- **No-root:** [recover](RECOVERY.md), [compatibility](COMPATIBILITY.md).
- **Root Stable:** [Overview](../root-edition/README.md), [install and activate](../root-edition/ROLLOUT.md), [evidence and gates](../root-edition/RELEASE-ACCEPTANCE.md).

The Root hardware evidence is from **LG OLED55C3RLA, firmware 43.21.71** with a
Magic Remote. Other hardware is unvalidated. Keep your working installation and
private backups; never publish credentials, pairing data or device inventories.

See [release scope and known limitations](../root-edition/ROOT-0.1.1.md), including the unresolved intermittent emergency-gesture observation.
