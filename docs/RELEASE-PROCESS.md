# Signing and publishing update feeds

The normal release trigger is a version change merged into `main`. Set
`release` and the changed component versions in `release-versions.json`, update
the matching application/service manifests and add `docs/RELEASE-X.Y.Z.md`.
No tag, terminal command, draft creation or Publish click is needed.

The existing four-platform build runs automatically. After its successful
completion, **Automatic release**:

1. Checks that the source is a successful `main` build from this repository and
   that the requested release has not already been published.
2. Runs the full test suite on Linux and macOS against that exact commit.
3. Downloads only that build's artifacts, checks payload versions and hashes in
   all seven installer files, and creates the public No-root ZIP and Root TAR
   bundles, release notes, `BUILD-INFO.json` and checksums.
4. Creates/resumes a draft targeting the exact build commit and uploads the
   prepared assets. A draft/tag for another commit stops the workflow.
5. Calls the protected signing workflow directly: it creates both feeds and
   rollback assets, signs them, uploads them, verifies every referenced package,
   publishes as latest and verifies again.

Already published versions are skipped. Failed tests, builds, packaging or
signing never advance a new release to latest. Retrying the failed workflow can
resume a draft for the same commit. Publication rechecks the draft immediately
before upload. A newer published version blocks older release attempts.

For pipeline maintenance, **Automatic release** also accepts a successful build
run ID for its exact commit and `validate_only=true`. This rebuilds/verifies the
complete release asset set without creating a draft, signing or publishing.
The signing workflow's separate `publish=false` mode validates production
signatures without changing release assets. These modes are for testing the
pipeline; normal releases need neither manual invocation.

For an already prepared draft or an explicit repair of a current release,
`node scripts/publish-release.cjs vX.Y.Z` remains the signing entry point.
It queues signing and publication; waiting for the workflow result is required.
An installer-only release preserves the existing older signed Home rollback.
A new Home release uses the nearest previous stable release's actual Home IPK.

The GitHub **release-signing** environment holds `UPDATE_SIGNING_PRIVATE_KEY` as
an encrypted environment secret. Only branch `main` may use that environment.
The secret is passed only to the preparation step and is never written into an
artifact or a log. Keep the offline key backup. Re-provisioning requires an
explicit operator action; changing the signing identity also requires updating
and deploying the clients' pinned public key.

The workflow has a `publish=false` input for an end-to-end generation/signing
check that leaves release assets and publication state untouched. Its artifact
contains only public feeds, IPKs and metadata. Existing published releases can
be repaired through the same workflow; older-than-latest tags are rejected.

For a read-only check of existing public/draft feeds:

```sh
node scripts/publish-release.cjs vX.Y.Z --check-only
```

Do not publish directly with `gh release edit` or the web Publish button: these
bypass preparation. GitHub does not emit draft-created/edited workflow events,
so the version change in `main` is the normal release entry point. The read-only **Release
update feed** workflow still detects invalid feeds after public release edits.
The signing workflow verifies inline after publishing because changes made by
`GITHUB_TOKEN` do not trigger another release workflow.

A wrong/missing key, absent bundle, version regression, incompatible rollback,
changed package without a component-version bump, or mismatched provenance
stops the workflow. A Helper version change needs a compatible, tested rollback
baseline; the automation stops rather than publish an unusable No-root offer.
The previous stable release must have current build metadata and public bundles.
Version selection, release notes and TV acceptance remain development work;
all release build, packaging, signing and publication commands run in CI.
