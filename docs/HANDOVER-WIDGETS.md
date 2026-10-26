# Handover — Widgets POC/MVP (tvOS home screen)

A working proof-of-concept for **tvOS-style home-screen widgets** on the LG webOS
launcher: **Clock**, **Weather**, and **Now Playing**, laid out on the dock's six-column grid, with a protected upper-left logo area. This document hands it to a
clean-up pass so it can be evolved safely.

## 1. Context and goal

- The launcher (`launcher/`) is a web app built for a **Chrome 38-era webview**
  (see `.browserslistrc`; `scripts/compile-tv-web.cjs` enforces ES5
  JS and Chrome-38-supported CSS via `doiuse`).
- Widgets only appear in the **tvOS appearance** (`appearance === 'tvos'`),
  hidden in `existing`. A separate master Widgets switch defaults on, persists
  as `cytv-widgets-visible`, and disconnects HA live updates when off without changing
  individual widget configuration.
- Data comes from **Home Assistant (HA)** over its WebSocket API with a long-lived
  token. In the browser preview, a fake `window.WidgetPreview` provider stands in.
- Widgets are deliberately **non-interactive, decorative, pointer-events:none**
  so they never interfere with the remote-focus grid.

## 2. What exists today

### New files
| File | Role |
| --- | --- |
| `launcher/ui/widgets.jsx` | Widget renderers + structured grid + `mountWidgetSettings` (Home settings section). Bundled into `home-ui.js`. |
| `launcher/widget-data.js` | ES5 classic script. Config store + ES5 HA WebSocket watch, one-shot REST helper + preview fallback. Exposes `window.WidgetData`. |
| `docs/WIDGETS.md` | User-facing setup/caveats doc. |
| `preview/glass-letters.html` | Standalone experiment page for the "glass letters" layered-SVG technique (live sliders). Not part of the TV package. |

### Modified files
| File | Change |
| --- | --- |
| `launcher/ui/index.jsx` | Export `createWidgets` / `mountWidgetSettings`. |
| `launcher/app.js` | Create widgets at boot; own the active `WidgetData.watch()` lifecycle on visibility, appearance, master and configuration changes. |
| `launcher/appearance.css` | Widget grid/panel styles + user-supplied **SF Pro Display/Text** faces and Inter/Noto fallbacks. |
| `launcher/index.html` | Load `widget-data.js`. |
| `launcher/renewal-panel.js` | Mount widget settings into `#themeSection`. |
| `preview/bridge.js` | `window.WidgetPreview` fake provider. |
| `scripts/preview.py` | Added `widget-data.js` to `LAUNCHER_FILES` allowlist (also fixes GitHub Pages export). |

Note: **no native/Luna service changes** — the HA bridge is entirely web-side, so
it works identically on No-root and Root editions.

## 3. Data flow

```
preview → window.WidgetPreview (fake)
   OR
HA /api/websocket → WidgetData.watch(callback)
                   auth_required → auth → auth_ok
                   subscribe_events(state_changed) → get_states
                   initial snapshot + incremental state updates
                                   │
                                   ▼
                          widgets.update(snapshot)
```

- `WidgetData.watch()` returns a disposer. The launcher owns the active watch
  while the master switch is on in a visible tvOS document. It disposes the
  socket when the master is off, the document hides or Existing is selected;
  resume/configuration changes start a fresh watch as needed.
- Transient failures reconnect with exponential delays from 1 to 30 seconds.
  `auth_invalid` stops automatic retries until the connection is restarted or
  configuration is saved. No token or server diagnostics belong in public logs.
- Authentication follows HA's `auth_required` / token `auth` / `auth_ok` flow,
  then subscribes to `state_changed` before loading `get_states`. Events received
  during the initial snapshot are queued and applied; later events update the
  local state map incrementally. See [HA WebSocket API](https://developers.home-assistant.io/docs/api/websocket/).
- `WidgetData.refresh()` retains its one-shot `GET /api/states` REST helper for
  callers that need it; it is not recurring launcher polling.
- Artwork remains an authorized same-origin XHR converted to a data URL;
  external artwork URLs are ignored.
- Blank media entity scans all `media_player.*` entities for `playing`,
  `media_content_type: music` and a nonempty title. A pinned entity restricts
  selection to that player. Missing, paused, stopped or unreachable music hides
  Now Playing. Weather starts disabled on new installations; a saved explicit
  enabled choice is respected, and enabled Weather keeps missing-data placeholders.
- Apple Home is not a direct browser data source. Use HA media-player entities;
  see the official [Apple TV integration](https://www.home-assistant.io/integrations/apple_tv/).
  Verify HomePod entity metadata on the actual HA setup before claiming support;
  a registered device page alone does not prove playing/music/title metadata.
  Enter the HA server base URL without dashboard/configuration suffixes,
  not the HomePod address, plus a Profile → Security long-lived token in
  Home settings → Widgets. See [widget setup](WIDGETS.md).

## 4. Structural design (what to preserve)

- `widgetLayoutFor()` in `launcher/ui/layouts.js` derives named regions from
  `layoutFor('tvos')`: six dock tracks, 298px pitch and 250px cards at 1920×1080.
  Chrome 38-compatible positioned regions implement the grid; CSS Grid is not used.
- Logo exclusion: upper-left two tracks through y420 remain empty. The actual
  SVG stays at x88/y62; no widget or decorative outline enters this region.
- Clock: x90/y468, 250×250 green analog face, oversized cardinal numerals,
  live white hands and a short localized date. SVG hand references must come
  from the mounted SVG: Nano JSX recreates SVG children during rendering.
- Weather: x984/y170, 250×250 blue face. Now Playing: x1282/y170,
  548×274 compact 2:1 artwork-led card. Artwork is 212×212 at local x24/y31;
  bottom-aligned copy begins at x254: localized Now Playing label (13px), title
  (24px) and artist (22px), without album text. A 30px music glyph sits top right.
  Music ends at y444; the clock ends at y718, above the dock at y784.
  Unassigned cells stay clear.
- The whole widget layer remains decorative (`aria-hidden`, no focus targets,
  `pointer-events: none`) and hides during app browsing, Home controls and editing.
  Music has no transport controls or fabricated seek/progress data.
- Missing music hides Now Playing without shifting other regions; Weather
  retains its placeholders. Disabled widgets hide independently.
  The clock timer pauses when the appearance or document is hidden.
- Now Playing reuses `dock-glass-home.jpg` with the dock-style fill, radius and
  shadow plus a taupe tint and refraction overlay. Reduce effects uses an opaque fallback.
- The browser preview includes original inline sample cover artwork; production
  artwork continues to come from the authorized HA bridge.

The header master control is `#btnWidgets`, a switch labelled “Widgets”. It is
reachable by pointer or from the dock with Up (Settings) → Right (Widgets) → OK.
Toggling returns focus to the dock; the card layer itself stays outside navigation.

## 5. Constraints that must not be broken

1. **Chrome 38 webview**: no `backdrop-filter`, no `gap` in flex, ES5 output,
   CSS must pass `doiuse` (validate with `npm run lint:compat` and
   `npm run build:home`).
2. **Remote focus/navigation untouched**: widgets must remain non-interactive
   (`pointer-events: none`) and outside the focus grid.
3. **Edition-agnostic**: keep the bridge web-side; don't couple to native helper
   services.
4. **Preview parity**: the fake provider (`WidgetPreview`) must keep working so
   the feature is testable without HA.
5. **Classic scripts vs UI modules**: `widget-data.js` is an ES5 classic script
   (loads before the dynamic `app.js`); `ui/*.jsx` are bundled by esbuild →
   Babel. Keep this split.

## 6. Known debt / rough edges (clean-up targets)

Prioritized:

1. **Duplicate config model** — `readConfig`/`saveConfig` are implemented
   separately in `widgets.jsx` and `widget-data.js` (both touch
   `localStorage['cytv-widgets']`). Centralize (single source of truth in
   `widget-data.js`, expose getters/setters) to avoid drift.
2. **Unused `dataSource` param** — `createWidgets(dataSource)` receives
   `WidgetData` but never uses it; wiring is implicit via `window.WidgetData`
   global + pub/sub. Consider an explicit controller/DI if it aids testability,
   without over-engineering.
3. **Widget regression** — `tests/widgets.cjs` now covers the compiled launcher,
   logo exclusion, dock alignment, data/empty/disabled states and remote navigation.
   Run `npm run test:widgets`; current-browser checks do not replace TV acceptance.
4. **Fixed TV composition** — the six-column widget geometry is now centralized
   in `layouts.js` and derives from dock metrics. Alternative screen compositions
   remain follow-up work.
5. **i18n gaps** — widget UI copy (weather labels, settings
   labels, WX_LABELS) is mostly English; add keys to `catalogs.js`/i18n flow to
   match repo conventions.
6. **Unassigned cells** — outlines were removed for the HomeView composition.
   A developer grid overlay is only a verification artifact, not a user setting.
7. **User-supplied typography and portrait** — seven SF Pro Display/Text font
   files and `assets/profile.jpg` are present for the local candidate. Inter and
   Noto remain fallbacks. Their presence does not establish redistribution rights;
   they are not covered by the repository MIT license. See `THIRD_PARTY_NOTICES.md`.
8. **Clock rendering** — live SVG hand transforms replace the old rebuilt digital
   glass lettering; the old SVG sequence counter has been removed.
9. **Settings text inputs are pointer-only** — remote arrow-focus cycles toggle
    buttons, not the `<input>`s. Acceptable for MVP; a custom on-screen keyboard
    is a separate follow-up if full remote editing is required.
10. **HA path unverified on real hardware** — the WebSocket + artwork XHR/CORS/TLS behavior on
    an actual TV webview hasn't been tested with a real HA instance. Keep the
    graceful fallback (Weather placeholders and hidden Now Playing when unreachable).

## 7. Recommended remaining clean-up

1. Keep `npm run test:widgets`, `npm run test:home-ui`, `npm run test:legacy-ui`
   and `npm run lint:compat` passing as the composition evolves.
2. Consolidate the duplicate config model in `widget-data.js` and `widgets.jsx`.
3. Remove the unused `dataSource` parameter if explicit dependency injection is
   not needed; avoid adding a controller abstraction solely for this cleanup.
4. Add widget copy to the existing i18n catalogs.
5. Update `docs/WIDGETS.md` if setup or behavior changes.
6. Leave font/portrait redistribution review, a slot-assignment UI and hardware/HA validation as
   separate follow-ups requiring external inputs or product decisions.

## 8. Verification commands

```sh
npm run build:home          # compiles launcher (validates CSS vs Chrome 38)
npm run lint:compat         # TV web compatibility check
npm run test:home-ui        # appearance/tvOS behavior
npm run test:widgets        # logo clearance, alignment and widget states
npm run test:legacy-ui      # classic launcher behavior
python3 scripts/preview.py --open   # interactive preview (widgets in tvOS)
```

Manual sanity: open preview → Settings pill → tvOS → widget grid appears with
clock + weather + now playing; the logo stays clear, the analog clock sits below it, and weather/music align
with dock columns. No reserved outlines are displayed. Verify the compact music
card has no transport controls. Toggle the header Widgets switch by pointer and
Up → Right → OK; all cards hide, the live connection closes, focus returns to the dock, and the
choice survives restart without altering individual enabled settings.

## 9. Open questions / blocked items

- **Asset rights**: the local user-supplied SF Pro fonts and portrait have no
  redistribution grant recorded here. No publication is part of this change.
- **Visual sign-off**: the new HomeView-inspired composition has browser-rendered
  previews and still needs maintainer visual acceptance.
- **Grid shape**: current six-column dock-aligned composition is fixed; further
  arrangements must preserve the protected logo zone.
- **Slot assignment UI**: user has not committed to making slots user-adjustable;
  region assignments are centralized in `widgetLayoutFor()`.
- **Clock styling**: the analog SVG updates hand transforms every ten seconds;
  alternate faces are a separate design decision.
- **Hardware/HA validation**: needs a real TV + HA instance.

## 10. Where to look next for style/patterns

- `launcher/ui/appearance-panel.jsx` — settings section pattern.
- `launcher/renewal-panel.js` — how settings sections are mounted into
  `#themeSection` (widgets mount alongside appearance/theme).
- `launcher/ui/layouts.js` — shared dock metrics and named widget regions.
- `tests/home-appearance.cjs` — Playwright harness pattern for new widget tests.
- `scripts/bundle-home-ui.cjs` / `scripts/tv_web_build.py` — build pipeline; new
  `ui/*` modules are picked up automatically; new classic scripts must be added
  to `LAUNCHER_FILES` in `scripts/preview.py`.
