// Capture only the demo preview, never an installed TV's personal app inventory.
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');

(async () => {
  const output = path.resolve(__dirname, '../build/reference');
  fs.mkdirSync(output, {recursive: true});
  const browser = await chromium.launch({headless: true, channel: process.env.BROWSER_CHANNEL || 'chrome'});
  try {
    const page = await browser.newPage({viewport: {width: 1920, height: 1080}, locale: 'en'});
    await page.goto('http://127.0.0.1:8765/launcher/index.html');
    await page.locator('#tiles .add-app').waitFor();
    if (await page.locator('#homeStatus').isVisible()) await page.locator('#homeStatus').click();
    await page.locator('#btnSettings').click();
    await page.locator('[data-appearance="tvos"]').click();
    await page.mouse.move(0, 0);
    await page.keyboard.press('Escape');
    await page.locator('#tiles .item').first().hover();
    await page.mouse.move(0, 0);
    await page.evaluate(() => document.fonts.ready);
    await page.waitForTimeout(700); // Capture the settled focus/entry state.
    await page.screenshot({path: path.join(output, 'current-home.png')});
    const metrics = await page.evaluate(() => {
      const bounds = selector => {
        const el = document.querySelector(selector), rect = el.getBoundingClientRect(), css = getComputedStyle(el);
        return {x: rect.x, y: rect.y, width: rect.width, height: rect.height, display: css.display, visibility: css.visibility, opacity: css.opacity};
      };
      return {
        viewport: {width: innerWidth, height: innerHeight},
        first: bounds('#tiles .item'), focusedCard: bounds('#tiles .focused .card'),
        second: bounds('#tiles .item:nth-child(2)'), shelf: bounds('#homeShelf'),
        dock: bounds('#dockBand'), status: bounds('#homeStatus'), controls: bounds('#topButtons')
      };
    });
    fs.writeFileSync(path.join(output, 'current-metrics.json'), JSON.stringify(metrics, null, 2) + '\n');
    await page.keyboard.press('ArrowDown');
    await page.waitForTimeout(700);
    await page.screenshot({path: path.join(output, 'current-scrolled.png')});
    console.log('Saved demo screenshots and geometry in ' + output);
  } finally { await browser.close(); }
})().catch(error => {console.error(error); process.exitCode = 1;});
