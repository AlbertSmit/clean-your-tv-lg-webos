# TV web compatibility build

The web frontend targets **Chromium 38**, the engine documented for webOS 3.x.
The same compiled assets run on later Chromium-based webOS engines. This is a
frontend build target, not a claim that Home Helper, input devices or firmware
services work on every TV. webOS 1.x/2.x WebKit engines are outside this target.

Source builds require Node.js **20.19+** (Node 22 is used in CI) and npm:

```sh
npm ci --ignore-scripts --no-audit --no-fund
npm run lint
npm run lint:compat
npm run test:compat
```

All production TV web packages pass through `scripts/tv_web_build.py`:
No-root Home, Root Home, Home Updater and Root Updater. Desktop and Android
installers embed these compiled packages. Native executables, TV Node services
and Python code retain their own runtimes. Helper JavaScript has a separate
Node-targeted build described below; other TV Node services are not transformed.
The installed cytv apps do not require Node/npm on the user's computer.

## Processing and validation

- The root `.browserslistrc` defines `Chrome 38` for ESLint, Babel, PostCSS and
  doiuse. `npm run lint` runs ESLint's browser API compatibility rule on TV web
  JavaScript and JSX in `launcher/`, `root-edition/ui/` and `updater-app/`.
  Conditional feature checks do not suppress unsupported API errors
  (`ignoreConditionalChecks: true`); use a compatible implementation instead.
  Node services, build/test tooling and desktop preview code have separate
  runtimes and are excluded. Browser APIs in inline HTML scripts are not checked
  by ESLint; those scripts still pass the build's syntax gate.
- Babel preset-env transforms modern JavaScript syntax into ES5. Acorn checks
  every emitted script against ES5, including scripts embedded in HTML.
- A bundled core-js runtime loads before application scripts and supplies missing
  ECMAScript built-ins. It is packaged locally, with licenses, without a CDN.
  It does not supply platform-specific Luna APIs or every modern browser API.
  ESLint's optional ECMAScript built-in checks remain off because the bundled
  core-js runtime supplies those APIs; browser API checks remain enabled.
- PostCSS preset-env/Autoprefixer target the same Browserslist entry in
  `.browserslistrc`. For example, `inset` becomes physical offsets and alpha hex
  colors become compatible color notation. CSS files, `<style>` elements and
  `style` attributes all pass through this step.
- doiuse checks the **transformed** CSS. Unsupported features left after PostCSS,
  including CSS Grid and flexbox gap, fail the build. Use compatible layouts and
  margins for those cases; do not globally disable the checks. An extra value
  check rejects `overflow-wrap: anywhere`, which doiuse misses.

There are two narrow, documented allowances: original `overflow` values
(`visible`, `hidden`, `auto`, `scroll`) are accepted despite doiuse's broad
partial-support warning; an optional `prefers-reduced-motion` override has a
scoped source comment because older engines safely ignore that media query.
Newer overflow values are still rejected. The linter uses compatibility data;
it is not an exhaustive proof of browser behavior.

Use these boundaries when choosing features:

| Feature | TV build policy |
| --- | --- |
| Modern syntax and JSX in Home UI modules | Author in source; Babel emits ES5 and Acorn verifies it. |
| ECMAScript built-ins such as `Object.assign`, `Array.from` and `Promise` | Supplied by the packaged core-js bundle. |
| Browser APIs such as `fetch` and `AbortController` | Unsupported in Chrome 38; ESLint rejects them. Use XHR for requests. |
| CSS custom properties and `inset` | Allowed in source when PostCSS converts them successfully. |
| CSS Grid, flexbox `gap`, `backdrop-filter` | Unsupported; use compatible layouts, margins and static effects. |

Run `npm run lint:compat` to check both browser APIs and the transformed assets.
API detection is static and cannot reliably cover aliases, computed property
access or dependency internals. CORS, TLS, firmware APIs and performance still
need device testing. See the [compatibility rule documentation](https://github.com/amilajack/eslint-plugin-compat)
for the ESLint check's configuration and scope.

Legacy scripts remain separate classic scripts so their existing globals and UMD
wrappers keep their behavior. Compatible ES5 sources keep their original bytes.
The Home presentation has one additional bundle step, described below. Build
products are staged separately; the compiler never overwrites a developer's app
configuration, inventory or icons in the source tree.

## Home presentation modules

The candidate Home UI uses small modules under `launcher/ui/`, with
`launcher/ui/index.jsx` as their entry point. Nano JSX **0.2.1** provides
lightweight declarative markup; esbuild **0.28.2** bundles these modules into
`home-ui.js` before the existing Babel ES5 conversion and Acorn gate. JSX is a
source-authoring choice; it does not change the Chromium 38 target. Legacy
inventory, input and modal scripts continue to own their existing behavior.
Do not introduce a second renderer for the app grid or duplicate input handlers.

After installing dependencies, work through the preview or compiled output:

```sh
npm run dev
# Opens the preview on http://127.0.0.1:8765/
npm run build:home
# Compiles launcher/ into build/home-app/
```

These scripts invoke `python3 scripts/preview.py --open --port 8765` and
`python3 scripts/tv_web_build.py --input launcher --output build/home-app`,
respectively. Opening the raw `launcher/index.html` directly is unsupported:
the generated `home-ui.js` exists in the compiled output. Edit source modules,
then reload the preview to rebuild. Do not edit the generated bundle.
Nano JSX core and its MIT notice are included locally in `home-ui.js` and
`home-ui-LICENSE.txt`; the TV does not download a framework from a CDN.

The optional No-root tvOS appearance defaults off. `cytv-appearance` selects `existing`
or `tvos`, while `cytv-reduced-effects` stores its boolean effects preference.
Both are device-local cosmetic settings, separate from the five `cytv-theme`
palettes and excluded from the strict profile backup envelope. Ordinary
restarts retain them; reinstall and profile transfer need not. The full-bleed
static backdrop uses a user-supplied photograph, with a local preblurred
copy for the dock and a small thumbnail for the grid. There is no dynamic
streaming integration or live blur filter. Asset provenance is recorded in
[`launcher/assets/README.md`](../launcher/assets/README.md).

The idle header shows a compact clock and an avatar-shaped Settings button at
the top right. Clicking the button or pressing Up from the top app row reveals
the existing Inputs, network and Settings actions; Back or Down returns to the
grid. Down scrolls the grid with a muted backdrop, and mouse-wheel navigation is
supported. All five Existing themes remain available.

The tvOS header also exposes a Widgets switch (`#btnWidgets`, role `switch`).
From the dock, Up selects Settings, Right selects Widgets and OK toggles it,
then returns focus to the dock; the pointer can toggle it too. The separate
`cytv-widgets-visible` preference defaults to true and persists across restarts.
Turning it off disconnects widget HA live updates without rewriting individual widget
settings. It does not change the Existing appearance. Now Playing uses a compact
548×274 card aligned to the six-column dock: 212px artwork at x24/y31,
bottom-aligned copy at x254 (localized Now Playing label 13px, title 24px,
artist 22px; no album), a 30px upper-corner glyph and no transport controls.
Its dock-glass texture has a taupe tint and refraction overlay. Weather defaults
to off for new installations; a saved explicit enabled choice remains respected.
The ES5 data watcher uses native WebSocket `/api/websocket`, authenticates with
the HA token, subscribes to `state_changed`, loads `get_states` and applies later
updates incrementally. The watch is disposed while the master is off, the
document is hidden or Existing is selected. Transient failures retry with 1–30s
exponential backoff; invalid authentication stops automatic retries until a new
watch/configuration. One-shot REST `refresh()` remains a helper, not the normal
launcher update loop. Artwork still uses authorized same-origin XHR.
HA connection steps and metadata requirements are in [Widgets](WIDGETS.md).

The local candidate includes user-supplied SF Pro Display (400/500/600/700) and
SF Pro Text (300/400/600), with Inter Display and Noto fallbacks. The seven font
files retain their supplied names under `launcher/fonts/`; obsolete optional
`SFProDisplay-*.woff2` references are removed. Inter Display 4.1 remains covered
by its retained SIL Open Font License. The supplied SF fonts and photographs
are user-supplied assets; the repository MIT license does not cover them, and
no redistribution license is asserted. See
[third-party notices](../THIRD_PARTY_NOTICES.md).
Browser/build verification does not establish performance or visual fidelity on
LG 50UP77006LB; physical-TV acceptance remains pending.

The initial HTML shows the existing localized Home heading in a plain system font
while language and profile checks complete. Settings and the legacy No-root
updater build their markup on first open; updater RPC entry points and early
Helper/Root exit handling remain separate classic scripts. Recovery and direct
Helper entry dismiss the startup surface independently of optional timing metrics.
The local clock renders immediately. Initial installed-app and connection requests,
and each widget watch start, wait for two animation frames followed by a timer
(with timer-only fallbacks). Changed preferences/configuration or visibility
invalidate pending widget work before it starts. Existing appearance skips unused
widget markup until tvOS is selected. New tvOS tiles enter together for 160ms;
the selected tile is visible immediately and inventory refresh reuses tile nodes.
The `widgetsCreated` milestone is therefore absent during Existing startup.
Initial `inventoryRefreshStart` now follows the first rendering proxy opportunity.
These scheduling checks provide rendering/input opportunities, not measured speed
gains. Cold boot, standby return, first remote input, direct Helper entry and
recovery still require physical-TV acceptance on LG 50UP77006LB.

## Regression checks

`npm run test:compat` verifies the ESLint configuration (including rejected browser
APIs, allowed polyfilled built-ins and source scope), syntax conversion, missing built-ins, polyfill
ordering, inline assets, rejected unsupported CSS and repeatable HTML injection.
`npm run lint:compat` runs ESLint before compiling and checking the TV web assets.
`scripts/test.sh` runs the regression and compatibility linter. CI also runs the browser
regression on the compiled Home frontend:

```sh
python3 scripts/tv_web_build.py --input launcher --output build/legacy-ui
npx playwright install chromium
BROWSER_CHANNEL=chromium TV_WEB_DIR=build/legacy-ui npm run test:legacy-ui
BROWSER_CHANNEL=chromium TV_WEB_DIR=build/legacy-ui npm run test:startup-ui
```

The browser test disables `inset` and selected JS APIs to reproduce issue #20.
It checks actual card hit-testing, dimensions, icon fallback, scrolling,
launch/navigation and full-screen dialogs. This models the reported engine
limitations in a current browser; it is not an emulator of an entire old TV.
Hardware confirmation is still required on the original webOS 3.5 device.
`test:startup-ui` holds profile replies and frame callbacks to verify the startup
surface, deferred services, stale widget work, lazy panel mounts, recovery before
status replies, script-load failure and direct Helper input isolation.

## Helper Node compatibility

`scripts/helper_build.py` and `scripts/compile-helper.cjs` target **Node 0.12**
independently of Browserslist. Both `build-cytv.py` and `build.sh` compile the
Helper app and its status/inventory service, including vendored JS. Every
emitted `.js` file passes an ES5 parse check. Babel always runs, including on
sources that parse as ES5: strict block function declarations still fail in
Node 0.12 without transformation. Each top-level module loads local
core-js and safe-buffer before importing application dependencies. The original
Buffer constructor is preserved; only missing safe Buffer methods are added.
A Node 0.x shim also forwards callback arguments through `process.nextTick`.

`websocket.js` selects ws 6.2.4 below Node 10 and ws 8.21.0 on newer TV Node.
The legacy tree includes async-limiter and the pure JS UTF-8 validator from
ws 7.5.11; see its retained source notes. SSAP clients disable compression and
keep their handshake/payload limits. TV-provided webos-service remains external.
Published historical Helper baselines retain their original bytes.

Run `node tests/helper-compat.cjs` with current Node, or set `NODE012` to a
Node 0.12.2 executable. The regression compiles the actual Helper sources,
exercises controller startup/error handling with TV hardware/Luna substitutes,
and service status/listApps, and performs a real local WSS register/subscribe,
fragmented text, ping/pong and close exchange. Invalid UTF-8 and oversized
payloads must be rejected. CI downloads a SHA-256-pinned official Linux x64
Node 0.12.2 archive. Packaged service tests also use that runtime when available.
This verifies Node compatibility, not access to a TV's evdev devices.

References: [LG engine versions](https://webostv.developer.lge.com/develop/specifications/web-api-and-web-engine),
[Babel preset-env](https://babeljs.io/docs/babel-preset-env),
[PostCSS preset-env](https://preset-env.cssdb.org/),
[doiuse](https://github.com/anandthakker/doiuse).
