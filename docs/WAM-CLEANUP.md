# Optional Root WAM cleanup

**Unreleased cytv change for issue #95.** These controls are absent from published
installers until a later verified release includes this change. They are separate
from normal installation, diagnostics and the on-TV Homebrew Installer. Do not
run them as routine maintenance: first establish that `/var` is low on space.

## Review and confirm

Close TV applications and keep the TV on. With a matching development desktop
build, open **Maintenance → Clear WAM session data and caches (root required)**.
With a matching console build, run:

```sh
cytv clean-wam-cache --edition root
```

Use your existing trusted Root SSH connection. TV Python is not required; this
path needs verified root-owned Node.js 8+ and safe system tools. A No-root profile,
noninteractive mode or a locally recorded pending installation/removal stops the action. `--yes`
does not authorize cleanup or reboot. Preserve existing recovery records.

cytv inspects only these directories below `/var/lib/wam/Default/`:

- `Session Storage`
- `Cache`
- `Code Cache`
- `GPUCache`

The review shows their total logical file size, which is **not** a prediction of
freed disk blocks. Both cleanup and the later reboot prompt default to **No**.
Session Storage contains app state: deletion may sign you out or lose unsaved
work. The report that a C2 remained signed in is not a guarantee for other apps.
Local Storage, Service Worker, `databases`, managed Python and recovery records
are outside the selected trees and are never cleanup targets.

## Safety checks and failure recovery

The action refuses symlinks, hard-linked files, special files, non-root ownership,
group/other write access, nested mountpoints (including same-device mounts) and
unexpected filesystem boundaries. Inspection reads metadata, not app file
contents. Node preload environment variables are cleared before execution. It hashes the inspected tree metadata; changes before confirmation
stop cleanup before deletion. The TV script rechecks each inode before removal.
Traversal is bounded to 100,000 entries and depth 64; exceeding either limit stops
cleanup. Missing selected folders are a safe no-op. No new dependency, network
endpoint, persistent receipt or startup hook is created.

WAM can still write while the TV runs. If a folder changes during removal, cleanup
can stop after deleting some selected files. The installer reports uncertainty
and never retries automatically. Close apps, inspect the TV and retained storage
state, then decide whether to retry explicitly. Do not broaden the deletion paths
or remove other state to bypass a refusal.

After successful cleanup, reboot the TV explicitly. The optional reboot button
submits one request; SSH disconnection does not prove completion, so cytv leaves
reboot completion unverified and never resubmits it. If you decline, perform a real
TV restart yourself rather than standby. Open deleted files may retain disk space
until WAM exits. Check space over your existing SSH connection after restart:

```sh
df -Pk /var/lib
```

Then start installation explicitly. Initial private-Python provisioning still
requires **320 MiB** free; cleanup does not activate Home or resume installation.
If ABI or ownership checks also fail, solve those separately. Keep the failed
attempt's diagnostic report; do not share SSH credentials or raw app listings.

## Hardware evidence

The issue reporter described recovering space on OLED65C2AUA / firmware 04.40.90 /
webOS 22 by manually clearing these folders and rebooting. No physical TV has
been used to validate this new automated action. Node/shell temporary-filesystem
fixtures verify scope and refusal behavior; they do not establish app session,
reboot, standby or cold-boot compatibility. Device acceptance must record the
exact installer, model/firmware, free space before/after a real restart, resulting
app state and the subsequent Python/Root setup outcome. Keep issue #95 open until
its remaining reported failure and acceptance are resolved.
