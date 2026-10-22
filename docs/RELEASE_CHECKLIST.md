# Release checks

- Run scripts/test.sh and scripts/build.sh.
- Build from a clean inventory; inspect package contents for credentials and state.
- Preserve licenses and upstream attribution.
- Mark hardware-tested and untested paths explicitly.
- Keep a rollback package locally.
- Publish checksums with artifacts.
- Never upload firmware, SSH/SSAP keys, live device backups or raw personal logs.

## Root Edition gate

- Keep development-only tools out of production IPKs.
- Do not publish a Root Edition installer until the hardware gates in
  [Root Edition testing](../root-edition/TESTING.md) pass.
- Verify exact metadata, registration cache, both profiles and SAM Home rollback.
- Document native-button emergency behavior separately from No-root controls.
- Never present a diagnostic-app result as a production-launcher result.
