# Compatibility and known limits

| Configuration | Status |
| --- | --- |
| LG OLED55C3RLA, firmware 43.21.71 | Hardware used for development and tests |
| Launcher 1.0.13 + helper 0.6.13 | Recovery UI, app icons and hover labels tested on the same TV; underlying 0.6.12 input/watchdog behavior unchanged |
| LG OLED55C46LA (C4), firmware 33.31.68, webOS 24 (SDK 10.3.1) | Community test: launcher, short Home, long-Home stop and Resume Home, hold-Back exit and cold boot work. EIM registration gets no response, so cold boot shows LG Home for a few seconds before the guarded fallback opens the launcher |
| Other LG models / firmware / remotes | Unverified |
| macOS build / CLI | Used locally |
| Linux | Scripts intended to support it; not hardware-tested here |
| Windows | Not tested; requires an appropriate shell/toolchain |

The relay requires compatible `LGE M-RCU - Builtin [0]` and `[1]` devices and checks
capabilities before interception. Unsupported or busy devices cause it to exit.
Do not remove these checks to force compatibility.

- Developer Mode expiry may remove sideloaded apps.
- On some firmware (seen on webOS 24) `luna-send-pub` from the Developer Mode shell
  returns no response for `com.webos.service.eim`; `configure-tv.sh` then warns that
  early input restoration is not registered and startup uses the guarded fallback.
- Back navigation inside apps remains theirs; exiting may briefly show LG Home.
- Cold startup is not instant and can begin with a black screen. No fixed startup
  time or improvement across firmware is promised.
- Three short Home presses within two seconds stop interception until a manual helper launch; it does not erase data.
- Network and foreground monitoring depends on local SSAP pairing and connectivity.
- Wheel-to-tile navigation is not implemented; wheel events are passed through.
- App inventory is generated on your computer. Re-sync after installing/removing apps.
- Hiding a tile does not uninstall the app or disable system ads.

This is an alternative launcher, not an LG-supported system Home replacement.

Triple-Home recovery in the updated No-root Helper still needs verification on a physical TV; the reports above describe earlier releases.
