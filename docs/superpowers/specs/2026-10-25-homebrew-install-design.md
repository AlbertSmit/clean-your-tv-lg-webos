# Homebrew installation alongside cytv

Date: 2026-10-25. Status: implementation design; no Homebrew support is shipped by this document.

## Goal and execution handoff

Install and maintain the Root edition from the TV through Homebrew Channel,
while retaining cytv on Windows, macOS, Linux and Android and its No-root flow.
Both entry points must operate on the same installed product, profile and recovery
records. Installing through one must not require uninstalling to use the other.

The user requested planning first and **GPT-6.1 Sol** for implementation.
The current assistant has no tool for changing its own model. Select that model
in this task before executing the implementation plan.

Implementation uses branch `codex/homebrew-install`. The user authorized temporary
managed worktrees on 2026-10-26 to avoid interference between parallel tasks and
requires deleting them after work. This supersedes the earlier single-checkout
constraint. Save changes/commits and any needed PR or artifacts before removing
the worktree. Do not remove another task's active checkout.

The initial shared-checkout handoffs were completed and all Homebrew changes were
saved before moving this task to its isolated managed worktree.

## Findings from the current code

- `root-edition/build.py` creates a launcher IPK and a separate complete bundle.
  `root-edition/deploy.py` verifies that bundle and provisions recovery on the TV.
  Installing the launcher IPK alone does not install the complete product.
- `cytv/operations.py` orchestrates Root setup through SSH, builds the local
  inventory, handles retained operations, and prepares Root Updater.
- `root-edition/updater/bootstrap.py` and `system-updater/setup.py` prepare two
  distinct recovery/update services. The independent System Updater coordinates
  complete signed releases, not arbitrary individual IPK replacements.
- `cytv/python_runtime.py` can supply a pinned private ARMv7 interpreter when
  Python 3.9+ is missing. Its download/normalization currently happens on the host.
- Startup entries 50, 51 and 52 are currently ordinary copied scripts. Catalog
  submission requires reviewing all three and their removal semantics.
- Existing deployment refuses unknown or retained state intentionally. A new
  entry point must not bypass those protections to make reinstall appear easy.

## Chosen approach

Publish a separate **CYTV Installer** TV application through Homebrew Channel,
with an identity distinct from Root Home and the two updaters. Proposed identity:
`com.cleanyourtv.installer`; validate that it is unused before packaging.
The installer bootstraps the existing edition packages through shared device-side
operations. Homebrew updates this installer; the existing System Updater continues
to own complete product updates. The installer must not become another updater.

This costs an additional small TV application but avoids two independent systems
replacing Root Home and recovery components. The listing must explicitly describe
an installer. Use `utility` for this listing, rather than claiming it is itself the
launcher. Removing CYTV Installer removes only that installer: the screen and
listing must explain that the separately installed CYTV components have a complete
removal action. Removing any component directly must still be safe.

Alternatives considered:

1. List the current Root Home IPK: insufficient bootstrap and unsafe independent
   updates, so rejected for this implementation.
2. Turn Root Home into its own bootstrap and self-update coordinator: couples the
   running Home UI to its installation and recovery; larger change than needed.
3. Separate TV installer plus shared device operations: selected. No automatic
   promise that Homebrew maintainers will accept the listing or its packaging.

## Installation and ownership contract

The TV installer first inspects root execution, Node, Python, ARM ABI, free space,
package identities, existing journals, pending installs and recovery state.
Homebrew's documented `exec`/`spawn` service can run the fixed bundled entry point;
it does not guarantee root, so the entry point must verify effective UID itself.
Do not expose a shell input, arbitrary URL, arbitrary path or generic command API.

For a clean compatible TV the user sees the release, required components and any
private-runtime requirement before choosing Install. The coordinator then:

1. Verifies the exact offline bundle and inspects TV prerequisites without changing
   product state.
2. Prepares or reuses the verified interpreter; unsupported hardware stops here.
   Immutable runtime promotion uses the existing candidate-interpreter lock.
3. Re-inspects product state under the shared installation/update lease, then
   installs Root Home with its existing bounded recovery preparation.
4. Prepares Root Updater and its matching rollback baseline.
5. Offers explicit System Updater preparation using the existing trust contracts.
6. Discovers installed apps locally and preserves the existing profile if present.
7. Reports verified installation. Home activation is a separate existing guarded
   action and never clears an emergency-stop latch.

Host-side SSH and the TV installer call the same device operations. Keep cytv's
connection, credential handling and UI adapters on the host. Do not copy the
whole desktop installer onto the TV or implement a second sequence of shell
commands in browser JavaScript.

Existing installations are classified by actual receipts, hashes and protocols,
not by which installer was used. A current complete installation opens maintenance
without reinstall. A known older installation needs an explicitly supported
migration. A pending or uncertain installation offers inspection/recovery only;
absence of an installer process is not proof of completion. Never synthesize a
successful terminal installer event from package version readback.

## Private Python and release payload

Avoid fetching and executing arbitrary bootstrap scripts. Reuse the pinned runtime
and its current provenance/license/ABI rules. Normalize the runtime during the
release build, then ship a verified offline payload for supported ARMv7 TVs.
Before claiming parity with cytv, implement a small Node 8-compatible verifier and
installer for that normalized payload, preserving path, link, ownership, size,
hash and interpreter-binding checks. Never require Python to install Python.

Measure IPK size and TV staging space. If an embedded payload cannot meet actual
device limits, use a separately authenticated release asset and update this design
before implementation of downloading. Do not silently drop integrity checks or
publish a path that only works on developer machines with preinstalled Python.

## Recovery, removal and concurrency

All product setup, update and removal clients must share device-side exclusion.
The immutable interpreter can be prepared before the Python-based product lease;
product state is re-inspected under that lease before any product mutation.
UI reload,
network loss or closing the installer does not retry a submitted package operation.
Persistent operation identifiers and terminal receipts allow status and safe
continuation from cytv or the TV. The installer UI does not own the worker's life.

Managed startup hooks are receipt-owned 0700 regular wrappers. They invoke only
private `python_boot.js` and `startup_guard.py` under their owner's `/var/lib`
state. The guard reads installed package identity as bounded DATA through checked
descriptors and never executes a package startup script. Only the exact fixed
root-owned developer platform ancestor chain may be writable; package leaves and
files stay root-owned and nonwritable by group/others. Private readers stay strict.
The 2026-10-26 [device-boundary correction](2026-10-26-homebrew-device-boundary.md)
supersedes the former package-target symlink design.

The owners of hooks 50/51/52 are respectively Root Home, Root Updater and System
Updater. Missing, unsafe or foreign owner metadata suppresses automatic startup.
Exact v1 regular hooks and v2 links migrate to v3 (`version`, `path`, `owner_app`,
`sha256`) with retained previous proof before atomic replacement. Unlinking an
exact owned v2 link does not trust its replaceable target. Collisions and drift
remain errors. Independent private recovery can restore LG Home after package loss;
live workers must stop rearming without clearing emergency/off state.

The initial privileged HBC launch trusts the installed application. The built
bootstrap pins the outer payload-manifest SHA256. Before later Python execution,
copy/hash original-inventory bytes into a unique private 0700 `.exec-*` directory
under `/var/lib/clean-your-tv-installer`. Payload-consuming inspect/install/fresh
remove stage all required component data and manifests plus executable closure
without the unused runtime archive; `--payload` names that private tree. Status,
restore, activate and resume stage only the Root Updater code/support closure.
Imports never resolve from the shared source. Ephemeral staging during inspect is
allowed without product/Home/profile/runtime-slot/operation-receipt mutations.
Clean only the invocation's stage after child exit, retaining unknown drift. Durable
request snapshots and the original operation UUID/lease continue to authorize
all detached work and continuation.

Test deletion through LG's UI/Homebrew separately from CYTV's complete removal.
The system supplies no uninstall hook. No correctness claim may depend on cleanup
code being invoked by an external package remover. If safe direct removal cannot
be established, do not submit to the Homebrew catalog.

## Non-goals and unchanged guarantees

- No rooting, firmware modification, telemetry controls or wallpaper work.
- Homebrew installation initially supports Root only. cytv retains both editions.
- TV Node.js 8+ and Python 3.9+ remain the device execution floors.
- Do not broaden ARM/input/firmware support without evidence.
- Keep triple-Home escape, watchdogs, key-up and unrelated buttons intact.
- Keep private diagnostics, addresses, app inventories and credentials out of
  public test artifacts. Synthetic profiles are sufficient for automated tests.
- No release version is selected during feature preparation.

## Acceptance

Automated gates cover payload validation, state classification, concurrency,
interruption handling, ownership checks, packaging and cytv regression. Physical
TV acceptance must cover clean HBC setup, both installer handoff directions,
upgrade/rollback, direct removal, triple-Home, standby and separately cold boot.
Record exact artifacts/model/webOS/firmware and unresolved scenarios. Historical
C3 acceptance does not certify this new installation path.

Release integration targets `release/next`. Update the ten user guides when setup
behavior changes. Prepare a Homebrew submission only after accepted artifacts and
public HTTPS URLs exist; submission and maintainer approval remain distinct steps.

## Primary references reviewed on 2026-10-25

- [Homebrew submission format](https://www.webosbrew.org/develop/guides/publishing/how-to/)
- [Homebrew rules](https://www.webosbrew.org/develop/guides/publishing/rules/)
- [Removal and startup guidance](https://www.webosbrew.org/develop/guides/publishing/guidelines/)
- [Homebrew execution service](https://github.com/webosbrew/webos-homebrew-channel#interfaces)
- [Catalog repository](https://github.com/webosbrew/apps-repo)

Follow current catalog requirements at submission time, including honest AI-use
disclosure and meaningful human review and physical-TV testing.
