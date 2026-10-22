# Controls and recovery

For a **one-script installation**, run CLI commands from the repository folder.
The CLI is local; expose it in your current terminal:

```sh
export PATH="$PWD/build/tools/node_modules/.bin:$PATH"
```

The automatic device name is `clean-your-tv-<IP-with-dashes>` (for example
`clean-your-tv-192-168-1-50`), or the `DEVICE` override you supplied. Replace
`-d lgtv` in the commands below with `-d clean-your-tv-192-168-1-50`, using your
actual device name. Manual installations below use the profile `lgtv`.

- **Arrows / OK:** select and open apps. Hold OK on a tile to reorder it.
- **Short Home:** return to the launcher while the helper is active.
- **Hold Home for about two seconds:** release interception and open LG Home.

Long Home is an emergency stop, not a factory reset. It preserves preferences but
leaves a persistent stop flag. Automatic startup respects that flag. To resume,
select **Resume Home** in the launcher or open **Home Helper** manually from LG's app list, or run:

```sh
ares-launch -d lgtv com.local.nativehome
```

Opening the launcher alone does not clear the stop flag. If you hold Home by
accident, manually starting the helper restores interception. This release has no
pause/resume dialog; that UI remains an unreleased prototype.

If the helper fails, heartbeat timeouts and process cleanup release the physical
remote. Do not repeatedly clear stop flags after a failure: use LG Home and report
the issue. Keep the launcher assigned to a Quick Access key as another entry point.

If a quick power cycle leaves tiles visible but unresponsive, try long Home and
check arrows on LG Home. Report the helper version and whether it reproduces with
the helper stopped. Version 0.6.12 avoids a duplicate launch after system restoration.
