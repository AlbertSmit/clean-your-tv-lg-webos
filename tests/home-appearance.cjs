const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const appRoot = require('./compiled-launcher.cjs')();
const artifacts = path.resolve(__dirname, '../build/tests/appearance');

(async () => {
  fs.mkdirSync(artifacts, {recursive: true});
  const browser = await chromium.launch({headless: true, channel: process.env.BROWSER_CHANNEL || 'chrome'});
  try {
    const page = await browser.newPage({viewport: {width: 1920, height: 1080}, locale: 'en'});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.addInitScript(() => {
      delete Array.prototype.flat;
      delete Array.prototype.includes;
      window.launches = [];
      window.PalmServiceBridge = function () {
        this.cancel = function () {};
        this.call = function (uri, raw) {
          const params = JSON.parse(raw);
          if (uri.endsWith('/launch')) window.launches.push(params.id);
          const result = uri.indexOf('luna://com.cleanyourtv.system.updater.service/') === 0
            ? {returnValue: false, errorCode: -1, errorText: 'Service does not exist: com.cleanyourtv.system.updater.service'}
            : {returnValue: uri.endsWith('/launch')};
          setTimeout(() => this.onservicecallback(JSON.stringify(result)), 0);
        };
      };
    });
    await page.route('**/config.js', route => route.fulfill({body: 'window.CONFIG=' + JSON.stringify({
      columns: 5, dockApps: Array.from({length: 13}, (_, index) => 'test.' + index), hiddenApps: []
    }) + ';'}));
    await page.route('**/apps.js', route => route.fulfill({body: 'window.TV_APPS=' + JSON.stringify({
      apps: Array.from({length: 13}, (_, index) => ({id: 'test.' + index,
        title: index === 0 ? 'An app with a long title that must fit inside the selected tile' : 'App ' + String(index).padStart(2, '0'),
        icon: index === 12 ? 'missing-test-icon.png' : 'brand-v2-icon.png'})), inputs: []
    }) + ';'}));
    await page.goto(pathToFileURL(path.join(appRoot, 'index.html')).href);
    await page.waitForFunction(() => document.querySelectorAll('#tiles .item').length === 14);
    await page.locator('[data-appearance="tvos"]').waitFor({state: 'attached'});
    await page.evaluate(() => { window.originalTiles = Array.from(document.querySelectorAll('#tiles .item')); });
    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), 'test.2');
    await page.mouse.move(0, 0);
    await page.locator('#btnSettings').dispatchEvent('click');
    await page.locator('[data-appearance="tvos"]').click();
    assert.equal(await page.locator('html').evaluate(el => el.classList.contains('home-tvos')), true);
    assert.equal(await page.locator('[data-appearance="tvos"]').getAttribute('aria-pressed'), 'true');
    assert.equal(await page.evaluate(() => document.activeElement.dataset.appearance), 'tvos', 'live preview keeps Settings focus');
    assert.deepEqual(await page.locator('#tiles .item').first().evaluate(el => ({
      width: el.offsetWidth, transform: el.style.transform
    })), {width: 250, transform: 'translate3d(90px, 822px, 0px)'});
    assert.equal(await page.locator('#dockBand').evaluate(el => getComputedStyle(el).display), 'block');
    assert.equal(await page.locator('#tiles .item.dock .name').first().evaluate(el => getComputedStyle(el).display), 'none');
    assert.equal(await page.locator('#homeShelf').evaluate(el => el.offsetWidth), 1920);
    assert.equal(await page.locator('#topButtons').isVisible(), false, 'idle header matches the compact status control');
    await page.mouse.move(0, 0);
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), 'test.2');
    await page.screenshot({path: path.join(artifacts, 'tvos.png')});
    await page.keyboard.press('ArrowDown');
    assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), 'test.8', 'new layout navigates by six columns');
    assert.equal(await page.locator('body').evaluate(el => el.classList.contains('app-grid')), true);
    assert.equal(await page.locator('#stage').evaluate(el => el.style.transform), 'translate3d(0px, -724px, 0px)');
    assert.equal(await page.locator('[data-app-id="test.8"]').evaluate(el => el.style.transform), 'translate3d(686px, 1082px, 0px)');
    await page.mouse.move(950, 550);
    await page.mouse.wheel(0, -100);
    await page.waitForFunction(() => document.querySelector('#tiles .focused').dataset.appId === 'test.2');
    assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), 'test.2', 'wheel Up restores the dock state');
    await page.waitForTimeout(250);
    await page.mouse.wheel(0, 100);
    await page.waitForFunction(() => document.querySelector('#tiles .focused').dataset.appId === 'test.8');
    assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), 'test.8', 'wheel Down reveals the app grid');
    await page.mouse.move(0, 0);
    await page.keyboard.press('ArrowDown');
    assert.equal(await page.locator('#tiles .focused').count(), 1, 'partial final row keeps focus');
    await page.keyboard.press('ArrowLeft');
    await page.keyboard.press('Enter');
    assert.deepEqual(await page.evaluate(() => window.launches), ['test.12']);
    await page.evaluate(() => {
      for (let index = 0; index < 50; index++) HomeUI.setPreference('appearance', index % 2 ? 'existing' : 'tvos');
    });
    assert.equal(await page.evaluate(() => Array.from(document.querySelectorAll('#tiles .item')).every((el, index) => el === originalTiles[index])), true,
      'switching reuses all tile nodes');
    assert.equal(await page.locator('#homeShelf').count(), 1);
    assert.equal(await page.locator('[data-appearance]').count(), 2);
    const palettes = {classic: 'rgb(0, 0, 0)', midnight: 'rgb(5, 5, 16)', pixel: 'rgb(10, 26, 10)', bloom: 'rgb(26, 10, 26)', amber: 'rgb(26, 21, 5)'};
    for (const [theme, expected] of Object.entries(palettes)) {
      await page.evaluate(theme => ThemePanel.applyTheme(theme), theme);
      assert.equal(await page.locator('body').evaluate(el => getComputedStyle(el).backgroundColor), expected, theme + ' works after compilation');
    }
    await page.evaluate(() => HomeUI.setPreference('appearance', 'tvos'));
    await page.reload();
    await page.locator('#tiles .add-app').waitFor();
    assert.equal(await page.locator('html').evaluate(el => el.classList.contains('home-tvos')), true, 'appearance survives restart');
    await page.keyboard.down('Enter');
    await page.waitForTimeout(650);
    await page.keyboard.up('Enter');
    assert.equal(await page.locator('.moving').count(), 1);
    assert.equal(await page.locator('#homeStatus').evaluate(el => getComputedStyle(el).pointerEvents), 'none', 'editing hides the status control');
    await page.locator('#homeStatus').dispatchEvent('click');
    assert.equal(await page.locator('body').evaluate(el => el.classList.contains('controls-open')), false, 'status control cannot steal active editing');
    assert.equal(await page.locator('.moving').count(), 1);
    await page.keyboard.press('Escape');
    await page.keyboard.press('ArrowUp');
    assert.equal(await page.locator('#btnSettings').isVisible(), true, 'Up reveals LG controls');
    await page.keyboard.press('Escape');
    assert.equal(await page.locator('#btnSettings').isVisible(), false, 'Back returns to the Home composition');
    await page.locator('#homeStatus').click();
    await page.locator('#btnSettings').click();
    await page.getByRole('switch', {name: 'Reduce effects', exact: true}).click();
    assert.equal(await page.locator('html').evaluate(el => el.classList.contains('reduced-effects')), true);
    await page.locator('[data-appearance="existing"]').click();
    assert.equal(await page.locator('html').evaluate(el => el.classList.contains('theme-amber')), true, 'return preserves existing palette');
    assert.equal(await page.locator('#tiles .item').first().evaluate(el => el.offsetWidth), 360);
    await page.evaluate(() => {
      const original = Storage.prototype.setItem;
      Storage.prototype.setItem = function (key, value) {
        if (key === 'cytv-appearance') throw Error('Storage unavailable');
        return original.call(this, key, value);
      };
    });
    await page.locator('[data-appearance="tvos"]').click();
    assert.equal(await page.locator('html').evaluate(el => el.classList.contains('home-tvos')), false, 'failed write keeps current appearance');
    assert.equal(await page.locator('.appearance-error').textContent(), "Couldn't save changes. Please try again.");
    assert.deepEqual(errors, []);
    await page.close();

    const invalid = await browser.newPage({viewport: {width: 1920, height: 1080}});
    await invalid.addInitScript(() => localStorage.setItem('cytv-appearance', 'unknown-future-mode'));
    await invalid.goto(pathToFileURL(path.join(appRoot, 'index.html')).href);
    await invalid.locator('#tiles .add-app').waitFor();
    assert.equal(await invalid.locator('html').evaluate(el => el.classList.contains('home-tvos')), false, 'unknown preference falls back to existing');
    await invalid.close();
    console.log('PASS compiled JSX, six-column navigation, live/repeated switching, palette restoration, persistence, reduced effects and storage failure');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
