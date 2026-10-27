# Root cold-boot identity and presentation

**Goal:** distinguish startup-session failures from initial screen selection and remove clock-dependent Root session identity.

**Evidence:** on the supervised C3, kernel UUID survived cold power while btime changed; one cold start disabled Root, another retained healthy Root while Live TV remained foreground. Short Home passed in the second case. An inert `/tmp` probe disappeared after that actual AC-off/snapshot path. No firmware-wide lifetime guarantee follows.

**Architecture:** keep recovery-before-gate and all lifecycle authority checks. Replace UUID:btime identity centrally in `intent_runtime.boot_identity` with UUID plus a private volatile nonce shared under flock. Create once with atomic publication and trusted ownership/type checks; reject malformed or indirect records. Boot gate, health, shutdown, update and audio consumers use the existing function. Preserve explicit/emergency off and duplicate callbacks. Invalid identity during boot must attempt bound fail-closed recovery. Keep foreground policy unchanged until startup-screen evidence is understood.

- [x] Prove clock correction, volatile reset, concurrent callers, permissions and unsafe-record behavior with failing tests.
- [x] Implement the central identity fix without new dependencies or extra runtime inventory files.
- [x] Verify health/shutdown/gate consumers and existing fail-closed/duplicate/focus regressions; add early same-session fault audit.
- [x] Resolve native LG power-on-screen selection separately; never infer foreground success from routing readback.
- [x] Update English technical documentation and affected localized setup guidance; record actual device paths and limitations.
- [x] Run focused and full `scripts/test.sh`, build and verify payload, and obtain independent review.
- [ ] Save a PR to `release/next`. Deliver retained runtime only through supported checked setup/update; do not hand-edit code or integrity receipts. Hardware acceptance of new code remains pending until that delivery and the supervised matrix actually run.

Native Home auto-launch was already on. Implemented one optional hardware-start fallback after guarded restart; latest foreground read preserves other apps, launch never holds the operation lock, and in-flight cancellation stays off. Foreground observation and launch are not atomic platform operations. Review found and corrected log-failure recovery ordering and JSON-null session rejection.
