# Release integration flow

Features, fixes and maintenance integrate in `release/next`. Only a finalized
release PR from that branch may merge into `main`. This repository calls its
primary branch `main`, not `master`. The preparation branch has no version in
its name: choose the version when the candidate's scope is known.

## Collect changes without choosing a version

1. Create `release/next` from `main`, or fast-forward the existing branch to
   `main` after the previous release. Use merge commits for all PRs. Squash and
   rebase merging are disabled to preserve ancestry across release cycles.
2. Start the new cycle with `release-plan.json` containing `version: null`, empty
   `changes`/`excluded` lists and empty `acceptance`. Keep the last shipped
   `release-versions.json` value until freeze; it is not the next version.
3. Target implementation PRs at `release/next`. Record linked issues using
   GitHub's closing references or a plain `Related issues: #123, #456` line.
   Links and inventory numbers refer to this repository. Do not close a partially
   delivered issue merely because its PR merged.
4. Open a draft `release/next` → `main` PR using the release template. Its policy
   check remains unsuccessful until the version, scope and acceptance are final.
5. After merging implementation PRs, collect the inventory on `release/next`:

   ```sh
   git fetch origin main
   python3 scripts/release-flow.py collect
   ```

   This updates the plan with PR titles and linked issues without selecting a
   version. Review the summaries, add any extra related issues, and commit it.
   The collector includes only merged implementation PRs present in the commit
   range since `origin/main`; previous releases are not repeated.

An issue describes work; its implementation enters through a PR. Metadata-only
commits such as preparing the plan and selecting versions may be made directly
on the preparation branch. Product changes should enter through reviewed PRs.

## Freeze and validate the candidate

Choose the final version based on the actual scope. Set it in `release-plan.json`
and `release-versions.json`, update changed component manifests/versions, and
write `docs/RELEASE-X.Y.Z.md`. Component versions are independent of the overall
release version. A final plan looks like:

```json
{
  "schema": 1,
  "version": "1.2.0",
  "changes": [
    {"pr": 123, "issues": [45, 67], "summary": "Fix focus after returning Home"}
  ],
  "excluded": [
    {"pr": 124, "reason": "Reverted in full before candidate freeze"}
  ],
  "acceptance": "TV model and firmware; tested paths; untested paths; rollback evidence/link"
}
```

The required **Release policy** status is produced by a trusted
`pull_request_target` workflow executing policy from `main`. Feature PRs receive a separate **Integration policy** status, so their checks
cannot satisfy the release gate on another PR with the same SHA. Candidate commits
are fetched and read as data; their scripts are never executed by this workflow.
It rejects:

- A PR to `main` from any branch other than this repository's `release/next`.
- An unset, invalid, unchanged or regressing release version; mismatched metadata;
  missing release notes or empty hardware acceptance evidence.
- Missing, duplicate or unexpected implementation PRs in the release inventory.
  Every merged PR must be included or explicitly excluded with a reason. Partial
  delivery belongs in `changes` with an accurate summary; exclude only changes
  that will not ship.
- Omitted issues linked to included PRs. The gate checks closing references and
  `Related issues:` lines and verifies that listed issues are actual issues.
- An unsuccessful or incomplete trusted push build of the exact candidate SHA.
  Android and all four desktop jobs must each succeed. The policy waits up to
  35 minutes; rerun it if builds finish later.

`main` additionally requires up-to-date Linux/macOS tests, a PR and resolved
conversations. Administrators follow the same rules. Force pushes and branch
removal are disabled. No second maintainer approval is mandatory, allowing solo
maintenance; review the release diff before merging and keep repository write
access limited to trusted maintainers.

Apply the [release checklist](RELEASE_CHECKLIST.md) and Root Edition hardware
gates. CI cannot certify physical TV behavior: record actual acceptance and
untested paths honestly. Any new candidate commit invalidates its previous
checks and triggers a fresh complete build. Mark the PR ready only after all
checks and acceptance are complete.

## Merge, publish and notify

Merge the release PR using a merge commit. The existing publication pipeline
reuses the successful candidate installers after verifying that the exact second
parent and Git tree match the resulting `main` commit. It runs the full tests,
packages, signs and verifies the release without recompiling platform installers.
A merge means integrated;
shipping is confirmed only after publication and verification of the packages
and signed update feeds.

Ordinary PRs run only affected checks: TV/webOS, installer, Android, preview or
packaging/release tools. Shared dependencies enable every affected group; unknown
paths conservatively enable all checks. Documentation-only changes skip application
checks and Pages builds while keeping the required Linux/macOS status names green.
Once a candidate is frozen (final new version, matching plan, acceptance and notes),
every subsequent candidate commit, including a documentation correction, needs a
complete build so shipped artifacts remain bound to that exact source tree.
Feature branches run tests on PR events; `main` and `release/next` also run tests
on pushes. Preview Pages runs its own focused tests instead of the full suite.

Packaging saves `RELEASE-INVENTORY.json` with the tag, exact source commit,
release PR, included implementation PRs, their issues and delivered summaries.
The asset is included in checksums. Notification scope comes from this frozen
inventory, not from later edits to PR descriptions.

After successful publication and final verification, automation comments on
every included implementation PR, every listed issue and the release PR. A
shared issue receives one comment listing all of its delivered changes.
Excluded PRs receive no shipping notice. Notices describe the delivered portion
and do not close issues automatically.

Retries verify the signed feeds again, bind the release tag and build metadata
to the inventory's source commit, verify its checksum and compare it with the
committed plan. A hidden `<!-- shipped:vX.Y.Z -->` marker identifies each
GitHub Actions bot comment. Existing matching comments are reused/updated;
human comments with the same marker are not touched. A failed target does not
prevent notices to other targets. The workflow reports the missing targets and
fails so the delivery can be retried.

If publication fails, no shipping notice is sent. If notices fail after
publication, the product is already released: do not republish it just to retry
comments. Run **Retry release notifications** on `main` with the published tag.
It shares the publication concurrency lock and only delivers missing/changed
notices. Releases predating this inventory format are verified and skipped.
Never reuse a published version for changed contents; use a new patch release.
Resolve a failed publication before integrating the next release.

After the release merges, fast-forward `release/next` to `main`, clear the plan
for the next cycle, and continue collecting features without a new version.

## Initial rollout and protection maintenance

The first installation is an infrastructure bootstrap: merge the workflow,
script, tests and documentation through an installation PR from `release/next`
to `main`, with product versions unchanged. Existing CI must pass. This one-time
step installs the trusted policy before its status becomes mandatory; the
already published product version is skipped by the publication planner.
It does not publish a product release or send shipping notices.

Then an administrator applies and reads back repository merge settings and the
complete branch protection policy:

```sh
python3 scripts/release-flow.py protect
```

This requires repository administration permission. Run it only for intentional
policy setup: it manages the exact required checks and merge methods described
above. Do not require the new status before the bootstrap merge, as its trusted
workflow does not exist on `main` yet. Product releases after bootstrap must
follow the final candidate gate; there is no permanent bootstrap exception.

Workflow changes themselves take effect only after integration into `main`.
Release-branch Android signing uses the persistent preview identity on trusted
pushes; PR workflows receive no signing secrets. Stable feed signing and
publication remain restricted to `main` and the `release-signing` environment.
