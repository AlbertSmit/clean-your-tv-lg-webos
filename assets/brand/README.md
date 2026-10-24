# Clean Your TV — B1 identity

Approved direction: B1, an asymmetric house with a flowing orange roof.
The project lockup reads **clean your tv / FOR LG webOS**.

## Masters

- `logo-light.svg`, `logo-dark.svg`: horizontal signature, including compatibility subtitle.
- `logo-stacked-light.svg`, `logo-stacked-dark.svg`: vertically arranged signature.
- `symbol-color.svg`, `symbol-reversed.svg`: standalone house for light/dark backgrounds.
- `symbol-black.svg`, `symbol-white.svg`: true single-colour house marks.
- `wordmark.svg`: custom lettering only, converted from the approved study into smoothed vector contours.
- `readme-logo.png`: Markdown-compatible README header on a white background.
- `brand-overview.svg`, `brand-overview.png`: identity and application-family preview.

SVG masters contain vector paths, no raster images, filters, external fonts or live text.
The subtitle and Root R were outlined from Outfit (SIL OFL; see `../../launcher/fonts/OFL.txt`).
The principal lettering preserves the custom forms from the approved generated study.

## Palette

| Role | HEX | RGB |
| --- | --- | --- |
| Warm dark brown | #241D19 | 36, 29, 25 |
| Orange roof/accent | #FF4C20 | 255, 76, 32 |
| Cream | #FFF8EB | 255, 248, 235 |

Use cream/brown for text; orange is an identifying accent rather than small body text.
The `FOR LG webOS` line describes compatibility; no LG corporate symbol is used.

## Usage

Keep at least 24 units of clear space around the 256-unit symbol. Do not stretch,
rotate, outline, add effects, or independently rearrange parts of the signature.
Use the provided reversed variant on dark backgrounds. Use the symbol alone below
360 px horizontal signature width; keep standalone symbols at least 16 px.
The 80/130 px TV tiles use their own generous internal padding.
README embeds `readme-logo.png` with standard Markdown image syntax so viewers
that disable raw HTML still display the logo. Its white background blends into the light README page.

Root tiles add a small orange R badge; ordinary Home/Updater tiles do not.
Helper is the directional pad with orange centre; Updater is the paired rotating arrow.
Installer uses the project Home symbol. See `../icons/README.md` for package mappings.

## Validation

Inspected the signature on cream and dark brown and the house at 16/32/80/130 px.
Inspected the complete application family and smaller menu previews.
SVG audits identify expected complexity in custom lettering and tiny subtitle
components: the full signature is for headers, while the standalone symbol is the
small-size artwork. This is a visual reference check, not trademark clearance.
