# v1.1.0 — system updates and automatic Root Python

**Candidate preparation; not published.** The release PR remains in draft.
Physical-TV acceptance, the new Helper rollback transition and exact final
artifacts still need validation before merging into main or publishing.

| Component | Previous release | Candidate |
| --- | --- | --- |
| cytv installer | 0.2.16 | 0.3.0 |
| Home | 1.3.8 | 1.4.0 |
| Home Helper | 0.6.18 | 0.6.19 |
| Root Edition | 0.1.12 | 0.2.0 |
| Home Updater | 0.1.6 | 0.2.0 |
| Root Updater | 0.1.1 | 0.2.0 |
| Android installer | 0.1.7-preview / code 8 | 0.2.0-preview / code 9 |
| New fixed System Updater supervisor | Not shipped | 1.0.0 / protocol 1 |

## Included changes

- Compile No-root Helper app/service JS for TV Node 0.12.2+ with Babel,
  core-js and safe-buffer. Select a compatible WebSocket implementation on old
  TV runtimes and preserve controller errors when logging fails (#47).
  Input-device, standby and cold-boot acceptance on the reported LG 49UJ750V
  remains outstanding.
- Update compatible TV edition components through a signed release set with an
  independent supervisor, preserved profile and explicit rollback. Computer
  setup provisions the supervisor and captures existing recovery baselines;
  uncertain operations, conflicting legacy installers and downgrades are refused.
- Root setup automatically supplies a verified private ARMv7 Python when the TV
  has no suitable Python 3.9+. Working system interpreters skip the download.
  Desktop and Android installers do not contain the additional runtime archive.
  The optional download is about 26.3 MB, normalized SSH transfer about 51.5 MB
  and installed regular files about 119.3 MB. Staging requires additional free
  space. No system Python, system libc or global PATH changes are made.
- Persist and validate interpreter bindings for Root, watchdogs, boot recovery,
  independent updaters and interrupted removal. Verify executable bytes before
  running retained interpreters. Keep runtime slots needed by recovery/rollback.
  `cytv --prepare-python-runtime` prepares a verified offline cache without a TV.
- Identify individual Root requirement failures and record safe numeric SSH
  command exit statuses in diagnostic JSON without credentials or raw output.
- Correct deterministic IPK archive metadata, protected installation staging,
  older-TV Node URL/HTTPS compatibility and certificate trust for updater and
  renewal services. Preserve unresolved installation/recovery evidence.
- Fix Android operation receipt creation on filesystems that reject hard links.
- Maintain subsequent release candidates after verified publication and preserve
  release scope/notification provenance.

Related implementation PRs: #36, #38, #39, #40, #42 and #43. The preparation PR
is collected into release-plan.json after integration. Issue #37 remains open for
UK6540PTD device feedback; issue #24's original unfinished removal is not claimed
resolved by its separate Android receipt fix.

## Device feedback and limits

The issue #37 TV is **LG UK6540PTD, firmware 05.50.70, ARM32**, not LG C3.
The reporter confirmed Python 2.7.12 and no available Python 3. The new managed
runtime has not been tested on that TV. ARM32 QEMU startup and automated tests
do not establish compatibility with its loader, libc, webOS APIs, remote input,
cold boot or rollback.

Root and on-TV system updates still require their other platform prerequisites,
including appropriate root services and TV Node.js. Supplying Python does not
replace those requirements. Unrooted TVs use the computer installer. Existing
Root/updater infrastructure transitions require computer-assisted setup; this
release does not promise that a legacy app-only OTA update installs new runtime
or supervisor infrastructure.

Previously recorded hardware evidence remains limited to its original model,
firmware and artifact scope. New physical Android/TV checks, normal/cold startup,
Home/back handling, failsafe, complete system upgrade and rollback are pending.
The Helper 0.6.19 archive and rollback approval must be recorded from actual
validation; the retained 0.6.18 approval does not authorize this new package.

## Test installers

Maintainers can explicitly run **cytv standalone builds** on `release/next` with
`test_build=true` after version metadata and these notes are present. This produces
GitHub Actions artifacts for device feedback while acceptance remains empty.
It does not finalize the candidate, publish a release, sign OTA feeds, or allow
merging the release PR. Final publication still requires the complete existing
release policy and a fresh build of the actual finalized commit.
