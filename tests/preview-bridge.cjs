const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const context = {window: {TV_APPS: {apps: []}}, document: {getElementById: () => null}, setTimeout, clearTimeout};
vm.createContext(context);
vm.runInContext(fs.readFileSync('preview/bridge.js', 'utf8'), context);
function call(method, payload = {}) {
  return new Promise(resolve => {
    const bridge = new context.window.PalmServiceBridge();
    bridge.onservicecallback = raw => resolve(JSON.parse(raw));
    bridge.call('luna://com.cleanyourtv.root.preview.service/' + method, JSON.stringify(payload));
  });
}
(async () => {
  let reply = await call('status');
  assert.equal(reply.result.result.intent.phase, 'disabled');
  await call('enable');
  reply = await call('status');
  assert.equal(reply.result.result.intent.phase, 'trial');
  const transaction = reply.result.result.journal.transaction;
  assert.equal((await call('confirm', {transaction: 'wrong'})).returnValue, false);
  assert.equal((await call('confirm', {transaction})).returnValue, true);
  assert.equal((await call('status')).result.result.intent.phase, 'active');
  assert.equal((await call('restore')).result.result, 'restored');
  reply = await call('status');
  assert.equal(reply.result.result.intent.phase, 'disabled');
  assert.equal(reply.result.result.effective.sam_home, 'com.webos.app.home');
  assert.equal(reply.result.result.effective.profiles.defaultApps.categories.home, 'com.webos.app.home');
  assert.equal(reply.result.result.effective.profiles.idleApp.appId, 'com.webos.app.home');
  async function updater(method) {
    return new Promise(resolve => {
      const bridge = new context.window.PalmServiceBridge();
      bridge.onservicecallback = raw => resolve(JSON.parse(raw));
      bridge.call('luna://com.cleanyourtv.root.updater.service/' + method, '{}');
    });
  }
  context.window.ROOT_VERSION = '0.1.1';
  reply = await updater('restoreProfile');
  assert.equal(reply.returnValue, true);
  assert.equal(reply.result, null, 'Demo profile bootstrap must proceed without a real updater');
  reply = await updater('check');
  assert.equal(reply.result.installed.version, '0.1.1');
  assert.equal(reply.result.canInstall, false);
  assert.equal(reply.result.reason, 'current');
  assert.equal((await updater('status')).result, null);
  assert.equal((await updater('install')).returnValue, false, 'Browser preview cannot install packages');
  console.log('PASS browser Root demo trial, confirmation and restore');
})().catch(error => { console.error(error); process.exit(1); });
