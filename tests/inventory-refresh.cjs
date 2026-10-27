const {chromium} = require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert = require('node:assert/strict');
const path = require('node:path');
const {pathToFileURL} = require('node:url');
const appRoot = require('./compiled-launcher.cjs')();
const apps = Array.from({length: 42}, (_, i) => ({id:'inventory.' + i, title:'App ' + ('0' + i).slice(-2),
  icon:i === 2 ? 'missing-test-icon.png' : 'brand-v2-icon.png', dominantColor:[20,40,60]}));
apps[3].dominantColor = ['invalid',0,0];
apps[3].iconColor = '#123456';

(async () => {
  const browser = await chromium.launch({headless:true, channel:process.env.BROWSER_CHANNEL || 'chrome'});
  try {
    for (const appearance of ['existing', 'tvos']) {
      const page = await browser.newPage({viewport:{width:1920,height:1080}, locale:'en'});
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));
      await page.addInitScript(appearance => {
        localStorage.clear();
        localStorage.setItem('cytv-appearance', appearance);
        localStorage.setItem('tvhome.color.inventory.1', '[9,9,9]');
        window.inventoryRequests = [];
        window.canvasReads = 0;
        const getImageData = CanvasRenderingContext2D.prototype.getImageData;
        CanvasRenderingContext2D.prototype.getImageData = function () {
          canvasReads++;
          return getImageData.apply(this, arguments);
        };
        window.PalmServiceBridge = function () {
          this.cancel = function () {};
          this.call = function (uri) {
            if (uri.endsWith('/listApps')) { inventoryRequests.push(this); return; }
            const reply = uri.indexOf('luna://com.cleanyourtv.system.updater.service/') === 0
              ? {returnValue:false,errorCode:-1,errorText:'Service does not exist: com.cleanyourtv.system.updater.service'} : {returnValue:false};
            setTimeout(() => this.onservicecallback(JSON.stringify(reply)), 0);
          };
        };
      }, appearance);
      await page.route('**/config.js', route => route.fulfill({body:'window.CONFIG=' + JSON.stringify({columns:5,dockApps:apps.map(a=>a.id),hiddenApps:[]})}));
      await page.route('**/apps.js', route => route.fulfill({body:'window.TV_APPS=' + JSON.stringify({apps,inputs:[]})}));
      const open = async () => {
        await page.goto(pathToFileURL(path.join(appRoot,'index.html')).href);
        await page.waitForFunction(() => window.inventoryRequests.length === 1 && document.querySelectorAll('#tiles .item').length === 43);
        await page.waitForFunction(() => document.querySelector('[data-app-id="inventory.2"] .missing-icon'));
      };
      await open();
      assert.equal(await page.locator('#tiles .focused').getAttribute('data-app-id'), 'inventory.0', 'startup focuses the first saved app');
      assert.equal(await page.evaluate(() => canvasReads), 0, 'validated colors and hex fallback avoid canvas reads');
      assert.equal(await page.locator('[data-app-id="inventory.0"] .card').evaluate(el=>el.style.background), 'rgb(20, 40, 60)');
      assert.equal(await page.locator('[data-app-id="inventory.3"] .card').evaluate(el=>el.style.background), 'rgb(18, 52, 86)');
      assert.equal(await page.locator('[data-app-id="inventory.41"] img').getAttribute('src'), null, 'deep icon waits for navigation');
      if (appearance === 'tvos') assert.equal(await page.locator('[data-app-id="inventory.6"] img').getAttribute('src'), null, 'idle tvOS loads dock icons first');
      const unchanged = await page.evaluate(apps => {
        const nodes = Array.from(document.querySelectorAll('#tiles .item'));
        const observer = new MutationObserver(() => {});
        observer.observe(document.getElementById('tiles'), {childList:true,subtree:true,attributes:true,characterData:true});
        inventoryRequests[0].onservicecallback(JSON.stringify({returnValue:true,apps}));
        const result = {same:nodes.every((node,i)=>node===document.querySelectorAll('#tiles .item')[i]), mutations:observer.takeRecords().length};
        observer.disconnect();
        return result;
      }, apps);
      assert.deepEqual(unchanged, {same:true, mutations:0}, 'unchanged inventory performs no grid writes');

      await page.reload();
      await page.waitForFunction(() => inventoryRequests.length === 1 && document.querySelectorAll('#tiles .item').length === 43);
      await page.waitForFunction(() => document.querySelector('[data-app-id="inventory.2"] .missing-icon'));
      const patched = await page.evaluate(() => {
        window.tileNodes = Array.from(document.querySelectorAll('#tiles .item'));
        const focused = document.querySelector('#tiles .focused');
        inventoryRequests[0].onservicecallback(JSON.stringify({returnValue:true,apps:[
          {id:'inventory.0',title:'Changed title'},
          {id:'inventory.1',title:'Changed icon',icon:'brand-v2-largeIcon.png'},
          {id:'inventory.2',title:'Broken renamed'}
        ]}));
        return {same:tileNodes.every((node,i)=>node===document.querySelectorAll('#tiles .item')[i]),
          focus:focused===document.querySelector('#tiles .focused'),count:tileNodes.length};
      });
      assert.deepEqual(patched, {same:true,focus:true,count:43}, 'partial refresh patches metadata and keeps every saved node and focus');
      assert.equal(await page.locator('[data-app-id="inventory.0"]').getAttribute('aria-label'), 'Changed title');
      assert.equal(await page.locator('[data-app-id="inventory.0"] .name').textContent(), 'Changed title');
      assert.equal(await page.locator('[data-app-id="inventory.0"] .card').evaluate(el=>el.style.background), 'rgb(20, 40, 60)');
      assert.equal(await page.locator('[data-app-id="inventory.1"] img').getAttribute('src'), 'brand-v2-largeIcon.png');
      await page.waitForFunction(() => canvasReads > 0);
      assert.notEqual(await page.evaluate(()=>localStorage.getItem('tvhome.color.inventory.1')), '[9,9,9]', 'changed artwork replaces stale cached color');
      assert.equal(await page.locator('[data-app-id="inventory.2"] .card').getAttribute('data-initial'), 'B', 'failed image fallback follows changed title');
      assert.equal(await page.locator('[data-app-id="inventory.2"] img').evaluate(el=>el.style.display), 'none');
      await page.keyboard.press('ArrowDown');
      const next = appearance === 'tvos' ? 6 : 5;
      assert.equal(await page.locator('[data-app-id="inventory.'+next+'"] img').getAttribute('src'), 'brand-v2-icon.png', 'focused icon loads synchronously');
      assert.equal(await page.locator('[data-app-id="inventory.'+(next+1)+'"] img').getAttribute('src'), 'brand-v2-icon.png', 'nearby row icons load with scroll geometry');
      assert.equal(await page.locator('[data-app-id="inventory.41"] img').getAttribute('src'), null);
      assert.deepEqual(errors, []);
      await page.close();
      console.log('PASS', appearance, 'inventory identity, partial metadata, color fallbacks and geometry icon loading');
    }
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode=1;});
