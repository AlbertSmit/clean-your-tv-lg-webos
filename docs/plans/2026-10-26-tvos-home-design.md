# Optional tvOS-style Home screen — implementation design

The subsequent [reference audit](2026-10-26-tvos-reference-diff.md) supersedes the
initial prototype geometry and shelf composition. This design now incorporates
the reference audit's geometry and a full-bleed cinematic composition. The modular
setup is implemented; pixel-perfect visual parity is outstanding.

Status: architecture accepted on 2026-10-26. Modular implementation is underway;
physical-TV acceptance and final visual fidelity remain unverified.

## Goal and reference

Add a Home screen appearance closely matching the latest officially documented
Apple TV Home Screen, while retaining the existing launcher and its five color
themes. The maintainer confirmed this reference on 2026-10-26. Apple's current
guide identifies tvOS 27. Match composition and focus treatment as closely as
the LG runtime, available app artwork and device performance permit.

Primary references, checked 2026-10-26:

- [Current Apple TV guide](https://support.apple.com/guide/tv/welcome/tvos)
- [Current Home Screen image](https://help.apple.com/assets/6A0B92AC55AFD81B2E01CA2A/6A0B92B055AFD81B2E01CA30/en_GB/e7c77afd81b6db94c8925dcae4996e7f.png)
- [Appearance settings](https://support.apple.com/en-sg/guide/tv/atvb46af4f11/tvos)
- [Top Shelf guidance](https://developer.apple.com/design/human-interface-guidelines/top-shelf)
- [Focus guidance](https://developer.apple.com/design/human-interface-guidelines/focus-and-selection/)

Apple documents six icons across by default, with five in Large mode. Measure
spacing, shelf height, corner shape, focus enlargement and label positions from
the selected image before implementing them. Do not infer exact timings or
refraction from still images. Some Apple guide deep links still identify tvOS 26;
record the version of each reference rather than assuming every linked image is 27.

No Apple binary, package or runtime was supplied. REA is unnecessary for source
analysis or reference-image reconstruction. If exact motion remains a requirement,
use a selected recording or authorized Apple runtime as a later evidence source.

## Accepted experience

- Settings gains `Home screen: Existing / tvOS-style`, separate from color theme.
- Existing remains the initial default. Switching back restores the selected
  Classic, Midnight, Pixel, Bloom or Amber palette and existing layout settings.
- The new appearance uses a six-column landscape app grid, a generous upper shelf,
  clear focused-card enlargement/elevation and focused app labels. Preserve the
  existing app order; a different column count changes row grouping only.
- Use a full-bleed static backdrop for the original fictional series **Sundown**.
  The dock/grid uses a local preblurred duplicate. No live blur filters or dynamic
  streaming recommendations are part of this implementation.
- The idle header contains a compact clock and an avatar-shaped Settings button
  at the top right. Clicking the button or pressing Up from the top app row
  reveals the existing Inputs, network and Settings actions. Back or Down returns
  to the grid. Down scrolls the first dock near the top and mutes the backdrop;
  mouse-wheel scrolling is also supported.
- Approximate glass with translucent fills, gradients and bounded shadows.
  Provide an explicit **Reduce effects** setting for older engines.
- Switching preserves the focused app by ID, settles editing/held-key state and
  recomputes geometry without duplicating grids or event handlers.

## Architecture and alternatives

Accepted: retain AppLibrary and the existing controller; extract a small layout
and presentation boundary. Each appearance supplies dimensions, row/column
positions, scroll bounds, focus bounds, shelf visibility and background treatment.
One controller continues to own inventory, launching, input, edit/hide/undo and
modal arbitration. Reuse tile nodes and cached icon colors.

Relevant seams are `launcher/app.js` geometry at lines 14–17 and 633–660, and
focus presentation at 698–738. Preserve `#tiles .item[data-app-id]`, which startup
health checks use. Add separately scoped appearance CSS and only the small modules
needed for the boundary. Use Nano JSX 0.2.1 for small declarative presentation
modules under `launcher/ui/`, bundled by esbuild 0.28.2 from `ui/index.jsx` into
`home-ui.js`. The existing Babel/core-js ES5 conversion and strict compatibility
gate remain mandatory after bundling. Legacy scripts retain their current globals.
A JSX runtime does not own inventory, navigation or modal state.

Alternatives considered:

| Approach | Benefit | Cost | Decision |
| --- | --- | --- | --- |
| Shared controller plus layout/presentation | Reuses working remote and app behavior | Small geometry refactor | Recommended |
| CSS-only extra theme | Small initial patch | Hardcoded JS geometry prevents a faithful layout | Insufficient |
| Nano JSX core for presentation modules | Declarative markup and small modules, compiled ahead of delivery | One bundling step and a constrained DOM ownership boundary | Accepted after maintainer requested easier modular development |

## Artwork and fonts

The cinematic backdrop is original generated artwork for the fictional series
**Sundown**, not Apple artwork or a streaming-service integration. The local image
and its preblurred derivative are documented with the generation prompt in
[`launcher/assets/README.md`](../../launcher/assets/README.md).

Apple's [font license, section 2B](https://developer.apple.com/fonts/) restricts
embedding SF fonts for this use, so SF is not bundled. Use static Inter Display
4.1 Regular, Medium and SemiBold from the [official Inter 4.1 archive](https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip),
with its retained SIL Open Font License at `launcher/fonts/Inter-OFL.txt`.
Exact Apple font metrics and artwork remain deviations; still-image evidence does
not establish Apple motion timing or optical effects. Physical-TV acceptance on
LG 50UP77006LB remains pending.

## State and recovery

Do not reuse `tvhome.layout`: it already stores app order/hiding. Use a validated,
separate `cytv-appearance` preference (`existing` / `tvos`) and boolean
`cytv-reduced-effects` preference, leaving `cytv-theme` intact. Apply appearance after
profile recovery and before the first grid render. Unknown preference values
fall back to Existing. Handle storage failure
without preventing launch or recovery.

Important existing limitation: `user-data.js` and `profile-bootstrap.js` only
allow/capture order, layout and language. The current theme is not backed up.
For the first iteration, keep cosmetic preferences device-local and outside the
strict legacy profile envelope; document that they survive ordinary restarts but
are not guaranteed through reinstall or profile transfer. Any later backup support
must cover both launcher/updater validators, system profile validation and older
rollback consumers. Do not add new keys to an envelope old validators reject.

Narrowly correct the Settings mount path that currently attaches duplicate hover
listeners when rebuilding its button list. Ensure layout switching closes or
settles active editing/picker/undo states and returns focus predictably.

## Performance and compatibility

Keep the production Chromium 38 baseline and ES5 output in `docs/TV-WEB-BUILD.md`.
Do not relax compatibility checks to introduce CSS Grid, flex gap or backdrop
filters. The target TV's actual firmware, engine and GPU headroom require device
inspection; model specifications alone do not establish performance.

Cache stable layout measurements and batch reads before writes. Remove avoidable
forced layout in focus changes. Bound icon sampling instead of creating a
full-resolution canvas solely for two pixels, preserving existing fallback colors.
Update only affected focus nodes, with finite transform/opacity transitions.
Avoid continuous parallax, video backgrounds, animated blur and global layer hints.

Proposed device acceptance targets, not measured guarantees: visual focus feedback
begins within 100 ms, no navigation stalls over 100 ms in the agreed test sequence,
animations follow the observed display cadence, and no retained DOM/listener growth
after 50 layout switches and Settings cycles. Compare the same app inventory and
device state against the current appearance before setting a final frame budget.

## Later enhancement: liquid glass experiment

The maintainer supplied [Liquid Glass with CSS and SVG](https://kube.io/blog/liquid-glass-css-svg/)
as a possible later enhancement. Its SVG displacement maps with
`backdrop-filter: url(#filter)` are outside the current compatibility baseline;
the author describes the technique as Chrome-only. Keep the initial translucent
fills, gradients and bounded shadows. A future opt-in experiment first needs the
actual LG app engine version, a feature and visual probe in that engine, and
physical-TV performance acceptance. A matching model number or a desktop Chrome
result alone does not establish support. This is not part of the present setup.

## Implementation sequence and subagents

1. Record existing screenshots, behavior and device performance. Preserve current
   uncommitted changes to theme-panel.js and preview.py in this single checkout.
2. Extract layout/presentation metrics while proving Existing behaves identically.
   Integrate this shared contract before parallel editing starts.
3. Build a static, reference-measured tvOS-style visual prototype in the preview.
   Review composition before adding further motion.
4. Work in parallel with explicit file ownership: one agent owns appearance CSS
   and presentation; one owns preference/bootstrap/Settings integration; one owns
   independent regression coverage and compatibility review. The primary agent
   integrates shared-controller changes. All agents use this checkout.
5. Add restrained focus motion, performance improvements and switching/recovery.
   Include new assets in preview allowlists and verify production packages.
6. Complete browser checks, full repository tests, affected localized guides and
   physical-TV acceptance. Implementation PRs target release/next; no release
   version or publication is part of the design phase.

## Verification and completion criteria

- Run npm ci first (completed for this planning session). During implementation,
  run scripts/test.sh, compile launcher assets and run test:legacy-ui against
  compiled assets across its current compatibility profiles.
- Add meaningful checks for both appearances, switch/reload persistence, invalid
  preferences, unavailable storage, focus retention, partial rows, long labels,
  missing icons, late inventory, reorder/hide/undo, Inputs, Settings, language
  picker and Back behavior. Verify profile restore still boots either appearance.
- Compare reference and prototype screenshots at 1920×1080. Record deviations
  caused by local artwork, font availability and inexpensive glass rendering.
- On the actual LG, record firmware/SDK, viewport and user agent; test cold launch,
  standby resume, sustained D-pad input, Magic Remote, app launch/return and switch
  back to every existing theme. Installation and desktop screenshots do not
  establish device acceptance.
- Preserve triple-Home emergency release, watchdog, key-up delivery and unrelated
  buttons. Helper/input-service changes are not required by this design.
- Update English developer docs and all ten localized guides for changed controls.
  Reconcile linked issue labels if an issue is taken during implementation; no
  GitHub issue was selected or investigated in this planning pass.

## Planning evidence and implementation status

Three read-only subagents audited architecture, performance and official Apple
references. The maintainer accepted setup and requested small modules with a
compiled JSX option. Nano JSX core was selected for presentation composition,
while controller ownership and the Chromium 38 target remain unchanged.
Source inspection establishes structure, not observed runtime behavior.

The fidelity pass uses six columns of 250×150 tiles at x=90, y=822 with a
298-pixel horizontal pitch and a 1.2 focus scale in the 1920×1080 design viewport.
The glass dock is x=40, y=784, width=1824, height=230. The first Down movement
brings the dock near the top and mutes the full-bleed **Sundown** backdrop.
A small local preblurred duplicate supplies the dock/grid treatment instead of
live blur. Focus transitions remain finite. Existing remains the initial default;
the five palettes remain available. These new controls are No-root only. Appearance and effects preferences stay outside
profile backups. Developer scripts provide `npm run dev` and `npm run build:home`;
raw source HTML is not a supported preview path. The bundled Nano JSX runtime
and license ship offline.

Parallel implementation has explicit ownership for the build/module boundary,
appearance styling and regression coverage, and documentation/localization.
The primary agent integrates controller and Settings behavior in this checkout.
Browser/build results must be recorded when run; this document does not imply
those checks or the physical-TV acceptance sequence have passed. Exact motion,
Apple optical effects, and LG 50UP77006LB performance remain unverified.
