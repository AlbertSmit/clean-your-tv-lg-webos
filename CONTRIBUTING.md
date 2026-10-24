# Contributing

Write technical and developer documentation in English. Maintain the ten localized
user guides under `docs/i18n/` when changing user-facing setup or controls.

Keep changes small and reproducible. Run `scripts/test.sh`; describe the test model,
firmware, expected behavior and actual behavior. Separate standby tests from cold
boots. Never claim compatibility from a successful package installation alone.

Input changes must preserve triple-Home emergency release (long Home in legacy
Helper versions through 0.6.13), watchdog behavior, key-up delivery
and unrelated buttons. Do not automatically clear emergency-stop state. Explain
any new persistent state, permission or network endpoint in the pull request.

Share only redacted logs. Exclude SSH/SSAP credentials, addresses, SSIDs, app
inventories and personal screenshots. Report security issues privately to the
repository maintainer once a reporting channel is configured; do not publish credentials.
