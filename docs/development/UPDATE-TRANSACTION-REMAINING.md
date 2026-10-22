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
3. Implemented locally: the independent updater persists the receipt after the renewal queue drains. The UI snapshot is captured before the pause; its diagnostic history is advisory. The receipt, not that snapshot, controls restoration of the enabled preference.
4. Implemented locally: `importUpdatePause` accepts a validated receipt only from the updater bus identity. It preserves a local user preference, rejects conflicting transactions, cancels scheduling and persists a stopped pause before allowing resume. Package-state erasure is covered by integration tests using both real managers.
5. Implemented locally: resume only after a verified terminal outcome (healthy candidate or verified rollback). Keep ambiguous installer outcomes blocked and visible in recovery.
6. Recover safely if either service exits between every pair of durable writes and RPC replies. Retry must not create a second installation or undo a later user preference.
7. Implemented locally: removed the manual-disable guard. Unavailable state, failed pause or missing receipt still block installation. Validate the complete path in the lab before release.

Do not mark these steps complete based solely on local mocks. A rooted TV and a separate disposable package remain necessary to validate LS2, installation lifecycle and preservation of state.

## Offline LS2 plan

Run `node scripts/plan-updater-permissions.cjs /var/luna-service2-dev` to print a deterministic, hashed plan. It does not write to a TV or register a manifest. The alternative `/var/luna-service2` is accepted explicitly; other roots are rejected. Each plan creates only three dedicated `com.cleanyourtv.updater.permissions` files.

The UI group exposes seven updater methods only. The backend group allows Homebrew `checkRoot`, `getAppInfo`, `install` and renewal `status`, `pauseForUpdate`, `importUpdatePause`, `resumeAfterUpdate`. There are no `all`/`public` grants, wildcard method paths, shell execution, new root service roles or system Home/profile permissions. Updater code now reads versions via Homebrew's wrapper instead of SAM's internal method.

The format follows the locally inspected Homebrew Channel 0.7.3 `services/elevate-service.ts` manifest fields and a captured webOS manifest. Homebrew itself uses broader grants and patches its own manifest; this plan deliberately does not copy that policy.

Not yet established: acceptance of a permission-only manifest, merging of grants for clients that already have a permission entry, service-instance matching, refresh/reboot persistence, and whether package replacement invalidates these grants. A scoped apply/remove implementation and final lab runbook are now available in `scripts/update-permissions.cjs` and `UPDATE-LAB-RUNBOOK.md`; written files are still not evidence of granted rights. Before production deployment, verify these points in the isolated lab, preserve pre-existing content, reject filename collisions, and define rollback that deletes only files whose hashes still match the generated plan. Never replace Homebrew or production app permission files to make a test pass.

The next step is the bounded device session in [UPDATE-LAB-RUNBOOK.md](UPDATE-LAB-RUNBOOK.md). Do not expand feature scope.
