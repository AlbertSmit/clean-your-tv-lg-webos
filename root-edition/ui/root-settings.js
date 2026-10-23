(function () {
  'use strict';
  var panel, message, buttons, selected = 0, busy = false, confirmExit = false, previous, rootStatus = null;
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
  function control(method, payload) {
    return request('luna://com.cleanyourtv.root.preview.service/' + method, payload || {}, 30000).then(function (reply) {
      if (!reply || reply.returnValue !== true || !reply.result || reply.result.returnValue !== true)
        throw new Error(reply && reply.errorText || 'Root control did not confirm success. Check status before retrying.');
      return reply.result.result;
    });
  }
  function refreshMode() {
    rootStatus = null; buttons[3].disabled = true; buttons[3].textContent = 'Checking Home control…';
    return control('status').then(function (status) {
      rootStatus = status;
      var phase = status.intent && status.intent.phase;
      buttons[3].textContent = phase === 'active' ? 'Home control is on' : phase === 'trial' ? 'Keep using Home' : 'Try Home control';
      buttons[3].disabled = phase === 'active' || (phase && phase !== 'disabled' && phase !== 'trial');
      if (!panel.hidden && buttons[selected].disabled) move(1);
      if (confirmExit) return;
      if (phase === 'disabled' || !phase) message.textContent = 'Home control is off. Try it for one minute, then confirm to keep Home as your home screen.';
      if (phase === 'trial') message.textContent = 'Press Home and Back to test your remote. Select Keep using Home within one minute, or LG Home will return automatically.';
      if (phase === 'active') message.textContent = 'Home control is on and will stay on after restarting the TV. Return to LG Home below to turn it off.';
    }).catch(function (e) { message.textContent = e.message; });
  }
  function changeMode() {
    if (!rootStatus || buttons[3].disabled) return;
    var confirming = rootStatus.intent && rootStatus.intent.phase === 'trial';
    var payload = confirming ? {transaction:rootStatus.journal && rootStatus.journal.transaction} : {};
    busy = true; buttons.forEach(function (b) { b.disabled = true; });
    message.textContent = confirming ? 'Verifying input and recovery protection…' : 'Starting a one-minute trial… The previous Home Helper must be stopped first.';
    control(confirming ? 'confirm' : 'enable', payload).then(function () {
      busy = false; buttons.forEach(function (b) { b.disabled = false; });
      return refreshMode();
    }).catch(function (e) {
      busy = false; buttons.forEach(function (b) { b.disabled = false; });
      var error = e.message;
      refreshMode().then(function () { message.textContent = error; });
    });
  }
  var order = [3, 4, 0, 1, 2];
  function focus(index) {
    selected = index;
    if (!buttons[selected].disabled) buttons[selected].focus();
  }
  function move(direction) {
    var index = order.indexOf(selected);
    for (var count = 0; count < order.length; count++) {
      index = (index + direction + order.length) % order.length;
      if (!buttons[order[index]].disabled) return focus(order[index]);
    }
  }
  function close() {
    if (busy) return;
    panel.hidden = true; confirmExit = false;
    if (previous && previous.focus) previous.focus();
  }
  function activate(index) {
    if (busy || buttons[index].disabled) return;
    if (index === 2) return close();
    if (index === 3) return changeMode();
    if (index === 4) {
      confirmExit = false; buttons[1].textContent = 'Return to LG Home';
      if (!window.RootUpdates) { message.textContent = 'Software updates require the one-time computer setup.'; return; }
      panel.hidden = true;
      window.RootUpdates.open({onClose:function () { panel.hidden = false; focus(4); refreshMode(); }}); return;
    }
    if (index === 0) { launch('com.palm.app.settings').catch(function (e) { message.textContent = e.message; }); return; }
    if (!confirmExit) {
      confirmExit = true;
      message.textContent = 'Return to LG Home and turn off Home control? Your apps and settings will be kept. Select Confirm return, or press Back to cancel.';
      buttons[1].textContent = 'Confirm return'; focus(1); return;
    }
    busy = true; buttons.forEach(function (b) { b.disabled = true; });
    message.textContent = 'Restoring original Home… Keep the TV powered on.';
    exit().then(function () { busy = false; close(); }).catch(function (e) {
      busy = false; confirmExit = false; buttons[1].textContent = 'Return to LG Home'; message.textContent = e.message;
    }).finally(function () { buttons.forEach(function (b) { b.disabled = false; }); if (!panel.hidden) focus(1); });
  }
  function build() {
    panel = document.createElement('section'); panel.className = 'root-settings'; panel.hidden = true;
    panel.setAttribute('role','dialog'); panel.setAttribute('aria-modal','true'); panel.setAttribute('aria-label','Home settings');
    var card = document.createElement('div'); card.className = 'root-settings-card'; panel.appendChild(card);
    function text(parent, tag, value, className) {
      var element = document.createElement(tag); element.textContent = value;
      if (className) element.className = className;
      parent.appendChild(element); return element;
    }
    var heading = document.createElement('div'); heading.className = 'settings-heading'; card.appendChild(heading);
    text(heading, 'h1', 'Home settings'); text(heading, 'span', 'Root Edition', 'settings-edition');
    text(card, 'p', 'Manage Home, software updates and your TV.');
    var home = document.createElement('section'); home.className = 'settings-section'; card.appendChild(home);
    text(home, 'h2', 'Home control');
    text(home, 'p', 'Choose what opens when you press Home on your remote.');
    message = text(home, 'p', '', 'settings-status'); message.setAttribute('aria-live','polite');
    var homeActions = document.createElement('div'); homeActions.className = 'renewal-actions'; home.appendChild(homeActions);
    var more = document.createElement('section'); more.className = 'settings-section'; card.appendChild(more);
    text(more, 'h2', 'Updates and TV');
    text(more, 'p', 'Update Home or open LG settings for picture, sound and network.');
    var links = document.createElement('div'); links.className = 'renewal-actions settings-links'; more.appendChild(links);
    var leave = document.createElement('section'); leave.className = 'settings-section'; card.appendChild(leave);
    text(leave, 'h2', 'Return to LG Home');
    text(leave, 'p', 'Turn off Home control and restore the LG home screen. Your apps and settings are kept.');
    var leaveActions = document.createElement('div'); leaveActions.className = 'renewal-actions'; leave.appendChild(leaveActions);
    var footer = document.createElement('div'); footer.className = 'settings-footer'; card.appendChild(footer);
    text(footer, 'p', 'Emergency exit: press Home 3 times within 2 seconds.');
    var back = document.createElement('div'); back.className = 'renewal-actions'; footer.appendChild(back);
    buttons = [];
    order.forEach(function (i) {
      var labels = ['TV settings','Return to LG Home','Back to Home','Checking Home control…','Software updates'];
      var b = document.createElement('button'); b.textContent = labels[i];
      b.onclick = function () { selected = i; activate(i); };
      b.onfocus = function () { selected = i; };
      (i === 3 ? homeActions : i === 4 || i === 0 ? links : i === 1 ? leaveActions : back).appendChild(b);
      buttons[i] = b;
    });
    document.body.appendChild(panel);
    document.addEventListener('keydown', function (e) {
      if (panel.hidden) return;
      if ([9,13,27,37,38,39,40,461].indexOf(e.keyCode) === -1) return;
      e.preventDefault(); e.stopImmediatePropagation();
      if (busy) return;
      if (e.keyCode === 461 || e.keyCode === 27) return close();
      if (e.keyCode === 13) { if (!e.repeat) activate(selected); return; }
      move(e.keyCode === 37 || e.keyCode === 38 || (e.keyCode === 9 && e.shiftKey) ? -1 : 1);
    }, true);
  }
  window.RenewalPanel = {
    isOpen: function () { return !!panel && !panel.hidden; },
    open: function () {
      if (!panel) build();
      if (!panel.hidden) return;
      previous = document.activeElement; confirmExit = false;
      message.textContent = 'Checking whether Home control is on…';
      buttons[1].textContent = 'Return to LG Home'; panel.hidden = false; focus(4); refreshMode();
    }
  };
}());
