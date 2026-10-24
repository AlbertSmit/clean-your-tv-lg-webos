# Published Helper baseline

`com.local.nativehome_0.6.16_arm.ipk` is the exact public Helper from
[v0.10.8](https://github.com/Razdva122/clean-your-tv-lg-webos/releases/tag/v0.10.8),
extracted from its digest-verified `clean-your-tv-no-root-1.3.4.zip`.

SHA-256: `ccabf56c814d2aaf35853d95be2aac67614a67b79e223151b93260d58b82f5f1`.

The builder pins this hash and reuses these bytes while the Helper version is
0.6.16. This preserves the signed update/rollback baseline. Current Helper
source differs in icon assets and appinfo formatting only; the executable and
service files match the public baseline. A future Helper version resumes normal
source compilation and requires a separately validated rollback baseline.
