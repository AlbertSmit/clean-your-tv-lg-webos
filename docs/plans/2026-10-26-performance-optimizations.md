# Performance Optimizations Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the webOS tvOS-style launcher snappy by eliminating frame drops during navigation, reducing launch time, and removing GPU/CPU bottlenecks.

**Architecture:** Target the three biggest offenders identified in code review: (1) SVG displacement filter on dock, (2) full DOM rebuild on every change, (3) per-tile canvas color extraction on image load. Then address layout thrashing, animation properties, and bundle size.

**Tech Stack:** Vanilla JS (ES5), CSS, webOS WebKit (often single-core, limited GPU acceleration)

---

### Task 1: Remove SVG Displacement Filter from Dock Glass

**Files:**
- Modify: `launcher/ui/dock-glass.js:1-82`
- Modify: `launcher/appearance.css:50-62` (remove dockTexture/dockOptics styles)

**Step 1: Verify current behavior**
- Open launcher in browser devtools
- Enable tvOS mode (localStorage cytv-appearance = 'tvos')
- Record performance profile while navigating dock
- Note Paint times for dockOptics filter

**Step 2: Replace SVG filter with static backdrop**
- Remove `createOptics()` and SVG filter creation
- Keep static `dockTexture` using pre-blurred image
- Add CSS `backdrop-filter: blur()` fallback for modern engines
- Ensure `reducedEffects` still disables all dock effects

**Step 3: Test**
- Verify dock still looks correct (translucent glass over backdrop)
- Verify no console errors
- Profile again - Paint should drop from ~15ms to ~1ms

**Step 4: Commit**
```bash
git add launcher/ui/dock-glass.js launcher/appearance.css
git commit -m "perf: replace SVG displacement filter with static backdrop

feDisplacementMap + feGaussianBlur on 1872x278 bounds caused
15ms+ paint per frame on webOS WebKit. Static backdrop image
with CSS backdrop-filter fallback reduces to <1ms."
```

---

### Task 2: Pre-compute Icon Dominant Colors at Build Time

**Files:**
- Modify: `launcher/apps.js` (add `dominantColor` field to each app)
- Modify: `launcher/app.js:549-621` (remove canvas color extraction, use pre-computed)
- Create: `scripts/compute-icon-colors.py` (build script)

**Step 1: Write build script**
```python
#!/usr/bin/env python3
# scripts/compute-icon-colors.py
# Reads apps.js, loads each icon, computes dominant color via PIL,
# writes updated apps.js with dominantColor field
```

**Step 2: Run script to update apps.js**
- Add `dominantColor: [r, g, b]` to each app entry
- Remove `iconColor` if redundant (keep for backward compat)

**Step 3: Modify app.js createTile()**
- Remove `image.onload` canvas logic entirely
- Read `tile.app.dominantColor` directly
- Fallback to `iconColor` parsing if missing

**Step 4: Test**
- Verify ambient glow and card backgrounds still work
- Verify no canvas errors in console
- Launch time should improve (no 20-30 canvas readbacks)

**Step 5: Commit**
```bash
git add launcher/apps.js launcher/app.js scripts/compute-icon-colors.py
git commit -m "perf: pre-compute icon dominant colors at build time

Eliminates 20-30 canvas drawImage + getImageData readbacks on launch.
GPU->CPU sync was blocking main thread for 50-100ms total.
Colors now stored in apps.js as dominantColor: [r,g,b]."
```

---

### Task 3: Incremental Tile Updates (Replace rebuild())

**Files:**
- Modify: `launcher/app.js:171-208` (rebuild function)
- Modify: `launcher/app.js:353-434` (picker/renderPicker)
- Modify: `launcher/app.js:535-546` (initializeApps refresh callback)

**Step 1: Add helper functions**
```javascript
function appendTile(tile, index) { ... }
function removeTile(index) { ... }
function moveTileDOM(fromIndex, toIndex) { ... }
function updateTilePositions(startIndex) { ... }
```

**Step 2: Refactor rebuild() to incremental**
- Keep `rebuild()` for full reset (preference change)
- Add `insertTile(app, index)`, `deleteTile(index)`, `reorderTiles(from, to)`
- Picker add: call `insertTile()` instead of `rebuild()`
- Hide/undo: call `deleteTile()` / `insertTile()`
- Inventory refresh: diff and patch only changed tiles

**Step 3: Test**
- Add app via picker - should not re-render existing tiles
- Hide app - should only remove one tile
- Undo - should restore one tile
- Preference change - full rebuild still works
- Focus/index consistency after each operation

**Step 4: Commit**
```bash
git add launcher/app.js
git commit -m "perf: incremental tile updates instead of full rebuild

rebuild() destroyed/recreated 20-30 DOM nodes on every add/hide/undo.
Now uses insertTile/deleteTile/moveTileDOM for O(1) DOM ops.
Full rebuild retained only for appearance preference changes."
```

---

### Task 4: Switch left/top Animations to transform (GPU Composited)

**Files:**
- Modify: `launcher/style.css:321-330` (.item transitions)
- Modify: `launcher/appearance.css:64-65` (tvOS .item transitions)
- Modify: `launcher/app.js:631-637` (layoutTiles - use transform)
- Modify: `launcher/app.js:693-739` (focusTile - use transform)

**Step 1: Update CSS**
```css
.item {
  /* Remove left/top from transition */
  transition: opacity 400ms ease, transform 400ms cubic-bezier(...);
  will-change: transform, opacity;
}
.item.shown { transform: translate3d(0,0,0); }
```

**Step 2: Update layoutTiles() to use transform**
```javascript
e.el.style.transform = 'translate3d(' + tileLeft(t) + 'px,' + tileTop(t) + 'px,0)';
/* Remove left/top style assignments */
```

**Step 3: Update focusTile() glass position**
- Already uses transform - verify it's translate3d

**Step 5: Test**
- Navigate with remote - verify 60fps (no layout thrashing)
- DevTools Rendering → "Layout Shift Regions" should show none during nav
- DevTools Layers panel - tiles should be on own compositor layer

**Step 6: Commit**
```bash
git add launcher/style.css launcher/appearance.css launcher/app.js
git commit -m "perf: animate transform instead of left/top for GPU compositing

left/top transitions trigger layout on every frame. transform:translate3d()
keeps tiles on compositor thread. Adds will-change for layer promotion."
```

---

### Task 5: Event Delegation on Tile Container

**Files:**
- Modify: `launcher/app.js:616-620` (createTile event bindings)
- Modify: `launcher/app.js:253-271` (bindHold)
- Modify: `launcher/app.js:272-286` (tileClick)

**Step 1: Add single delegated listeners on tilesContainer**
```javascript
tilesContainer.addEventListener('mouseover', onTileMouseOver);
tilesContainer.addEventListener('click', onTileClick);
tilesContainer.addEventListener('mousedown', onTileMouseDown);
tilesContainer.addEventListener('mouseleave', onTileMouseLeave);
```

**Step 2: Remove per-tile listeners in createTile/bindHold**
- Use `event.target.closest('.item')` to find tile
- Map element to tile index via `tiles.findIndex`

**Step 3: Test**
- Hover/focus still works
- Click launches app
- Long press (600ms) enters edit mode
- No memory leaks (listeners removed on rebuild)

**Step 4: Commit**
```bash
git add launcher/app.js
git commit -m "perf: event delegation on tile container

Reduces 75+ event listeners (3 per tile) to 4 on container.
Less memory, faster attach/detach during rebuild."
```

---

### Task 6: Lazy-load Tile Icons

**Files:**
- Modify: `launcher/app.js:549-621` (createTile)
- Modify: `launcher/app.js:631-647` (layoutTiles)

**Step 1: Add IntersectionObserver for visible tiles**
```javascript
var iconObserver = new IntersectionObserver(function(entries) {
  entries.forEach(function(entry) {
    if (entry.isIntersecting) {
      var img = entry.target.querySelector('img');
      if (img.dataset.src) { img.src = img.dataset.src; img.removeAttribute('data-src'); }
      iconObserver.unobserve(entry.target);
    }
  });
}, { rootMargin: '200px' });
```

**Step 2: In createTile, set data-src instead of src**
```javascript
image.dataset.src = app.icon || 'missing-icon';
image.src = ''; // or 1x1 transparent placeholder
iconObserver.observe(element);
```

**Step 3: In layoutTiles, observe all tiles**
- Call `iconObserver.observe(tile.el)` for each tile

**Step 4: Test**
- Network tab: only first 6-8 icons load initially
- Scroll down - remaining icons load as they approach viewport
- No layout shift (cards have fixed size)

**Step 5: Commit**
```bash
git add launcher/app.js
git commit -m "perf: lazy-load tile icons with IntersectionObserver

Only loads icons for visible/near-viewport tiles.
Reduces initial launch requests from 25+ to ~6.
Uses 200px rootMargin for smooth scrolling."
```

---

### Task 7: Remove nano-jsx from home-ui.js Bundle

**Files:**
- Modify: `launcher/ui/tile.jsx` → inline in `home-ui.js` as createTileView/createAddView (already done in build)
- Modify: `scripts/bundle-home-ui.cjs` (remove nano-jsx bundling)
- Modify: `build/home-app/home-ui.js` (verify output)

**Step 1: Verify current home-ui.js build output**
- Check `build/home-app/home-ui.js` includes nano-jsx core (~700 lines)

**Step 2: Replace nano-jsx h() calls with document.createElement**
- Tile view: 3 elements (div.item > div.card + img, div.name)
- Add view: similar
- Shelf: 5 static elements
- Status: button with nested spans
- Dock glass: already vanilla JS

**Step 3: Update bundle script**
- Remove nano-jsx from bundle
- Output should be ~200 lines vs ~900

**Step 4: Test**
- Verify tiles render correctly
- Verify shelf/status/dock glass work
- Bundle size reduction

**Step 5: Commit**
```bash
git add scripts/bundle-home-ui.cjs launcher/ui/tile.jsx launcher/ui/shelf.jsx launcher/ui/status.jsx build/home-app/home-ui.js
git commit -m "perf: remove nano-jsx runtime from home-ui bundle

nano-jsx core (700 lines) only used for 4 simple component factories.
Replaced with direct document.createElement - saves ~50KB minified,
reduces parse/eval time on launch."
```

---

### Task 8: Fix Layout Thrashing in focusTile/keydown

**Files:**
- Modify: `launcher/app.js:646` (headerBottom measurement)
- Modify: `launcher/app.js:954-958` (getBoundingClientRect in keydown)
- Modify: `launcher/app.js:706` (scrollFor called during focus)

**Step 1: Cache headerBottom on layout change**
- Move measurement to `layoutTiles()` where layout is already computed
- Store in module variable

**Step 2: Replace getBoundingClientRect with layout math**
- Top button positions computable from `layout.left`, `layout.columnWidth`
- No DOM measurement needed

**Step 3: Batch scroll/transform updates with rAF**
```javascript
function scheduleFocusUpdate(index) {
  if (focusRaf) cancelAnimationFrame(focusRaf);
  focusRaf = requestAnimationFrame(function() {
    focusTile(index);
  });
}
```

**Step 4: Test**
- DevTools Performance: no "Forced Reflow" markers during navigation
- Rapid key presses don't queue multiple layouts

**Step 5: Commit**
```bash
git add launcher/app.js
git commit -m "perf: eliminate forced layouts in focus/navigation

Cached headerBottom in layoutTiles(). Replaced getBoundingClientRect()
with layout math. Batched focus updates with rAF."
```

---

### Task 9: Font Optimization (WOFF2 + font-display)

**Files:**
- Modify: `launcher/style.css:164-168` (@font-face Outfit)
- Verify: `launcher/fonts/` has WOFF2 files

**Step 1: Check font files**
- `fonts/outfit.ttf` → convert to WOFF2 subset (latin + latin-ext)
- Or use existing Inter WOFF2 from appearance.css

**Step 2: Update @font-face**
```css
@font-face {
  font-family: 'Outfit';
  src: url('fonts/outfit.woff2') format('woff2');
  font-weight: 300 500; /* only weights used */
  font-display: swap;
}
```

**Step 3: Test**
- Network tab: font loads async, text visible immediately
- No flash of invisible text (FOIT)

**Step 4: Commit**
```bash
git add launcher/style.css launcher/fonts/outfit.woff2
git commit -m "perf: optimize font loading with WOFF2 and font-display: swap

TTF → WOFF2 saves ~60%. font-display: swap prevents FOIT.
Subset to latin + latin-ext (weights 300, 500 only)."
```

---

### Task 10: Ambient Glow Optimization

**Files:**
- Modify: `launcher/app.js:741-752` (updateAmbient)
- Modify: `launcher/style.css:184-190` (.ambient)

**Step 1: Pre-generate gradient textures**
- Create 6-8 radial gradient PNGs (one per common hue)
- Or use CSS `background-image: url()` with data URIs

**Step 2: Swap background-image instead of recalculating gradient**
```javascript
var gradients = {
  '255,0,0': 'url(data:image/png;base64,...)',
  // ...
};
nextLayer.style.backgroundImage = gradients[color] || defaultGradient;
```

**Step 3: Test**
- Focus changes - no style recalc for large radial gradients
- DevTools: no "Recalculate Style" on ambient layers

**Step 4: Commit**
```bash
git add launcher/app.js launcher/assets/ambient-gradients/
git commit -m "perf: pre-render ambient glow gradients

Large radial-gradient() recalc on every focus caused style thrashing.
Pre-rendered 8 gradient textures swapped via background-image."
```

---

### Execution Order

1. **Task 1** (SVG filter) - Highest impact, lowest risk
2. **Task 2** (pre-compute colors) - High impact, isolated change
3. **Task 4** (transform animations) - High impact, CSS-only mostly
3. **Task 3** (incremental tiles) - Medium risk, high reward
4. **Task 5** (event delegation) - Low risk
5. **Task 6** (lazy icons) - Medium risk
6. **Task 7** (remove nano-jsx) - Build change only
7. **Task 8** (layout thrashing) - Requires careful testing
8. **Task 9** (fonts) - Low risk
9. **Task 10** (ambient) - Nice to have

---

### Verification Checklist

After all tasks:
- [ ] Launch to interactive < 500ms (was ~1.5s)
- [ ] Remote navigation 60fps (no frame drops)
- [ ] Dock scroll smooth (no jank)
- [ ] Memory stable over 5 min use (no leaks)
- [ ] All existing features work: add/hide/undo/picker/themes
- [ ] reducedEffects mode still works
- [ ] Both 'existing' and 'tvos' appearance modes work