const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
let now = 0, timerId = 0;
const timers = new Map();
function advance(ms) {
  now += ms;
  for (const [id, timer] of timers) {
    if (timer.at <= now) { timers.delete(id); timer.fn(); }
  }
}
const context = {window: {TV_APPS: {apps: []}}, document: {getElementById: () => null},
  setTimeout: (fn, delay) => { const id = ++timerId; timers.set(id, {fn, at: now + delay}); return id; },
  clearTimeout: id => timers.delete(id)};
vm.createContext(context);
vm.runInContext(fs.readFileSync('preview/bridge.js', 'utf8'), context);
function call(method, payload = {}) {
  return new Promise(resolve => {
    const bridge = new context.window.PalmServiceBridge();
    bridge.onservicecallback = raw => resolve(JSON.parse(raw));
    bridge.call('luna://com.cleanyourtv.root.preview.service/' + method, JSON.stringify(payload));
    advance(30);
  });
}
(async () => {
  let reply = await call('status');
  assert.equal(reply.result.result.intent.phase, 'disabled');
  await call('enable');
  reply = await call('status');
  assert.equal(reply.result.result.intent.phase, 'active');
  advance(120000);
  assert.equal((await call('status')).result.result.intent.phase, 'active');
  assert.equal((await call('restore')).result.result, 'restored');
  reply = await call('status');
  assert.equal(reply.result.result.intent.phase, 'disabled');
  assert.equal(reply.result.result.effective.sam_home, 'com.webos.app.home');
  assert.equal(reply.result.result.effective.profiles.defaultApps.categories.home, 'com.webos.app.home');
  assert.equal(reply.result.result.effective.profiles.idleApp.appId, 'com.webos.app.home');
  console.log('PASS browser Root demo activation and restore');
})().catch(error => { console.error(error); process.exit(1); });
