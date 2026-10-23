(function () {
  'use strict';
  var panel, message, details, buttons, previous, selected = 0, timer, onClose;
  var busy = false, recovery = false, offer = null, transaction = null, health = null, installing = false, errorText = '';
  var terminal = ['complete', 'rolled-back', 'aborted'];
  function unprovisioned() {
    var error = Error('Updater unavailable. Run the one-time computer setup for Software updates.');
    error.unavailable = true; return error;
  }
  function rpc(method, payload) {
    return new Promise(function (resolve, reject) {
      var bridge, done = false, timeout;
      function finish(error, result) {
        if (done) return; done = true; clearTimeout(timeout);
        if (bridge) try { bridge.cancel(); } catch (_) {}
        if (error) reject(error); else resolve(result);
      }
      timeout = setTimeout(function () { finish(Error('Updater response timed out. Open Recovery to check status.')); }, 110000);
      try {
        bridge = new PalmServiceBridge();
        bridge.onservicecallback = function (raw) {
          try {
            var reply = JSON.parse(raw);
            if (reply.returnValue !== true) return finish(/does not exist|not found|unknown service|not registered/i.test(reply.errorText || '') ? unprovisioned() : Error(reply.errorText || 'Updater operation failed. Open Recovery.'));
            finish(null, reply.result);
          } catch (_) { finish(Error('Invalid updater response. Open Recovery.')); }
        };
        bridge.call('luna://com.cleanyourtv.root.updater.service/' + method, JSON.stringify(payload || {}));
      } catch (_) { finish(unprovisioned()); }
    });
  }
  function active() { return transaction && terminal.indexOf(transaction.phase) < 0; }
  function enabled() { return buttons.filter(function (b) { return !b.hidden && !b.disabled; }); }
  function focus(index) {
    var list = enabled(); if (!list.length) return;
    selected = (index + list.length) % list.length; list[selected].focus();
  }
  function close() {
    clearTimeout(timer); panel.hidden = true;
    if (onClose) { var callback = onClose; onClose = null; callback(); }
    else if (previous && previous.focus) previous.focus();
  }
  function show(index, visible, disabled) { buttons[index].hidden = !visible; buttons[index].disabled = !!disabled; }
  function render() {
    var phase = transaction && transaction.phase;
    var descriptions = {
      preparing:'Preparing update and preserving your launcher profile…',
      downloading:'Downloading and verifying both update and rollback packages…',
      'backed-up':'Profile and rollback package verified.',
      'restoring-route':'Restoring LG Home before installation…',
      installing:'Installing Root update. Keep the TV powered on.',
      'awaiting-launch':'Opening the updated Root launcher…',
      verifying:'Test your launcher and remote, then confirm within two minutes. Without confirmation the previous version will be restored.',
      complete:'Update complete. Your launcher profile is preserved. Root mode can be enabled again through its protected trial.',
      'rolling-back':'Restoring the previous Root package and saved profile…',
      'verifying-rollback':'Checking the restored Root launcher and saved profile…',
      'rolled-back':'Previous Root version and profile restored. LG Home remains selected.',
      'recovery-required':'Recovery required. LG Home remains selected. Recover status first; rollback stays blocked until the installer has definitely stopped.',
      aborted:'Update stopped before replacement. Check status before trying again.'
    };
    message.textContent = errorText || descriptions[phase] || (recovery ? 'Inspect the independent updater and recover a previous transaction.' : 'Check for a signed Root release. Your apps, inputs, settings and tile order will be preserved.');
    if (transaction && transaction.error) message.textContent += ' ' + transaction.error;
    var installed = offer && offer.installed;
    details.textContent = 'Installed: ' + (installed && installed.version || installed || window.ROOT_VERSION || 'unknown');
    if (offer && offer.candidate) details.textContent += '\nAvailable: ' + offer.candidate.version + '\n' + (offer.candidate.notes || '');
    if (offer && !offer.canInstall && offer.reason) details.textContent += '\n' + offer.reason;
    show(0, !recovery && !health, busy || active());
    show(1, !recovery && !health && !installing, busy || active() || !offer || !offer.canInstall);
    show(2, !recovery && installing, busy || active());
    show(3, true, busy);
    show(4, !!(transaction && transaction.phase === 'recovery-required' && transaction.installEvidence && transaction.installEvidence.terminal && !transaction.rollbackAttempted), busy);
    show(5, !!health, busy);
    show(6, !recovery && !!(transaction && (phase === 'complete' || phase === 'rolled-back') && transaction.oldRoute && transaction.oldRoute.active), busy);
    show(7, true, false);
    if (!panel.hidden) focus(selected);
  }
  function schedule() {
    clearTimeout(timer);
    if (!panel.hidden && (active() || health)) timer = setTimeout(function () { refresh(false); }, 1500);
  }
  function refresh(check) {
    if (busy) return Promise.resolve();
    busy = true; render();
    return rpc('status', {}).then(function (state) {
      transaction = state;
      if (transaction && terminal.indexOf(transaction.phase) >= 0) health = null;
      if (check && !recovery) return rpc('check', {}).then(function (value) { offer = value; });
    }).then(function () { if (check || transaction && terminal.indexOf(transaction.phase) >= 0) errorText = ''; }).catch(function (error) { errorText = error.message; }).then(function () { busy = false; render(); schedule(); });
  }
  function operation(method, payload) {
    if (busy) return;
    busy = true; errorText = ''; render();
    rpc(method, payload).then(function (state) {
      if (method === 'confirm') health = null;
      if (state && state.phase) transaction = state;
    }).catch(function (error) { errorText = error.message; }).then(function () { busy = false; render(); return refresh(false); });
  }
  function activate(index) {
    if (buttons[index].hidden || buttons[index].disabled) return;
    if (index === 7) return close();
    if (busy) return;
    if (index === 0) return refresh(true);
    if (index === 1) { installing = true; message.textContent = 'Install Root ' + offer.candidate.version + '? LG Home will be selected during installation. Keep the TV powered on; confirm the updated launcher within two minutes.'; show(1, false); show(2, true); focus(0); return; }
    if (index === 2) {
      if (recovery || active() || !offer || !offer.canInstall || !window.RootProfile) return;
      busy = true; render();
      window.RootProfile.capture().then(function (profile) { return rpc('install', {version:offer.candidate.version, profile:profile}); }).then(function (state) { transaction = state; }).catch(function (error) { errorText = error.message; }).then(function () { busy = false; render(); schedule(); }); return;
    }
    if (index === 3) return operation('reconcile', {});
    if (index === 4) return operation('rollback', {});
    if (index === 5 && health) return operation('confirm', health);
    if (index === 6) { close(); if (window.RenewalPanel) window.RenewalPanel.open(); }
  }
  function build() {
    panel = document.createElement('section'); panel.className = 'root-settings root-updates'; panel.hidden = true;
    panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'true'); panel.setAttribute('aria-label', 'Root Software updates');
    var card = document.createElement('div'); card.className = 'root-settings-card'; panel.appendChild(card);
    var title = document.createElement('h1'); title.textContent = 'Software updates'; card.appendChild(title);
    message = document.createElement('p'); message.setAttribute('aria-live', 'polite'); card.appendChild(message);
    details = document.createElement('p'); details.className = 'root-update-details'; card.appendChild(details);
    buttons = ['Check for updates', 'Update', 'Install update', 'Recover status', 'Roll back', 'Confirm working update', 'Root mode settings', 'Back'].map(function (label, index) {
      var button = document.createElement('button'); button.textContent = label; button.onclick = function () { activate(index); }; card.appendChild(button); return button;
    });
    document.body.appendChild(panel);
    document.addEventListener('keydown', function (event) {
      if (panel.hidden || [9,13,27,37,38,39,40,461].indexOf(event.keyCode) < 0) return;
      event.preventDefault(); event.stopImmediatePropagation();
      if (event.keyCode === 27 || event.keyCode === 461) return close();
      var list = enabled(); if (!list.length) return;
      if (event.keyCode === 13) return list[selected % list.length].onclick();
      focus(selected + (event.keyCode === 37 || event.keyCode === 38 || (event.keyCode === 9 && event.shiftKey) ? -1 : 1));
    }, true);
  }
  function open(options) {
    options = options || {}; if (!panel) build();
    if (panel.hidden) previous = document.activeElement;
    onClose = options.onClose || null;
    recovery = options.recovery === true; installing = false; selected = 0; errorText = options.error || ''; panel.hidden = false; render();
    if (!options.error) refresh(!recovery);
  }
  window.RootUpdates = {rpc:rpc, open:open, isOpen:function () { return !!panel && !panel.hidden; }, confirmLaunch:function (identity) { health = identity; open(); }};
}());
