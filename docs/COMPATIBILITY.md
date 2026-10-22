# Compatibility and known limits

| Configuration | Status |
| --- | --- |
| LG OLED55C3RLA, firmware 43.21.71 | Hardware used for development and tests |
| Launcher 1.0.13 + helper 0.6.13 | Recovery UI, app icons and hover labels tested on the same TV after rooting; underlying 0.6.12 input/watchdog behavior unchanged |
| Other LG models / firmware / remotes | Unverified |
| macOS build / CLI | Used locally |
| Linux | Scripts intended to support it; not hardware-tested here |
| Windows | Not tested; requires an appropriate shell/toolchain |

The relay requires compatible `LGE M-RCU - Builtin [0]` and `[1]` devices and checks
capabilities before interception. Unsupported or busy devices cause it to exit.
Do not remove these checks to force compatibility.

- Developer Mode expiry may remove sideloaded apps.
- Back navigation inside apps remains theirs; exiting may briefly show LG Home.
- Cold startup is not instant and can begin with a black screen. No fixed startup
  time or improvement across firmware is promised.
- Long Home stops interception until a manual helper launch; it does not erase data.
- Network and foreground monitoring depends on local SSAP pairing and connectivity.
- Wheel-to-tile navigation is not implemented; wheel events are passed through.
- App inventory is generated on your computer. Re-sync after installing/removing apps.
- Hiding a tile does not uninstall the app or disable system ads.

This is an alternative launcher, not an LG-supported system Home replacement.
