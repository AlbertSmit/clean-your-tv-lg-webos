# Homebrew installation alongside cytv — implementation plan

> **For agentic workers:** Use the executing-plans skill to implement this plan
> task by task in this session. The user requested GPT-6.1 Sol for implementation.
> Do not spawn workers merely to bypass that requested model handoff.

**Goal:** Add installation from Homebrew Channel on rooted TVs while maintaining
cytv and preserving cross-installer updates, profiles and recovery.

**Architecture:** A separate TV installer bootstraps the existing Root product
through shared device-side operations. Homebrew owns the installer package;
System Updater owns product release sets. Both entry points use the same receipts,
package identities and guarded recovery paths.

**Tech stack:** Existing Python 3.9+, TV Node.js 8+, LS2/Homebrew services, existing
web build, reproducible IPK tooling and GitHub release pipeline.

**Spec:** [Homebrew installation design](../specs/2026-10-25-homebrew-install-design.md).

## Global constraints

- Use the temporary managed Homebrew worktree authorized by the user on
  2026-10-26. Save results in Git/PR and remove this worktree after work; preserve
  necessary artifacts separately. Do not switch another task's checkout.
- Implementation branch: `codex/homebrew-install`; PR base: `release/next`.
- Exclusive checkout handoff confirmed on 2026-10-26 by both adjacent tasks.
  Branch `codex/homebrew-install` is checked out from `39dd72c5`.
- GPT-6.1 Sol is selected for implementation.
- Node.js 8+ and Python 3.9+; Root-only Homebrew entry; both cytv editions retained.
- No release version bump during preparation. No catalog/release publication
  from unaccepted artifacts.
- Preserve independent recovery, terminal package evidence, signature checks,
  explicit Home activation and emergency-off state.
- No blanket symlink acceptance and no shell commands supplied by UI input.
- No reset of unknown state, blind retry, deletion of journals or app-only update
  substituted for a complete signed release.
- New setup UI and instructions need the existing ten-language coverage.

## Task 0 — Obtain the checkout and capture the baseline

**Files:** Read `CONTRIBUTING.md`, `docs/RELEASE-FLOW.md`, both plan documents,
`root-edition/UPDATES.md`, `docs/OPTIONAL-PYTHON.md` and `scripts/test.sh`.

- [x] Inspect the current installation architecture and catalog requirements.
- [x] Create the separate branch without switching the active Android checkout.
- [x] Continue with GPT-6.1 Sol after the model selection.
- [x] Ensure the Android task has stopped editing/testing this checkout and has
  saved its work. Re-read `git status --short`; never assume its earlier snapshot
  remains current. Keep `output/` and these plan files out of unrelated commits.
- [x] Switch and refresh the integration base only after that handoff:

```sh
git switch codex/homebrew-install
git fetch origin release/next
git merge --ff-only origin/release/next
npm ci
bash scripts/test.sh
```

If this branch has acquired its own commits, inspect ancestry instead of blindly
using the fast-forward command. Record pre-existing failures separately. Save the
design and plan in a documentation-only commit on this branch.

## Task 1 — Define shared installation state and operation ownership

Foundation reviewed in `85a9f1ae` + `110033d0`; complete current/migration
observers and whole-product removal remain Task 4 dependencies.

**Create:** `root-edition/installation.py`,
`root-edition/tests/test_installation.py`.
**Modify:** `root-edition/deploy.py`, `root-edition/build.py`,
`root-edition/build_updater.py`, `cytv/operations.py`.
**Existing regression:** `root-edition/tests/test_setup_deploy.py`,
`root-edition/tests/test_update_setup.py`, `tests/cytv/test_root_preflight.py`.

**Interface:** `classify(snapshot: dict) -> dict` is pure. Snapshot keys are
`supported`, `packages_match`, `receipts_match`, `pending`, `retained`,
`complete`, `migration_supported`. Return exactly `state`, `can_install`,
`can_maintain`, `reason`. States are `unsupported`, `recovery_required`,
`installed`, `migration_required`, `conflict`, `fresh`. Reason values are fixed
machine codes, localized by the client. Do not include raw private paths/logs.

- [x] Add failing cases for every state, especially pending/retained state taking
  precedence over a matching package version:

```python
def test_pending_matching_packages_are_not_a_finished_install(self):
    result = classify(dict(supported=True, packages_match=True,
        receipts_match=True, pending=True, retained=True, complete=True,
        migration_supported=False))
    self.assertEqual(result['state'], 'recovery_required')
    self.assertFalse(result['can_install'])
    self.assertFalse(result['can_maintain'])
```

- [x] Implement the classifier and a device-side snapshot adapter using existing
  installed-file, runtime-binding and receipt checks. Unknown fields/protocols
  cannot become `fresh`. A complete installation requires all expected components.
- [x] Introduce a shared device lock with operation UUID and durable stage record.
  Bind it to existing updater/deployment journals instead of replacing them.
  Cover deploy and updater entry points in this foundation. Full-project cytv
  removal spans multiple SSH sessions with host-local terminal receipts; Task 4
  must integrate its complete device-side coordination before cross-entrypoint
  exclusion can be marked complete. Never infer terminal completion from a stale
  lock, absent package or dead process.
- [x] Add contention and restart tests with temporary directories and injected
  package observers. One client starts an operation; the second gets status only.
- [x] Package the new module through explicit support inventories; update tests
  that verify those inventories, preserving strict extra-file rejection.
- [x] Run focused tests, inspect diff, commit this tested contract.

```sh
python3 -m unittest discover -s root-edition/tests -p 'test_installation.py'
python3 -m unittest discover -s root-edition/tests -p 'test_setup_deploy.py'
python3 -m unittest discover -s tests/cytv -p 'test_root_preflight.py'
```

## Task 2 — Make startup ownership and direct removal safe

Implemented and reviewed in `4117979d`, with personalization mode fix
`0a8a6f64` reviewed separately (Root 541, System 92, cytv 315 tests
with 23 existing skips). Physical-TV acceptance remains Task 8. Existing updater
state is not silently reprovisioned; supported migration remains Task 4.

**Modify:** `root-edition/startup_hook.py`, `root-edition/service/boot-recover.sh`,
`root-edition/runtime/persistent_lifecycle.py`,
`root-edition/runtime/persistent_recovery.py`,
`root-edition/updater/bootstrap.py`, `system-updater/setup.py`,
`root-edition/build.py`, `root-edition/build_updater.py`, `system-updater/build.py`,
`cytv/root_updater_remove.py`, `cytv/system_updater_remove.py`.
**Tests:** extend `root-edition/tests/test_startup_hook.py`,
`root-edition/tests/test_persistent_recovery.py`,
`root-edition/tests/test_update_setup.py`; create
`tests/system_updates/test_component_removal.py`.

**Interface:** Keep `startup_hook.install(secure, write)` and `remove(secure)`.
Introduce receipt schema 2 with exact `path`, `target`, `owner_app`, `target_sha256`
alongside `version`. Read schema 1 only for verified migration/removal. Store the
previous receipt so failure does not lose ownership evidence.

- [x] Test missing target, foreign symlink, changed target bytes, writable parent,
  wrong owner, copied legacy hook, interrupted migration and repeated removal.
  Use `lstat`/`readlink` to inspect a link itself, not a permissive `resolve` check.
- [x] Package startup scripts under the three owning packages. Atomically replace
  only a previously verified owned hook with the exact intended symlink. The
  link allowance must not change general `secure`/`safe_bytes` semantics.
- [x] Add bounded package-presence checks to already-running lifecycle workers:
  disappearance of Root Home restores LG routing and leaves activation disabled.
  Disappearance of an updater blocks new work and resolves only safely recoverable
  existing work using retained verified code. Do not remove its rollback data.
- [x] Simulate each package disappearing during idle, active Home and each update
  phase. Assert no further routing activation, no update replay and preserved
  recovery evidence. Distinguish the temporary replacement window of an owned
  update transaction from external package deletion.
- [x] Update the existing cytv removal helpers to verify/archive both exact legacy
  copied hooks and new receipt-owned symlinks without following foreign links.
  Include interrupted removal and retained-registration compatibility tests.
- [x] Run lifecycle/update regression and commit. This task gates Homebrew
  publication even though the installer itself is a separate package.

```sh
python3 -m unittest discover -s root-edition/tests
python3 -m unittest discover -s tests/system_updates
```

## Task 3 — Prepare a reproducible offline bootstrap payload

Implemented in `85d9219b` + ABI correction `618c69e5`; scoped reviews passed.
Node 8.12/current and source-free tests passed. Two builds matched 109 files
and 59,862,509 bytes; diagnostic IPK 58,123,938 bytes. This is not the final
installer IPK or physical-TV acceptance.

**Create:** `homebrew/build.py`, `homebrew/payload.py`,
`homebrew/runtime.js`, `homebrew/tests/test_payload.py`,
`homebrew/tests/runtime.cjs`.
**Modify:** `cytv/python_runtime.py` only to extract reusable build-side
normalization if needed; `scripts/test.sh`, `scripts/ci-scope.py`.

**Interface:** `build_payload(root_bundle, root_updater_bundle, supervisor_bundle,
runtime_archive, output) -> Path` produces a manifest with `schema: 1`, exact
component inventories and SHA-256/size per regular file. No recursive wildcard
trust and no network calls during device execution. Runtime JS exports
`inspect(payloadRoot)` and `prepare(payloadRoot)`; inspect never mutates.

- [x] Add tests proving an omitted/extra file, wrong size/hash, unsafe relative
  path, symlink, duplicate archive member, mismatched component baseline and
  invalid runtime binding are rejected before executing payload code.
- [x] Reuse the current Root, Root Updater and System Updater builders as inputs.
  Normalize the currently pinned Python archive during build and include its
  license/provenance. Reuse existing limits and compatible ABI predicates.
- [x] Implement Node 8-compatible streaming verification and constrained runtime
  extraction. Require root-owned parents, exclusive staging, resource limits,
  exact output inventory and smoke/readback checks before selecting an interpreter.
  A valid installed system Python skips private runtime installation.
- [x] Test without Python or a computer-side installer, using only Node and
  existing verified TV utilities. Unsupported ABI and
  inadequate storage return actionable errors with zero installation submissions.
- [x] Build twice in distinct output directories; compare hashes and report IPK
  and temporary-space requirements. If measured limits invalidate offline delivery,
  revise the design before introducing a downloaded bootstrap.
- [x] Register tests in the existing suite/scope selector and commit.

```sh
python3 -m unittest discover -s homebrew/tests -p 'test_payload.py'
node homebrew/tests/runtime.cjs
```

## Task 4 — Reuse one device-side setup coordinator from cytv and TV

**Create:** `root-edition/install_driver.py`,
`root-edition/tests/test_install_driver.py`, `tests/cytv/test_shared_root_install.py`.
**Modify:** `cytv/operations.py`, `root-edition/deploy.py`,
`root-edition/setup.py`, `root-edition/setup_updater.py`,
`system-updater/setup.py`, explicit bundle inventories.

**Interface:** Fixed CLI actions `inspect`, `install`, `status`, `restore`,
`remove`, with validated operation UUID. Explicit `--resume` continues the original
verified request; `status --verify-current` distinguishes historical completion
from fresh installation/removal proof. `install` consumes a verified local
payload and explicit options for migration and supervisor preparation. Emit JSON
events containing `operation`, `stage`, `state`, `code`; diagnostic detail stays
in private logs. Retain existing terminal package-observer evidence underneath.

- [x] Write a fake device adapter that records calls and can fail at every
  package/provisioning boundary. Assert the specified order: verified preflight,
  Root deployment, Root Updater baseline, optional supervisor preparation, final
  readback. Assert Home activation never happens as an install side effect.
- [x] Factor existing local device functions into this orchestration. Keep SSH
  transport and UI-specific host inventory work outside it; use the current
  local service inventory path for TV installation.
- [x] Move the complete Root product removal sequence under the shared device
  coordinator, retaining the existing exact terminal receipts and ownership checks;
  host-local package-absence readback must not unlock a reservation.
- [x] Make cytv invoke the shared coordinator and consume its operation records.
  Preserve its existing status/doctor/recovery interfaces and current safe refusals.
- [x] Test HBC-origin install inspected/maintained by cytv and cytv-origin install
  inspected/maintained by the TV entry point without reset or duplicate install.
  Test pending status, profile preservation, emergency-off and journal conflicts.
- [x] Explicitly supported legacy migrations get tests with exact baseline
  fixtures. Other retained installations remain recoverable, not overwritten.
- [x] Run installer and TV tests and commit.

```sh
python3 -m unittest discover -s root-edition/tests -p 'test_install_driver.py'
python3 -m unittest discover -s tests/cytv
bash scripts/test.sh tv installer
```

Reviewed implementation: `95276cfb`, `d3eb6211`, `8c420232`. Stable aggregate
TV/installer gates passed on `d3eb6211` (Root 583, System 93, payload 8, cytv
324 with 23 existing skips); the final component-lease correction passed 122 Root
and 3 System CLI tests and scoped re-review. Unknown old infrastructure remains
blocked rather than migrated implicitly. Physical-TV acceptance is still Task 8.

## Task 5 — Add the TV installer UI and fixed Homebrew bridge

**Create:** `homebrew/app/appinfo.json`, `homebrew/app/index.html`,
`homebrew/app/app.js`, `homebrew/app/bridge.js`, `homebrew/app/style.css`,
`homebrew/app/i18n.js`, `homebrew/bootstrap.js`,
`homebrew/tests/bridge.cjs`, `homebrew/tests/ui.cjs`.
**Modify:** `homebrew/build.py`, existing TV-web build/scope/test configuration.

**Interface:** `bridge.inspect()`, `bridge.start(options)`,
`bridge.status(operationId)`, `bridge.restore(operationId)` and
`bridge.remove(operationId)` return structured results. The only privileged
command is the fixed installed bootstrap path with enumerated action and validated
UUID. Backend options are validated again, independently of UI validation.

- [x] Verify the documented Homebrew `exec`/`spawn` behavior against its current
  source and fixtures. Lack of HBC, root UID or required methods blocks setup.
  Do not assume a successful LS2 reply establishes root or installation success.
- [x] Test that options containing shell syntax, arbitrary paths/URLs or invalid
  UUIDs never reach exec/spawn. Reopening the UI calls inspect/status only.
- [x] Implement remote navigation and screens for prerequisites, install review,
  progress, installed state, recovery-required and unsupported devices. Show the
  existing product/version when present and offer maintenance rather than reinstall.
- [x] Run the worker independently from the UI and reconnect through the saved
  operation ID. Cancel before submission is supported; after submission the UI
  explains the operation continues and offers status, never blind retry.
- [x] Add explicit Home activation and complete-product removal controls through
  existing guarded flows. Removing the installer package itself is not presented
  as removing the separately installed product.
- [x] Add all ten locales, focus/Back behavior and long-message tests. Reuse
  project icons with provenance; no generated store art is needed for this task.
- [x] Compile through existing compatibility tooling; inspect a packaged preview
  with keyboard/remote-equivalent controls and commit verified changes.

```sh
node homebrew/tests/bridge.cjs
node homebrew/tests/ui.cjs
npm run test:compat
npm run lint:compat
```

Reviewed implementation: `6936b26f` + `049edcaa`. Real installer IPK is
59,594,044 bytes; two builds match SHA256
`b45dd5a06c63eb3cdd8431c5cff4f538c15d90410fde4408bd6efac1883ee91f`.
Node 8/current, compatibility, source-free and packaged UI gates passed;
Homebrew Python 17 and focused coordinator 60 tests passed. Explicit TV
continuation currently covers only backend-proven final-readback cases; earlier
uncertain stages retain status/restore/cytv diagnosis. This remains an automated
UI/package result, not physical-TV acceptance or catalog availability.

## Task 6 — Add release metadata and a reviewable catalog submission

**Create:** `scripts/homebrew-manifest.py`,
`tests/setup/test_homebrew_manifest.py`,
`homebrew/catalog/cleanyourtv-installer.yml`, `homebrew/README.md`.
**Modify after Android changes are integrated:** `scripts/assemble-release.py`,
`scripts/prepare-release.py`, `scripts/publish-release.cjs`,
`.github/workflows/cytv.yml`, release-verification tests as required.

**Interface:** `manifest(ipk_bytes, ipk_url, icon_url, source_url) -> dict` reads
identity/version/title from the built IPK and computes its actual size and SHA-256.
Use `rootRequired: true`. Catalog title is `CYTV Installer`, category `utility`,
pool `main`; point to one stable release-asset manifest URL.

- [x] Add failing tests for malformed IPK, unexpected app identity, version drift,
  non-HTTPS release URL, wrong payload hash, accidental rootRequired false and
  manifest omitted from checksum/publication verification.
- [x] Build the installer from exact candidate artifacts. Generate its manifest
  after packaging and verify the same bytes again after publication. Reuse the
  established publication gate; do not create an independent release workflow.
- [x] Ensure later unrelated releases keep the stable manifest URL valid. Record
  installer version separately from product release versions at candidate freeze.
- [x] Draft the catalog description with prerequisites, product-component/removal
  behavior, source/license, screenshots, hardware evidence and support link.
  Validate schema with the current apps-repo tooling before submission.
- [x] Keep unaccepted artifacts out of stable feeds and do not open a public
  catalog PR before Task 8 passes. Record genuine human review and AI disclosure.
- [x] Run packaging/release tests and commit. A passing manifest test is not
  catalog approval or TV acceptance.

```sh
python3 -m unittest discover -s tests/setup -p 'test_homebrew_manifest.py'
bash scripts/test.sh setup
```

Reviewed implementation: `c5db64e3` through `67eba06f`. Public promotion is
disabled while `homebrew/release.json` is absent; a later accepted record selects
one originating project release and exact artifact bytes. Unrelated releases
carry only previously approved bytes/metadata; unaccepted CI failures are optional,
accepted promotion requires successful workflow/job. Final focused metadata/policy
17, automatic-release 11 and CI-scope 4 tests passed; upstream schema and real
candidate build checks passed. Public reachability, screenshots and hardware/human
approval remain pending; no catalog submission or public delivery occurred.

## Task 7 — Document both paths and run the combined regression

**Modify:** `README.md`, `docs/INSTALL.md`, `docs/MANUAL_INSTALL.md`,
`docs/UPDATES.md`, `docs/CLI.md`, `root-edition/README.md`,
`root-edition/UPDATES.md`, `root-edition/package/README.md`,
`docs/OPTIONAL-PYTHON.md`, `docs/RELEASE-FLOW.md` where packaging requires it,
and all affected guides in `docs/i18n/` (`en`, `ru`, `de`, `es`, `fr`, `hi`,
`it`, `ko`, `pl`, `pt-BR`).

- [x] Explain supported TV requirements, two installation paths, installer-vs-product
  updates, direct package deletion, full removal, interpreter delivery and
  cross-installer recovery. Keep unreleased instructions clearly marked.
- [x] List every persistent path, startup link, service permission and network
  endpoint changed by this feature in the PR description.
- [x] Run the combined suite, package build and integrity checks on this feature
  branch after integrating any changed base. Review the complete diff for unintended
  Android/No-root/telemetry changes.

```sh
bash scripts/test.sh
git diff --check
git diff --stat origin/release/next...HEAD
```

- [ ] Open a draft implementation PR to `release/next` with accurate tests and
  outstanding hardware gates. Attach it to this task. If any issue is linked,
  read its full discussion and maintain its status per AGENTS.md; do not invent
  an issue or claim unrelated reports fixed.

## Task 8 — Physical-TV acceptance, release and catalog gate

**Create:** `docs/development/HOMEBREW-INSTALL-ACCEPTANCE.md` for actual results.
**Update:** release inventory/candidate documentation only through normal flow.

- [ ] Build a candidate; record commit, IPK/bundle hashes, model, webOS, firmware,
  HBC version, Node/Python and initial installation state. Keep private diagnostics
  outside the public record. Obtain a supervised TV session for disruptive tests.
- [ ] Verify this matrix with actual observations, not checked boxes copied from
  older acceptance documents:

| Scenario | Required observation |
| --- | --- |
| Clean HBC install with system Python | Full setup and usable Home without computer |
| Clean HBC install without Python | Verified pinned runtime and full setup without computer |
| cytv install → TV maintenance | Same profile, identity and recovery records |
| HBC install → cytv maintenance | Status, restore and removal work without reinstall |
| Concurrent cytv/TV operations | One owner, second client safely blocked |
| Upgrade and rollback | Complete signed set and preserved profile |
| Lost UI/network/reboot during each stage | Correct persisted status; no blind replay |
| Triple-Home and frozen UI | LG Home restored; emergency-off remains set |
| Standby and cold boot separately | Observed routing/recovery and normal remote input |
| Direct deletion of each installed component | No stranded Home routing or recurring worker |
| Removal of CYTV Installer only | Separately installed product remains coherent |
| Complete product removal | LG Home restored; ownership-verified cleanup |
| No-root cytv regression | Existing install/maintenance still works |

- [ ] Keep failed/unavailable scenarios explicit. Resolve material removal or
  recovery failures before release; never promote automated tests to TV evidence.
- [ ] Complete human review, normal release freeze, exact-candidate validation,
  verified publication and required issue notifications/statuses.
- [ ] Confirm public manifest/IPK URLs and exact hashes, then submit the prepared
  catalog change with honest evidence. Maintainers decide acceptance; an open PR
  is not availability in Homebrew Channel.

## Planning-turn verification and remaining handoff

Only these two documentation files and the new branch reference were created by
this planning task. No application code, device state, release, issue or external
catalog entry was changed. Implementation boxes intentionally remain unchecked.
The model switch and exclusive-checkout handoff must precede Task 0 execution.
