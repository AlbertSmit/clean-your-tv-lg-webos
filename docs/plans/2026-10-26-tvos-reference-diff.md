# tvOS 27 reference audit and prototype diff

This audit pins the visual references for the fidelity pass requested by the
maintainer on 2026-10-26. The initial measurements below describe the earlier
prototype; the implemented refinement and current measurements follow them.

## References

Both of these source guides currently identify tvOS 27. Neither establishes an
exact OS patch/build or the date the illustration was captured.

| State | Official page | Raw image | Native size | SHA-256 |
| --- | --- | --- | --- | --- |
| Top Shelf / first-row focus | [Open an app](https://support.apple.com/en-gb/guide/tv/atvb87e1c725/tvos) | [PNG](https://help.apple.com/assets/6A0B92AC55AFD81B2E01CA2A/6A0B92B055AFD81B2E01CA30/en_GB/99d30260802e5e08cd6ff2c8000468a5.png) | 1146 × 644 | `130c33a9c27fdd2cea2ee625ee8b60fdcd6d89a47f945bbcce9acb392a61e44d` |
| Scrolled grid / folder focus | [Appearance settings](https://support.apple.com/en-sg/guide/tv/atvb46af4f11/tvos) | [PNG](https://help.apple.com/assets/6A0B92AC55AFD81B2E01CA2A/6A0B92B055AFD81B2E01CA30/en_GB/e306ffaeeee92bf6ad18e57a6ed72940.png) | 1146 × 644 | `f2ee730a2e97e11b933957cfe362d5b95f7d041817a22091d49ebe0dc4e6c3b4` |

The welcome-page screenshot includes a TV frame and stand; do not use it as a
flat-screen pixel baseline. The paired focus illustration in the app-opening
guide is a cropped callout, not a second full-screen state.

Reference images are retained under ignored `build/reference/` for local analysis,
not bundled in the launcher. Current screenshots use only public demo apps.

## Initial prototype differences

Approximate measurements from the Top Shelf reference, mapped to 1920 × 1080.
Allow approximately ±4 px; these are image observations, not recovered Apple
implementation constants. The prototype values come from its rendered DOM.

| Element | Apple reference | Current prototype |
| --- | --- | --- |
| Unfocused tile | ~250 × 151 | 252 × 142 |
| First base tile position | ~91, 823 | 134, 588 |
| Horizontal pitch | ~297 | 280 |
| Focused tile | ~302 × 183, about 1.21× | 277 × 156, 1.10× |
| Dock bounds | ~40, 785, 1823 × 230 | Hidden |
| Next row top | ~1053 | 828 |
| Shelf | Full-bleed artwork behind the dock | Inset panel at 134,142, 1652 × 370 |
| Status | Small time/avatar pill at top right | Clock left; three large action pills right |
| First-row labels | Hidden in this state | Focused app label visible |

The scrolled reference also shows the dock moving near the top, with the grid
below it and a muted background. The prototype currently retains its initial
grid origin until its generic scroll bounds require movement. That is a separate
state mismatch; matching only the initial row coordinates is insufficient.

## Fidelity pass scope

1. Make the shelf a full-bleed background treatment. Preserve an inexpensive,
   local fallback for apps without suitable artwork.
2. Correct tile height, horizontal pitch, margins, row origins and focused scale
   together in `ui/layouts.js` and scoped appearance CSS.
3. Restore the translucent dock with measured bounds and corner shape. Distinguish
   its top-row and scrolled positions.
4. Replace the visible header composition with a compact status control. Keep
   Settings, Inputs and networking accessible through a deliberate LG control
   surface, without retaining three large pills on the reference Home state.
5. Match label visibility, focus shadow/rim and the shelf expansion affordance.
   Implement actual shelf expansion before displaying an instruction for it.
6. Re-capture both states and compare geometry masks before adding refraction.

## Implemented refinement

The refined appearance uses an original static cinematic still, a translucent
dock with a preblurred image layer, low-opacity white-to-transparent icon sheen,
thin glass rims and a compact upper-right clock/control button. Pressing Down or
using the pointer wheel lifts the dock and reveals the grid over a softened still.
The larger header actions appear only when requested. All five previous palettes
and the Existing layout remain available through No-root Settings.

| Element | Apple image estimate | Current measured output |
| --- | --- | --- |
| Base tile | ~250 × 151 | 250 × 150 |
| First base tile position | ~91, 823 | 90, 822 |
| Horizontal pitch | ~297 | 298 |
| Focused tile | ~302 × 183 | 300 × 180 |
| Dock | ~40, 785, 1823 × 230 | 40, 784, 1824 × 230 |
| Status pill | ~1687, 50, 176 × 59 | 1688, 50, 176 × 60 |
| Second row, initial state | ~1053 | 1052 |
| Dock after Down | ~60 from top | 60 from top |

These geometry differences are within the approximate source-image measurement
boundary. They do not establish a whole-screen pixel match: original artwork,
series branding, installed app images and avatar differ. Glass uses static,
preblurred imagery rather than real-time refraction. The UI font is static Inter
Display 4.1 with its OFL; Apple's SF license does not permit embedding SF in this
webOS package. See [asset provenance](../../launcher/assets/README.md).

There is no misleading shelf-expansion instruction: Up from the dock reveals the
LG actions. Full-screen shelf expansion and native Apple gesture/motion parity
remain outside the implemented controls.

## Comparison method and limits

`node scripts/capture-home.cjs` captures the running demo preview on port 8765 at
1920 × 1080, saves settled Top Shelf and second-row screenshots, and records DOM
geometry in `build/reference/current-metrics.json`. It never contacts the TV.

The local comparison page `build/reference/index.html` provides side-by-side,
opacity overlay and raw difference views for both states. It compares in the
reference's native 1146 × 644 coordinate space; the prototype is downsampled.
The independently generated `side-by-side.png`, `overlay.png` and `difference.png`
reflect the refined appearance. `before-fidelity.png` preserves the earlier
comparison. The page links both so the structural improvement can be inspected.

Different artwork, inventories, clock values and font rasterization dominate a
raw whole-screen pixel difference. Do not present its percentage as a fidelity
score. A meaningful pixel-perfect fixture requires matching content and states;
use region masks for layout, dock, focus and status, and separately assess actual
LG app artwork. The screenshots cannot establish exact animation timing, remote
gesture behavior or optical glass effects. No official Home focus-motion capture
was established in this bounded source search.

The new appearance selector is currently in No-root Settings. Root shares the
rendering dependency but does not yet expose that selector; the shared-origin
browser demo can inherit the No-root preference. Installed editions have their
own app storage. Physical LG performance remains unverified.
