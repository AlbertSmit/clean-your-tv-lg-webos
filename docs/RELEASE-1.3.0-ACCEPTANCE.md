# v1.3.0 candidate acceptance

Status: **SCOPED MAINTAINER ACCEPTANCE RECORDED — FINAL BUILD/PUBLICATION CHECKS PENDING**.
The maintainer authorized 1.3.0 preparation and release after verification,
supervised the installed-source tests below, and explicitly deferred the
intermittent standby follow-up to issue #90. Acceptance covers the observed paths
and stated limitations only. Final protected builds must pass before publication.
Homebrew Installer human/artifact acceptance is absent, so it is not selected for
public promotion. No failed observation or unperformed test is counted as a pass.

## Supervised installed-source retest — 2026-10-26

The repository maintainer supervised this session on **OLED55C3RLA, firmware
43.21.71, webOS 11.2.0**, re-read from the same TV. Source
`1e6e92ce52a2df6c681ad711877936f0401e80ee` entered `release/next` through PR #88
(merge `31c38c82e25c001fefb9d1db9b4a866df3cbea26`). Component versions were
Root 0.4.0, Root Updater 0.3.0 and System Updater 1.1.0. The existing verified
private Python binding was reused; this was not a fresh optional-Python or
Homebrew Installer acceptance session.

The installed-source rebuild contained 159 files; its historical serialized manifest SHA256
is `2de2a6a8e262bffaad544b4b02575dc9de411772c997de1d9aaaa1cf279e5a32`.
All three installed private package readers matched corrected source SHA256
`7b3d97986aed1c4043eed11ed2bac76275219d38c3aca78268f64594ca2086f7`.
The generic Root/Root Updater/System bundle manifest hashes were respectively
`8df8d431e166d044c026b7052f9be07f654393b9b7dc4e4d4e96f6d7f9932126`,
`6f17acbb29eaca371ea3f38f6181550cb13d838d1c3466f7eb7526c14f63b080` and
`efa6e9558de9ea176d6fce3cd10d5c2a1a378e21644bb362f02f664e9f46974e`.
Root personalization and its installed snapshot were independently checked;
private inventories, operation identifiers, backups and raw logs are not public.

| Check | Observed result |
| --- | --- |
| Original terminal, never-provisioned install cancellation | One genuine subscribed removal; original request/snapshot/install terminal retained; cancellation terminal preceded archival; host pending preserved in history then retired |
| Ordinary CLI archive and fresh corrected setup | PASS; new operation, Root/Root Updater installed, recovery and rollback baseline verified, explicit activation succeeded |
| Home, arrows, OK, Back, volume, app launch and app-to-Home | Maintainer confirmed PASS |
| Triple-Home, wait and repeated Home | PASS; LG Home remained and Root did not automatically re-enable |
| System Updater bootstrap while emergency-off | PASS; bootstrap complete and disabled Root/LG routing preserved |
| Explicit re-enable | PASS; active intent, guardian and recovery verified |
| First remote-off/30-second standby/wake | FAILED once: Clean opened automatically, but Emby → short Home returned LG; input observer startup failed and safely disabled Root |
| Explicit UI re-enable and repeat standby/wake | PASS; Emby → Home returned Clean; active intent, guardian and recovery verified |
| Separate remote-off/AC-off-30-second cold boot | Home control PASS: initial unconfigured-channels screen, then Home opened Clean and Emby → Home returned Clean; active intent, guardian and recovery verified |

The intermittent standby failure is open as [issue #90](https://github.com/Razdva122/clean-your-tv-lg-webos/issues/90),
`bug` / `status:planned`. The maintainer requested that follow-up separately and
asked to continue release preparation. It is an accepted known limitation, not
an implemented fix. Automatic foreground launch of Clean after cold boot was
not observed; no such claim follows from working Home control.

The installed-source local checks collected 1,236 Python cases: 1,212 passed and
24 optional environment cases were skipped; JS/native checks passed. The installer
group was repeated with its required SSH/WebSocket dependencies. Independent
recovery/host safety review passed after an atomic-admission crash correction.
PR #88 exact-head Linux/macOS and integration-policy checks passed. Homebrew
Installer TV/human acceptance remains separate and no public approval is created.

## Final host correction and scope

PR #91 uses POSIX TV parent paths on Windows for three ordinary upload routes and
the internal recovery tool. Actual staging regressions reproduced all four
failures before correction. The full installer suite with Qt passed 341 tests,
with two isolated-platform skips; independent focused review passed. Linux/macOS
CI at `c796c27f8255baaa3de28cfae39b83575068a7e5` passed before normal merge.
A complete rebuild after this host-only change retained the same 159-file payload
manifest and all three component bundle hashes listed above. Thus no private
runtime substitution or new untested TV payload is inferred from host metadata.
All five platform jobs (Android, Windows, Linux, macOS ARM64/x64) passed at
finalization source `112d8dfe` in build run 40380605534. Those artifacts are
superseded by the packaging correction below and are not the final release proof.

PR #92 preserves the exact SHA256SUMS-verified published v1.2.0 Helper 0.6.19
package through the existing hash-pinned baseline mechanism. The current source
package writer changes gzip headers and omits five historical parent-directory
entries; file contents and their metadata are unchanged. Keeping the published
archive satisfies the strict same-version package guard without weakening it.
Helper SHA256 remains
`52510c9115a518a05849f6618516b41886aea54b7f74ea4763ffeeaf63c03e7b`.

The final 159-file payload manifest SHA256 is
`97d01249f7b4524835334a026baa2b456fdf89b01a41360e7cb41969ac93f084`.
All three Root/Root Updater/System bundle manifest hashes still match the
TV-tested hashes listed above. This component-level identity is the basis for
retaining Root acceptance; the outer payload is not claimed identical after the
published Helper baseline was restored. Strict `prepare_manifests` preflight
against real v1.2.0 packages passed, as did 6 build-asset tests, 341 Installer
tests (two isolated-platform skips), 10 release-feed tests and the system release
test. Independent focused review found no blockers. The new final candidate
still requires exact-head protected checks and artifact/publication verification.

The final documentation pass reviewed current README, setup/manual/CLI/desktop,
Root update/recovery/testing, Android preview, compatibility and all twelve guides
(en/ru/de/es/fr/it/pl/pt-BR/hi/ko/zh-Hans/zh-Hant). Current component/download
references and twelve-language availability are synchronized for 1.3.0; the known
standby fallback is included in every guide. Historical model records remain at
their original versions and Homebrew-only sections remain explicitly unpublished.

## Earlier portability correction — historical artifact identities

PR #85 source `a4c020f0ae5c9c297fcbabcf279285d9f2290b2b` supersedes earlier private package-writer closures
and candidate hashes below. Full local suite passed1,221 Python cases (two
isolated-Linux-root skips), Qt/JS/native/compatibility, twelve-locale browser and
actual Helper Node0.12.2. Native macOS console/GUI,159-file payload and frozen
GUI/package smoke passed. Independent portability-delta review passed without
findings.

Both actual Python3.12.14 and3.14.2 built the complete Installer0.1.0 twice;
all four IPKs and both serialized manifests were byte-identical. Historical IPK:
61,270,588bytes, SHA256 `9f14ffb4f3f8e867592d048fcc47b0e5fa3455e4ba4efc8768d3248145f7e86b`;
proposed manifest SHA256 `a88987c00e627129287058881ae703765e409550890e337c490173e702009dfe`;
payload manifest SHA256 `0039f76bb5249884222fdfc94d0daebb95602edff07e1b043bed1b2f76a7ddd8`.
These remain source-specific unpublished artifacts without human/TV acceptance.

Integrated feedback build40344669122 ata97e779f passed Android, Linux, both
macOS targets and Homebrew, but failed Windows before packaging: one TV runtime
fixture imported POSIX fcntl. Its adjacent fixture already had a POSIX guard;
#85 corrects that boundary while retaining portable host/native package checks.
The downloaded APK's actual hash/embedded source/versions, non-debuggable report
and retained pinned signer were verified. Local-versus-Linux Homebrew bytes had
different nested gzip OS header metadata despite equal control/data/deflate
bodies. #85 uses the existing stdlib GzipFile pattern instead. Exact rebuilt
integrated Linux bytes and Windows native smoke still require a fresh feedback
run; current results are maintained in PR #64. Do not count the old run as
all-platform success or adopt its hashes for new private code.

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

Final source Linux/macOS/ARM CI run40340914902 passed. PR #83 merged as
`28c6e280b4bef496b6d824c1df642f9d740ab45a`; this release-record update changes
only documentation/inventory relative to reviewed sourceabf324e1. The exact
integrated all-platform feedback-build run and artifact checks are maintained in
release PR #64; those unpublished builds do not freeze acceptance. Prior37d47e27
run40338324428 is historical after the private-code correction. No source or
platform-build success establishes physical compatibility.

## Observed supervised session — older artifacts only

This is the preserved pre-#88 record; current installed-source results are above.

Detailed model/firmware/webOS/HBC/UID/ABI and device diagnostics remain in the
maintainer's private record. Public source/package identities and generic outcomes
are recorded here without addresses, credentials, app inventories or screenshots.

| Check | Actual older-session result | At this earlier record, before #88 |
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

- Installed-source package/private identities are recorded above; final platform
  build provenance/checksums must match the frozen source. Peak staging/free-space
  acceptance for the unpromoted Homebrew Installer remains unmeasured.
- Fresh corrected Root setup reusing the verified private Python binding passed;
  system-Python and fresh offline-runtime preparation remain NOT RUN.
- cytv→HBC and HBC→cytv maintenance, concurrent clients/original continuation,
  interruptions and unknown outcomes: final NOT RUN.
- Supported published1.2 infrastructure migration/rebootstrap, missing-package
  cleanup, full removal with LG recovery, signed whole-edition update/rollback
  and retained profile/recovery evidence: final NOT RUN.
- Final corrected-source basic controls, emergency, standby repeats and separate
  cold-boot Home control are recorded above. Standby is mixed with unresolved #90;
  frozen-UI/observer fault injection, held arrows, pointer and wheel were not
  repeated in this session. Do not count unperformed paths as passes.
- No-root setup/maintenance/removal and Developer Mode renewal boundaries: NOT RUN.
- Protected-signer Android upgrade, private-data/pending-receipt retention and
  physical use: NOT RUN; Android remains preview.
- Simplified/Traditional Chinese glyphs, selection and remote focus on TV: NOT RUN.
- The repository maintainer supervised the recorded console tests. Meaningful
  Homebrew code/artifact human review remains pending; no approval is fabricated.

See the full [Homebrew matrix and state inventory](development/HOMEBREW-INSTALL-ACCEPTANCE.md).
Do not repeat uncertain requests or delete retained evidence to obtain a success.

## Documentation and publication gates

Reviewed README, Root installation/runtime/update/recovery docs, Homebrew packaging
and authority/state inventory, current source commands and twelve guides:
en, ru, de, es, fr, it, pl, pt-BR, hi, ko, zh-Hans, zh-Hant. #83 updates candidate
SDK/private-boundary guidance and Root0.4.0 source-build examples; historical
published package/hardware statements stay separate. The internal original-intent
callback does not change user setup or controls.

- [x] Merged scope, selected versions and observed source/artifact identities recorded.
- [x] Current source/host regression and private-payload equality evidence recorded.
- [x] Real supervised console acceptance and unresolved issue #90 retained accurately.
- [x] Tested recovery/emergency transitions and untested signed rollback paths distinguished.
- [x] Homebrew public assets withheld until its separate exact human/TV approval.
- [x] Current notes, user guides and known limitations reviewed for the frozen release.
- [ ] Exact-head Linux/macOS and Android/four desktop builds and release policy pass.
- [ ] Publication verifies assets/checksums/both signed feeds and provenance.
- [ ] Existing shipping notices and issue statuses verified without duplicates.

`release-plan.json` records this limited acceptance; `homebrew/release.json` stays
absent. PR #64 remains draft until exact-head builds and policy pass. Publication
and issue closure are separate from source integration and this acceptance record.
