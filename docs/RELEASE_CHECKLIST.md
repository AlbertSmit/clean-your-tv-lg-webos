# Release checks

- Run scripts/test.sh and scripts/build.sh.
- Build from a clean inventory; inspect package contents for credentials and state.
- Preserve licenses and upstream attribution.
- Mark hardware-tested and untested paths explicitly.
- Keep a rollback package locally.
- Publish checksums with artifacts.
- Never upload firmware, SSH/SSAP keys, live device backups or raw personal logs.
