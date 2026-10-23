# Choose your edition

Both editions share the Home interface and run on the TV after setup. Root
Preview is separate from the stable No-root release; installing it does not
upgrade or remove your ordinary launcher.

| | No-root Edition | Root Preview |
| --- | --- | --- |
| Status | Stable release | Separate preview; permanent mode tested on one C3 |
| Root required | No | Existing root required; installer does not obtain it |
| Everyday external device | None | None |
| Setup | Computer, LG Developer Mode and local pairing | Computer, verified root SSH, compatibility and recovery checks |
| Short Home | On-TV helper redirects it | System Home routing; old helper must be stopped |
| Confirmed Back exit | Preserves navigation; LG can briefly flash | No LG flash observed in tested Kinopoisk exits |
| Emergency exit | Hold Home about two seconds | Three short Home presses within two seconds |
| Enable again | Resume Home / Home Helper | Try Root mode, then Keep Root mode before trial expires |
| Normal exit | Hold Home stops helper | Settings → Exit Root mode → Confirm exit |
| Startup evidence | Standby and cold boot on tested setup | Permanent software-reboot startup confirmed; final cold/standby/failsafe matrix pending |
| Developer Mode | Session must remain active; auto-renewal is opt-in Beta | Not used by Root installer; do not install Developer Mode over root |
| Updates | Signed Home update path in stable release | Separate Root package; no in-app production updater |
| Early black screen | Known limitation | Not solved |

## Get started

- **No-root:** [Install](INSTALL.md), [recover](RECOVERY.md), [compatibility](COMPATIBILITY.md).
- **Root Preview:** [Overview](../root-edition/README.md), [install and activate](../root-edition/ROLLOUT.md), [evidence and gates](../root-edition/RELEASE-ACCEPTANCE.md).

The Root hardware evidence is from **LG OLED55C3RLA, firmware 43.21.71** with a
Magic Remote. Other hardware is unvalidated. Keep your working installation and
private backups; never publish credentials, pairing data or device inventories.
