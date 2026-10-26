# Release 1.3.0 preparation plan

> Execute inline using verification-before-completion and the repository release flow.

**Goal:** Integrate Homebrew PR #74 into candidate #64, build all deliverables, obtain exact-candidate acceptance, and publish through the protected normal release workflow.

**Authority:** docs/RELEASE-FLOW.md, docs/RELEASE_CHECKLIST.md, root-edition/TESTING.md and docs/development/HOMEBREW-INSTALL-ACCEPTANCE.md. User authorizes integration and release; user also requires removal of temporary worktrees after saving code/artifacts.

## Constraints

- Never replace hardware/human acceptance with automated tests or earlier C3 results. No invented acceptance text or CI bypass.
- Use merge commits and preserve release/next inventory. Preserve open partial issues and existing requests; verify statuses at handoff/publication.
- Keep Android application/signing identity, Helper 0.6.19 exact archive pin and all recovery receipts unchanged.
- Publish all included deliverables only after their gates; Homebrew approval stays absent until exact candidate is accepted. No catalog availability claim before maintainer approval.

## Steps

- [x] Read candidate #64, implementation #74 and failed CI; fix test cwd via tempfile.gettempdir() and run nine targeted regressions; push28d1aeb5.
- [ ] Wait for exact-head Linux/macOS/optional-Python CI; mark #74 ready and merge using --merge --match-head-commit. Do not use --admin.
- [ ] Collect release inventory, update #64 scope/version/packaging/docs/test/remaining gate record immediately.
- [ ] Commit version metadata: release1.3.0, Home1.4.2 (app and renewal service), cytv0.4.0 (__init__ plus release metadata), Root0.4.0, Home/RootUpdater0.3.0 (both app/service manifests and release metadata), supervisor1.1.0 (builder constant, protocol1 unchanged), Android0.3.0-preview/code11 (Gradle and release metadata); Helper remains0.6.19. Write docs/RELEASE-1.3.0.md and an honest pending acceptance record. Select release-plan version but leave acceptance empty until supplied.
- [ ] Run npm ci, NODE012=... bash scripts/test.sh, package/content/reproducibility/rollback verification and docs/localized-guide pass on combined versioned source. Build desktop locally and dispatch cytv.yml on release/next with test_build=true and homebrew_candidate=true for protected Android/all four desktop targets/offline Installer artifacts. Keep RC draft.
- [ ] Save public v1.2.0 rollback assets with verified checksums and signed-feed provenance. Verify new artifacts' source, metadata, embedded versions, credentials exclusion and signer continuity.
- [ ] Supervised final-candidate physical acceptance, including both installation clients, fresh/no-system-Python preparation, switching clients, operations interrupted/unknown outcomes, emergency/restore, removals, standby and separate cold boot, supported update and rollback. Record actual human reviewer/model/firmware/hashes/limitations. Unavailable tests remain explicit.
- [ ] Freeze exact accepted artifact identities and Homebrew approval only after its gates. Refresh notes/all affected translations and #64, dispatch/verify exact final-source platform builds and required policy. Ready/merge #64 only when protection and acceptance pass.
- [ ] Verify publication assets/checksums/both signed feeds/inventory, automatic issue/PR notices and accurate issue labels. Preserve needed artifacts, remove only owned worktree/build directories.
