# Third-party notices

- Launcher: derived from OmkarK97/webos-vibehack, MIT. Original Gathin and OmkarK97
  notices are retained in LICENSE. The font license is retained at launcher/fonts/OFL.txt.
- Outfit: SIL Open Font License 1.1, retained alongside the font.
- ws: bundled Node WebSocket dependency; license in native/app/vendor/ws/LICENSE.
- Legacy Helper uses ws 6.2.4, the UTF-8 validator from ws 7.5.11 and
  async-limiter 1.0.1 (MIT); sources, local changes and licenses are retained in
  `native/app/vendor/ws-legacy/`. Modern TV Node continues to use ws 8.21.0.
- webos-service: supplied by the TV runtime, not redistributed here.
- Zig, Python and LG's webOS CLI are external build/setup prerequisites.
- The optional Root TV runtime is CPython 3.13.17 from python-build-standalone
  release 20261021 (`armv7-unknown-linux-gnueabi`). It is downloaded separately
  only when required; ordinary installers do not embed the archive. Upstream
  Python and dependency license files accompany that runtime. Pin, provenance,
  checksum and update procedure: [optional Python](docs/OPTIONAL-PYTHON.md).
- Outbound HTTPS services bundle the Mozilla CA store converted by curl, under MPL 2.0.
  The snapshot, source, SHA-256 and refresh instructions are recorded in
  `docs/TLS-TRUST.md`; each service ships `ca-LICENSE.txt` alongside `ca-bundle.crt`.
- Compiled TV web apps include core-js (MIT) for ECMAScript compatibility and may
  include Babel helpers (MIT). Their license texts are retained in each web app's
  `compat-LICENSE.txt`. Babel and PostCSS are build tools, pinned by package-lock.json.
- Home presentation modules bundle Nano JSX core 0.2.1 (MIT) locally in
  `home-ui.js`, with its license retained as `home-ui-LICENSE.txt`. esbuild
  0.28.2 is a build tool pinned by package-lock.json. No CDN runtime is required.
- Compiled Helper app and service include core-js, safe-buffer and Babel helpers
  (MIT), with licenses in each package directory's `compat-LICENSE.txt`.

TV app icons are downloaded only for a user's local app inventory. They are not
included in a clean public checkout or generic release package.

## Desktop wizard: Qt for Python

The optional windowed cytv distributions include PySide6 Essentials and Shiboken6
(Qt for Python), distributed under LGPL-3.0 (with applicable Qt exceptions) or
commercial terms. cytv uses the LGPL distribution with dynamically linked Qt
libraries. This does not change the license of cytv itself.

- Project and source: https://code.qt.io/cgit/pyside/pyside-setup.git/
- Qt source: https://code.qt.io/cgit/qt/
- License: https://www.gnu.org/licenses/lgpl-3.0.html

The LGPL-3.0 and accompanying GPL-3.0 license texts are included in the payload's
`licenses/Qt` directory. The pinned desktop runtime is Qt for Python 6.10.2;
its corresponding source is available under tag `v6.10.2` in the repositories above. Desktop packages use an unpacked application directory so
users can replace the dynamically linked libraries with compatible builds.

## Noto language fonts

Noto Sans, Noto Sans Devanagari and Noto Sans KR from the Google Fonts repository (https://github.com/google/fonts), distributed under the SIL Open Font License 1.1. Static regular subsets for Latin, Cyrillic, Devanagari and Hangul are bundled locally in `launcher/fonts/`; original copyright and license texts are included as `NotoSans-OFL.txt`, `NotoSansDevanagari-OFL.txt`, and `NotoSansKR-OFL.txt`.


The independent System Updater bundles Mozilla CA root certificates from the
curl CA Extract bundle. The certificate data and MPL 2.0 license are distributed
as `updater-service/ca-bundle.crt` and `updater-service/ca-LICENSE.txt`, and copied
into the supervisor bootstrap bundle.

## Inter Display and candidate cinematic artwork

The No-root tvOS appearance bundles static Inter Display 4.1 Regular, Medium and
SemiBold, from the [official Inter 4.1 release archive](https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip):
`launcher/fonts/InterDisplay-Regular.woff2`, `InterDisplay-Medium.woff2` and
`InterDisplay-SemiBold.woff2`. Copyright (c) 2016 The Inter Project Authors;
distributed under SIL Open Font License 1.1, retained as
`launcher/fonts/Inter-OFL.txt`. [Inter source](https://github.com/rsms/inter).
The local candidate also contains seven user-supplied proprietary Apple SF Pro
files, retaining their supplied names: `sf-pro-display_regular.woff2`,
`sf-pro-display_medium.woff2`, `sf-pro-display_semibold.woff2`,
`sf-pro-display_bold.woff2`, `sf-pro-text_light.woff`,
`sf-pro-text_regular.woff2`, and `sf-pro-text_semibold.woff2`.
These are not covered by the repository MIT license; no redistribution license
is asserted. [Apple font information](https://developer.apple.com/fonts/).

The launcher uses a 96×96 derivative of an unchanged user-supplied portrait.
The shelf uses a crop and a thumbnail derivative of a user-supplied photograph.
These photographs are not covered by the repository MIT license; no
redistribution license is asserted. Their sources and processing notes are
recorded in [`launcher/assets/README.md`](launcher/assets/README.md).
