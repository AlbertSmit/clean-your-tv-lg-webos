# Issue 107 Windows follow-up implementation plan

> Execute inline using executing-plans. Keep this independent of the pending BX routing contract.

**Goal:** Prevent Windows checkout corruption of POSIX scripts and avoid encoding crashes in redirected console output.
**Architecture:** Enforce LF with Git attributes; reject CR-bearing shell scripts at the existing payload integrity boundary, including IPK contents. Configure standard output/error to preserve their encoding with backslash replacement of unsupported characters before any CLI parsing or translation.
**Tech stack:** Git attributes, Python standard library, unittest, existing PyInstaller CI.
**Spec:** GitHub issue #107 (Windows follow-up only).

## Constraints

Preserve binary assets byte-for-byte, existing security/recovery checks and published artifacts. No version bump or BX compatibility claim. Target release/next. Existing main-checkout changes belong to other work.

## Tasks

- [x] Reproduce exact v1.2.0 Windows/Linux nested IPK differences and strict cp1252 output failure; record hashes.
- [x] Write a real core.autocrlf=true checkout regression and payload tests for loose and IPK-contained CRLF shell scripts, mixed/bare CR and unchanged binary assets. Run before implementation; expect failures.
- [x] Add .gitattributes and minimal rejection at package.verify_payload; rerun tests.
- [x] Write CLI subprocess tests for localized help, parser errors, UTF-8 fidelity and redirected cp1252. Run before implementation; expect UnicodeEncodeError.
- [x] Configure real standard text streams before CLI parsing; preserve encoding and use backslashreplace. Reuse a subprocess smoke script for source and frozen executables.
- [x] Add frozen Windows CI output checks and verify payload LF during its existing --check-payload check. Build a fresh local payload and exercise exact artifacts.
- [x] Update English technical documentation, all twelve localized guides and a bounded investigation record; distinguish candidate fixes from published releases and unresolved BX work.
- [ ] Run scripts/test.sh, independent code review, diff checks and meaningful build checks. Commit/push a partial-fix PR, update issue evidence/status, archive the temporary worktree after preserving work.
