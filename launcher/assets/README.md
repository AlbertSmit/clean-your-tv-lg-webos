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
Apple SF fonts are not embedded under the restriction in
[Apple's font license, section 2B](https://developer.apple.com/fonts/).
Inter is a substitute; exact font, artwork and motion parity and LG 50UP77006LB
hardware acceptance remain outstanding.
