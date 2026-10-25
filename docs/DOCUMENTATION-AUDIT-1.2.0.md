# Documentation audit — 1.2.0 candidate, 2026-10-25

Inventory: #60/#59, #61/#55 (partial), #62/#51 (diagnostics only), #63.
The release PR is #58. This audit does not certify hardware acceptance.

- Reviewed the inventory's changes in README, MANUAL_INSTALL, CLI, Root README,
  LG-FIRMWARE-UPDATES and all ten localized guides: en, de, es, pt-BR, fr, it, ko,
  hi, pl and ru. Existing candidate sections cover confirmed Helper start,
  early migration validation, guarded cleanup, sanitized diagnostic fields and
  Homebrew firmware blocking. They remain candidate-only until publication.
- Added RELEASE-1.2.0 with component versions, partial delivery, old-driver and
  app-only update limitations, restart behavior, recovery/rollback boundaries
  and outstanding physical checks. Updated CHANGELOG to distinguish published
  1.1.0 from this candidate and Android README to match the new manifest.
- Reviewed INSTALL, DESKTOP_INSTALL, UPDATES, RECOVERY, COMPATIBILITY, Root
  UPDATES/RECOVERY/TESTING and prerequisites against this scope. Setup commands,
  required privileges, endpoints and recovery-service contracts are unchanged.
  Keep published 1.1.0 download links and version-specific build examples until
  1.2.0 publication. Historical hardware records retain their original versions.
- Updated Home/renewal, updater/service, cytv and Android manifests together
  with release-versions.json. Root service metadata is synchronized; Root app and Root Updater versions are generated from
  release metadata by their builders. Helper and the fixed supervisor retain
  their existing versions and approval boundaries.

Verification commands/results and exact candidate hashes belong in PR #58.
Local package validation must inspect embedded manifests and payload hashes;
final platform builds and signed publication remain separate gates.

Before publication, record actual TV acceptance or an explicit maintainer
release-risk decision. Once publication is verified, reconcile current stable
download/version guidance and all ten translations, replacing candidate-only
wording without changing historical acceptance claims. Until then, the stable
guides correctly describe 1.1.0 and candidate instructions remain separate.
