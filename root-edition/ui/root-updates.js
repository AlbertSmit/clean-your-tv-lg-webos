(window.HomeI18n && window.HomeI18n.ready ? window.HomeI18n.ready : function (callback) { callback(); })(function () {
(function () {
  'use strict';
  function t(source, params) { if (window.HomeI18n) return window.HomeI18n.t(source, params); return String(source).replace(/\{(\w+)\}/g, function (_, key) { return params && params[key] !== undefined ? params[key] : '{' + key + '}'; }); }
  var panel, title, message, details, buttons, previous, selected = 0, timer, onClose;
  var busy = false, recovery = false, offer = null, transaction = null, health = null, errorText = '';
  var recoveryParent = false;
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
  function back() {
    if (recoveryParent) {
      recovery = false; recoveryParent = false;
      selected = enabled().indexOf(buttons[3]); render();
      focus(enabled().indexOf(buttons[3])); return;
    }
    close();
  }
  function rollbackAllowed() {
    return !!(transaction && transaction.phase === 'recovery-required' && transaction.installEvidence && transaction.installEvidence.terminal && !transaction.rollbackAttempted);
  }
  function currentOrNewer(candidate, installed) {
    var a = String(candidate).split('.'), b = String(installed).split('.');
    if (a.length !== 3 || b.length !== 3) return false;
    for (var i = 0; i < 3; i++) {
      if (!/^\d+$/.test(a[i]) || !/^\d+$/.test(b[i])) return false;
    }
    for (var j = 0; j < 3; j++) {
      if (Number(a[j]) !== Number(b[j])) return Number(a[j]) > Number(b[j]);
    }
    return true;
  }
  function show(index, visible, disabled) { buttons[index].hidden = !visible; buttons[index].disabled = !!disabled; }
  function render() {
    var phase = transaction && transaction.phase;
    title.textContent = t(recovery ? 'Recovery' : 'Software updates');
    panel.setAttribute('aria-label', title.textContent);
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
    message.textContent = t(errorText || descriptions[phase] || (recovery ? 'Inspect the independent updater and recover a previous transaction.' : busy ? 'Checking for updates…' : offer && offer.canInstall ? 'A new version of Home is available.' : 'Your apps and settings stay saved.'));
    if (transaction && transaction.error) message.textContent += ' ' + transaction.error;
    var installed = offer && offer.installed;
    details.textContent = t('Installed: {version}', {version:installed && installed.version || installed || window.ROOT_VERSION || t('unknown')});
    if (!recovery && offer && offer.candidate && currentOrNewer(offer.candidate.version, installed && installed.version || installed || window.ROOT_VERSION)) details.textContent += '\n' + t('Available: {version}', {version:offer.candidate.version}) + '\n' + (offer.candidate.notes || '');
    if (!recovery && offer && !offer.canInstall && offer.reason) {
      var reasons = {current:'This Root version is up to date.', 'missing-rollback':'A verified recovery package for this version is missing. Run the one-time computer setup.'};
      details.textContent += '\n' + t(reasons[offer.reason] || 'This release cannot be installed with the current setup.');
    }
    if (recovery) {
      details.textContent = '';
      if (transaction && transaction.prior) details.textContent = t('Rollback version: {version}', {version:transaction.prior.version});
      if (!transaction || phase === 'aborted') details.textContent += '\n' + t('No saved update is available to roll back.');
      else if (phase === 'complete') details.textContent += '\n' + t('This update is already confirmed. Rollback is no longer available.');
      else if (phase === 'rolled-back') details.textContent += '\n' + t('The previous version has already been restored.');
      else if (!rollbackAllowed()) details.textContent += '\n' + t('Rollback is blocked until the installer has definitely stopped. Refresh status to check.');
      else details.textContent += '\n' + t('The previous Home version and saved settings will be restored.');
    }
    buttons[3].textContent = t(recovery ? 'Refresh status' : 'Recovery');
    show(0, !recovery && !health && !!errorText, busy || active());
    show(1, !recovery && !health, busy || active() || !offer || !offer.canInstall);
    show(2, false);
    show(3, true, busy);
    show(4, recovery && rollbackAllowed(), busy);
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
    if (index === 7) return back();
    if (busy) return;
    if (index === 0) return refresh(true);
    if (index === 1) return window.HomeI18n.confirm({title:'Install Home update?',message:t('Install Root {version}? LG Home will be selected during installation. Keep the TV powered on; confirm the updated launcher within two minutes.', {version:offer.candidate.version}),action:'Install update'}, function () {
      if (busy || panel.hidden || recovery || active() || !offer || !offer.canInstall || !window.RootProfile) return;
      busy = true; render();
      window.RootProfile.capture().then(function (profile) { return rpc('install', {version:offer.candidate.version, profile:profile}); }).then(function (state) { transaction = state; }).catch(function (error) { errorText = error.message; }).then(function () { busy = false; render(); schedule(); }); return;
    });
    if (index === 3) {
      if (!recovery) { recovery = true; recoveryParent = true; selected = 0; errorText = ''; render(); return refresh(false); }
      return operation('reconcile', {});
    }
    if (index === 4) return window.HomeI18n.confirm({title:'Restore previous Home?',message:t('Restore Home {version} and the saved settings? Keep the TV powered on.', {version:transaction.prior && transaction.prior.version || t('unknown')}),action:'Restore previous Home'}, function () { if (!buttons[4].hidden && !buttons[4].disabled) operation('rollback', {}); });
    if (index === 5 && health) return operation('confirm', health);
    if (index === 6) { close(); if (window.RenewalPanel) window.RenewalPanel.open(); }
  }
  function build() {
    panel = document.createElement('section'); panel.className = 'root-settings root-updates'; panel.hidden = true;
    panel.setAttribute('role', 'dialog'); panel.setAttribute('aria-modal', 'true'); panel.setAttribute('aria-label', t('Root Software updates'));
    var card = document.createElement('div'); card.className = 'root-settings-card'; panel.appendChild(card);
    title = document.createElement('h1'); title.textContent = t('Software updates'); card.appendChild(title);
    message = document.createElement('p'); message.setAttribute('aria-live', 'polite'); card.appendChild(message);
    details = document.createElement('p'); details.className = 'root-update-details'; card.appendChild(details);
    buttons = ['Try again', 'Update', 'Install update', 'Recovery', 'Roll back', 'Confirm working update', 'Root mode settings', 'Back'].map(function (label, index) {
      var button = document.createElement('button'); button.textContent = t(label); button.onclick = function () { activate(index); }; card.appendChild(button); return button;
    });
    document.body.appendChild(panel);
    document.addEventListener('keydown', function (event) {
      if (panel.hidden || [9,13,27,37,38,39,40,461].indexOf(event.keyCode) < 0) return;
      event.preventDefault(); event.stopImmediatePropagation();
      if (event.keyCode === 27 || event.keyCode === 461) return back();
      var list = enabled(); if (!list.length) return;
      if (event.keyCode === 13) return list[selected % list.length].onclick();
      focus(selected + (event.keyCode === 37 || event.keyCode === 38 || (event.keyCode === 9 && event.shiftKey) ? -1 : 1));
    }, true);
  }
  function open(options) {
    options = options || {}; if (!panel) build();
    if (panel.hidden) previous = document.activeElement;
    onClose = options.onClose || null;
    recovery = options.recovery === true; recoveryParent = false; selected = 0; errorText = options.error || ''; panel.hidden = false; render();
    if (!options.error) refresh(!recovery);
  }
  window.RootUpdates = {rpc:rpc, open:open, isOpen:function () { return !!panel && !panel.hidden; }, confirmLaunch:function (identity) { health = identity; open(); }};
}());

});
