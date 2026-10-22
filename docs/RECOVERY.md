# Controls and recovery

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
