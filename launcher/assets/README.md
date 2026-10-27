# Home appearance photo assets

The optional No-root tvOS appearance uses a user-supplied photograph. The
repository contains its full-size runtime crop, a preblurred source retained for
the dock texture build script, and a small derivative for the grid backdrop.

| File | Dimensions | Bytes | Provenance |
| --- | --- | --- | --- |
| `cinema-backdrop.jpg` | 1920×1080 | 596521 | User-supplied photograph, cropped and resized for the shelf |
| `cinema-backdrop-soft.jpg` | 1920×1080 | 128475 | Preblurred user-supplied photograph, retained as a dock texture build source; not packaged |
| `cinema-backdrop-shelf.jpg` | 480×270 | 36765 | Shelf thumbnail resized from the preblurred photo; packaged for the grid |
| `profile-avatar.jpg` | 96×96 | 6594 | Local thumbnail resized from the unchanged user-supplied portrait |

The user-supplied photographs are not covered by the repository MIT license, and
no redistribution license is asserted. Keep the originals in the repository for
local provenance and texture regeneration; the public launcher payload includes
only the derivatives it uses. No names or identifying details are documented.

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

The unchanged user-supplied portrait is retained as `profile.jpg`; the launcher
uses its 96×96 derivative, `profile-avatar.jpg`. Neither is covered by the
repository MIT license; no redistribution license is asserted. The original is
not included in the public launcher payload.

Now Playing reuses the existing `dock-glass-home.jpg` texture with the dock-style
fill, radius and shadow. Reduce effects uses an opaque fallback. This reuses a
local static texture without adding a live blur filter or network request.
Hardware performance and HA acceptance remain outstanding.
