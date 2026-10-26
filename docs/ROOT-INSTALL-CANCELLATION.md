# Internal recovery: cancel a never-provisioned Root install

This is a narrow maintainer recovery operation, not normal setup, an install
continuation, a repair command or a release acceptance claim. It is currently
limited to a failed product install at `root-deploy`, with the original Root
`install-observed` journal, an independently saved genuine SDK install terminal,
no migration, and no Root Updater/System or provisioning/activation state.

Use separately reviewed source in an isolated checkout. Do not patch a retained
worker, private runtime, bundle manifest, original request/submission, host
pending record, ownership receipt, or SDK container permissions. Never submit
another install to resolve this operation.

## Admission and code identity

Build the maintained Root Updater **code bundle** without installing it:

```sh
npm ci
python3 root-edition/build_updater.py --output build/root-recovery-code
python3 scripts/root-install-recovery.py digest --code-bundle build/root-recovery-code
```

The digest pins the complete worker bundle and the separately maintained
`root-edition/cancel_install.py`. The recovery module intentionally is not added
to historical worker inventories. Both the host and the device check the pin.
The host uses exactly one saved Root profile whose pending operation matches
the explicit operation UUID, with saved automatic SSH authentication.

Run `inspect`, supplying the original UUID/candidate and reviewed code digest:

```sh
python3 scripts/root-install-recovery.py inspect \
  --code-bundle build/root-recovery-code \
  --operation ORIGINAL_UUID --candidate ORIGINAL_CANDIDATE_SHA256 \
  --code-sha256 REVIEWED_RECOVERY_CODE_SHA256
```

This uploads trusted code to a new private temporary directory and checks the
original immutable snapshot, private support/runtime and interpreter binding,
request, submission, candidate, saved SDK terminal and exact product lease.
Every installed Root byte must match the original package. It rejects unknown
private entries, provisioning state (including dangling links), other product
components, project routing, non-LG Home routes, installer activity and live
original workers. The result includes a proof digest; `admissible` does not mean
that installation or cancellation completed. No product record, package or
host pending receipt changes during inspection. The temporary code directory is
removed after a successful invocation; preserve it on a failed/unknown invocation
until any process is confirmed stopped, then remove only that staging directory.

Admission does not establish human input acceptance. Confirm LG Home controls
immediately before a reviewed device mutation. Keep private backups and raw
hardware diagnostics outside the repository and public GitHub records.

## Explicit cancellation and unknown outcomes

After reviewing the concrete proof and authorizing removal, invoke the same
command with action `remove` and `--proof-sha256 REVIEWED_PROOF_SHA256`.
It repeats admission under the **same original product lease** and provision
lock. A single atomic deploy write preserves the complete original proof and
sets `cancellation-admitted`, which unchanged historical resume code refuses.
A crash before the separate cancellation receipt can recover from this exact
embedded proof. The original request, submission, snapshot, code and SDK install
terminal remain unchanged.

The separate cancellation receipt saves `remove-submitting` before one subscribed
SDK remove. A lost terminal is unknown and **cannot be replayed**, including when
the package is absent. A saved actual removal terminal allows readback and
remaining bookkeeping without another remove. No install, provisioning, restore,
activation, emergency-latch reset or chmod/chown occurs on this path.

After removal, package and registration absence and LG Home routing must pass.
The original lease becomes terminal at `cancelled-and-removed` only after actual
removal/readback. A cancellation receipt without the terminal lease reports
`cancellation-terminal-pending`; it cannot retire host pending. The failed install
never becomes an install-success record. An old resume after terminalization is
read-only; concurrent changes to original evidence before that point cause
recovery to fail closed rather than silently accepting revised proof.

## Host reconciliation and archival

Run action `reconcile` with the same UUID, candidate, reviewed code and proof.
It obtains the host session lock and performs fresh device inspection. Only
`cancelled-and-removed` with a terminal original lease permits preserving the full
original host pending record and device disposition in a private recovery-history
file, then retiring the active pending file. Neither package absence nor a
locally invented completion can do this.

Keep the removed Root state in place until that disposition has been verified.
Then reuse the existing strict `Installer.prepare_root_reinstall(already_removed=True)`
archive path, without calling install. It records/reconciles the archive identity
and preserves the old Root evidence by rename. Cancellation terminalization
**must precede archival**, so an old resume cannot see a fresh Root tree under a
nonterminal original lease. If archive fails, retain its host receipt and use the
existing status reconciliation; do not delete it or reset the lease.

A later fresh install requires a new UUID, reviewed fixed artifacts and separate
normal setup authorization. Successful cancellation alone proves no runtime
compatibility, standby behavior or cold-boot recovery. Windows path work and
release acceptance remain separate.

## Verification

Focused tests exercise exact pinned services DATA, original evidence drift,
provisioning artifacts, active installer/worker rejection, old resume exclusion,
one real remove, lost terminals, and crashes before the separate receipt, after
terminal removal, after final deploy readback and before lease terminalization.
Host tests prove that unknown/wrong dispositions preserve pending and verified
cancellation preserves its history. Run the repository test suite before
integration. Real hardware admission can verify source/package identity without
authorizing or proving actual cancellation.
