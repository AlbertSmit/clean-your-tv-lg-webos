# v1.3.0 candidate acceptance

Status: **PREPARATION — NOT ACCEPTED FOR PUBLICATION**.
Selected metadata does not freeze or approve a release. The user authorized
release preparation and publication after verification; no physical result or
meaningful Homebrew human-review result has been supplied for this candidate.

## Candidate and evidence

Release 1.3.0; cytv0.4.0; Home1.4.2; Helper0.6.19; Root0.4.0;
Home/Root Updater0.3.0; supervisor1.1.0/protocol1; Android0.3.0-preview/code11.
Homebrew0.1.0 is proposed for final exact acceptance; ordinary unapproved CI
continues to produce development0.0.0. Final integrated frozen source, exact package/manifest hashes, trusted platform-build run and artifact signer evidence are pending.

The approved isolated Installer test at source1be47b2c passed installation, actual file hashes and fixed HBC read-only inspection. Launch was acknowledged, but the foreground screen was not confirmed. Only Installer was then removed with terminal/absence proof; the previous product baseline was unchanged. This does not validate product installation, activation, controls, boot or rollback. Local reproducible Installer0.1.0 SHA256: c3061975151fc9d25c54d7814cf670b0f7a9e3052dc4bf5d2ea9b1b0ee0077cd (59,725,142 bytes); superseded by any later integrated candidate build. Detailed device diagnostics remain private.

PR #74 implementation source7b8738bc passed full local automated checks
(1,151 Python cases with23 environmental skips, plus JS/native/browser gates),
actual Helper Node0.12.2 and bootstrap Node8, reproducible IPK and scoped review.
A subsequent test-only portability correction28d1aeb5 replaces macOS-only
/private/tmp with tempfile.gettempdir(); nine targeted regressions passed and
Linux/macOS CI passed. Implementation Linux/macOS/ARM CI subsequently passed at28d1aeb5. Combined
versioned candidate verification must be recorded independently. These earlier checks do not approve
new versioned artifacts or certify a TV.

## Required supervised record

- TV model, firmware, webOS, HBC version, input ABI and actual effective UID: pending.
- Supervising human, meaningful code reviewer, date and exact source/artifact IDs: pending.
- Fresh Root installation with suitable system Python and without Python: NOT RUN.
- cytv→HBC and HBC→cytv maintenance without profile reset: NOT RUN.
- Original request continuation, concurrent clients and interrupted/unknown outcomes: NOT RUN.
- Existing 1.2.0 infrastructure migration or explicit supported rebootstrap: NOT RUN.
- Home/Back/navigation/held arrows/OK/volume/pointer/wheel/app launching: NOT RUN.
- Change Home, triple-Home, frozen UI/observer recovery, no automatic emergency re-enable: NOT RUN.
- Individual package deletion and complete-product removal with LG Home recovery: NOT RUN.
- Standby and true cold boot, recorded separately: NOT RUN.
- Signed whole-edition update/rollback and retained profile/recovery evidence: NOT RUN.
- No-root normal setup, maintenance, removal and Developer Mode renewal boundaries: NOT RUN.
- Protected-signer Android update/private-data/pending-receipt retention and physical use: NOT RUN.
- Simplified/Traditional Chinese glyph rendering, language selection and remote focus on TV: NOT RUN.
- Peak package/runtime/product storage and free-space measurements: NOT MEASURED.

Preserve private diagnostics outside public records. Do not repeat uncertain
operations or delete recovery records to make a test pass. See the full twenty-row
[Homebrew acceptance matrix](development/HOMEBREW-INSTALL-ACCEPTANCE.md).

## Publication gates

- [ ] All versioned packages/build metadata and final source agree.
- [ ] Required Linux/macOS/ARM tests and Android/four desktop builds pass.
- [ ] Needed local and GUI/package smoke checks pass on the combined candidate.
- [ ] Human review and physical acceptance/limitations are recorded honestly.
- [ ] Supported old-infrastructure transition, rollback and emergency/removal gates pass.
- [ ] Exact Homebrew IPK/manifest are accepted before adding release.json.
- [ ] All affected documentation/translations/commands/download and recovery instructions reviewed.
- [ ] Candidate description, inventory, release notes and final Release policy agree.
- [ ] Publication verifies assets/checksums/both signed edition feeds and provenance.
- [ ] Existing shipping automation notices and issue statuses verified without duplicate comments.

No shipping claim or issue closure is authorized by this record alone.
