# Clean Your TV — LG webOS

**Your apps. A quieter home screen. A way back.**

A community launcher and optional native Home-button helper for LG webOS TVs.
Based on [webos-vibehack](https://github.com/OmkarK97/webos-vibehack).
**No root. No firmware flashing. No always-on computer, Raspberry Pi or router script.**
The launcher and native helper run on the TV itself on the tested setup.
A computer is needed to build, install and configure them, and later for updates;
it can be switched off during everyday use. No USB drive or external server is required.
LG Developer Mode must remain active. Local network connectivity is still needed
for the helper's paired power/foreground monitoring.

> Tested on **LG OLED55C3RLA (C3), firmware 43.21.71**.
> Other models, remotes and firmware versions are unverified. Not affiliated with LG.

[Install](docs/INSTALL.md) · [Recovery](docs/RECOVERY.md) ·
[Compatibility](docs/COMPATIBILITY.md) · [Build](docs/BUILD.md) · [Update & remove](docs/MAINTENANCE.md)

![Clean Your TV menu with a five-app dock and Inputs, Wi-Fi and Settings shortcuts](docs/launcher-menu.png)

*Launcher 1.0.11, rendered locally with an example five-app configuration.
Your apps and their order are configured during setup; they are not bundled.*

## What it does

| Feature | Behavior |
| --- | --- |
| Personal home screen | Local app grid, configurable dock, hidden tiles and tile ordering; no sponsored rows in this launcher |
| Short Home | Native on-TV interception returns to the launcher without passing through LG Home on the tested setup |
| Hold Home for 2 seconds | Stops interception and returns to LG Home |
| Resume interception | Manually open **Native Home Prototype** from LG Apps |
| Wi-Fi shortcut | Opens LG's network setup overlay |
| Automatic startup | Returns after standby and cold boot using input restoration plus a guarded fallback helper; no external device runs the startup logic |
| Exit with Back | Returns after watched apps exit, preserving in-app navigation and exit confirmation; LG Home can briefly flash |
| Quick standby/resume | Avoids relaunching a launcher already restored by webOS, preserving arrows and OK after a fast power cycle |
| Remote controls | Arrows, held arrows, OK, volume and pointer remain usable; wheel events are forwarded |
| Failure recovery | Watchdog cleanup releases interception if the handler stalls; long Home provides a manual escape |
| Local interface | App tiles, font and splash assets are stored locally; the menu does not wait for an Internet download |

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
