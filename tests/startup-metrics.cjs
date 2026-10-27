const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('launcher/startup-metrics.js', 'utf8');
function load(usePerformance, useFrames) {
  let now = 100, frames = [];
  const root = {setTimeout(callback, delay) { assert.equal(delay, 16); frames.push(callback); }};
  if (usePerformance) root.performance = {now() { assert.equal(this, root.performance); return now; }};
  if (useFrames) root.requestAnimationFrame = callback => frames.push(callback);
  const context = {window: root, Date: {now: () => now}};
  vm.runInNewContext(source, context);
  return {root, context, advance(value) { now = value; }, frame() { frames.shift()(); }, count: () => frames.length};
}
for (const performance of [false, true]) for (const frames of [false, true]) {
  const h = load(performance, frames), metrics = h.root.HomeStartup;
  assert.equal(metrics.snapshot().firstJS, 0);
  h.advance(135); metrics.mark('appStart');
  h.advance(150); metrics.mark('appStart');
  assert.equal(metrics.snapshot().appStart, 35, 'only the first occurrence is retained');
  metrics.mark('app.id/private-value'); metrics.mark('__proto__');
  assert.deepEqual(Object.keys(metrics.snapshot()).sort(), ['appStart', 'firstJS']);
  const snapshot = metrics.snapshot(); snapshot.appStart = -1; snapshot.private = 'inventory';
  assert.equal(metrics.snapshot().appStart, 35, 'snapshot cannot mutate retained values');
  assert.equal(metrics.snapshot().private, undefined);
  metrics.paintProxy(); metrics.paintProxy(); assert.equal(h.count(), 1, 'one bounded proxy schedule');
  h.frame(); assert.equal(metrics.snapshot().firstPaintProxy, undefined);
  h.advance(175); h.frame(); assert.equal(metrics.snapshot().firstPaintProxy, 75);
  assert.equal(h.count(), 0);
  for (let i = 0; i < 10000; i++) metrics.mark('unknown' + i);
  assert.equal(Object.keys(metrics.snapshot()).length, 3, 'unrecognized names cannot grow the record');
  vm.runInNewContext(source, h.context);
  assert.deepEqual(Object.keys(h.root.HomeStartup.snapshot()), ['firstJS'], 'a new document starts a new sample');
}
const i18n = fs.readFileSync('launcher/i18n.js', 'utf8');
for (const reply of [true, false]) {
  let bridge, timeout, now = 100;
  const root = {performance: {now: () => now}, navigator: {language: 'en'}, localStorage: {getItem: () => null},
    setTimeout(callback) { timeout = callback; }, clearTimeout() {}, PalmServiceBridge: function () {
      bridge = this; this.call = function () {}; this.cancel = function () {};
    }};
  root.window = root;
  vm.runInNewContext(source, root);
  vm.runInNewContext(i18n, root);
  let ready = false; root.HomeI18n.ready(() => { ready = true; });
  assert.equal(ready, false);
  now = 150;
  if (reply) bridge.onservicecallback('{"returnValue":false}'); else timeout();
  assert.equal(ready, true);
  assert.equal(root.HomeStartup.snapshot().languageReady, 50);
  assert.equal(root.HomeStartup.snapshot().languageReply, reply ? 50 : undefined,
    'service timeout is readiness fallback, not a service reply');
}
console.log('PASS bounded local startup metrics, clock/frame fallbacks, language reply versus timeout');
