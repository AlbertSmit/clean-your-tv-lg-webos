# Build

Requirements: Bash, Python 3, Node.js, webOS CLI, Zig 0.14.1, and a C compiler for tests.

```sh
scripts/test.sh
scripts/build.sh
```

Use `ZIG=/absolute/path/to/zig` and `ARES_PACKAGE=/absolute/path/to/ares-package`
when tools are not on PATH. Generic builds use an empty app inventory. For a useful
launcher, run `sync-apps.py` before packaging. Do not publish personalized packages.

Development outputs: launcher 1.2.0, helper 0.6.13, and SHA256SUMS in `dist/`.

The build stages an allowlisted set of source files and empty state directories.
A package postprocessor sets those two directories to prisoner:jailer, mode 0770,
for the tested Developer Mode environment. No root access is required to install.

The relay, controller and startup service use separate locks, heartbeats and a
persistent emergency stop. The startup service claims a boot before launching so
a failure cannot produce an automatic retry loop. A manual helper launch resumes
a stopped setup. See RECOVERY.md before changing this behavior.

Private runtime state includes pairing keys, control files and logs under the
helper's `state/` directory. Never build a public package from a live TV backup.

For the independent development updater package, run `scripts/build-updater.sh`. Read [UPDATES.md](UPDATES.md) before installing it; it is not part of v0.7.1.
