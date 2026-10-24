# Signing and publishing update feeds

Prepare the draft release with its final installers, the public No-root ZIP,
Root TAR bundle and `BUILD-INFO.json`. The metadata must identify the exact
source commit and its `release-versions.json`. Then run:

```sh
node scripts/publish-release.cjs vX.Y.Z
```

This queues **Sign and publish release** on `main`. Wait for that workflow to
finish; queuing alone does not mean the release is published. It automatically:

1. Reads the actual Home, Helper and Root IPKs from the release bundles and
   verifies their embedded application IDs/versions against committed metadata.
2. Finds the nearest older stable release. A new Home version uses that release's
   actual Home package as rollback. An installer-only release preserves the
   existing older signed rollback, verifying its signature and exact package.
3. Creates fresh `update.json`, `previous-update.json` and `root-update.json` from
   final package hashes and signs them with the pinned production key.
4. Uploads the candidate and rollback IPKs, updates `BUILD-INFO.json` and
   `SHA256SUMS`, then downloads and verifies both feeds and all referenced IPKs.
5. Publishes the draft as latest only after validation, and verifies it again.

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
so the checked command is the release entry point. The read-only **Release
update feed** workflow still detects invalid feeds after public release edits.
The signing workflow verifies inline after publishing because changes made by
`GITHUB_TOKEN` do not trigger another release workflow.

A wrong/missing key, absent bundle, version regression, incompatible rollback,
changed package without a component-version bump, or mismatched provenance
stops the workflow. A Helper version change needs a compatible, tested rollback
baseline; the automation stops rather than publish an unusable No-root offer.
The previous stable release must have current build metadata and public bundles.
This automates OTA signing/publication, not release version selection, installer
builds, or TV acceptance testing.
