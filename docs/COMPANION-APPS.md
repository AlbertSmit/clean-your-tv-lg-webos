# Companion application entry flows

Home Helper's tile opens an explanatory panel inside Home. It reads controller
status and the saved Home choice without starting input capture or clearing the
emergency stop. Starting a stopped Helper is an explicit, confirmed action.
`nativeHomeAuto: true` remains the silent boot entry; `nativeHomeStart: true` is
used by the confirmed action and by the installer after completing installation.
The detached controller retains its lock, watchdog and emergency release.

The tile entry uses an anonymous public-bus launch rather than registering the
controller's LS2 name a second time. Status recognizes the controller's process
title as well as its script path because webos-service renames its process.

Both standalone Updaters explain that they restore Home after update problems;
normal updates remain in Home settings. Returning to Home is the primary action.
No saved transaction, service failure and an active update have distinct states.
Restore requires a saved prior version and the existing installer safety checks,
then confirmation explaining that post-update settings will be lost. Technical
status and error data are available through diagnostics. Root Updater reopens its
panel on relaunch after returning to Home.

## Home Root icon investigation, 24 October 2026

Read-only inspection of the test TV's installed Home Root 0.1.10 found:

- Both icon PNGs matched the source hashes before this change.
- Sizes were 80 × 80 and 130 × 130; files were readable (0644) and their app
  directory was traversable (0755).
- The installed manifest, application manager and default launch point all
  referred to the same existing `brand-v2-icon.png` and `brand-v2-largeIcon.png`.

These checks rule out a missing or incorrectly packaged resource on that TV.
They do not establish what pixels LG Home displayed or prove a cache failure.
Reusing the same filenames across branding updates can leave cached artwork;
the new Root manifest uses `home-root-icon.png` and `home-root-largeIcon.png`.
Root Updater similarly has its own icon URLs. Both Root symbols omit the R badge.
No TV installation, reboot or cache deletion was performed during this work.
Visual confirmation after installing the updated package remains necessary.

## Verification

Run `bash scripts/test.sh` using the project's Python build environment.
The optional `node tests/companion-ui.cjs` browser suite requires Playwright and
its Chromium browser. Set `CHROMIUM_PATH` to an existing Chrome executable if
needed. It stages the actual Root Updater package, uses deterministic device API
responses and checks manual Helper entry, emergency restart confirmation, remote
navigation, both Updaters, missing service, restore confirmation and relaunch.
Screenshots are written to `build/companion-ui/`.
