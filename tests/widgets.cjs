const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const appRoot = require('./compiled-launcher.cjs')();
const artifacts = path.resolve(__dirname, '../build/tests/widgets');

function intersects(a, b) {
  return a.x < b.x + b.width && a.x + a.width > b.x &&
    a.y < b.y + b.height && a.y + a.height > b.y;
}

(async () => {
  fs.mkdirSync(artifacts, {recursive: true});
  const browser = await chromium.launch({headless: true, channel: process.env.BROWSER_CHANNEL || 'chrome'});
  try {
    const page = await browser.newPage({viewport: {width: 1920, height: 1080}, locale: 'en-GB'});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(() => {
      localStorage.setItem('cytv-appearance', 'tvos');
      localStorage.setItem('cytv-widgets', JSON.stringify({enabled: {clock: true, weather: true, nowPlaying: true}}));
    });
    await page.addInitScript({content: fs.readFileSync(path.resolve(__dirname, '../preview/bridge.js'), 'utf8')});
    await page.route('**/config.js', route => route.fulfill({body: 'window.CONFIG={columns:6,dockApps:[],hiddenApps:[]};'}));
    await page.route('**/apps.js', route => route.fulfill({body: 'window.TV_APPS=' + JSON.stringify({
      apps: Array.from({length: 12}, (_, index) => ({id: 'test.' + index, title: 'App ' + index, icon: 'brand-v2-icon.png'})), inputs: []
    }) + ';'}));
    await page.clock.install({time: new Date(2026, 10, 1, 10, 0)});
    await page.clock.resume();
    await page.goto(pathToFileURL(path.join(appRoot, 'index.html')).href);
    await page.locator('.w-np-title').filter({hasText: 'Midnight City'}).waitFor();
    await page.evaluate(() => document.fonts.ready);
    async function waitForWidgetGeometry() {
      await page.waitForFunction(() => {
        const widgets = document.querySelector('.widgets');
        const music = document.querySelector('.w-np');
        const avatar = document.querySelector('.status-avatar img');
        const style = widgets && getComputedStyle(widgets);
        const musicStyle = music && getComputedStyle(music);
        const artwork = document.querySelector('.w-np-art.has-thumb img');
        return style && style.visibility === 'visible' && style.opacity === '1' &&
          (style.transform === 'none' || style.transform === 'matrix(1, 0, 0, 1, 0, 0)') &&
          music && !music.classList.contains('entering') &&
          (musicStyle.visibility === 'hidden' || musicStyle.opacity === '1' &&
            (musicStyle.transform === 'none' || musicStyle.transform === 'matrix(1, 0, 0, 1, 0, 0)')) &&
          (!artwork || artwork.complete && artwork.naturalWidth > 0) &&
          avatar && avatar.complete && avatar.naturalWidth > 0;
      });
    }
    await waitForWidgetGeometry();
    const bounds = {};
    for (const [name, selector, expected] of [
      ['clock', '.w-clock', {x: 90, y: 468, width: 250, height: 250}],
      ['weather', '.w-wx', {x: 984, y: 170, width: 250, height: 250}],
      ['music', '.w-np', {x: 1282, y: 170, width: 548, height: 274}]
    ]) {
      bounds[name] = await page.locator(selector).boundingBox();
      assert.deepEqual(bounds[name], expected, name + ' must occupy its dock-aligned region');
      assert.equal(await page.locator(selector).evaluate(el => getComputedStyle(el).pointerEvents), 'none');
    }
    const logo = await page.locator('.shelf-mark').boundingBox();
    assert(logo && logo.width > 0 && logo.height > 0, 'logo must be present');
    for (const [name, rect] of Object.entries(bounds)) {
      assert(!intersects(rect, logo), name + ' must not overlap the logo');
      assert(!intersects(rect, {x: 88, y: 62, width: 548, height: 358}), name + ' must clear the reserved logo zone');
      assert(rect.y + rect.height <= 718, name + ' must clear the dock');
    }
    assert.equal(bounds.music.width, bounds.music.height * 2, 'compact music must have a true 2:1 ratio');
    assert.equal(await page.locator('.w-np-controls').count(), 0, 'compact card has no transport controls');
    for (const index of [1, 3, 4, 5]) {
      const tile = page.locator('#tiles .item').nth(index);
      assert.equal(await tile.evaluate(el => el.style.transform), 'translate3d(' + (90 + index * 298) + 'px, 822px, 0px)');
    }
    assert.equal(await page.locator('.glass-slot-reserved').count(), 0);
    assert.equal(await page.locator('.widgets').getAttribute('aria-hidden'), 'true');
    assert.equal(await page.locator('.widgets button, .widgets input, .widgets [tabindex]').count(), 0);
    assert(await page.locator('.w-clock-hour').getAttribute('transform'), 'clock hands must show the live time');
    assert.equal(await page.locator('.w-wx-icon path').count(), 1, 'weather icon must update the mounted SVG');
    assert.equal(await page.locator('.w-np-art img').evaluate(img => img.complete && img.naturalWidth > 0), true);
    assert.equal(await page.locator('.status-avatar img').evaluate(img => img.complete && img.naturalWidth > 0), true);
    assert(await page.evaluate(() => document.fonts.check('400 24px "SF Pro Display"')));
    assert(await page.evaluate(() => document.fonts.check('300 122px "SF Pro Text"')));
    assert.equal(await page.locator('.w-np-texture').evaluate(el => getComputedStyle(el).backgroundImage),
      await page.locator('#dockTexture').evaluate(el => getComputedStyle(el).backgroundImage));
    assert.equal(await page.locator('.w-np-texture').evaluate(el => el.style.backgroundPosition), '-1282px -170px');
    await page.evaluate(() => HomeUI.setPreference('reducedEffects', true));
    assert.equal(await page.locator('.w-np-texture').isVisible(), false);
    await page.evaluate(() => HomeUI.setPreference('reducedEffects', false));
    await page.locator('.w-np').waitFor({state: 'visible'});
    assert.equal(await page.locator('.w-np-texture').isVisible(), true);
    await page.screenshot({path: path.join(artifacts, 'homeview-widgets.png')});
    await page.screenshot({path: path.join(artifacts, 'homeview-widgets-detail.png'), clip: {x: 70, y: 150, width: 1780, height: 590}});

    const originalFocus = await page.locator('#tiles .focused').getAttribute('data-app-id');
    await page.keyboard.press('ArrowRight');
    assert.notEqual(await page.locator('#tiles .focused').getAttribute('data-app-id'), originalFocus);
    await page.keyboard.press('ArrowDown');
    await page.waitForFunction(() => document.body.classList.contains('app-grid'));
    assert.equal(await page.locator('.widgets').evaluate(el => getComputedStyle(el).visibility), 'hidden');
    await page.keyboard.press('ArrowUp');
    await page.waitForFunction(() => !document.body.classList.contains('app-grid'));
    await waitForWidgetGeometry();

    const perWidgetConfig = await page.evaluate(() => localStorage.getItem('cytv-widgets'));
    const focusBeforeToggle = await page.locator('#tiles .focused').getAttribute('data-app-id');
    await page.keyboard.press('ArrowUp');
    await page.keyboard.press('ArrowUp');
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#btnWidgets').evaluate(el => el.classList.contains('focused')), true);
    assert.equal(await page.locator('#btnWidgets').getAttribute('aria-checked'), 'true');
    await page.keyboard.press('Enter');
    await page.locator('.widgets').waitFor({state: 'hidden'});
    assert.equal(await page.locator('#btnWidgets').getAttribute('aria-checked'), 'false');
    assert.equal(await page.locator('.widgets').isVisible(), false);
    assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), focusBeforeToggle);
    assert.equal(await page.evaluate(() => localStorage.getItem('cytv-widgets')), perWidgetConfig,
      'master switch must preserve individual widget settings');
    await page.screenshot({path: path.join(artifacts, 'widgets-off.png')});
    await page.reload();
    await page.locator('#tiles .item').first().waitFor();
    assert.equal(await page.locator('#btnWidgets').getAttribute('aria-checked'), 'false', 'master switch must survive reload');
    assert.equal(await page.locator('.widgets').isVisible(), false);
    await page.locator('#btnWidgets').click();
    await page.locator('.w-np').waitFor({state: 'visible'});
    assert.equal(await page.locator('#btnWidgets').getAttribute('aria-checked'), 'true');
    await page.evaluate(() => {
      window.originalSetItem = Storage.prototype.setItem;
      Storage.prototype.setItem = function (key, value) {
        if (key === 'cytv-widgets-visible') throw new Error('Storage unavailable');
        return originalSetItem.call(this, key, value);
      };
    });
    await page.locator('#btnWidgets').click();
    assert.equal(await page.locator('#btnWidgets').getAttribute('aria-checked'), 'true', 'failed save must not change the switch');
    await page.evaluate(() => { Storage.prototype.setItem = originalSetItem; });

    await page.evaluate(() => {
      window.widgetWatchStops = 0;
      WidgetData.watch = function (callback) {
        window.pushWidgetState = callback;
        return function () { window.widgetWatchStops++; };
      };
      document.dispatchEvent(new Event('visibilitychange'));
    });
    await page.waitForFunction(() => typeof window.pushWidgetState === 'function');
    await page.evaluate(() => { pushWidgetState({nowPlaying: {playing: true, title: 'Streamed music'}}); });
    await page.locator('.w-np').waitFor({state: 'visible'});
    await page.evaluate(() => pushWidgetState(null));
    // Stream callbacks must update the UI without polling or visibility events.
    await page.locator('.w-np').waitFor({state: 'hidden'});
    await waitForWidgetGeometry();
    for (const [name, selector] of [['clock', '.w-clock'], ['weather', '.w-wx']]) {
      assert.deepEqual(await page.locator(selector).boundingBox(), bounds[name], 'missing data must preserve ' + name + ' geometry');
    }
    await page.evaluate(() => {
      pushWidgetState({nowPlaying: {playing: true, title: 'Kitchen music'}});
    });
    await page.locator('.w-np').waitFor({state: 'visible'});
    await waitForWidgetGeometry();
    assert.deepEqual(await page.locator('.w-np').boundingBox(), bounds.music, 'music must return to its assigned region');
    await page.evaluate(() => {
      pushWidgetState({nowPlaying: {playing: false, title: 'Paused music'}});
    });
    await page.locator('.w-np').waitFor({state: 'hidden'});
    assert.equal(await page.locator('.w-np').isVisible(), false, 'paused music must hide the card');
    await page.evaluate(() => {
      localStorage.setItem('cytv-widgets', JSON.stringify({enabled: {clock: false, weather: false, nowPlaying: false}}));
      document.dispatchEvent(new Event('visibilitychange'));
    });
    assert.equal(await page.locator('.w-clock').isVisible(), false);
    assert.equal(await page.locator('.w-wx').isVisible(), false);
    assert.equal(await page.locator('.w-np').isVisible(), false);
    await page.evaluate(() => {
      const settings = document.createElement('div');
      document.body.appendChild(settings);
      HomeUI.mountWidgetSettings(settings);
      settings.querySelector('[role="switch"]').click();
      settings.remove();
    });
    assert.equal(await page.locator('.w-clock').isVisible(), true, 'settings saves must notify the running widgets immediately');
    await page.evaluate(() => HomeUI.setPreference('appearance', 'existing'));
    assert.equal(await page.locator('.widgets').isVisible(), false);
    assert.equal(await page.locator('#btnWidgets').isVisible(), false, 'Existing appearance must not expose the new switch');
    await page.keyboard.press('ArrowUp');
    for (let index = 0; index < 5; index++) await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#btnWidgets').evaluate(el => el.classList.contains('focused')), false, 'Existing remote focus must skip the hidden switch');
    assert.deepEqual(errors, []);
    const afternoon = await browser.newPage({viewport: {width: 1920, height: 1080}});
    await afternoon.addInitScript(() => localStorage.setItem('cytv-appearance', 'tvos'));
    await afternoon.clock.install({time: new Date(2026, 10, 1, 12, 0)});
    await afternoon.clock.resume();
    await afternoon.goto(pathToFileURL(path.join(appRoot, 'index.html')).href);
    await afternoon.locator('#tiles .item').first().waitFor();
    assert.equal(await afternoon.locator('#btnChurch').isVisible(), false, 'the church shortcut only shows from 09:30 until 12:00');
    await afternoon.keyboard.press('ArrowUp');
    assert.equal(await afternoon.locator('#btnSettings').isVisible(), true, 'outside church hours Up opens the LG controls directly');
    await afternoon.close();
    console.log('PASS widgets: dock alignment, logo exclusion, artwork, empty/disabled states and remote navigation');
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error); process.exitCode = 1;});
