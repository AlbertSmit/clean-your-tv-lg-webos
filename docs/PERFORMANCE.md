# Launcher performance

This page documents the performance work landed to make the tvOS-style Home
launcher feel snappy on real webOS hardware. webOS renders web apps with a
WebKit engine (Chrome 38-era baseline) that is often single-core with limited
GPU-accelerated filters, so the biggest wins come from removing expensive
compositing and layout work rather than micro-optimizing loops.

## What was slow

| Hot spot | Cost |
|----------|------|
| SVG `feDisplacementMap` + `feGaussianBlur` filter on the dock | ~15 ms+ of paint per frame — ran on every frame the dock was visible |
| Canvas color extraction (`drawImage` + `getImageData`) for every tile icon on launch | 20–30 GPU→CPU readbacks, blocking the main thread for 50–100 ms |
| `rebuild()` on add / hide / undo | Destroyed and recreated all 20–30 tile DOM nodes + event listeners + images |
| Tile positioning via `left`/`top` | Changing these invalidates layout on every focus change, scroll and reorder |
| `getBoundingClientRect()` on every Up-arrow keypress | Forced a synchronous layout per key |
| Clock interval running while the launcher was hidden | Unnecessary periodic wakeups |

## What changed

### 1. Dock glass: SVG filter → static backdrop texture

`launcher/ui/dock-glass.js` previously built an SVG `filter` with
`feImage` + `feDisplacementMap` + `feGaussianBlur` over a 1872×278 region.
That filter is extremely expensive on webOS and re-rasterized per frame.

Now the dock uses the pre-rendered `dock-home.jpg` / `dock-grid.jpg`
textures, swapped via `background-image`. `createDockGlass()` only toggles
the active texture and the `data-glass` attribute. The `reduced-effects`
preference still disables the effect entirely.

### 2. Icon colors: baked-in + cached, computed once

Color resolution is now cheapest-first:

1. `dominantColor` baked into `launcher/apps.js` at build time by
   `scripts/compute-icon-colors.py` (static/packaged apps).
2. A `localStorage` cache keyed by app id (`tvhome.color.<id>`) so colors
   persist across launches without re-analyzing the image.
3. A one-time canvas computation (the original algorithm) that is then
   cached — so each app's color is computed at most once ever.

This removes the 20–30 canvas readbacks that used to stall every launch.

### 3. Incremental tile insertion

`rebuild()` still handles initial render, preference changes and the
guarded inventory refresh. But the frequent interactions — add from the
picker and hide/undo — now go through `insertTileAt()`, which creates
exactly one tile and re-lays-out without touching the rest of the DOM.
`hideApp()` already removed a single node; undo now re-inserts a single
node instead of rebuilding everything.

### 4. Compositor-only positioning

Tiles, the stage and the focus glass now move with `transform:
translate3d(...)` instead of `left`/`top`. This keeps every navigation,
scroll and reorder on the compositor thread and never invalidates layout.
Entrance is a pure opacity fade. `will-change: transform, opacity` promotes
tiles to their own layers.

### 5. Removed forced layouts

- Top-button geometry for Up-arrow navigation is measured once and cached,
  invalidated only when tile layout changes (`topButtonRects`).
- The `#glass` and stage transforms are set via `translate3d`.

### 6. Idle hygiene

- The 1 s clock interval is suspended while the document is hidden and
  refreshed immediately on return.
- Dead `hsvToRgb` path removed; `tileBackground` kept for fallback.

## How to verify

- **Chrome DevTools → Performance**: record remote navigation — long tasks
  should be gone; `Paint` for the dock is a single draw, not a filter pass.
- **DevTools → Rendering → Layout Shift Regions**: no layout shifts while
  moving focus with the keyboard.
- **DevTools → Layers**: tiles are on their own compositor layers.
- **DevTools → Performance (Memory)**: no detached DOM growth across
  multiple add/hide/undo cycles.
- **Network**: launch loads icon images only as their tiles become relevant
  (no change here yet), and the dock textures load once.

## Files touched

- `launcher/ui/dock-glass.js` — SVG filter removed.
- `launcher/appearance.css`, `launcher/style.css` — texture/transition/`will-change` updates.
- `launcher/app.js` — color resolution, incremental insert, `translate3d` positioning, cached geometry, clock pause.
- `launcher/apps.js` (generated) — `dominantColor` fields.
- `scripts/compute-icon-colors.py` — new build-time color tool.
- `tests/home-appearance.cjs` — assertions updated for `transform` positioning.

## Known trade-offs

- Dock glass is now a static texture, not a live refraction effect. The
  visual result is close, and a CSS gradient overlay keeps the translucent
  look, but the dynamic displacement effect is gone by design.
- `font-display` was considered for the bundled fonts but is unsupported by
  the Chrome 38 baseline, so it was not shipped (the compat lint enforces
  this).
