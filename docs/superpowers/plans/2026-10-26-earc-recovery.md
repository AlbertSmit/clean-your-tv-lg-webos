# eARC Recovery Implementation Plan

**Goal:** Deliver the approved eARC-only Root change as a separate PR to release/next.
**Architecture:** A private Python runtime owns serialized audio transactions and an opt-in power subscription worker. The existing privileged RPC launches only fixed commands. A Root subpanel reports capabilities, saved policy and restoration separately.
**Tech stack:** Existing Python 3.9+, Node 8+ Root service, ES5-compatible compiled TV web UI. No new dependencies or network endpoints.
**Spec:** ../../research/2026-10-26-earc.md (maintainer approved implementation on 2026-10-26).

## Constraints

- eARC only; no Bluetooth, microphone, volume controls or version bumps.
- Automatic recovery is experimental, off by default, one attempt per observed wake.
- Never infer audible success from API success; preserve emergency/off state.
- Skip unknown, ARC-only and combined/WOW Orchestra modes.
- Keep incomplete transactions for explicit recovery; never replay after a restart.

## Execution

- [x] Add failing Python tests for pure ARC eligibility, restored setting, interrupted transactions, stale policy, wake deduplication, timeout and user route changes. Run `python3 -m unittest discover -s root-edition/tests -p test_audio_recovery.py` and observe missing-feature failures.
- [x] Implement `runtime/audio_recovery.py` with private atomic policy/journal, a separate operation lock, fixed Luna calls, cancellation and power subscription. Use the existing product update mutex around settings effects. Run the focused tests to green.
- [x] Add RPC tests for strict payloads/root gating and package tests for real service/runtime/UI contents. Implement `service/audio-recovery.js`, service registration, provisioning allowlists, runtime inventory and boot startup; inhibit automatic policy on explicit/fault Home restoration. Verify focused tests and existing provisioning/build tests.
- [x] Add UI tests for capability gating, duplicate clicks, Back during recovery, stale responses and focus restoration. Implement `ui/root-audio.js`, the settings entry and packaging/preview integration. Verify with Node and browser screenshots at 1920x1080/1280x720.
- [x] Translate every new source string and update twelve user guides, Root README and developer acceptance notes. Run catalogue parity and compatibility checks.
- [x] Run `scripts/test.sh` and inspect actual IPK/support inventory; request an independent code review, fix actionable findings and rerun affected checks. Record untested physical behavior explicitly.
- [ ] Commit only eARC work, push codex/earc-recovery, open and attach a draft implementation PR targeting release/next, then archive the temporary managed worktree after preserving the commit remotely.

## Device acceptance

Pending: NANO95/Q950A cold boot and standby timing separately, Quick Start+ conditions, working audio interruption, ARC-only/WOW skips, disable while pending, update/removal, rollback and emergency release. Software checks cannot establish compatibility.
