# Homebrew device-boundary correction

Approved by the maintainer in chat on2026-10-26. This corrects the existing
Homebrew/shared-coordinator feature after real package testing; no publication
or update of the TV's existing Root installation is implied.

## Required behavior and trust boundary

- Recognize aarch64 kernels only when Linux and the independent ARM32 little-endian
  EM_ARM soft-float EABI5 shell checks pass (and ARM Node for the Node bootstrap).
  Keep all foreign OS/ELF64/hard-float/ARMv6/unsafe-tool refusals. Applied in5e4d482f.
- Standard shared developer application containers can be root-owned writable
  directories. Treat only their exact fixed chain as a package-data boundary:
  require real root-owned directories and reject symlinks/foreign ownership, with
  one DATA-only owner exception: exactly `/media/developer/apps/usr/palm/packages`
  may also have observed metadata UID 501. No other ancestor gains that owner
  exception. The package leaf/descendants/files remain root-owned and not writable by
  group/others. Read metadata through stable descriptors and detect replacement.
  Keep private Store/runtime/interpreter checks strict. Legacy writable leaves
  stay recovery/migration cases, not implicitly trusted current packages.
- HBC's initial privileged application launch is a trusted installed-app boundary;
  code launched from an app cannot retrospectively authenticate its first byte.
  Pin the expected payload-manifest SHA into the built bootstrap. Authenticate
  later metadata/bytes to that original identity, not a second self-consistent
  manifest read. Never modify shared platform directory permissions.
- Before Python execution, use a unique0700 temporary tree under the existing
  strict /var/lib/clean-your-tv-installer staging parent. Copy/hash exact bytes
  from the original anchored inventory; invoke Python/imports only from there.
  For inspect/install/fresh remove copy complete required component inputs plus
  code (root/root-updater/supervisor/baseline as used), excluding the unused large
  runtime archive. Pass the PRIVATE snapshot as --payload; do not reopen original
  replaceable manifests to authorize durable worker contents. For status/restore/
  activate/resume copy only the root-updater code/import/support closure, excluding
  IPKs. The existing durable per-request worker snapshot/lease/UUID rules remain.
  Remove only this invocation's stage after its child exits; unknown drift stays
  actionable. Ephemeral verification staging is permitted during inspection;
  inspection still changes no product/Home/profile/runtime slot/operation receipt.
- Replace package-target init.d symlinks with exact receipt-owned0700 regular
  wrappers invoking only private guarded CYTV code. Validate package identity as
  DATA before owner boot/worker startup. Never execute a package startup script.
  Missing/unsafe packages suppress rearming while independent recovery can restore
  LG Home. Preserve emergency state and all removal/unknown-outcome invariants.
- New receipt representation must migrate only exact owned v1 regular hooks and
  exact owned v2 symlinks, with retained crash proof/idempotent cleanup. Unknown
  target/bytes/receipt collisions stay blocked. Removal authority for a saved owned
  link must not require trusting its replaced target. Keep host removal helpers
  and current-installation/health/Updater/System observers consistent.
- New package builds must explicitly provide secure own app/service/package leaf
  directory modes where needed, without changing shared container permissions.
  Retain original third-party licenses, both host installation paths and ten locales.

## Verification

Targeted matrix in /private/tmp/cytv-device-boundary-review-report.md is the review
brief (local scratch, not a public dependency). Maintain durable regression tests
for shared chain/strict leaf/private boundaries, the exact UID-501 shared metadata
container with root-owned own leaves/files (other owners and paths refused),
fd/path replacement, original manifest/file replacement before execution, no
import from original source,
private hook replacement/deletion and v1/v2 migration/removal. Use actual emitted
packages and source-free payload checks; actual Node8 must pass.

All existing physical acceptance gates remain. Only the separately approved
isolated Installer install/hash/read-only inspect/launch/removal may be repeated
on the saved TV; do not update its existing Root/Updater/profile/Home. Keep all
actual device diagnostics private; public records use generic bounded results.
