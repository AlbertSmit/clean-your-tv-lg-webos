/* Browser-only webOS simulation. Injected by scripts/preview.py, never packaged. */
(function () {
  'use strict';
  var homeEnabled = true;
  var enabled = false, rootPhase = 'disabled';
  var firmwareBlocked = false;
  var rootTransaction = 'preview-root-activation';
  var toastTimer;
  function message(text) {
    var toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = 'Preview · ' + text;
    toast.classList.add('shown');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () { toast.classList.remove('shown'); }, 2400);
  }
  window.PalmServiceBridge = function () { this.timer = null; };
  window.PalmServiceBridge.prototype.cancel = function () { clearTimeout(this.timer); };
  window.PalmServiceBridge.prototype.call = function (uri, raw) {
    var bridge = this, payload = JSON.parse(raw || '{}');
    bridge.timer = setTimeout(function () {
      var result = {returnValue: false, errorText: 'Unavailable in browser preview'};
      if (uri === 'luna://org.webosbrew.hbchannel.service/getConfiguration') {
        result = {returnValue:true, root:true, blockUpdates:firmwareBlocked};
      } else if (uri === 'luna://org.webosbrew.hbchannel.service/setConfiguration') {
        if (Object.keys(payload).length === 1 && typeof payload.blockUpdates === 'boolean') {
          firmwareBlocked = payload.blockUpdates;
          result = {returnValue:true, blockUpdates:firmwareBlocked};
        }
      } else if (uri.indexOf('luna://com.cleanyourtv.system.updater.service/') === 0) {
        var systemMethod = uri.split('/').pop();
        if (systemMethod === 'restoreProfile' || systemMethod === 'status') result = {returnValue:true,result:null};
        else if (systemMethod === 'check') {
          var rootEdition = payload.edition === 'root';
          var names = rootEdition ? ['root','root-updater','root-infrastructure'] : ['home','helper','updater'];
          result = {returnValue:true,result:{edition:payload.edition,release:'v1.0.3',canInstall:false,
            reason:'Browser preview: no real updates are checked or installed.',notes:'Browser preview: no real updates are checked or installed.',
            components:names.map(function (name) { var version = name === 'home' ? '1.3.8' : name === 'helper' ? '0.6.18' : name === 'updater' || name === 'root-updater' ? '0.1.6' : window.ROOT_VERSION || '0.0.1'; return {name:name,installed:version,version:version}; })}};
        }
      } else if (uri === 'luna://com.webos.applicationManager/launch') {
        if (payload.id !== 'com.local.nativehome') {
          var app = (window.TV_APPS.apps || []).filter(function (a) { return a.id === payload.id; })[0];
          message(app ? app.title : payload.id === 'com.webos.app.firstuse-overlay' ? 'Network settings' : payload.id === 'com.palm.app.settings' ? 'TV settings' : payload.id);
        }
        result = {returnValue: true};
      } else if (uri.indexOf('luna://com.gathin.tvhome.renewal/') === 0 && ['homeStatus','setHomeControl','openLGHome'].indexOf(uri.split('/').pop()) >= 0) {
        var homeMethod=uri.split('/').pop();
        if(homeMethod==='setHomeControl')homeEnabled=payload.enabled;
        if(homeMethod==='openLGHome')message('LG Home · settings kept');
        if(['homeStatus','setHomeControl','openLGHome'].indexOf(homeMethod)>=0)result={returnValue:true,enabled:homeEnabled};
      } else if (uri === 'luna://com.local.nativehome.service/listApps' || uri === 'luna://com.cleanyourtv.root.preview.service/listApps') {
        result = {returnValue:true, apps:(window.TV_APPS.apps || []).concat([{id:'preview.gallery', title:'Photo & Video', icon:'../preview/icons/browser.svg'}])};
      } else if (uri === 'luna://com.palm.connectionmanager/getStatus') {
        result = {returnValue: true, isInternetConnectionAvailable: true, wifi: {state: 'connected', ssid: 'Demo Wi-Fi'}};
      } else if (uri === 'luna://com.webos.service.bus/signal/registerServerStatus') {
        result = {returnValue: true, connected: true};
      } else if (uri.indexOf('luna://com.cleanyourtv.root.preview.service/') === 0) {
        var rootMethod = uri.split('/').pop();
        if (rootMethod === 'enable') {
          rootPhase = 'active';
        } else if (rootMethod === 'restore') {
          rootPhase = 'disabled';
        }
        if (['status', 'enable', 'restore'].indexOf(rootMethod) >= 0) {
          var home = rootPhase === 'disabled' ? 'com.webos.app.home' : 'com.cleanyourtv.root.preview';
          var state = {intent: {phase: rootPhase}, journal: {transaction: rootTransaction},
            effective: {sam_home: home, profiles: {defaultApps: {categories: {home: home}}, idleApp: {appId: home}}}};
          result = {returnValue: true, result: {returnValue: true, result: rootMethod === 'restore' ? 'restored' : state}};
        }
      } else if (uri.indexOf('luna://com.cleanyourtv.root.updater.service/') === 0) {
        var updaterMethod = uri.split('/').pop();
        if (updaterMethod === 'restoreProfile' || updaterMethod === 'status') {
          result = {returnValue: true, result: null};
        } else if (updaterMethod === 'check') {
          var version = window.ROOT_VERSION || '0.0.1';
          result = {returnValue: true, result: {installed: {version: version}, canInstall: false,
            reason: 'current', candidate: {version: version,
              notes: 'Browser preview: no real updates are checked or installed.'}}};
        }
      } else if (uri.indexOf('luna://com.gathin.tvhome.renewal/') === 0) {
        var method = uri.split('/').pop();
        if (['status', 'enable', 'disable', 'check'].indexOf(method) >= 0) {
          if (method === 'enable') enabled = true;
          if (method === 'disable') enabled = false;
          result = {returnValue: true, state: {enabled: enabled, last: {status: 'healthy', remainingSeconds: 864000, checkedAt: Date.now()}}};
        }
      } else if (uri === 'luna://com.cleanyourtv.updater.service/check') {
        result = {returnValue: true, result: {home: '1.2.2', state: 'current', canInstall: false,
          candidate: {home: '1.2.2', notes: 'Browser preview: no real updates are checked or installed.'}}};
      } else if (uri === 'luna://com.cleanyourtv.updater.service/healthy') {
        result = {returnValue: true};
      }
      if (bridge.onservicecallback) bridge.onservicecallback(JSON.stringify(result));
    }, 30);
  };
  // Fake widget data for the browser preview (no Home Assistant on the LAN).
  window.WidgetPreview = {
    refresh: function (cfg, cb) {
      setTimeout(function () {
        cb({
          source: 'preview',
          nowPlaying: {
            playing: true,
            title: 'Midnight City',
            artist: 'M83',
            album: 'Hurry Up, We’re Dreaming',
            source: 'Apple TV · AirPlay',
            // Original sample cover, kept inline so the preview needs no network.
            artwork: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(
              '<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600" viewBox="0 0 600 600">' +
              '<defs><linearGradient id="sky" x2="0" y2="1"><stop stop-color="#101d47"/>' +
              '<stop offset=".6" stop-color="#756291"/><stop offset="1" stop-color="#ecb19b"/></linearGradient>' +
              '<linearGradient id="water" x2="0" y2="1"><stop stop-color="#d59aa1"/><stop offset="1" stop-color="#182d4d"/></linearGradient></defs>' +
              '<path fill="url(#sky)" d="M0 0h600v600H0z"/><circle cx="415" cy="170" r="64" fill="#f6decd"/>' +
              '<path fill="#24354e" d="M0 330h55v-85h40v85h50V190h30v140h45v-58h35v58h30V155h36v175h45v-90h50v90h40v-50h55v50h54V216h35v114h50v270H0z"/>' +
              '<path fill="url(#water)" d="M0 372h600v228H0z"/>' +
              '<path stroke="#f8c5b0" opacity=".5" stroke-width="3" d="M340 401h150m-175 22h205m-245 24h200m-145 26h165m-195 29h210m-160 32h180"/>' +
              '<text x="36" y="64" fill="#f7ede9" font-family="sans-serif" font-size="26" letter-spacing="7">MIDNIGHT CITY</text></svg>')
          },
          weather: {
            condition: 'partlycloudy',
            temp: 21,
            unit: '°C',
            high: 24,
            low: 12,
            humidity: 45,
            source: 'Home'
          }
        });
      }, 80);
    }
  };
}());
