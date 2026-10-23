# Root candidate runtime

Install these Python files under `/var/lib/clean-your-tv-root/runtime` as root-owned files without group/world write permission. Python 3 and `/usr/bin/luna-send` are required. Invoke `/usr/bin/python3 /var/lib/clean-your-tv-root/runtime/cli.py COMMAND` as root.

- `status`: read actual system profiles and independent Home setting, journal and recovery integrity.
- `trial`: activate **com.cleanyourtv.root.preview** for at most 60 seconds using a detached rollback guardian. Refuses any unresolved journal, unexpected baseline, missing Home registration or missing recovery provisioning.
- `restore`: conflict-checked removal of only the owned override, rescan, restore stock Home and verify the full original profiles. Retries bounded transport failures. Exit 2 means recovery is unresolved; preserve state for retry/investigation.
- `boot`: recovery-only callback. Spawns recovery for a pending transaction unless the exact live guardian owns it. A failsafe marker overrides that exception.
- `enable` / `confirm`: rejected with `hardware-validation-required`. This candidate has no permanent activation mode.

Runtime state is `/var/lib/clean-your-tv-root`; owned profile is `/var/webos-profile/override/clean-your-tv-root.json`. Both directories must be root-owned and not group/world writable, and must reside on the same filesystem for crash-safe hard-link publication. Runtime never edits app files, stock libraries, zoom behavior, or the existing no-root launcher.

Recovery provisioning is `recovery-provision.json`: version 1, mode `recovery-only`, absolute `boot_callback`, and `files` mapping absolute callback and every runtime Python path to its SHA-256 hex digest. All files and ancestors must be trusted. The installed callback must invoke the fixed runtime `cli.py boot`. The installer finalizes this manifest only after boot activity registration is verified. A valid manifest establishes installed-byte integrity, not hardware acceptance.

Device-specific assumptions requiring hardware acceptance: webOS systemprofile getProfiles/debug/rescan methods; defaultApps and idleApp schema; settingsservice general.defaultApps readback representing SAM's setting; applicationmanager setDefaultApp; appCategory home registration; stock app `com.webos.app.home`; Linux `/proc` guardian identity; `/var/luna/preferences/webosbrew_failsafe`; filesystem durability; boot activity delivery under reboot and failsafe. Trial requires all three original routing values to name stock Home and idleApp.support true.

Local tests exercise policy, real file ownership/conflict handling, subprocess timer readiness, abrupt publication process death, provisioning gates, isolated identity and restoration. They do not establish TV boot, remote Home/Back routing or power-loss behavior.

## Existing No-root helper

Trial preflight refuses an existing controller PID marker or running known No-root relay, including ambiguous stale markers. It rechecks before publishing the profile. It never edits the helper's control or blocked files and never relaunches that app. The legacy `stop` command creates the same blocked latch as a user disable, while manual relaunch clears it; an automatic stop/relaunch cannot preserve user intent. Explicitly stopping the old helper is therefore required before this candidate's trial; it remains stopped afterward. Transparent pause/resume requires a separate transaction-aware helper protocol and is not provided here. Do not launch the helper during a Root trial.

During hardware acceptance, use the existing long-Home gesture to disable the No-root helper first. After Root restoration, verify stock routing and explicitly use the existing helper button to re-enable No-root if desired. Neither runtime nor uninstaller removes stale controller markers automatically; investigate stale state rather than blindly deleting it.
