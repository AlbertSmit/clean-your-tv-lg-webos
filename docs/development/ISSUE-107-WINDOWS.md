# Issue 107: Windows payload and console investigation

Scope: partial Windows follow-up for [#107](https://github.com/Razdva122/clean-your-tv-lg-webos/issues/107).
The original BX/webOS 5 routing, recovery, startup and removal report remains unresolved.
No TV was contacted or changed during this investigation. No publication/version bump.

## Exact published evidence (2026-10-27)

Downloaded v1.2.0 assets and checked each listed file against its published SHA256SUMS.
Read the frozen executables with PyInstaller CArchiveReader without executing them.

| Artifact | SHA-256 |
| --- | --- |
| Windows EXE | `ade3d26e40236b168a4657f010b80abecfec4eeaa22cb1bf54cbce9b0f59076a` |
| Linux executable | `9991b3caf8303268d46c1b2c7eb0f69f551e0e667da9952a46c21eb0bcf0869b` |
| Published standalone Root 0.3.0 IPK, also embedded in Linux | `ba28ca89dc036769dfd046937f7711dd8a43dc96f908d8e9863dbf9fcfb1aeca` |
| Root 0.3.0 IPK embedded in Windows | `089e9b2ca9875ef1e895c6073ce0ced803b9f237df6bbb072577ed2e82d65b77` |

All 26 differing files inside the two Root IPKs differ only by CRLF versus LF.
The packaged recovery service's `boot-recover.sh` has nine CRLF endings in Windows;
the published standalone/Linux copy has nine LF endings. Its Windows hash is
`fe6cebafa8202e46b42a6e52def73ba8ba440fd44d5ed2eb718284c1efe68e5f`;
the standalone/Linux hash is
`1742012913a83fdb6bfddb7e31ffd5f0d7de01927763c0a35956277a574fc467`.
No loose `.sh` member in either frozen payload had CRLF. This evidence applies
to these exact v1.2.0 artifacts; it does not characterize every Windows release.

With no attributes policy, a real Git checkout using `core.autocrlf=true` converts
a tracked LF shell script to CRLF. The existing builders intentionally read bytes,
so the conversion enters the IPK before the integrity hashes are recorded. Matching
hashes alone cannot detect that defective build. `.gitattributes` now keeps source
text at LF and preserves binary packages/media. The payload gate rejects CR in
loose and IPK-contained shell scripts without rewriting packages or their hashes.

The real CLI `--language ru --help`, with a temporary `--data-dir` and
`PYTHONIOENCODING=cp1252:strict`, exits with UnicodeEncodeError before the fix.
The same failure reproduces for Korean, Simplified Chinese and Hindi. Standard
text output/error streams now keep their chosen encoding and use backslashreplace
before parsing/translating. UTF-8 text remains intact; legacy output may contain
literal Unicode escapes. Custom output callbacks and absent GUI streams are retained.

## Verification and limits

Regression tests exercise real Git checkout bytes, binary preservation, correctly
hashed loose/nested CRLF and bare-CR rejection, valid LF packages, localized help
and parser errors under strict cp1252, and UTF-8 fidelity. Both failing regressions
were observed before the implementation. A fresh full payload build passed the
existing integrity/component checks plus the new shell check. Two actual Root
0.5.0 IPKs built on the same macOS host from native and `core.autocrlf=true`
source checkouts match byte-for-byte:
`e3a586775f5fcc46c1383379702b37bed925bafe87694c75fb3c57c197aa5af2`.
This isolates checkout conversion; it is not a native Windows build or a published
Root package identity.

Frozen macOS console and native Windows CI use the actual entrypoint and redirected
output. Frozen Python chooses its own native stream encoding; forcing
PYTHONIOENCODING in the parent is not proof of a frozen cp1252 stream. The source
subprocess cases explicitly cover cp1252; native Windows artifact checks cover the
runner's actual redirected streams. This is not a test on the reporter's computer.

The full BX contract needs the reporter's offered patch and original redacted
errors, consistent setup/activation/rollback/boot/removal behavior, and exact-build
BX plus newer-device acceptance. No fallback routing, permission relaxation,
timeout change or automatic recovery-state reset is included here.

Local final validation: `npm ci --ignore-scripts --no-audit --no-fund`, then
`PATH=/private/tmp/c4-test-venv/bin:$PATH PYTHONDONTWRITEBYTECODE=1 bash scripts/test.sh`
passed: 1391 Python cases with two expected skips, plus JS/C/compatibility checks.
The real macOS frozen console passed its runtime probe and redirected localized
help/error cases (UTF-8 forcing case intentionally skipped for the frozen build).
Both workflow YAML files parsed and `git diff --check` passed. Independent AI
review found no actionable code defects; this is not human/device acceptance.
Native Windows frozen verification runs in the PR workflow and again for the
full candidate build. Final candidate artifact identity and BX acceptance remain
release gates; no historical v1.2.0 package is modified by this change.
