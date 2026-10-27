# Optional Root WAM cache cleanup

**Unreleased 1.4.0 candidate behavior; absent from published installers.**
This is a separate console/desktop maintenance action, not part of installation,
diagnostics, Android UI or the on-TV Homebrew Installer. First check whether
`/var` is actually short of space. A large app-storage total on another partition
does not establish that private Python has enough space in `/var/lib`.

## Review and confirm

Close TV apps. In a matching candidate desktop build, open **Maintenance → Clear
WAM caches (root required)**. In a matching console build, run:

```sh
cytv clean-wam-cache --edition root
```

Use your existing trusted Root SSH connection. TV Python and Node are not needed.
No-root profiles, noninteractive mode and locally recorded pending installations
or removals are refused. Preserve recovery records and resolve those operations
first. `--yes` cannot authorize this action; the cleanup prompt defaults to **No**.

The review shows approximate disk usage of `Cache` and `Code Cache`, available
space in `/var/lib`, the manual alternative and these limits:

- The only requested WAM types are `cache` and `codecache`.
- Session Storage, cookies, Local Storage, Service Worker and databases
  are not requested for deletion. This is not a reset of all app data. GPUCache
  is not a separately selected path; internal shader-cache handling belongs to
  the TV engine and is not promised unchanged on untested firmware.
- Apps may download or rebuild cached data; their next launch can be slower.
- Sizes are estimates, not a locked snapshot or a promise of recovered space.

cytv calls the TV's own `com.webos.service.webappmanager/clearBrowsingData` API.
It never deletes WAM files itself, changes ownership, stops/masks services or
falls back to a shell cleanup when the API is missing, denied or unconfirmed.
An omitted `types` argument or `all` would clear a much broader set of data; cytv
always sends the explicit fixed pair above.

A positive reply means the request was accepted. Recheck actual free space:

```sh
df -Pk /var/lib
```

If the connection fails, some cache may already have been cleared. Inspect space
before deciding to retry; cytv does not retry automatically. No reboot, service
restart or installation resume is requested. Start setup again explicitly after
checking space. Initial private-Python provisioning still needs **320 MiB** free;
cache cleanup does not resolve ABI, ownership or interrupted-operation failures.

## Free space yourself instead

Cancel the action if you prefer manual maintenance. Removing unused apps in LG
settings may help their installation partition, but may not free `/var`; verify
`df -Pk /var/lib` afterwards. Never delete private Python or recovery records to
make room, and do not change ownership of WAM's service-owned directories.

For an experienced Root operator, inspect only the known storage first:

```sh
df -Pk /var/lib
du -skx "/var/lib/wam/Default/Session Storage" /var/lib/wam/Default/Cache "/var/lib/wam/Default/Code Cache" /var/lib/wam/Default/GPUCache
```

**Manual Session Storage deletion can sign you out and lose unsaved app state;
it cannot be undone.** The C2 reporter remained signed in, which is not a promise
for other apps. A running WAM can change files and hold deleted data open. Before
manual deletion, establish a device-specific maintenance procedure that prevents
all WAM writers and respawns, and includes verified recovery of TV services. A
single process check or closing visible apps is not such a barrier. Service names,
stop propagation and recovery differ across firmware; do not copy an unverified
stop/mask sequence or alter ownership to bypass the automatic action's limits.

Only after that prerequisite is satisfied, and after reviewing the exact path,
the destructive Session Storage command is:

```sh
rm -rf -- "/var/lib/wam/Default/Session Storage"
```

Local Storage, Service Worker, databases, cookies and recovery state remain outside
that path. Restore the services using the reviewed maintenance procedure. If a real
TV restart is required, explicitly choose when to run `reboot` once; standby is
not a restart. Then recheck space and app state before starting setup again. Do
not infer successful cleanup or reboot from SSH disconnection.

## Evidence and remaining acceptance

On OLED55C3RLA / firmware **43.21.71**, SDK **11.2.0**, a separately authorized
single API request for `cache` and `codecache` returned true. Free space increased
from **511948 to 612704 KiB** (about **98.4 MiB**); WAM remained active. Aggregate
content/identity fingerprints of Session Storage, Local Storage, Service Worker,
databases and cookie files were unchanged. No reboot or install was performed.
The original root-owner-only filesystem cleaner refused this TV's normal `wam`
UID 505, which motivated using WAM's native API instead of relaxing deletion guards.

This was a direct API experiment, not acceptance of an exact frozen installer.
The C3 had about 500 MiB free before testing, so it did not reproduce the reporter's
low-space installation failure. Exact candidate installer checks, normal app
behavior and other models/firmware remain acceptance work. The reported C2's large
Session Storage is not automatically cleared; issue #95 remains partially addressed
and open. See the [source review and measurements](research/2026-10-27-wam-storage-cleanup.md).
