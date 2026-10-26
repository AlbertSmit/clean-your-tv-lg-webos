# v1.3.0 candidate acceptance

Status: **PREPARATION — NOT ACCEPTED FOR PUBLICATION**.
Selected versions do not freeze or approve a release. The maintainer authorized
preparation and release after verification; final hardware acceptance and
meaningful Homebrew human review remain outstanding. The maintainer is away;
source work does not authorize unsupervised TV reactivation or erase a failed test.

## Candidate and exact source evidence

Release1.3.0; cytv0.4.0; Home1.4.2; Helper0.6.19 unchanged exact archive pin;
Root0.4.0; Home/Root Updater0.3.0; supervisor1.1.0/protocol1;
Android0.3.0-preview/code11 with existing signer/application/private-data identity.
Homebrew0.1.0 is proposed for exact acceptance; unapproved CI uses development0.0.0.

PR #83 source `abf324e19c4882e079bea4722813bcb8a39c2ea2` passed:

- Full local `scripts/test.sh`:1,220 Python cases, two isolated-Linux-root skips,
  Qt, JS/native/compatibility, twelve-locale browser and actual Helper Node0.12.2.
- Real System Manager/Device/private-authority regressions: both original SDK
  legs through candidate health, all-owner/cache refusal, durable intent before
  effects, interrupted unknown requests without fresh-manager/worker replay.
  Focused12, System107 and selected Root78 passed; committed-source archive and
  source-deleted isolated14-module emitted closure passed.
- Native macOS console/GUI build, embedded159-file public payload validation and
  frozen GUI/package smoke. Private closures are rebuilt with the candidate;
  equality of public component IPKs alone is insufficient.
- Two Installer0.1.0 builds were byte-identical:61,270,342bytes, SHA256
  `c238810ee6f37cc892003eb4c795cf52aed61da56a91034bcd44e72af1fdd61c`.
  Proposed serialized manifest SHA256
  `a4cb06ebf363e7d27d993a1ab34599774a847bb9acee1047f8556c9e7efd78d0`;
  payload manifest SHA256
  `0ad47d81af435ba311fe34ea975e97de80f3f97acdf8cc103bad181d1e42140c`.
  These source-specific unpublished artifacts are not a public approval record.

Independent whole-change review and its three corrections passed; the subsequent
original-System-call delta passed specification/code review without blocking
findings. One nonblocking new-test note remains: an `intent.json` sentinel is not
the real persistent-intent record, so those sentinel assertions do not establish
emergency-intent acceptance. Existing real-runtime coverage is separate; hardware
retest is still required.

Final source CI run40340914902 and exact integrated all-platform test builds must
finish and be recorded before candidate freeze. Prior37d47e27 Linux/macOS/ARM run
40338324428 passed, but is historical after the subsequent private-code change.
No source success establishes physical compatibility.

## Observed supervised session — older artifacts only

Detailed model/firmware/webOS/HBC/UID/ABI and device diagnostics remain in the
maintainer's private record. Public source/package identities and generic outcomes
are recorded here without addresses, credentials, app inventories or screenshots.

| Check | Actual older-session result | Final corrected artifacts |
| --- | --- | --- |
| Isolated Installer install, on-TV hashes and fixed HBC inspect | PASS at correction sourcecb1c789a | NOT RUN |
| One launch with bounded foreground observation | PASS on third sample; immediate read was premature | NOT RUN |
| Exact Installer-only terminal removal/absence; prior baseline unchanged | PASS | NOT RUN |
| Supported old Root0.2/Updater0.2 removal, archives and fresh Root0.4/Updater0.3 setup | PASS after narrowly corrected shared-container handling; original operation continued, no replay | NOT RUN |
| Root controls, held-arrow release, OK/Back/volume/pointer/wheel, app-to-Home | Maintainer confirmed PASS | NOT RUN |
| Triple-Home emergency exit, waiting and repeated Home | Maintainer confirmed LG Home remained; explicit off retained | NOT RUN |
| System1.1 setup with emergency intent still disabled | PASS on corrected host source86980b7a | NOT RUN |
| Explicit settings re-enable, standby30seconds and controls | Maintainer confirmed PASS | NOT RUN |
| True cold boot: remote off, AC removed30seconds, on | **FAILED**: broadcast TV; Home opened LG Home | **NOT RUN; release blocker** |

Installed Root/Updater public packages in that session came fromcb1c789a; corrected
host/System work used86980b7a. New private closures in #83 were not delivered to
that TV. Read-only diagnosis observed ordinary0777 SDK owner trees/metadata after
cold boot, intact private recovery, disabled Root and no pending host package
request. This is a measured layout, not a firmware-wide explanation. Do not
silently re-enable or patch retained private code to make the failed row pass.

The earlier isolated Installer SHA256 was
`f29e4975537735e53527a1296326e2fd46428393eac88eeb07a55e099d814c2b`
(61,228,554bytes). It is historical evidence, superseded by new candidate builds.
Historical C3 releases and prior all-platform build40316833884 likewise do not
validate the final corrected source or versioned packages.

## Remaining supervised matrix

- Final exact source, package/manifest identities, supervisor/Root private
  inventories, peak staging space and free-space measurements: pending.
- Fresh Root setup with system Python and optional offline Python: final NOT RUN.
- cytv→HBC and HBC→cytv maintenance, concurrent clients/original continuation,
  interruptions and unknown outcomes: final NOT RUN.
- Supported published1.2 infrastructure migration/rebootstrap, missing-package
  cleanup, full removal with LG recovery, signed whole-edition update/rollback
  and retained profile/recovery evidence: final NOT RUN.
- Final controls/emergency, observer/frozen-UI recovery, standby and separate
  true cold boot: NOT RUN; do not carry older successes into these rows.
- No-root setup/maintenance/removal and Developer Mode renewal boundaries: NOT RUN.
- Protected-signer Android upgrade, private-data/pending-receipt retention and
  physical use: NOT RUN; Android remains preview.
- Simplified/Traditional Chinese glyphs, selection and remote focus on TV: NOT RUN.
- Named supervising human and meaningful Homebrew code/artifact review: pending.

See the full [Homebrew matrix and state inventory](development/HOMEBREW-INSTALL-ACCEPTANCE.md).
Do not repeat uncertain requests or delete retained evidence to obtain a success.

## Documentation and publication gates

Reviewed README, Root installation/runtime/update/recovery docs, Homebrew packaging
and authority/state inventory, current source commands and twelve guides:
en, ru, de, es, fr, it, pl, pt-BR, hi, ko, zh-Hans, zh-Hant. #83 updates candidate
SDK/private-boundary guidance and Root0.4.0 source-build examples; historical
published package/hardware statements stay separate. The internal original-intent
callback does not change user setup or controls.

- [ ] Final integrated source, versions, inventory and artifact identities agree.
- [ ] Required Linux/macOS/ARM and exact Android/four desktop builds pass.
- [ ] Combined-candidate local/native/package checks are recorded.
- [ ] Final physical acceptance, limitations and human Homebrew review are real.
- [ ] Supported transition, emergency/removal and signed rollback gates pass.
- [ ] Exact Homebrew approval precedes any release.json/catalog promotion.
- [ ] Candidate description, documentation, release notes and policy agree.
- [ ] Publication verifies assets/checksums/both signed feeds and provenance.
- [ ] Existing shipping notices and issue statuses verified without duplicates.

`release-plan.json` acceptance remains empty; `homebrew/release.json` is absent.
PR #64 stays draft. Publication and issue closure do not follow from this record.
