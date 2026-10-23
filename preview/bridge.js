/* Browser-only webOS simulation. Injected by scripts/preview.py, never packaged. */
(function () {
  'use strict';
  var enabled = false;
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
      if (uri === 'luna://com.webos.applicationManager/launch') {
        if (payload.id !== 'com.local.nativehome') {
          var app = (window.TV_APPS.apps || []).filter(function (a) { return a.id === payload.id; })[0];
          message(app ? app.title : payload.id === 'com.webos.app.firstuse-overlay' ? 'Network settings' : payload.id === 'com.palm.app.settings' ? 'TV settings' : payload.id);
        }
        result = {returnValue: true};
      } else if (uri === 'luna://com.palm.connectionmanager/getStatus') {
        result = {returnValue: true, isInternetConnectionAvailable: true, wifi: {state: 'connected', ssid: 'Demo Wi-Fi'}};
      } else if (uri === 'luna://com.webos.service.bus/signal/registerServerStatus') {
        result = {returnValue: true, connected: true};
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
}());
