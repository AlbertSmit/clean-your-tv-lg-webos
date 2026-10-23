(function () {
  'use strict';
  var data = window.RootProfileData, failed = false, booted = false;
  var marker = 'tvhome.root.restored.v1';
  function recovery(error) {
    failed = true;
    window.RootUpdates.open({recovery:true, error:'Launcher profile could not be restored. ' + error.message});
  }
  function save(profile) {
    profile = data.validate(profile);
    var raw = JSON.stringify(profile);
    localStorage.setItem(data.key, raw);
    if (localStorage.getItem(data.key) !== raw) throw Error('Local profile readback failed');
    return profile;
  }
  function icon(url) {
    if (typeof url === 'string' && /^data:image\/(png|jpeg|webp);base64,/.test(url)) return Promise.resolve(url);
    return new Promise(function (resolve, reject) {
      if (typeof url !== 'string' || !url || url.indexOf('..') >= 0 || /[?#\\]/.test(url) || /^([a-z]+:|\/)/i.test(url)) return reject(Error('Only packaged icons can be preserved'));
      var xhr = new XMLHttpRequest(); xhr.open('GET', url, true); xhr.responseType = 'blob'; xhr.timeout = 5000;
      xhr.onload = function () {
        if ((xhr.status !== 0 && xhr.status !== 200) || !xhr.response || xhr.response.size > 256 * 1024) return reject(Error('Packaged icon is missing or too large'));
        var reader = new FileReader(); reader.onload = function () { resolve(reader.result); }; reader.onerror = function () { reject(Error('Could not read icon')); }; reader.readAsDataURL(xhr.response);
      };
      xhr.onerror = xhr.ontimeout = function () { reject(Error('Could not read packaged icon')); }; xhr.send();
    });
  }
  window.RootProfile = {capture:function () {
    if (failed) return Promise.reject(Error('Stored profile is unreadable. Open Recovery.'));
    return Promise.resolve().then(function () {
      var snapshot = {schema:1, inventory:JSON.parse(JSON.stringify(window.TV_APPS)), config:JSON.parse(JSON.stringify(window.CONFIG)), settings:{}};
      var order = localStorage.getItem('tvhome.order'); if (order !== null) snapshot.settings['tvhome.order'] = order;
      return Promise.all(snapshot.inventory.apps.map(function (app) { return icon(app.icon).then(function (embedded) { app.icon = embedded; }); })).then(function () { return save(snapshot); });
    });
  }};
  function boot(restored) {
    if (booted) return; booted = true;
    window.RootLauncherRendered = false;
    var script = document.createElement('script'); script.src = 'app.js';
    script.onerror = function () { recovery(Error('Launcher could not start')); };
    script.onload = function () {
      if (!restored || ['verifying', 'verifying-rollback'].indexOf(restored.phase) < 0) return;
      try {
        if (window.RootLauncherRendered !== true) throw Error('Launcher did not finish rendering');
        var expected = window.TV_APPS.apps.filter(function (a) { return window.CONFIG.hiddenApps.indexOf(a.id) < 0; }).map(function (a) { return a.id; }).sort();
        var actual = Array.prototype.map.call(document.querySelectorAll('#tiles .item'), function (el) { return el.getAttribute('data-app-id'); }).sort();
        if (JSON.stringify(expected) !== JSON.stringify(actual)) throw Error('Restored launcher tiles do not match the saved profile');
        var health = {transaction:restored.transaction, version:window.ROOT_VERSION};
        window.RootUpdates.rpc('ready', health).then(function () {
          if (restored.phase === 'verifying') window.RootUpdates.confirmLaunch(health);
          else window.RootUpdates.open();
        }).catch(recovery);
      } catch (error) { recovery(error); }
    };
    document.body.appendChild(script);
  }
  var saved = null, localError = null;
  try { var raw = localStorage.getItem(data.key); if (raw !== null) saved = data.validate(JSON.parse(raw)); } catch (error) { localError = error; }
  window.RootUpdates.rpc('restoreProfile', {}).then(function (restored) {
    if (restored) {
      if (!restored.transaction || restored.version !== window.ROOT_VERSION) throw Error('Backup version does not match this Root package');
      var identity = restored.transaction + ':' + restored.version;
      var profile = data.validate(restored.profile);
      var alreadyRestored = saved && !localError && (restored.phase === 'aborted' || localStorage.getItem(marker) === identity);
      if (alreadyRestored) profile = saved;
      else {
        save(profile);
        if (profile.settings['tvhome.order'] === undefined) localStorage.removeItem('tvhome.order');
        else localStorage.setItem('tvhome.order', profile.settings['tvhome.order']);
        localStorage.setItem(marker, identity);
      }
      window.TV_APPS = profile.inventory; window.CONFIG = profile.config;
    } else {
      if (localError) throw localError;
      if (saved) { window.TV_APPS = saved.inventory; window.CONFIG = saved.config; }
    }
    boot(restored);
  }).catch(function (error) {
    // Existing personalized packages remain usable before one-time updater provisioning.
    // An empty generic package cannot establish that a missing backup is harmless.
    if (!localError && !booted && error.unavailable === true && (saved || (window.TV_APPS && window.TV_APPS.apps.length))) {
      if (saved) { window.TV_APPS = saved.inventory; window.CONFIG = saved.config; }
      boot(null);
    } else recovery(error);
  });
}());
