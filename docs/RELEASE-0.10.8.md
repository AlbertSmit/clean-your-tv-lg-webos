# v0.10.8 — No-root ARM32 runtime detection

Includes cytv **0.2.11**, Home **1.3.3**, Home Helper **0.6.16**,
Root Edition **0.1.7**, and No-root Updater **0.1.5**.

The No-root installer no longer equates an aarch64 kernel with a lack of ARM32
support. It reads the first 20 bytes of the TV shell ELF header and verifies
little-endian ARM32 userspace on supported ARM kernels before package installation.
The check only reads system information; it does not execute Home Helper or
intercept remote-control input. Unknown or incompatible runtimes remain blocked.
A verified 32-bit shell establishes ARM32 execution support, not full Helper,
remote-control or firmware compatibility.

Generated diagnostic JSON now includes allowlisted `kernel_arch`, `userland_abi`
and `arm32_supported` fields under `tv`. Raw ELF data, command output, addresses,
keys and passphrases are excluded. Regression tests cover aarch64 with ARM32
userspace, incompatible/malformed ELF headers, and report propagation/privacy.
The clearer failure message is translated into all ten supported languages.

This addresses the second installation blocker reported in issue #15 after
v0.10.6 resolved SSH authentication. The reporter's LG OLED48C3LA on webOS26 /
11.2.0-3701 still requires a retest; no additional hardware support is claimed.

## Downloads and retry

Close the old installer, download `cytv-windows-x64.exe` from this release and
confirm **cytv 0.2.11**. Choose **No-root** and follow the existing Developer Mode
and pairing steps. If it still fails, attach the new diagnostic JSON and the
visible error, with private information redacted. Do not share keys or passphrases.

macOS ARM64/Intel ZIPs, Linux x64 Debian and console executables are included.
The manual TV bundles and signed update feeds are retained from v0.10.7;
TV component versions and recovery infrastructure are unchanged.
`BUILD-INFO.json` records provenance and `SHA256SUMS` covers release assets.
macOS builds are ad-hoc signed, not Apple-notarized.
