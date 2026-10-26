# Cold-boot SDK DATA and private execution boundary

Status: implementation design within the maintainer-approved package-DATA/private-execution correction. The maintainer also authorized supervised Root rebootstrap and controls/emergency/standby/cold-boot acceptance. This does not authorize forced reactivation, overwriting retained private code, or publication before the existing gates.

## Problem and evidence

At integrated0fd26d57, ordinary Root controls, explicit activation, triple-Home emergency/off persistence and standby passed supervised testing. A true cold boot returned broadcast/LG Home. Private recovery integrity stayed valid, with no pending package operation. Bounded diagnostics found the three Root product package trees and appinfo files changed from0755/0644 to0777, retaining UID0 and real paths. The strict package DATA reader and installed execute-bit comparisons therefore reject legitimate post-boot state. This observation does not identify the platform component changing modes or establish a universal firmware rule.

Private execution, runtime, receipts, hooks and ownership remain strict. Do not repair SDK permissions, remove a safety latch, or reinterpret bytes as terminal installer evidence.

## Chosen architecture

Authenticate fixed installed SDK DATA by independently selected private expected hashes. Ordinary SDK rwx bits cannot authenticate bytes after this observed cold boot. Continue executing only private verified code and snapshots. A plain semantic id/type read from a writable app is insufficient for an automatic guard.

Alternatives rejected: chmod/chown on startup changes shared platform state and will not survive normalization; globally removing mode checks loses authority at semantic readers; accepting arbitrary old/candidate/cache packages hides transitions. The existing private current/transaction model remains the authority, rather than introducing another mutable global current record.

This refines the already approved boundary and keeps its intended result: missing, changed or unproven owner packages inhibit rearm; independent private recovery remains usable. No new endpoint, root privilege, UI installation consent or automatic emergency reset is added.

## Digest-required SDK reader

Retain a strict unanchored reader where independent byte authority is unavailable. Add a separate mandatory-digest read for only the current allowlisted rooted app/service/package paths. Validate the expected digest before opening data and verify the returned bytes before parsing them.

Preserve real-directory descriptor traversal, O_NOFOLLOW, root ownership of own leaves/files, regular types, single-link files, bounded sizes/counts, read-fd stability and final path/inode/content bindings. Retain the one observed UID501 exception only at the exact shared packages container. Foreign owners elsewhere, symlinks, hardlinks, special files, same-length changed content and replaced paths remain refusals. Permit ordinary observed0777 bits only for this SDK DATA scope; no special-bit or private-path exception is implied. Concurrent metadata/path changes may fail closed.

Private readers, interpreter/tool checks, runtime staging/promotion, leases and wrappers retain their current nonwritable/mode requirements. SDK desired archive modes remain deterministic build metadata. Never copy observed0777 into a private snapshot or treat installed execute bits as permission to execute shared code.

## Private byte authority

A small canonical, data-only resolver supplies expected owner metadata/full inventories. Bundle one authoritative implementation wherever needed; never import another retained installation's modules. Reuse checked private receipts/descriptors rather than learning expected hashes from installed bytes.

- Root: authenticated current descriptor and checked cached IPK in Root Updater state. An explicit initial-bootstrap path must use the authenticated original request/bundle before current exists. Root's initial release.json becomes stale after updates and is not universal current authority.
- Root Updater: authenticated installed-package inventory at bootstrap, and the System-selected component when a proved System transaction supersedes it. Resolve edition ownership, transaction phase, completion and synchronization consistently with existing writers. A stale System baseline cannot arbitrarily override a committed standalone Root update.
- System Updater: persist an own installed-package inventory or authenticated own IPK after the real terminal/readback, derived from its independently verified original IPK. Its product baseline does not contain its own package. The new receipt is private, bounded and covered by setup/continuation invariants. Missing old proof is migration/recovery, not permission to hash current installed metadata and adopt it.

Legacy installations without recoverable exact original package proof stay inhibited for automatic startup. Existing verified legacy removal and independent recovery must remain usable. Deliver new private code through supported fresh provisioning/rebootstrap; no in-place edits to retained code or receipts.

## Purpose and phase selection

The resolver must select the package for the exact purpose and durable phase; do not return a blanket prior-or-candidate set.

- The init.d marker action is admission, not rearm: authenticate phase-appropriate Root DATA, create the current-boot marker and return promptly even while the transient HBC failsafe exists. Do not wait for an existing marker or cleared flag there; HBC clears its flag only after run-parts returns. This action never enables intent.
- Normal boot/rearm requires committed current identity and the existing normal-boot marker, failsafe, intent, routing and guardian conditions. Unresolved/conflicting state remains recovered/off.
- A pending updater worker may use a phase-authorized candidate for health only after its existing successful install evidence, or prior package for proved rollback health. Before submission, prior remains the expected identity.
- Unknown submission remains unknown even when bytes match. No identity read synthesizes terminal success, resubmits a package, or discards original receipts. A private recovery worker or explicit trusted-source recovery may inspect the original journal; this grants no ordinary update or Home rearm authority.
- Candidate health must remain possible before commit; current-only checks at the top of worker loops must not misclassify replacement as confirmed deletion. Unknown/integrity failure must not be collapsed into an external-deletion terminal.
- External deletion remains absent even if private cache bytes exist. Never recreate SDK files from cache merely to manufacture presence. Missing/changed owner prevents rearm; private LG Home restoration must not depend on owner identity success.
- Preserve emergency/off and the presently disabled intent. Only a separately explicit user setup/activation action may enable Home.

Every selected private authority must be strictly read, shape/scope/digest checked and tied to the actual writer/phase. On disagreement refuse rather than pick the highest version or whichever record matches installed bytes.

## Consumers and complete readback

Move automatic startup_guard presence, Root home_present, rooted updater presence/version checks and installation.device_snapshot to digest-bound identity. Continue semantic id/type/version validation after hashing. Cheap identity remains distinct from completion: complete readback still validates all installed bytes, private code/profile/baseline and actual terminal evidence.

Use descriptor-bound SDK reads for full Root/Root Updater/System checks and bootstrap/deploy readback. Remove installed ordinary execute-bit equality as authority, retaining strict desired archive format and private executable modes. Avoid a fresh unbound appinfo reopen for version display.

Root presence is polled every two seconds. Avoid repeatedly decompressing a large IPK on that path: an in-process cache of authenticated expected metadata may be keyed by strictly reread private descriptor/journal identity and checked cache identity. It is not another persistent current authority. Installed metadata is checked on each observation; anchor changes invalidate the cache.

Root private startup still only marks normal boot; it does not enable intent. Marker creation must precede the existing rearm gate, never wait inside init.d for marker/failsafe readiness. Existing gate ordering must be tested rather than inferred from the missing marker. Updater startup invokes literal private workers only. Restoration remains independent.

The HBC JS intake also needs digest-required reads for writable SDK source data. Preserve its original outer pin/inventory, byte hashes before copy and anchored private second stage. Private staged modes come from the trusted execution contract, not current SDK bits. Initial user-initiated privileged HBC bootstrap and browser execution of SDK web assets remain explicit platform trust assumptions: a pin in a mutable initial bootstrap cannot authenticate its own first instruction. This change does not claim otherwise.

## Build and compatibility contract

Update all canonical helper inventories, source-free import closures, generated baselines and private code hash lists together. Keep current unpublished target versions unless an actual delivered compatibility change requires otherwise; no release has shipped these candidates. Missing new self anchors in older infrastructure cannot be silently repaired. Preserve original legacy driver/support proof and removal paths, including after package mode drift/deletion.

Review affected installation/runtime/recovery docs and twelve user guides. Explain any actual changed setup/rebootstrap requirement; do not add backend details to ordinary user flows. Keep stable downloads and historical hardware claims separate.

## Verification and delivery

Regression fixtures must reproduce complete root-owned SDK0777 trees and metadata, plus the fixed shared UID501 case. Prove unchanged anchored bytes accepted; wrong/same-length content, missing/conflicting/stale anchors, wrong owner, links/specials/replacement races rejected; private0777 always rejected. Test missing-marker/failsafe-present admission returns after creating the marker, without waiting or enabling intent. Test all three owner guards, initial setup, committed current, phase-authorized candidate/rollback and unknown submissions. Preserve terminal/no-replay, disabled/emergency and missing-owner recovery invariants.

Run meaningful affected suites, full scripts/test.sh with actual Node0.12.2/8 where available, emitted/source-free/cross-client checks and reproducible payloads. One coupled implementation owner, scoped spec/quality review, final whole-change review; no parallel mutation of this trust contract.

Do not patch the currently installed private runtime. After reviewed builds are ready, use standard verified removal/rebootstrap with archives to test final exact artifacts, preferably the clean on-TV Installer path and cross-client maintenance. Record fresh consent at normal setup/activation UI; retain unknown outcomes instead of replaying. Repeat controls/emergency, standby and true cold boot separately. Publication, human Homebrew review, exact artifact approval, final trusted platform builds, notifications and issue labels remain their existing gates.


## Implemented interface decisions (local source, acceptance still pending)

`package_data.read_verified` is separate from strict `read`; every writable SDK
read requires an independent SHA256. `package_identity.inventory` selects the
private inventory for `current`, `worker`, or `admission`; `identity` returns
metadata parsed from the verified bytes and optionally checks the complete
inventory. Only `bootstrap_inventory` may use the explicitly supplied original
Root setup records; ordinary observations have no release.json fallback.

Root private current descriptors gain a writer owner/id. Standalone publications
also carry the last System publication id from their prior descriptor, so
consecutive standalone updates and rollback/abort remain distinguishable from
stale System state without clocks or version ordering. Signed/public descriptors,
proof bytes and cache SHA identities are unchanged. System completion refreshes
the existing Root Updater original-file/executable inventory. Comparing captured
prior archives permits only exact equality of independently checked private full
payload maps, never a prior-or-target match against observed SDK bytes.

System retains its original own IPK before submission and publishes its own
inventory after terminal/full readback. Explicit original-bundle continuation
can retain a missing own IPK against the existing private bootstrap pin; inspection
and boot cannot create it. Root's bundle declares `updater/store.py` and the
existing bounded `updater/package.py` parser; System uses its own bundled support
copies. No retained installation is an import source. Expected-map caching is
in-process and keyed by strictly reread descriptor plus checked cache identity.

The original private worker may reconcile an owned replacement window, including
known-terminal rollback with partial SDK DATA. Such an observation is uncertainty,
not normal presence or confirmed external deletion. The original managers retain
submission/terminal/no-replay control; private recovery does not enable intent.
