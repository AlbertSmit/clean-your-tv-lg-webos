# v1.3.0 — Homebrew installation and shared recovery

**Unreleased preparation candidate.** Version metadata is selected; physical
acceptance and final protected builds are not complete. No new public download
or Homebrew catalog availability is claimed.

| Component | Published 1.2.0 | Selected candidate |
| --- | --- | --- |
| cytv installer | 0.3.1 | 0.4.0 |
| Home | 1.4.1 | 1.4.2 |
| Home Helper | 0.6.19 | 0.6.19, unchanged exact archive pin |
| Root Edition | 0.3.0 | 0.4.0 |
| Home and Root Updaters | 0.2.1 | 0.3.0 |
| Android installer | 0.2.1-preview / code 10 | 0.3.0-preview / code 11 |
| System Updater supervisor | 1.0.0 / protocol 1 | 1.1.0 / protocol 1 |
| Homebrew CYTV Installer | Not published | 0.1.0 proposed for exact acceptance; development CI remains 0.0.0 until approval |

## Included behavior

- #85: keep the TV-only updater binding fixture on POSIX while retaining native
  Windows build/smoke coverage. Canonical gzip metadata removes the measured
  Python/host OS header difference from package hashes. Tar/ownership/modes,
  published Helper pin and runtime guards remain unchanged. Rebuild the private
  package-writer copies and their enclosing inventories.

- #79: tolerate the measured shared package-metadata directory owner only at
  that platform container; package leaves and private execution remain guarded.
- #83: authenticate observed SDK0777 DATA through phase-selected private hashes,
  preserve established live Home health until update suspension captures intent,
  validate every required owner before deferring uncertainty, and record original
  System install intent after guarded preflight but before effects/submission.
  Boot marker admission returns before HBC clears its temporary failsafe; normal
  rearm, private execution and unknown-operation no-replay remain guarded.

- #77 Homebrew device correction: accept verified ARM32 userspace on aarch64 kernels, read package data through the platform container boundary, execute verified code from private snapshots and use receipt-owned private startup guards. Missing or unsafe owner packages block rearming. POSIX device fixtures are isolated from portable Windows host tests.

- #66 / #65, partial: desktop recovery keeps the selected No-root TV/port, asks
  separately before removal, verifies cleanup before reinstallation and offers
  the exact failed attempt's redacted diagnostic report. The G5 failure's cause
  remains unresolved.
- #67 / #24, partial: non-debuggable Android builds preserve the existing signer
  and pending prompts. This does not diagnose the original unfinished removal;
  Android stays preview pending final artifact and physical acceptance.
- #70 / #12 and #68, partial: source setup parses supported Node versions around
  CLI banners, preserving failed probe status and rejecting ambiguous output.
- #71 / #12, partial: Android maintenance retains edition and SSH port; Home
  settings distinguish unknown status from confirmed off and keep visible focus.
  Underlying Helper-status transport and reporter acceptance remain unresolved.
- #72 / #68, partial: static Outfit Light/Regular/Medium/Bold faces preserve
  intended weights on engines without variable-font axes. Actual LM6370PSB
  readability and the separate Helper-unavailable symptom await reporter results.
- #73 / #55, diagnostics only: Root retains private startup/exit/finalize evidence
  and exports bounded allowlisted attempt-specific categories/codes. OLED Flex
  recovery-service failure and firmware-contract investigation remain unresolved.
- #74: a separate Root-only CYTV Installer uses Homebrew's fixed exec service,
  verified offline bundles and optional pinned Python preparation. cytv retains
  No-root and Root installation. Both clients share durable ownership, original
  request/package proof, status, recovery and complete-product removal. The TV UI
  supports twelve languages and explicit activation. Owned package startup links and
  package-disappearance guards preserve recovery boundaries. Homebrew updates
  Installer separately from product updates; removing Installer leaves the
  installed product. Publication and catalog acceptance remain gated below.

- #75: synchronized component/service versions and explicit pending acceptance;
  isolate the legacy CLI test from local build outputs. The inventory includes
  this metadata PR when it merges into the candidate.

- #76, Chinese localization: Simplified Chinese (`zh-Hans`) and Traditional Chinese
  (`zh-Hant`) in Home, Root Home, the independent updaters, desktop/console,
  Android and Homebrew installers. Automatic selection respects explicit script
  tags and regional defaults; manual selection persists. Bundled static Noto
  Sans SC/TC subsets cover the offline TV interface. Two localized user guides
  are included. Physical Chinese-language TV acceptance remains pending.

No telemetry blocking, rotating wallpaper or unrelated device issue is claimed
fixed by this candidate. Included issues remain open where their original report
or requested device confirmation remains unresolved.

## Delivery, updates and rollback

Rebuild all desktop/console and Android installers, Home/Root packages, both
updaters and the supervisor. Keep Helper 0.6.19 byte-identical to its published
pin. Android application ID, certificate and private storage identity are retained.

The supervisor's infrastructure inventory and Root startup/bootstrap ownership
have changed. An app-only update cannot replace retained recovery code. Existing
installations need validated supported migration or explicit computer rebootstrap;
that acceptance and preservation of rollback/profile/recovery evidence are still
pending. Do not overwrite retained drivers or clear uncertain operation records.
Unsupported/unknown infrastructure must stop with recovery instructions.

Keep checksum-verified v1.2.0 packages and signed feeds as the rollback baseline.
Artifact integrity alone does not establish physical whole-edition rollback.

## Acceptance and remaining gates

See [1.3.0 candidate acceptance](RELEASE-1.3.0-ACCEPTANCE.md) and the detailed
[Homebrew matrix and state inventory](development/HOMEBREW-INSTALL-ACCEPTANCE.md).
Final-artifact physical rows remain NOT RUN. An earlier isolated Installer test
passed install/hash inspection, bounded foreground observation and exact removal.
A subsequent supervised rebootstrap passed controls, emergency release and standby
on its recorded older private runtime, but true cold boot FAILED: broadcast TV
started and Home opened LG Home. The corrected source has not been installed or
accepted on the TV. Repeat supported final-artifact setup, controls/emergency,
standby and true cold boot; cross-client maintenance, interruptions, missing-package
cleanup, signed upgrade/rollback and Homebrew human review remain separate gates.

`homebrew/release.json` stays absent until exact nondevelopment Installer IPK and
manifest hashes, immutable URLs and genuine TV/human acceptance are recorded.
Unaccepted development artifacts are excluded from public promotion. Catalog
metadata is a draft; catalog submission/maintainer acceptance is a separate step.

Candidate #64 must remain draft until exact-source platform builds, acceptance,
release policy, documentation and rollback gates pass. A merge is integration;
verified package/feed publication establishes shipping.
