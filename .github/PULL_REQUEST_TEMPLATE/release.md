## Release candidate

Base: `main`. Head: `release/next` in this repository.
Keep this PR in draft while collecting changes. Choose the version at freeze.

- [ ] `release-plan.json` lists every merged implementation PR and its issues.
- [ ] Reverted PRs are listed under `excluded` with a reason.
- [ ] Final version matches `release-versions.json` and release notes.
- [ ] Changed component manifests and versions agree.
- [ ] TV acceptance evidence and untested paths are recorded in `acceptance`.
- [ ] Complete platform builds and required tests pass for the current candidate.
- [ ] Rollback baseline is verified.

A merge integrates the release. Shipping notices follow verified publication.
