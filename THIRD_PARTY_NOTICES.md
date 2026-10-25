# Third-party notices

- Launcher: derived from OmkarK97/webos-vibehack, MIT. Original Gathin and OmkarK97
  notices are retained in LICENSE. The font license is retained at launcher/fonts/OFL.txt.
- Outfit: SIL Open Font License 1.1, retained alongside the font.
- ws: bundled Node WebSocket dependency; license in native/app/vendor/ws/LICENSE.
- webos-service: supplied by the TV runtime, not redistributed here.
- Zig, Python and LG's webOS CLI are external build/setup prerequisites.
- Outbound HTTPS services bundle the Mozilla CA store converted by curl, under MPL 2.0.
  The snapshot, source, SHA-256 and refresh instructions are recorded in
  `docs/TLS-TRUST.md`; each service ships `ca-LICENSE.txt` alongside `ca-bundle.crt`.
- Compiled TV web apps include core-js (MIT) for ECMAScript compatibility and may
  include Babel helpers (MIT). Their license texts are retained in each web app's
  `compat-LICENSE.txt`. Babel and PostCSS are build tools, pinned by package-lock.json.

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
