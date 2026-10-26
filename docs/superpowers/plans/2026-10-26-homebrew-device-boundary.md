# Homebrew device-boundary correction plan

> Execute with subagent-driven-development, one integrated implementation task
> followed by scoped spec/quality review and final stable verification.

**Goal:** Make the already integrated Installer work with standard webOS package
containers and ARM32-on-aarch64 while preserving private privileged execution.
**Spec:** ../specs/2026-10-26-homebrew-device-boundary.md

- [x] Task0: ABI regression/fix5e4d482f. Red/green JS current/actualNode8,
  Python current-adapter guard and actual generated shell ABI fragment. Host28OK,
  ProductABI1OK; all strict ELF checks retained.
## Task 1 — Correct the package trust and startup boundary

- [ ] Implement approved package-data boundary, anchored private execution
  staging and private startup-wrapper migration as one coupled trust contract.
  Update all named observers/build inventories/host cleanup and affected docs,
  including ten localized guides; do not weaken private readers or leases.
  Add the focused race/platform/receipt regressions, run affected suites, commit,
  and report exact source/evidence. No TV/public writes by implementer.

## Task 2 — Scoped review

- [ ] Review complete correction against spec and actual counterevidence;
  fix any Critical/Important issues, scope re-review only to corrections.
- [ ] Task3: Stable full suite, source-free/reproducible packages, actualNode8,
  and repeat the already approved isolated Installer test. Keep existing Root
  untouched; record only actual observations and known outcomes.
- [ ] Task4: Merge feature PR to release/next after required CI; collect inventory
  through normal PR workflow, refresh candidate64 and rebuild all platforms.
- [ ] Task5: Obtain separate supervised product update/activation/emergency/boot/
  rollback acceptance and meaningful human review before final freeze/publication.
  No invented hardware acceptance or public Homebrew approval.

Ruling: snapshot complete component DATA with code for actions that consume
payload, excluding runtime archive, and code-only for maintenance/status — avoids
adding a second Python manifest-authority API or reopening replaceable component
manifests — cost if wrong: up to roughly12.5MB ephemeral copying per inspection/
fresh operation; no51MB runtime archive is copied. Original loaded manifest bytes
and exact copies remain the authority. No unrelated persistent product state changes.
