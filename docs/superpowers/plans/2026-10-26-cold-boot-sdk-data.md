# Cold-boot SDK DATA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. One coupled implementation owner; dependent reviews are read-only.

**Goal:** Support observed post-boot SDK0777 DATA through private byte authority while keeping privileged execution and disabled/unknown recovery strict.

**Architecture:** A digest-required SDK reader and canonical phase-aware private metadata resolver replace installed mode authority. Existing private current/transaction records remain authoritative; System setup retains authenticated own-package proof. No shared permission repair or retained-code overwrite.

**Tech Stack:** Python3.9+, existing Node8 HBC runtime, standard library and existing bounded IPK parsers; no new dependencies.

**Spec:** ../specs/2026-10-26-cold-boot-sdk-data-design.md

## Global constraints

- Only allowlisted rooted SDK app/service/package DATA gains ordinary rwx tolerance after independent digest verification; private code/runtime/receipts/staging/hooks stay strict.
- Keep ownership/type/nofollow/link/size and descriptor/path/content binding checks; retain exact shared metadata UID501 exception only there.
- No hash adoption from installed bytes; no arbitrary prior/candidate/cache fallback; no unknown-outcome replay or fabricated terminal.
- Marker admission must write current-boot evidence and return even while HBC failsafe exists; only later rearm waits for marker/cleared flag. Never deadlock init.d.
- Preserve emergency/off, normal-boot/failsafe/profile/guardian checks and independent LG recovery. Current TV is disabled after the failed cold boot; source work does not enable it.
- No live private-code/receipt patching. New code reaches the TV only via supported, reviewed fresh provisioning with archives and explicit setup/activation.
- Preserve No-root/Helper policy and pinned Helper0.6.19. Existing unpublished targets remain Root0.4.0, Updater0.3.0, supervisor1.1.0/protocol1, cytv0.4.0, proposed Installer0.1.0; final source must be rebuilt.
- Existing initial HBC privileged-launch/browser trust assumptions remain explicit. Shared sources are never privileged import/exec inputs after anchored private staging.
- Follow CONTRIBUTING.md, release inventory/PR documentation and cleanup only this owned temporary worktree after preserving commits/artifacts.

## Preflight — completed evidence

- [x] Read-only actual cold-boot diagnostics: all three product SDK trees/metadata0777, UID0/no symlinks; private recovery healthy, intent disabled, no pending package request. Normal marker missing; modes cause both identity/mode readback failures.
- [x] Independent source audits saved privately: /private/tmp/cytv-cold-boot-boundary-design-options.md and /private/tmp/cytv-cold-boot-boundary-review.md.
- [x] Preserve prior source/tests/artifact identities and failed hardware record in release PR64. Original package-DATA/private-execution architecture and supervised Root rebootstrap are already authorized.

## Task 1 — Coherent SDK DATA authority correction

This is one trust contract: separating resolver/writers from consumers would leave phase-dependent guards unreviewable. No parallel source mutation.

**File map**

- Canonical DATA reads/resolver: root-edition/package_data.py and a focused root-edition/package_identity.py (or clearly justified equivalent). Reuse existing strict private readers/bounded IPK parser with an explicit source-free bundled closure.
- Identity/readback consumers: root-edition/startup_guard.py, runtime/device_adapter.py, installation.py, install_device.py, deploy.py; rooted paths in updater/device.py and system-updater/device.py. Retain No-root/Helper paths under their current policy.
- Private proof writers/continuations: root-edition/updater/bootstrap.py and existing Root/System transaction commit/rollback selection interfaces; system-updater/setup.py must persist authenticated own IPK/inventory before it can be lost, and gate installed authority by actual terminal/readback. Prefer existing content-addressed private cache + bootstrap pin over another mutable current record.
- JS intake: homebrew/runtime.js (bootstrap only if the explicit original pin contract requires it), matching runtime/bridge/payload tests. Keep private snapshots, copied hashes, archive pin, original loaded manifest authority and trusted private modes.
- Bundles/inventories: Root deploy SUPPORT_FILES/runtime, Root build/build_updater, System build CODE/infra, HBC payload helper equality, host coordinator and source-free imports. New helper hashes are declared without making old mandatory-five legacy proof/removal incompatible.
- Tests: package_data/identity/installation/startup guards; Root and System updater phase/integrity/rollback tests; HBC JS intake; host cross-client/emitted fixture tests.
- Docs: approved architecture specs, docs/development/HOMEBREW-INSTALL-ACCEPTANCE.md, affected installation/runtime/recovery/Homebrew guidance; review twelve localized guides for actual flow changes.

**Interfaces**

- `package_data.read_verified(path, *, sha256, limit=65536, uid=0, installed=...) -> bytes`: expected digest mandatory, fixed SDK scope, ordinary0777 accepted only in this hash-bound path; strict unanchored read remains separate.
- Resolver conceptual API: `package_identity.identity(owner, *, purpose='current')` returns only canonical appinfo/packageinfo expected records and a private binding identity; `inventory(owner, *, purpose='current')` returns the selected private full installed-file digest map. A purpose for worker/health selects from strictly read existing journal/evidence, not a caller-supplied target/version. Exact final API may follow existing modules, but record and review any interface adjustment.
- `current` never authorizes arbitrary pending rearm. Phase-aware presence/health and normal rearm remain distinct. Missing/conflicting authority raises a bounded recovery result, not confirmed deletion or permission to retry.
- Cache expected metadata only in-process, keyed by checked active private descriptor/journal/cache identity. Reread installed metadata each observation; do not decompress large IPKs every two seconds or persist another current authority.

**Implementation steps**

- [ ] Write failing real-fd DATA tests for full0777 own trees with private expected hashes, wrong content/UID/links/replacement and private0777 refusal. Record RED before production edits.
- [ ] Add the digest-required reader and canonical private anchor resolution. Reuse original current/signed/bootstrap record validators and bounded archive parsing; never import retained modules.
- [ ] Add authenticated System own-package retention/terminal/readback/continuation evidence. Missing legacy proof stays inhibited; verified legacy cleanup remains available.
- [ ] Add missing-marker/failsafe-present marker-admission regression: authenticate phase-appropriate identity, mark/return without rearm wait or intent mutation.
- [ ] Add failing all-owner and actual updater phase fixtures: initial setup, stable current, target health after real terminal, rollback health, stale/disagreeing records, missing cache/self proof and unknown submissions. Inspect current worker prechecks and Home pause/resume rules before choosing phases.
- [ ] Wire guarded presence and complete hash readback; remove SDK ordinary execute-bit equality as authority only. Preserve phase/deletion/unknown distinction, intent, original receipts, profile integrity, worker ownership and private modes.
- [ ] Add matching HBC source-intake DATA tests and update reads without weakening the first pin, byte copies or private snapshot ownership. Never inherit0777 into private execution.
- [ ] Synchronize bundle helper bytes, parser/import closure and legacy validation. Test actual emitted bundles with external cwd/source absent.
- [ ] Update affected docs and record twelve-guide review. Do not claim hardware success or public Homebrew approval.
- [ ] Run meaningful affected suites/actual Node8, diff check, self-review and commit. Save exact RED/GREEN/commands/known gaps in the plan workspace report. Do not run a duplicate full suite; parent owns final aggregate.

## Task 1b — Original System submission after durable intent

A separately reproduced functional defect remains after the scoped final-fix review: System Manager._apply persists installEvidence.intent before Device.install; Device.install's ordinary require_components then resolves worker identity and rejects that same intent as unknown before any transport submission. The existing Manager must still refuse every resumed unknown attempt. Fix the original synchronous submission contract without loosening background worker, startup, normal rearm or unknown-outcome authority.

- Reproduce with actual private identity fixtures, System Manager and Device, not an adapter stub. Read final-fix-review.md for the independent focused probe/evidence. Trace all callers before choosing a minimal existing-interface fix.
- Original known first invocation must submit exactly once, record real terminal evidence and proceed through candidate readback/health. Keep all required owners checked and missing/corrupt untouched owners blocking. Infrastructure-local continuation retains its separate bounded rules.
- After interruption before or after transport with intent but no terminal, a fresh Manager/worker must never replay or roll back an uncertain SDK submission. Do not clear/replace intent, synthesize outcomes, adopt writable SDK metadata or grant a general unknown bypass.
- Write failing regression first, then the smallest standard-library/existing-helper correction. Preserve emergency/off, profile and original package/cache evidence; no new privilege, durable schema, network endpoint or user flow.
- Cover original Root and Root-Updater System legs and uncertainty/owner refusal. Check No-root manager behavior if the shared call interface changes, without broad unrelated refactoring.
- Update the authority spec only for the actual internal contract; no localized user-flow change is expected. Run affected System/identity/worker suites and committed-HEAD emitted closure checks; parent owns a fresh aggregate and exact installer/native/platform builds after source freeze.
- No TV, remote network/GitHub mutation, subagents or extra worktrees. Sole source writer; commit and freeze explicitly before parent builds. Report RED/GREEN commands/output, exact commit, interface decisions/costs and remaining limits in task-1b-report.md.

## Task 1d — Canonical gzip metadata for exact cross-host package hashes

Measured release gate: at identical application/private source (localabf324e1 vs integrateda97e779f differing only docs/inventory), local Python3.14 emits gzip OS255 while Linux CI Python3.12 emits OS3. Actual three nested component IPKs have byte-identical deflate bodies and decompressed control/data; only gzip header OS differs. It cascades through package hashes, caches, manifests and HBC bootstrap pin. The existing same-host reproducibility check passes, but exact human artifact acceptance cannot reuse that local hash across release environments.

- Scope: cytv/package.py tgz uses gzip.compress(mtime=0). Use the existing standard-library gzip.GzipFile pattern already in cytv/python_runtime.py to write a canonical header (filename empty, mtime0, explicit existing compression level9), preserving USTAR bytes, IPK_MTIME, UID/GID/modes/directories and archive/member formats. No new library/framework or manual integrity bypass. Do not modify published Helper archives/pin.
- This builder source is copied as private root_package.py (Root Updater/coordinator infrastructure); all exact private bundle hashes need rebuild even when public component IPKs are unchanged. Reuse existing manifests/copies; no new inventory paths or durable schema.
- TDD: add a small portable host format regression using actual output; run it before production edits under bundled Python3.12.14 at /Users/pridannikov-d/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 (observed native gzip header OS19) and local .venv-release Python3.14. Fixed canonical gzip metadata/roundtrip and deterministic bytes are the contract; do not fake POSIX or edit compressed bytes in the test. Existing relevant metadata/permission/Helper-pin tests must still pass.
- Inspect all tgz/ipk callers and preserve trust/removal/legacy format behavior. No broad refactor. Update technical packaging/acceptance documentation only for the real deterministic format guarantee and source/candidate distinction; no user flow/translation change is expected.
- Run focused package/Root/System parser/build/source-free checks as needed and both actual Python versions for format regression. Parent owns final whole-suite, two-interpreter full HBC0.1 builds and Linux CI byte comparison, native and all-platform builds.
- No network/GitHub/TV mutations, subagents, worktrees or large duplicate Installer builds. Sole source writer in existing checkout branchcodex/portable-candidate-builds at01e6f5c7. Task1c one-line POSIX fixture correction is already committed and separate; do not reopen it.
- Commit/freeze explicit HANDOFF. Full report task-1d-report.md: RED/GREEN commands/output, exact source/bundle implications, decisions/costs and remaining gates.

## Task 2 — Review and stable artifacts (parent)

- [ ] Save one complete task diff; read-only spec/quality review against the written contract and counterevidence. Fix Critical/Important findings in one integrated wave; scoped rereview only.
- [ ] Final whole-change review. Freeze code before full scripts/test.sh (Qt and actual Node0.12.2), actual Node8, emitted/source-free proof, reproducible Installer and console/desktop smoke.
- [ ] Publish normal feature PR targeting release/next; no shared direct push/admin bypass. Merge only after required CI; collect all new PRs/self inventory through maintenance PR and refresh draft64.

## Task 3 — Final exact supervised device path (parent only)

- [ ] Preserve private backup/new archives and original known terminal results. No mutation on an unknown operation.
- [ ] Use canonical removal/rebootstrap, not chmod, live private-code overwrite or a synthetic receipt. Exercise the final on-TV Installer clean setup and cross-client status/maintenance where available; preserve intended profile limitations explicitly.
- [ ] Prove actual package hashes/terminal/readback, private owner anchors and cold-boot stable reads; keep exact source/package/manifest identities.
- [ ] User explicitly activates at normal setup/settings; test ordinary/held input, app→Home, triple-Home and no automatic reenable, standby and true cold boot separately. Record failed/unavailable rows honestly. Never repair a failed cold boot by silently enabling Home.
- [ ] Obtain meaningful named human Homebrew review/test acceptance before creating any public promotion record. Source work and automated review do not fabricate it.

## Task 4 — Freeze, publish and clean (parent)

- [ ] Final release inventory/version/docs/acceptance agree; old reports remain partial/open with correct labels. Final trusted Android/four desktop/Homebrew builds at exact frozen source pass.
- [ ] Normal release PR64/main merge only after policy and human/hardware gates. Verify publication, actual assets/checksums/both signed feeds/provenance and shipping notices/issue labels. Never equate merge/install with shipping.
- [ ] Preserve artifact/review/ledger evidence outside this worktree, report every Ruling and its cost, then remove only this owned temporary worktree/dependencies via git worktree remove.
