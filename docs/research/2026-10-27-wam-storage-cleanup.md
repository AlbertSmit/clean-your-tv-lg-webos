# WAM storage cleanup: source review and C3 experiment

Reviewed 2026-10-27 to decide how PR #100 can offer explicit cleanup without
root-owned filesystem deletion of live, service-owned WAM data.

## Primary-source findings

| Project/source | Observed approach | Consequence for this project |
| --- | --- | --- |
| [Dev Manager device storage](https://github.com/webosbrew/dev-manager-desktop/blob/d4a6044706a97165452943d0886d2fe3de3df69b/src/app/core/services/device-manager.service.ts#L134) | Runs `df` for a specified mount point; defaults to `/media/developer`. The maintainer distinguishes developer-app space from LG's user-visible storage in [issue #392](https://github.com/webosbrew/dev-manager-desktop/issues/392). | Measure `/var/lib` explicitly. Removing apps on another filesystem is not proof that private Python has room. |
| [Dev Manager staging](https://github.com/webosbrew/dev-manager-desktop/blob/d4a6044706a97165452943d0886d2fe3de3df69b/src/app/core/services/app-manager.service.ts#L199) | Uses unique installer staging files and cleans its owned partial upload on failure. It stages on the developer partition because webOS 11 appinstalld cannot use `/tmp`. | Clean only files owned by a known operation; do not treat arbitrary app data as disposable installer leftovers. |
| [Homebrew Channel install service](https://github.com/webosbrew/webos-homebrew-channel/blob/1a2b969e992617c9ba4b8a891542cb93a9e07b0a/services/service.ts#L450) | Downloads a unique IPK, verifies its hash, and delegates install/remove to appInstallService. The inspected install path is not a general WAM/session cleaner. | No equivalent universal filesystem cleanup was established from this source. Its temporary path is not evidence that every TV's installer can use the same path. |
| [webOS OSE WAM API](https://www.webosose.org/docs/reference/ls2-api/com-webos-service-webappmanager/#clearbrowsingdata) and [type mapping](https://github.com/webosose/wam/blob/a486711e2f093723609bd76d0566bf05edae1fcb/src/platform/webengine/blink_web_view_profile_helper.cc#L40) | `clearBrowsingData` passes explicit types to WAM's browser profile. `cache` and `codecache` have separate masks. Missing types defaults to all; `all` includes substantially more app data. The published type list has no independent Session Storage type. | Prefer the fixed pair `cache`, `codecache`. Never probe with empty/default parameters, request `all`, or substitute localStorage to claim Session Storage cleanup. |
| [webOS OSE dispatch](https://github.com/webosose/wam/blob/a486711e2f093723609bd76d0566bf05edae1fcb/src/webos/web_app_manager_service_luna.cc#L285) | Validates type names, dispatches the removal mask and returns a positive reply. The downstream removal call is void. | Treat reply as acceptance, then measure actual space; a reply alone is not completed disk recovery or installer success. |
| [WAM launch configuration](https://github.com/webosose/wam/blob/a486711e2f093723609bd76d0566bf05edae1fcb/files/launch/upstart/WebAppMgr.conf.upstart.in) | Uses the `wam` account and assigns its data directory to that account. | Service ownership is expected; it is not evidence of a damaged directory that should be chowned to root. OSE does not establish retail-TV compatibility. |
| [webos-iptv-player storage design](https://github.com/lennylxx/webos-iptv-player/blob/main/docs/storage-and-data.md) | Separates recreatable app-managed cache from settings, accounts, personal data and service-owned uploads. Clear Cache and Reset App are distinct operations. Its cache control does not claim to clear Chromium's HTTP cache. | Explain the exact data class affected and preserve the distinction between cache cleanup and session/account reset. |

Search results and source absence are not proof that no other cleaner exists.
Third-party commands were read as evidence; none was downloaded/executed on the TV.

## Read-only C3 investigation

Device: OLED55C3RLA, firmware 43.21.71, SDK 11.2.0. Existing Root SSH was used.
The original PR's filesystem cleaner refused before deletion because WAM's fixed
data directories belong to `wam` UID/GID 505, mode 755. Node v20.12.2 was present,
but the final native API approach does not require TV Node/Python.

The three observed `wam` processes belonged to `webapp-mgr.service`. PID1 was
systemd 255; the unit had Restart=on-failure and KillMode=control-group. No service
was stopped, masked or reconfigured. `ls-monitor -i com.webos.service.webappmanager`
confirmed that `clearBrowsingData` exists. Introspection was used instead of a
potentially destructive API probe.

Allowing UID505 in the old root deletion script would weaken its race assumptions.
Directory descriptors alone do not atomically bind an unlink to the inode checked
immediately before it. A service stop/mask design would require independent recovery,
writer/respawn exclusion and device-specific dependency acceptance. The native cache
API avoids adding that subsystem or changing ownership.

## Separately authorized physical API experiment

The operator approved one call with exactly:

```json
{"types":["cache","codecache"]}
```

Method: `luna://com.webos.service.webappmanager/clearBrowsingData`. No other cleanup
type, service stop, app launch, installation or reboot was requested.

| Measurement | Before (KiB) | After (KiB) |
| --- | ---: | ---: |
| Free in `/var/lib` filesystem | 511948 | 612704 |
| WAM Cache | 48880 | 132 |
| WAM Code Cache | 52412 | 404 |

The API replied `returnValue: true`; available space increased by 100756 KiB
(**98.39453125 MiB**). WAM stayed active. Aggregate identity/content fingerprints
of Session Storage, Local Storage, Service Worker, databases and cookie files were
unchanged. The private observation receipt is kept outside the repository;
addresses, credentials, app inventories, filenames and fingerprints are not published.

This direct API experiment was performed while reviewing source 227eda94, before
the native backend rewrite. It is not an exact frozen-installer acceptance test.
It did not reproduce low-space provisioning: free space already exceeded 320 MiB.
The Session Storage directory was only 32 KiB, unlike the C2 report's large buildup.
App login/playback behavior was not manually confirmed, and no reboot was tested.

## Agreed implementation direction and remaining gates

The maintainer selected native API automation for cache/codecache only, with
Session Storage left to explicitly warned manual maintenance. Keep Root-only
interactive default-No consent, `--yes` refusal to bypass consent, pending-operation
guards, bounded advisory measurements, a manual alternative, exact type allowlisting
and uncertain-outcome reporting without automatic retries or filesystem fallback.

The rewritten source backend’s read-only inspection and default-No console cancel
were also exercised on the C3 with --yes: zero cleanup Luna calls occurred.

Verify combined candidate checks and the
release inventory. Record the exact installer separately before release acceptance.
C2 Session Storage and original installation success remain unresolved; do not close
issue #95 or promote its status to released based on this C3 cache experiment.
