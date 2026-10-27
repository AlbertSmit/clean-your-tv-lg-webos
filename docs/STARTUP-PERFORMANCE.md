# Home startup measurements

Both Home editions expose `window.HomeStartup.snapshot()` in the local Web
Inspector console. It returns a copy of a fixed, bounded set of first-occurrence
elapsed times in milliseconds. Timing starts when `startup-metrics.js`, the first
Home source script, executes. It uses `performance.now()` when available and
`Date.now()` otherwise. Earlier document loading, CSS loading and TV app launch
work are outside this clock. Date-clock adjustments can affect the fallback.

Nothing is persisted, logged automatically or uploaded. The record contains only
fixed milestone names and numeric durations: no app IDs, inventories, addresses,
locale values, credentials or widget contents. Repeated refreshes, key presses and
resume events cannot grow or overwrite the record. A newly loaded document starts
a new record; returning to a retained document preserves its original sample.

| Milestone | Meaning |
| --- | --- |
| `firstJS` | Start of the first Home source script, always zero. A build's compatibility polyfills may execute earlier. |
| `languageReply` | First locale service callback, including unsuccessful replies; absent when no request is made or no callback arrives. |
| `languageReady` | Language gate released, including saved preference, service failure or timeout fallback. |
| `profileGateStart` | Edition-specific profile checks begin after the language gate. |
| `profileGateComplete` | Profile gate allows the main app script to load. This does not certify profile restoration or health. |
| `profileGateBlocked` | Profile recovery prevents the main script from loading. |
| `appStart` | Main app script begins executing. |
| `gridCreated` | First synchronous grid rebuild and initial focus assignment finish. |
| `inventoryRefreshStart` / `inventoryRefreshComplete` | Initial live inventory request starts / its callback and any permitted refresh finish, including failure fallback. Completion does not prove a successful inventory response. |
| `firstPaintProxy` | Two animation-frame callbacks after synchronous app setup; a rendering-opportunity proxy, **not actual first paint**, visible cards, decoded images, or animation completion. Timers are used only if animation frames are unavailable. |
| `firstHandledKey` | First keydown accepted by the main Home navigation/launch handler, including a navigation boundary. Unrecognized keys do not count. Modal-only interactions before that handler do not count. |
| `widgetsCreated` | Decorative widget DOM creation completes, including hidden widgets. |
| `widgetDataFirst` | First active widget watch callback is applied; it can contain an unavailable/empty state. Absent when widgets are hidden or no watch result arrives. |

Inspect differences such as `appStart - profileGateStart` for profile-gate wait,
`gridCreated - appStart` for initial grid work, and
`inventoryRefreshComplete - inventoryRefreshStart` for initial inventory request
and callback work. Missing marks mean the milestone has not occurred; they are
not zero-duration successes. Existing update health verification is independent
of all these metrics and retains its existing rendered-grid/profile checks.

## Device procedure

Record edition, package version, TV model, firmware, appearance, widget visibility,
number of tiles, and whether measurement tools were attached before each run.
Keep private device information and inventory contents out of shared evidence.
Use the same navigation key and send it at a consistent point after Home appears;
`firstHandledKey` includes the operator's waiting time and is not input latency.
Copy only the numeric snapshot into the results. Do not export console logs or
private diagnostics. Record visible startup and input behavior alongside timings;
the proxy cannot establish those outcomes.

Measure these cases separately, with several repeats and individual samples plus
the median/range for each case:

1. **Cold boot:** shut down and remove power using the TV's normal safe procedure,
   then boot and open Home. Record the power-off interval and Quick Start setting.
2. **Standby resume:** use the remote to enter standby and resume. Record standby
   duration and Quick Start setting. Check whether Home retained its document:
   unchanged first-only marks are the original startup sample, not resume latency.
3. **Reopen:** launch another app and return to Home. Record whether Home was
   retained or recreated. A retained document does not produce a fresh startup
   sample. Separately closing/recreating Home measures a new document and should
   be labeled as such.

Do not mix cold-boot, standby, retained reopen and recreated-document results.
For retained resume/reopen, measure external elapsed time and verify focus/input
behavior separately; this bounded startup record deliberately does not collect a
history. Browser tests cover hook behavior and compatibility fallbacks, not
physical TV speed or compatibility. No physical TV measurement has been made as
part of the instrumentation implementation.

## Automatic system-language cache

Automatic language selection stores the last successful system UI locale in
`tvhome.system-language.v1` in local storage. The value is one canonical supported
language code (for example, `de` or `pt-BR`); a well-formed unsupported system
locale uses `en`. This is a local startup cache, separate from the user's
`tvhome.language` preference and the captured profile settings. It adds no
profile schema fields, permissions or network endpoints. Locale values are not
included in startup metrics or logged.

With Automatic selected and a readable valid cache, Home releases the language
gate immediately using that cached language. The existing system locale request
runs in the background with its 1200 ms deadline. If a successful reply selects a
different canonical language, Home reloads only after saving and reading back the
new cache, and only while the preference is still Automatic. The existing page
keeps its language until the reload, so it does not mix newly translated labels
with the original interface. Regional changes that select the same supported
language do not reload. A user language choice takes precedence over a pending
system reply.

A missing, invalid or unreadable cache retains the blocking system request and
navigator-language fallback. Malformed replies, service failures, timeouts and
failed cache persistence cannot trigger a background reload. A future document
can retry the system request.

For measurements, distinguish the first document without a valid cache from
subsequent recreated documents with a valid cache; neither case establishes
whether the TV itself cold-booted. On a cached startup, `languageReady` can precede
`languageReply`. When checking a changed system language, record the initial
cached document and the replacement document separately: each has its own startup
record. Also check failed/unavailable service behavior and a user language choice
made before the background reply. No physical TV timing or acceptance is implied
by the cache's automated tests.
