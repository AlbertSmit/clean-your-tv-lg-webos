# Update, disable, rollback and uninstall

## Update

Read the release notes. Pause interception with long Home before updating. Keep
known-working packages locally. Do not uninstall first: that can remove app data.

Build the new version, then install helper followed by launcher. Refresh app inventory
and rerun `scripts/configure-tv.sh` to restore pairing/watch configuration if the
installer has replaced state. Manually open Native Home Prototype only when ready.
State preservation across every firmware/installer version is not guaranteed.

## Remove input restoration

Run on your computer with the configured `lgtv` device:

```sh
ares-novacom -d lgtv --run "luna-send-pub -n 1 luna://com.webos.service.eim/deleteDevice '{\"appId\":\"com.gathin.tvhome\"}'"
```

Check for `returnValue: true`. This removes the input registration; it does not
uninstall the applications. First hold Home for two seconds to stop interception.

## Uninstall

1. Hold Home for two seconds to stop interception.
2. Remove input restoration using the command above.
3. Remove the startup task if the service is still installed:

```sh
ares-novacom -d lgtv --run "luna-send-pub -n 1 luna://com.local.nativehome.service/disable '{}'"
ares-install -d lgtv --remove com.local.nativehome
ares-install -d lgtv --remove com.gathin.tvhome
```

Remove any Quick Access assignment manually. Uninstalling the launcher can delete
its saved tile ordering. Keep your local configuration if you want to reinstall.
Revoke the SSAP pairing through TV device/connection settings if desired; erase
`.lgtv-key.json` and `build/setup/ssap-key.json` on the computer when no longer needed.

## Rollback

Pause first, then reinstall your saved previous packages. Reconfigure pairing/input
registration if necessary. Previous helper versions have different recovery behavior;
read their instructions before manually starting the helper. This repository does
not silently downgrade or reset your TV.
