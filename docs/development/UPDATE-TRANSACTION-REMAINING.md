# Completing TV updates after the isolated test

This is an implementation checklist, not a working installation guide.

## Permission boundary

The C3 test showed that an installed JS service receives its own UID and a limited LS2 client permission set. Adding groups to `services.json` did not grant them. Direct SAM `getAppInfo` requires internal application permissions on this firmware. Homebrew exposes its own `getAppInfo`, but the laboratory updater could not call that endpoint either. The prototype must not advertise successful installation until the full package setup is tested.

Prepare a root-only setup path with narrow grants for the updater, rather than granting `all` or changing Homebrew's existing permissions. Required edges are:

- Home / Updater UI → the independent updater's explicit methods, still checking bus application identity.
- Updater → Homebrew checkRoot, getAppInfo and install.
- Updater → renewal status and transactional pause/resume.
- Home → its own renewal service, unchanged.

Only updater-owned permission artifacts may be installed or removed. Preserve pre-existing files and validate exact bytes before rollback. Account for manifest refresh, service restart, package replacement and reboot. No changes to production Home profiles, helper, or startup configuration are needed for this work.

## Pause protocol already implemented locally

`pauseForUpdate(id)` immediately prevents new renewal requests, waits for the service queue, persists the old enabled state, cancels the scheduled activity and marks the pause confirmed only after successful cancellation and persistence. The pause survives service restart. Retry uses the same ID and rechecks cancellation.

`resumeAfterUpdate(id)` accepts only the matching confirmed pause. Disabled remains disabled; previously enabled is scheduled again. Manual disable during the pause overrides the old preference. Schedule/write failures leave a retryable, stopped state. The two endpoints accept only the updater's LS2 service identity, with no caller-supplied identity fallback.

## Transaction integration progress and remaining work

1. Implemented locally: persist a unique transaction ID and intent in the independent updater before requesting a pause.
2. Implemented locally: require matching ID, confirmed pause, disabled state and no error before installation.
3. Receipt persistence in the independent updater is implemented locally. Move final profile capture after the queue has drained when the UI guard is removed.
4. Define a restricted receipt-import operation for the newly installed renewal service: package installation may remove its old state. Keep this operation bound to the updater identity and transaction, never a general enable-from-profile flag.
5. Implemented locally: resume only after a verified terminal outcome (healthy candidate or verified rollback). Keep ambiguous installer outcomes blocked and visible in recovery.
6. Recover safely if either service exits between every pair of durable writes and RPC replies. Retry must not create a second installation or undo a later user preference.
7. Only then remove the manual-disable UI guard and replace it with automatic progress text.

Do not mark these steps complete based solely on local mocks. A rooted TV and a separate disposable package remain necessary to validate LS2, installation lifecycle and preservation of state.
