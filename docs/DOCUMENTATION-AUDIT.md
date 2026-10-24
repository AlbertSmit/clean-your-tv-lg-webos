# Documentation audit — 2026-10-24

Scope: the primary `stable/` checkout's 61 tracked Markdown files, plus the local
workspace README. Release-desktop is a secondary checkout with uncommitted UI
work, not a second documentation source to edit. Archives and legacy symlinked
checkouts retain their historical contents. Third-party notices and vendored
library documentation are upstream material.

Sources of truth: `release-versions.json`, application manifests, `cytv` setup
and maintenance operations, the current Home settings implementations, build
scripts and dated hardware acceptance records. No TV installation, network
connection or new hardware validation was performed for this documentation pass.

## Findings and corrections

| Area | Outdated or conflicting information | Correction |
| --- | --- | --- |
| Installation | INSTALL covered only No-root and said Root had no supported installer | Shared No-root/Root entry point: requirements, cytv downloads, edition-specific setup, verification, recovery and manual/source paths |
| Project overview | Claimed the described release was No-root only; listed Home 1.1.0 and Helper 0.6.13 as current | Both editions; cytv 0.2.7, Home 1.3.3, Helper 0.6.16, Root 0.1.5 and No-root Updater 0.1.5 |
| Manual command examples | Home 1.2.2, Helper 0.6.13 and Root 0.1.1/0.1.3 filenames/build arguments | Current component versions; retain explicit legacy-version recovery guidance |
| Root overview and acceptance | Current distribution still described as Root 0.1.1/0.1.2 | Root 0.1.5, while keeping the original versions and limits of hardware evidence |
| Home controls | Old activation/exit labels and obsolete Keep confirmation in test instructions | Change Home enables/disables persistent routing; Open LG Home is a one-time visit; normal activation has no Keep step |
| Emergency gesture | Root rollout assumed every No-root Helper used holding Home | Triple Home for current builds; holding Home only for Helper through 0.6.13 |
| Beta renewal | Enable Beta presented as the current button | Current auto-renewal controls, historical label noted; real unrooted renewal remains unverified |
| Localized guides | All ten introductions described the desktop app and language selection as future work | Reference v0.10.3 availability and the shared install guide |
| Maintenance and recovery | No-root webOS CLI commands looked like general instructions | Clearly scoped to No-root source installs, with cytv and Root recovery/removal paths |
| Root doctor/package docs | Claimed no installer existed or permanent enable was unavailable | Distinguish read-only doctor from installer; describe implemented activation and manual updater setup |
| Compatibility and inventory | App discovery described as computer-only; Windows described only as a shell workflow | Document + / Add app refresh, native Windows cytv console, and separate source/OS acceptance limits |
| Build/contribution guidance | Updater described only against v0.7.1; English-only rule conflicted with localized guides | Current component source, separate updater build, localized user documentation and current emergency behavior |
| Historical development notes | Undated-looking blockers could be mistaken for current release requirements | Explicit history boundaries and links to current installation; retain original evidence |
| Local workspace map | stable described as v0.8.1; integrated Root and release checkout were missing | Current distribution and checkout roles |

## Evidence retained and remaining limits

Release notes, changelog entries, dated plans/specifications, RC records and
version-specific acceptance reports keep their original versions and outcomes.
Updating a version label does not certify a new binary. Root cold-power testing,
the intermittent gesture observation, C4 follow-up checks, C5/webOS 26 startup,
Termux end-to-end behavior and unrooted renewal remain subject to their documented
validation limits. Parallel runtime, release metadata and release-desktop changes were preserved.
The final command examples follow the concurrently prepared v0.10.4 metadata;
v0.10.3 remains the introduction point for desktop language selection.

Local file and heading links were checked across tracked Markdown. Three existing
links in `native/app/vendor/ws/README.md` refer to omitted upstream `doc/ws.md`;
these were left in the vendored documentation. External websites, published asset
availability and OS dialogs were not independently revalidated in this pass.

Current guides still use preview terminology in places because the Root package
identity and manual bundle maturity remain separate from model-scoped historical
stable acceptance. Do not remove those caveats simply to match a version number.
