# Clear Your TV — LG webOS

**Your apps. A quieter home screen. A way back.**

A community launcher and optional native Home-button helper for LG webOS TVs.
Based on [webos-vibehack](https://github.com/OmkarK97/webos-vibehack).
No firmware replacement or router process is required on the tested setup.

> **Experimental release.** Tested on **LG OLED55C3RLA (C3), firmware 43.21.71**.
> Other models, remotes and firmware versions are unverified. Not affiliated with LG.

[Install](docs/INSTALL.md) · [Recovery](docs/RECOVERY.md) ·
[Compatibility](docs/COMPATIBILITY.md) · [Build](docs/BUILD.md) · [Update & remove](docs/MAINTENANCE.md)

## What it does

| Feature | Behavior |
| --- | --- |
| Personal home screen | Local app grid, configurable dock, tile ordering |
| Short Home | Returns to the launcher while the helper is active |
| Hold Home for 2 seconds | Stops interception and returns to LG Home |
| Resume interception | Manually open **Native Home Prototype** from LG Apps |
| Wi-Fi shortcut | Opens LG's network setup overlay |
| Startup | Input restoration plus a guarded fallback helper |
| Exit with Back | Returns after watched apps exit; LG Home can briefly flash |
| Quick standby/resume | Avoids relaunching a launcher already restored by webOS |

This does not remove system advertisements, uninstall apps, or replace the operating
system's Home destination. It provides an alternative screen. Cold boot still has
an initial black interval; early display timing is under investigation.

## Get started

1. Enable LG Developer Mode and pair the webOS CLI with your TV.
2. Run the app-sync tool to build an inventory for **your** TV.
3. Build your personalized launcher and install the optional helper.
4. Configure the helper, then test long-Home recovery before daily use.

Follow the [installation guide](docs/INSTALL.md). The generic launcher release asset
has an empty inventory: sync and rebuild it before use. The helper asset is ready
to install on compatible ARM32 devices, but still needs local pairing/setup.

## Tested release

Launcher **1.0.11** + helper **0.6.12**. Two quick standby/resume cycles passed after
the focus fix, including arrows, OK and short Home. Earlier tests covered volume,
pointer, long-Home recovery and watchdog cleanup. The public build replaces the
original owner's watched-app list with your locally generated configuration;
that packaging/setup path has not yet been tested by a second user.

Developer Mode must remain active. A LAN outage can affect the optional power and
foreground watcher. Wheel input is forwarded, but wheel-to-tile selection is not
implemented. See [known limits](docs/COMPATIBILITY.md).

## Project layout

```text
launcher/          Web launcher and local splash image
native/app/        Home controller, policies and native entry point
native/prototype/  Remote relay/filter source and tests
native/service/    Guarded startup service
scripts/           Build and setup tools
docs/              Installation, recovery and limitations
```

## Credits

Built on the work of [OmkarK97/webos-vibehack](https://github.com/OmkarK97/webos-vibehack)
and [Gathin23/cleanyourtv](https://github.com/Gathin23/cleanyourtv).
MIT-licensed project code; Outfit uses SIL OFL and the bundled ws library uses MIT.
See [LICENSE](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md).

No firmware images, extracted proprietary binaries, TV credentials or personal
app inventories are included. Please redact logs before opening an issue.
