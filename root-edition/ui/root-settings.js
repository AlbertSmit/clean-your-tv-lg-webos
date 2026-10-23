(function () {
  'use strict';
  var panel, message, buttons, selected = 0, busy = false, confirmExit = false, previous;
  function request(uri, payload, timeout) {
    return new Promise(function (resolve, reject) {
      var bridge, timer, done = false;
      function finish(error, reply) {
        if (done) return;
        done = true; clearTimeout(timer);
        if (bridge) try { bridge.cancel(); } catch (_) {}
        if (error) reject(error); else resolve(reply);
      }
      timer = setTimeout(function () { finish(new Error('Response timed out. Check status before retrying.')); }, timeout);
      try {
        bridge = new PalmServiceBridge();
        bridge.onservicecallback = function (raw) {
          try { finish(null, JSON.parse(raw)); } catch (_) { finish(new Error('Invalid service response')); }
        };
        bridge.call(uri, JSON.stringify(payload));
      } catch (error) { finish(error); }
    });
  }
  function launch(id) {
    return request('luna://com.webos.applicationManager/launch', {id:id}, 10000).then(function (r) {
      if (r.returnValue !== true) throw new Error('Home restored, but screen could not open. Press Home.');
    });
  }
  var exit = createRootExit(function (method) {
    return request('luna://com.cleanyourtv.root.preview.service/' + method, {}, method === 'restore' ? 620000 : 15000);
  }, function () { return launch('com.webos.app.home'); });
  function focus(index) {
    selected = (index + buttons.length) % buttons.length;
    buttons[selected].focus();
  }
  function close() {
    if (busy) return;
    panel.hidden = true; confirmExit = false;
    if (previous && previous.focus) previous.focus();
  }
  function activate(index) {
    if (busy) return;
    if (index === 2) return close();
    if (index === 0) { launch('com.palm.app.settings').catch(function (e) { message.textContent = e.message; }); return; }
    if (!confirmExit) {
      confirmExit = true;
      message.textContent = 'Restore LG Home? The old Home helper stays off. Select Confirm exit to continue, or Back to cancel.';
      buttons[1].textContent = 'Confirm exit'; focus(1); return;
    }
    busy = true; buttons.forEach(function (b) { b.disabled = true; });
    message.textContent = 'Restoring original Home… Keep the TV powered on.';
    exit().then(function () { busy = false; close(); }).catch(function (e) {
      busy = false; confirmExit = false; buttons[1].textContent = 'Exit Root mode'; message.textContent = e.message;
    }).finally(function () { buttons.forEach(function (b) { b.disabled = false; }); if (!panel.hidden) focus(1); });
  }
  function build() {
    panel = document.createElement('section'); panel.className = 'root-settings'; panel.hidden = true;
    panel.setAttribute('role','dialog'); panel.setAttribute('aria-modal','true'); panel.setAttribute('aria-label','Root Edition settings');
    var card = document.createElement('div'); card.className = 'root-settings-card'; panel.appendChild(card);
    var title = document.createElement('h1'); title.textContent = 'Root Edition'; card.appendChild(title);
    message = document.createElement('p'); message.setAttribute('aria-live','polite'); card.appendChild(message);
    buttons = ['TV settings','Exit Root mode','Back'].map(function (label, i) {
      var b = document.createElement('button'); b.textContent = label; b.onclick = function () { activate(i); }; card.appendChild(b); return b;
    });
    document.body.appendChild(panel);
    document.addEventListener('keydown', function (e) {
      if (panel.hidden) return;
      if ([13,27,37,38,39,40,461].indexOf(e.keyCode) === -1) return;
      e.preventDefault(); e.stopImmediatePropagation();
      if (busy) return;
      if (e.keyCode === 461 || e.keyCode === 27) return close();
      if (e.keyCode === 13) return activate(selected);
      focus(selected + (e.keyCode === 37 || e.keyCode === 38 ? -1 : 1));
    }, true);
  }
  window.RenewalPanel = {
    isOpen: function () { return !!panel && !panel.hidden; },
    open: function () {
      if (!panel) build();
      if (!panel.hidden) return;
      previous = document.activeElement; confirmExit = false;
      message.textContent = 'Exit restores the original LG Home. It does not remove root or uninstall apps.';
      buttons[1].textContent = 'Exit Root mode'; panel.hidden = false; focus(0);
    }
  };
}());
