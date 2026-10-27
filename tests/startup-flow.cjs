const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const {chromium} = require('playwright');
const appRoot = require('./compiled-launcher.cjs')();
const url = pathToFileURL(path.join(appRoot, 'index.html')).href;

(async () => {
  const browser = await chromium.launch({headless: true, channel: process.env.BROWSER_CHANNEL || 'chrome'});
  try {
    const pageErrors = new Map();
    async function pageFor(mode) {
      const page = await browser.newPage({viewport: {width: 1920, height: 1080}});
      const errors = [];
      pageErrors.set(page, errors);
      page.on('pageerror', error => errors.push(error.message));
      await page.addInitScript(mode => {
        localStorage.clear();
        localStorage.setItem('tvhome.language', 'en');
        localStorage.setItem('cytv-appearance', 'tvos');
        window.PalmSystem = {launchParams: JSON.stringify({showHelper: mode === 'helper'})};
        window.serviceCalls = [];
        const frames = [];
        window.requestAnimationFrame = callback => { frames.push(callback); return frames.length; };
        window.runFrame = () => frames.splice(0).forEach(callback => callback(0));
        window.PalmServiceBridge = function () {
          this.cancel = function () {};
          this.call = (uri, raw) => {
            window.serviceCalls.push(uri);
            const method = uri.split('/').pop();
            const reply = result => this.onservicecallback(JSON.stringify(result));
            if (method === 'restoreProfile') {
              window.releaseProfile = () => reply(mode === 'recovery'
                ? {returnValue: false, errorText: 'Unreadable update backup'}
                : {returnValue: true, result: null});
              return;
            }
            if (uri.includes('system.updater') && method === 'status') {
              window.releaseStatus = () => reply({returnValue: true, result: null});
              return;
            }
            if (method === 'listApps') return;
            setTimeout(() => reply({returnValue: false}), 0);
          };
        };
      }, mode);
      await page.route('**/config.js', route => route.fulfill({body: 'window.CONFIG={columns:6,dockApps:[],hiddenApps:[]};'}));
      await page.route('**/apps.js', route => route.fulfill({body: 'window.TV_APPS={apps:[{id:"one",title:"One",icon:"brand-v2-icon.png"},{id:"two",title:"Two",icon:"brand-v2-icon.png"}],inputs:[]};'}));
      await page.route('**/startup-metrics.js', route => route.fulfill({body: ''})); // Surface must not depend on optional metrics.
      if (mode === 'script-error') await page.route('**/app.js', route => route.abort());
      await page.goto(url);
      await page.waitForFunction(() => typeof window.releaseProfile === 'function', null, {polling: 20});
      return page;
    }
    const page = await pageFor('normal');
    assert(await page.locator('#homeStartup').isVisible(), 'profile gate keeps the static surface visible');
    assert.equal(await page.locator('#homeStartup h1').textContent(), 'Home');
    assert.equal(await page.locator('#tiles .item').count(), 0);
    assert.equal(await page.locator('#renewalPanel, #updatePanel, [data-appearance]').count(), 0);
    assert.equal(await page.evaluate(() => RenewalPanel.isOpen()), false);
    await page.evaluate(() => releaseProfile());
    await page.waitForFunction(() => window.RootLauncherRendered === true, null, {polling: 20});
    assert.equal(await page.locator('#homeStartup').isVisible(), false);
    assert(await page.locator('#clock').textContent(), 'local clock renders synchronously');
    assert(await page.locator('.w-clock-hour').getAttribute('transform'), 'local widget clock renders before background work');
    await page.evaluate(() => {
      window.watchCount = 0;
      window.stopCount = 0;
      WidgetData.watch = callback => { watchCount++; window.lateWidget = callback; return () => { stopCount++; }; };
    });
    const background = () => page.evaluate(() => serviceCalls.filter(uri => /\/listApps$|connectionmanager/.test(uri)));
    assert.deepEqual(await background(), []);
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), 'two', 'first navigation works while deferred work is held');
    await page.evaluate(() => runFrame());
    assert.deepEqual(await background(), [], 'one frame is insufficient');
    await page.evaluate(() => { HomeUI.setPreference('widgetsVisible', false); HomeUI.setPreference('widgetsVisible', true); });
    await page.evaluate(() => runFrame());
    await page.waitForFunction(() => serviceCalls.some(uri => uri.includes('connectionmanager')), null, {polling: 20});
    assert.equal(await page.evaluate(() => watchCount), 0, 'stale initial watch does not start after preference changes');
    await page.evaluate(() => runFrame());
    await page.waitForFunction(() => watchCount === 1, null, {polling: 20});
    assert.equal((await background()).filter(uri => uri.endsWith('/listApps')).length, 1);
    assert.equal((await background()).filter(uri => uri.includes('connectionmanager')).length, 1);
    await page.evaluate(() => { HomeUI.setPreference('reducedEffects', true); HomeUI.setPreference('widgetsVisible', true); runFrame(); });
    assert.equal(await page.evaluate(() => watchCount), 1, 'cosmetic or unchanged preferences do not restart the watch');
    assert.equal(await page.evaluate(() => stopCount), 0);
    await page.evaluate(() => HomeUI.setPreference('widgetsVisible', false));
    assert.equal(await page.evaluate(() => stopCount), 1, 'turning widgets off disposes active work');
    await page.evaluate(() => lateWidget({nowPlaying: {title: 'Stale update'}}));
    assert.equal(await page.locator('.w-np-title').textContent(), '', 'disposed watch cannot publish stale content');
    await page.locator('#btnSettings').dispatchEvent('click');
    await page.locator('#renewalPanel').waitFor({state: 'visible'});
    assert.equal(await page.locator('[data-appearance]').count(), 2);
    const tileFocus = await page.locator('#tiles .focused').getAttribute('data-app-id');
    await page.keyboard.press('ArrowRight');
    assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), tileFocus, 'Settings owns remote input');
    await page.keyboard.press('Escape');
    await page.evaluate(() => { HomeUpdates.open(); });
    assert.equal(await page.locator('#updatePanel').count(), 0, 'unified updater route does not mount legacy DOM');
    await page.evaluate(() => releaseStatus());
    await page.keyboard.press('Escape');
    await page.evaluate(() => { window.SystemUpdates = null; HomeUpdates.open(); });
    assert.equal(await page.locator('#updatePanel').count(), 1, 'legacy fallback mounts on demand');
    assert.deepEqual(pageErrors.get(page), []);
    await page.close();

    for (const mode of ['recovery', 'script-error']) {
      const blocked = await pageFor(mode);
      assert(await blocked.locator('#homeStartup').isVisible());
      await blocked.evaluate(() => releaseProfile());
      await blocked.getByRole('dialog', {name: 'Software updates', exact: true}).waitFor({state: 'visible'});
      assert.equal(await blocked.locator('#homeStartup').isVisible(), false, mode + ' exposes recovery before status replies');
      assert.equal(await blocked.locator('#updatePanel').count(), 0);
      assert.equal(await blocked.evaluate(() => window.RootLauncherRendered === true), false);
      assert.deepEqual(pageErrors.get(blocked), []);
      await blocked.close();
    }
    const helper = await pageFor('helper');
    assert(await helper.getByRole('dialog', {name: 'Home Helper', exact: true}).isVisible());
    assert.equal(await helper.locator('#homeStartup').isVisible(), false);
    await helper.evaluate(() => releaseProfile());
    await helper.waitForFunction(() => window.RootLauncherRendered === true, null, {polling: 20});
    const focused = await helper.evaluate(() => document.activeElement.textContent);
    await helper.evaluate(() => document.dispatchEvent(new Event('webOSRelaunch')));
    assert.equal(await helper.evaluate(() => document.activeElement.textContent), focused, 'normal boot/relaunch preserves direct Helper entry');
    await helper.keyboard.press('ArrowDown');
    assert.equal(await helper.locator('#tiles .focused').getAttribute('data-app-id'), 'one', 'Helper owns modal input');
    assert.deepEqual(pageErrors.get(helper), []);
    await helper.close();
    console.log('PASS startup surface, delayed profile/recovery, lazy panels, deferred services and Helper input isolation');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exitCode = 1; });
