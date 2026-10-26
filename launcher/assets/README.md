# Candidate Home artwork

These assets are used by the optional No-root tvOS appearance. **Sundown** is a
fictional series title rendered separately by the UI; the backdrop contains no
text or interface elements. It is not an Apple or streaming-service image and
has no dynamic content integration.

| File | Dimensions | Bytes | Provenance |
| --- | --- | --- | --- |
| `cinema-backdrop.jpg` | 1672×941 | 197269 | Original artwork generated with the built-in image-generation tool on 2026-10-26 |
| `cinema-backdrop-soft.jpg` | 480×270 | 5629 | Local derivative, preblurred with radius 14 for the dock/grid treatment |

The static duplicate avoids a live CSS blur filter on the TV. It does not prove
acceptable memory use, focus cadence or visual performance on physical hardware.

## Generation prompt

> Original fictional cinematic noir-series backdrop. Detective with short dark hair and jacket over light open-collar shirt beside a vintage convertible at a Los Angeles hillside overlook at golden hour. Wide16:9, detective slightly left at x43%, head near upper third, car across lower third. Calm dark upper-left negative space for separately rendered title. Film-still photography, teal shadows left, pale salmon sunlight right, hazy city and palms. No recognizable celebrity, text, logos, watermark, UI or cards.

The artwork depicts a fictional noir detective and vintage convertible at a Los
Angeles sunset, with teal shadows and warm sunlight. The UI applies its title,
dock and controls separately. Preserve the original/derivative relationship when
replacing the asset; do not introduce live filters or network requests implicitly.

## Typeface provenance

The presentation uses static Inter Display 4.1 Regular, Medium and SemiBold from
the [official Inter 4.1 ZIP](https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip),
under the [retained SIL Open Font License](../fonts/Inter-OFL.txt). WOFF2 filenames:
`InterDisplay-Regular.woff2`, `InterDisplay-Medium.woff2`, and
`InterDisplay-SemiBold.woff2`, under `launcher/fonts/`.
The local candidate also uses seven user-supplied proprietary SF Pro Display/Text
files under their original names in `launcher/fonts/` (Display Regular, Medium,
SemiBold and Bold; Text Light, Regular and SemiBold). Display uses weights
400/500/600/700 and Text uses 300/400/600; Inter and Noto remain fallbacks.
No redistribution license is asserted for the SF files, and the repository MIT
license does not cover them. See [third-party notices](../../THIRD_PARTY_NOTICES.md).

## User-supplied profile and shared glass texture

`profile.jpg` is the unchanged user-supplied portrait used for the local Home
avatar. It is not covered by the repository MIT license; no redistribution
license is asserted. No publication is part of this update.

Now Playing reuses the existing `dock-glass-home.jpg` texture with the dock-style
fill, radius and shadow. Reduce effects uses an opaque fallback. This reuses a
local static texture without adding a live blur filter or network request.
Hardware performance and HA acceptance remain outstanding.
