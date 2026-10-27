!function () {
  "use strict";

  function startupMark(name) { if (window.HomeStartup) window.HomeStartup.mark(name); }
  startupMark('appStart');
  // Leave a rendering and input opportunity before background service work.
  function afterRender(callback) {
    function frame(next) {
      if (window.requestAnimationFrame) window.requestAnimationFrame(next);
      else setTimeout(next, 16);
    }
    frame(function () { frame(function () { setTimeout(callback, 0); }); });
  }

  function tr(text, params) {
    return window.HomeI18n ? HomeI18n.t(text, params) : text.replace(/\{(\w+)\}/g, function (m, k) {
      return params && params[k] !== undefined ? params[k] : m;
    });
  }
  function ht(markup) {
    return window.HomeI18n ? HomeI18n.html(markup) : markup;
  }
  // Shared layout, focus and remote-control state.
  var layout = HomeUI.layoutFor(HomeUI.preferences().appearance, CONFIG.columns),
    shelf = HomeUI.createShelf(),
    dockGlass = HomeUI.createDockGlass(),
    statusControl = HomeUI.createStatus(function () {
      if (moveState || pickerOpen || undoState || focusZone === 'inputs') return false;
      focusTopButton(2);
      return true;
    }, function () {
      if (!layout.tvos || moveState || pickerOpen || undoState || focusZone === 'inputs') return false;
      focusTopButton(3);
      return true;
    }, function () {
      if (!layout.tvos || moveState || pickerOpen || undoState || focusZone === 'inputs') return false;
      focusTopButton(4);
      return true;
    }),
    headerBottom = null;
  var toastTimer,
    columnCount = layout.columns,
    columnWidth = layout.columnWidth,
    KEY_OK = 13,
    KEY_BACK = 461,
    greetings = [[5, tr("Good night")], [12, tr("Good morning")], [17, tr("Good afternoon")], [22, tr("Good evening")], [24, tr("Good night")]],
    weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    getElement = function (e) {
      return document.getElementById(e);
    },
    stage = getElement("stage"),
    tilesContainer = getElement("tiles"),
    focusGlass = getElement("glass"),
    heroTitle = getElement("hero"),
    ambientLayers = [getElement("ambientA"), getElement("ambientB")],
    ambientIndex = 0,
    ambientColor = null,
    topButtons = [getElement("btnInputs"), getElement("btnWifi"), getElement("btnSettings"), getElement("btnWidgets"), getElement("btnChurch")],
    inputsPanel = getElement("inputsPanel"),
    tiles = [],
    focusZone = "grid",
    focusedTile = 0,
    focusedTopButton = 0,
    focusedInput = 0,
    inputRows = [],
    scrollOffset = 0,
    heroVisible = false,
    focusGlassVisible = false,
    moveState = null,
    activeBridges = [],
    topButtonRects = null;
  // Retain service bridges until their replies arrive; subscriptions stay alive.
  function callLuna(uri, params, callback, timeout) {
    var bridge, timer, done = false;
    function finish(result) {
      if (done) return;
      if (!(params && params.subscribe)) {
        done = true;
        clearTimeout(timer);
        var index = activeBridges.indexOf(bridge);
        if (index >= 0) activeBridges.splice(index, 1);
        if (timeout && bridge) try { bridge.cancel(); } catch (_) {}
      }
      callback && callback(result);
    }
    try {
      bridge = new PalmServiceBridge();
      bridge.onservicecallback = function (e) {
        var i;
        try {
          i = JSON.parse(e);
        } catch (e) {
          i = {
            returnValue: false
          };
        }
        finish(i);
      };
      activeBridges.push(bridge);
      if (timeout) timer = setTimeout(function () { finish({returnValue: false}); }, timeout);
      bridge.call(uri, JSON.stringify(params || {}));
    } catch (e) {
      finish({
        returnValue: false,
        errorText: String(e)
      });
    }
  }
  function launchApp(appId, title, params) {
    callLuna("luna://com.webos.applicationManager/launch", {
      id: appId,
      params: params || {}
    }, function (n) {
      false === n.returnValue && showToast(tr("Can't open {app}", {
        app: title || appId
      }));
    });
  }
  function showToast(message) {
    var toast = getElement("toast");
    toast.textContent = message;
    toast.classList.add("shown");
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      toast.classList.remove("shown");
    }, 2200);
  }
  function launchFirst(candidates, index, label) {
    var candidate = candidates[index];
    if (!candidate) {
      showToast(tr("Can't open {app}", {
        app: label
      }));
      return;
    }
    callLuna("luna://com.webos.applicationManager/launch", {
      id: candidate.id,
      params: candidate.params || {}
    }, function (r) {
      if (false === r.returnValue) {
        launchFirst(candidates, index + 1, label);
      }
    });
  }
  function openNetworkSettings() {
    launchFirst([{
      id: "com.webos.app.firstuse-overlay",
      params: {
        target: "network"
      }
    }, {
      id: "com.palm.app.settings",
      params: {
        target: "network"
      }
    }, {
      id: "com.palm.app.settings",
      params: {}
    }], 0, tr("Network settings"));
  }
  var legacyOrderKey = "tvhome.order";
  // App editing uses the existing grid positions and focus highlight.
  var library, hideButton, editHint, picker, pickerList, pickerStatus, pickerClose;
  var inventoryPending = false;
  var pickerOpen = false,
    pickerGeneration = 0,
    pickerIndex = 0,
    pickerButtons = [];
  var hideSelected = false,
    undoState = null,
    undoBar,
    undoButton,
    pointerTimer = null,
    suppressClick = false;
  function screenIds() {
    return tiles.filter(function (item) {
      return !item.add;
    }).map(function (item) {
      return item.app.id;
    });
  }
  function saveScreen(hidden) {
    try {
      library.save(screenIds(), hidden || library.hidden());
      return true;
    } catch (error) {
      showToast(tr("Couldn't save changes. Please try again."));
      return false;
    }
  }
  function rebuild(focusId) {
    tilesContainer.innerHTML = "";
    tiles = library.visible().map(createTile);
    var el = HomeUI.createAddView(tr('Add app'));
    var item = {
      add: true,
      app: {
        title: tr('Add app')
      },
      el: el,
      color: [100, 110, 125]
    };
    el.addEventListener('mouseover', function () {
      if (!moveState && !pickerOpen && !undoState) {
        focusTile(tiles.length - 1);
      }
    });
    el.addEventListener('click', function () {
      if (!moveState) {
        openPicker();
      }
    });
    tilesContainer.appendChild(el);
    tiles.push(item);
    layoutTiles();
    tiles.forEach(function (tile) {
      tile.el.classList.add('shown');
    });
    focusZone = 'none';
    var nextFocus = 0;
    for (var i = 0; i < tiles.length; i++) {
      if (focusId && tiles[i].app.id === focusId) {
        nextFocus = i;
        break;
      }
    }
    focusTile(nextFocus);
    startupMark('gridCreated');
  }
  // Insert a single app tile at a given index without re-rendering the
  // rest of the grid. Used by picker-add and hide-undo paths.
  function insertTileAt(app, index) {
    // Rebase focusedTile onto the same element after the splice, since a
    // stale index would make the next focusTile() clear focus from the
    // wrong tile (leaving two tiles with .focused).
    var focusedEl = tiles[focusedTile] && tiles[focusedTile].el;
    var tile = createTile(app);
    tiles.splice(index, 0, tile);
    if (focusedEl) {
      for (var i = 0; i < tiles.length; i++) {
        if (tiles[i].el === focusedEl) {
          focusedTile = i;
          break;
        }
      }
    }
    var next = tiles[index + 1];
    if (next && next.el) {
      tilesContainer.insertBefore(tile.el, next.el);
    }
    layoutTiles();
    tile.el.classList.add('shown');
    return tile;
  }
  function activateTile(item) {
    if (item.add) {
      openPicker();
    } else if (item.app.id === 'airplay') {
      callLuna('luna://airplay.service/showAirplayPage', {}, function (result) {
        if (!result || !result.returnValue) {
          launchApp(item.app.id, item.app.title);
        }
      }, 5000);
    } else {
      launchApp(item.app.id, item.app.title);
    }
  }
  function cancelHold() {
    clearTimeout(okHoldTimer);
    okHoldTimer = null;
    clearTimeout(pointerTimer);
    pointerTimer = null;
    okPressed = false;
  }
  function beginMoving(item) {
    if (!item || item.add || moveState || pickerOpen || undoState) {
      return;
    }
    moveState = {
      item: item,
      snapshot: tiles.slice()
    };
    item.el.classList.add('moving');
    document.body.classList.add('editing');
    hideButton.hidden = false;
    editHint.hidden = false;
    hideButton.classList.remove('focused');
    hideSelected = false;
    focusTile(tiles.indexOf(item));
  }
  function pointerMove(item) {
    if (!moveState || item.add) {
      return;
    }
    hideSelected = false;
    hideButton.classList.remove('focused');
    moveTile(tiles.indexOf(item));
  }
  function bindHold(item) {
    item.el.addEventListener('mousedown', function (event) {
      if (event.button !== 0 || moveState || pickerOpen || undoState) {
        return;
      }
      focusTile(tiles.indexOf(item));
      clearTimeout(pointerTimer);
      suppressClick = false;
      pointerTimer = setTimeout(function () {
        pointerTimer = null;
        suppressClick = true;
        beginMoving(item);
      }, 600);
    });
    item.el.addEventListener('mouseleave', function () {
      clearTimeout(pointerTimer);
      pointerTimer = null;
    });
  }
  function tileClick(item) {
    if (suppressClick) {
      suppressClick = false;
      return;
    }
    if (pickerOpen || undoState) {
      return;
    }
    if (moveState) {
      pointerMove(item);
      finishMoving(true);
    } else {
      activateTile(item);
    }
  }
  function selectHide() {
    if (!moveState) {
      return;
    }
    hideSelected = true;
    hideButton.classList.add('focused');
    hideButton.focus();
  }
  function hideApp() {
    if (!moveState) {
      return;
    }
    var item = moveState.item,
      snapshot = moveState.snapshot.slice(),
      oldHidden = library.hidden();
    var previous = tiles.slice();
    tiles = tiles.filter(function (tile) {
      return tile !== item;
    });
    if (!saveScreen(oldHidden.concat(item.app.id))) {
      tiles = previous;
      return;
    }
    moveState = null;
    hideSelected = false;
    item.el.classList.remove('moving');
    document.body.classList.remove('editing');
    hideButton.hidden = true;
    editHint.hidden = true;
    item.el.remove();
    layoutTiles();
    focusZone = 'none';
    focusTile(Math.min(focusedTile, tiles.length - 1));
    undoState = {
      ids: snapshot.filter(function (tile) {
        return !tile.add;
      }).map(function (tile) {
        return tile.app.id;
      }),
      hidden: oldHidden,
      id: item.app.id,
      app: item.app
    };
    undoBar.hidden = false;
    undoButton.focus();
  }
  function dismissUndo() {
    if (!undoState) {
      return;
    }
    undoState = null;
    undoBar.hidden = true;
    focusTile(focusedTile);
  }
  function undoHide() {
    if (!undoState) {
      return;
    }
    try {
      var state = undoState;
      var id = state.id;
      library.save(state.ids, state.hidden);
      dismissUndo();
      var app = library.visible().filter(function (candidate) { return candidate.id === id; })[0] || state.app || { id: id };
      var insertIndex = Math.max(0, Math.min(state.ids.indexOf(id), tiles.length - 1));
      var tile = insertTileAt(app, insertIndex);
      focusTile(tiles.indexOf(tile));
    } catch (error) {
      showToast(tr("Couldn't restore app. Please try again."));
    }
  }
  function closePicker() {
    if (!pickerOpen) {
      return;
    }
    pickerOpen = false;
    pickerGeneration++;
    picker.hidden = true;
    cancelHold();
    focusZone = 'none';
    focusTile(tiles.length - 1);
  }
  function focusPicker(index) {
    pickerIndex = Math.max(0, Math.min(index, pickerButtons.length - 1));
    pickerButtons[pickerIndex].focus();
    pickerButtons[pickerIndex].scrollIntoView({
      block: 'nearest'
    });
  }
  function renderPicker(apps) {
    pickerList.innerHTML = '';
    pickerButtons = [];
    apps.forEach(function (app) {
      var button = document.createElement('button');
      button.className = 'app-choice';
      button.dataset.appId = app.id;
      var icon = document.createElement('img');
      icon.src = app.icon || '';
      icon.alt = '';
      icon.onerror = function () {
        icon.style.visibility = 'hidden';
      };
      var title = document.createElement('span');
      title.textContent = app.title;
      button.appendChild(icon);
      button.appendChild(title);
      button.addEventListener('focus', function () {
        pickerIndex = pickerButtons.indexOf(button);
      });
      button.addEventListener('click', function () {
        try {
          library.add(app.id);
          closePicker();
          var tile = insertTileAt(app, tiles.length - 1);
          focusTile(tiles.indexOf(tile));
          showToast(tr('{app} added', {
            app: app.title
          }));
        } catch (error) {
          pickerStatus.textContent = tr("Couldn't save changes. Please try again.");
        }
      });
      pickerList.appendChild(button);
      pickerButtons.push(button);
    });
    pickerButtons.push(pickerClose);
    focusPicker(0);
  }
  function openPicker() {
    if (moveState || pickerOpen) {
      return;
    }
    dismissUndo();
    cancelHold();
    pickerOpen = true;
    var generation = ++pickerGeneration;
    picker.hidden = false;
    pickerStatus.textContent = tr('Checking installed apps…');
    pickerList.innerHTML = '';
    pickerButtons = [pickerClose];
    focusPicker(0);
    setFocusZone('picker');
    AppLibrary.installed(function (apps) {
      if (!pickerOpen || generation !== pickerGeneration) {
        return;
      }
      if (apps !== null) {
        library.refresh(apps);
        inventoryPending = true;
      }
      var choices = library.available();
      pickerStatus.textContent = apps === null ? tr('Showing the saved list. Could not refresh apps from the TV.') : choices.length ? tr('Choose an app to add to Home.') : tr('All installed apps are already on Home.');
      renderPicker(choices);
    });
  }
  function initializeApps() {
    library = AppLibrary.create(localStorage, window.TV_APPS && TV_APPS.apps || [], CONFIG);
    hideButton = document.createElement('button');
    hideButton.id = 'hideApp';
    hideButton.hidden = true;
    hideButton.innerHTML = ht('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3l18 18M10 5.2c5.5-1 10 6.8 10 6.8a20 20 0 0 1-3 3M6 6C3.4 8 2 12 2 12s4 7 10 7c1.4 0 2.7-.4 4-1M9 9a4.2 4.2 0 0 0 6 6"/></svg><span>Hide from Home</span>');
    hideButton.addEventListener('mouseover', selectHide);
    hideButton.addEventListener('click', hideApp);
    document.body.appendChild(hideButton);
    editHint = document.createElement('div');
    editHint.id = 'editHint';
    editHint.hidden = true;
    editHint.textContent = tr('← ↑ ↓ → Move   ·   OK Place   ·   Back Cancel   ·   ↓ Below last row to hide');
    document.body.appendChild(editHint);
    undoBar = document.createElement('div');
    undoBar.id = 'appUndo';
    undoBar.hidden = true;
    undoBar.setAttribute('role', 'status');
    var message = document.createElement('span');
    message.textContent = tr('App hidden. Add it back with +.');
    undoBar.appendChild(message);
    undoButton = document.createElement('button');
    undoButton.textContent = tr('Undo');
    undoButton.addEventListener('click', undoHide);
    undoBar.appendChild(undoButton);
    document.body.appendChild(undoBar);
    picker = document.createElement('section');
    picker.id = 'appPicker';
    picker.hidden = true;
    picker.setAttribute('role', 'dialog');
    picker.setAttribute('aria-modal', 'true');
    picker.setAttribute('aria-labelledby', 'appPickerTitle');
    picker.innerHTML = ht('<div class="app-picker-card"><h2 id="appPickerTitle">Add app</h2><p id="appPickerStatus" role="status"></p><div id="appPickerList"></div><button id="appPickerClose">Back to Home</button></div>');
    document.body.appendChild(picker);
    pickerList = getElement('appPickerList');
    pickerStatus = getElement('appPickerStatus');
    pickerClose = getElement('appPickerClose');
    pickerClose.addEventListener('click', closePicker);
    document.addEventListener('mouseup', function () {
      clearTimeout(pointerTimer);
      pointerTimer = null;
      setTimeout(function () {
        suppressClick = false;
      }, 0);
    });
    window.addEventListener('blur', cancelHold);
    document.addEventListener('visibilitychange', function () {
      if (document.hidden) {
        cancelHold();
        if (moveState) {
          finishMoving(false);
        }
      }
    });
    document.addEventListener('keydown', function (event) {
      var key = event.keyCode;
      if (pickerOpen) {
        event.preventDefault();
        event.stopImmediatePropagation();
        if (key === 27 || key === 461) {
          closePicker();
        } else if (key === 13 && !event.repeat) {
          pickerButtons[pickerIndex].click();
        } else if (key === 38 || key === 37) {
          focusPicker(pickerIndex - 1);
        } else if (key === 40 || key === 39) {
          focusPicker(pickerIndex + 1);
        } else if (key === 9) {
          focusPicker((pickerIndex + (event.shiftKey ? -1 : 1) + pickerButtons.length) % pickerButtons.length);
        }
      } else if (undoState) {
        event.preventDefault();
        event.stopImmediatePropagation();
        if (key === 13 && !event.repeat) {
          undoHide();
        } else if (key === 27 || key === 461 || key >= 37 && key <= 40) {
          dismissUndo();
        }
      } else if (moveState && hideSelected) {
        event.preventDefault();
        event.stopImmediatePropagation();
        if (key === 13 && !event.repeat) {
          hideApp();
        } else if (key === 27 || key === 461) {
          finishMoving(false);
        } else if (key === 38) {
          hideSelected = false;
          hideButton.classList.remove('focused');
          hideButton.blur();
          focusTile(focusedTile);
        }
      }
    }, true);
    document.addEventListener('keyup', function (event) {
      if (pickerOpen || undoState || hideSelected) {
        cancelHold();
        event.stopImmediatePropagation();
      }
    }, true);
    rebuild();
  }
  function refreshInventory() {
    startupMark('inventoryRefreshStart');
    AppLibrary.installed(function (apps) {
      if (apps !== null) {
        library.refresh(apps);
        inventoryPending = true;
        if (refreshVisibleTiles()) focusTile(focusedTile);
      }
      startupMark('inventoryRefreshComplete');
    });
  }
  function refreshVisibleTiles() {
    if (!inventoryPending || focusZone !== 'grid' || moveState || pickerOpen || undoState ||
        okHoldTimer || pointerTimer || document.hidden ||
        (window.RenewalPanel && window.RenewalPanel.isOpen())) return false;
    inventoryPending = false;
    var apps = library.visible(), focusedChanged = false;
    tiles.forEach(function (tile, index) {
      if (tile.add) return;
      var app = apps.filter(function (candidate) { return candidate.id === tile.app.id; })[0];
      if (!app || JSON.stringify(app) === JSON.stringify(tile.app)) return;
      updateTile(tile, app);
      if (index === focusedTile) focusedChanged = true;
    });
    loadVisibleIcons();
    return focusedChanged;
  }
  // Tile rendering, icon colors and grid geometry.
  // DOM colors are resolved cheapest-first: dominantColor baked into
  // apps.js, then a persisted localStorage cache, then a one-time canvas
  // computation cached for future launches. This avoids the 20-30 canvas
  // readbacks (GPU->CPU sync) that used to stall launch.
  function cachedColor(id) {
    try {
      var raw = localStorage.getItem('tvhome.color.' + id);
      if (raw) {
        var c = JSON.parse(raw);
        if (Array.isArray(c) && c.length === 3) return c;
      }
    } catch (_) {}
    return null;
  }
  function storeCachedColor(id, rgb) {
    try { localStorage.setItem('tvhome.color.' + id, JSON.stringify(rgb)); } catch (_) {}
  }
  function dominantColorFromImage(image) {
    try {
      var sample = document.createElement('canvas');
      sample.width = 12;
      sample.height = 12;
      var ctx = sample.getContext('2d');
      ctx.drawImage(image, 0, 0, 12, 12);
      var data = ctx.getImageData(0, 0, 12, 12).data;
      var best = null, bestScore = -1;
      var sum = [0, 0, 0], count = 0;
      for (var i = 0; i < data.length; i += 4) {
        if (data[i + 3] < 128) continue;
        var r = data[i], g = data[i + 1], b = data[i + 2];
        sum[0] += r; sum[1] += g; sum[2] += b; count++;
        var hsv = rgbToHsv([r, g, b]);
        var score = hsv[1] * Math.min(1, 1.4 * hsv[2]);
        if (score > bestScore) { bestScore = score; best = [r, g, b]; }
      }
      if (!count) return null;
      if (bestScore < 0.25) {
        var avg = [sum[0] / count, sum[1] / count, sum[2] / count];
        var h = rgbToHsv(avg);
        h[2] = Math.max(h[2], 0.55);
        return hsvToRgb(h);
      }
      var h2 = rgbToHsv(best);
      h2[1] = Math.min(1, 1.1 * h2[1]);
      h2[2] = Math.max(0.5, h2[2]);
      return hsvToRgb(h2);
    } catch (_) { return null; }
  }
  function computeColorOnload(tile, image) {
    var done = false;
    image.onload = function () {
      if (done) return;
      done = true;
      var rgb = dominantColorFromImage(image);
      if (rgb) {
        storeCachedColor(tile.app.id, rgb);
        // Cards with a fixed icon-background override keep that color; we
        // still resolve tile.color (ambient) from the artwork.
        if (!tile.card.hasAttribute('data-bg')) {
          tile.card.style.background = "rgb(" + rgb.join(",") + ")";
        }
        tile.color = rgb;
        if (tiles[focusedTile] === tile) updateAmbient(rgb);
      }
    };
    return null;
  }
  // Fixed card backgrounds mirroring each app icon's own background, so the
  // artwork blends into its card instead of sitting on a derived color.
  var APP_BG = {
    'com.apple.appletv': [0, 0, 0],
    'cdp-30': [0, 0, 0],
    'netflix': [255, 255, 255],
    'triple.nos.app': [255, 255, 255],
    'youtube.leanback.v4': [255, 255, 255]
  };
  function createTile(app) {
    var view = HomeUI.createTileView(app),
      element = view.element,
      card = view.card,
      image = view.image,
      tile = {
        app: app,
        el: element,
        card: card,
        color: null
      };
    tile.image = image;
    updateTile(tile, app);
    return element.addEventListener("mouseover", function () {
      "inputs" === focusZone || pickerOpen || undoState || (moveState ? pointerMove(tile) : focusTile(tiles.indexOf(tile)));
    }), element.addEventListener("click", function () {
      tileClick(tile);
    }), bindHold(tile), tilesContainer.appendChild(element), tile;
  }
  function updateTile(tile, app) {
    var image = tile.image, card = tile.card;
    var iconPath = (window.TV_ICONS && TV_ICONS[app.id]) || app.icon || 'missing-icon';
    if (tile.iconPath && tile.iconPath !== iconPath) {
      try { localStorage.removeItem('tvhome.color.' + app.id); } catch (_) {}
    }
    tile.app = app;
    tile.el.setAttribute('aria-label', app.title);
    tile.el.querySelector('.name').textContent = app.title;
    image.onload = null;
    image.style.display = '';
    card.classList.remove('missing-icon');
    card.removeAttribute('data-initial');
    card.removeAttribute('data-bg');
    card.style.background = '';
    var color = null, cardBackground;
    var bg = APP_BG[app.id];
    if (bg) {
      // Fixed card background mirroring the icon's own background.
      color = app.dominantColor || cachedColor(app.id);
      if (!color && app.iconColor) {
        color = parseHexColor(app.iconColor) || [68, 68, 68];
      }
      cardBackground = 'rgb(' + bg.join(',') + ')';
      card.style.background = cardBackground;
      card.setAttribute('data-bg', 'fixed');
      if (!color) {
        computeColorOnload(tile, image);
      }
    } else {
      // The card matches the icon's own background; dominantColor only tints the ambient light.
      color = app.dominantColor || cachedColor(app.id);
      if (app.iconColor) {
        cardBackground = tileBackground(app.iconColor);
        color = color || parseHexColor(app.iconColor) || [68, 68, 68];
      }
      if (!color) {
        computeColorOnload(tile, image);
      }
    }
    if (color && !cardBackground) {
      cardBackground = "rgb(" + color.join(",") + ")";
    }
    if (cardBackground) {
      card.style.background = cardBackground;
    }
    tile.color = color;
    image.onerror = function () {
      image.style.display = "none";
      card.classList.add("missing-icon");
      card.setAttribute("data-initial", tile.app.title.charAt(0));
    };
    // Prefer the bundled static icon map (deterministic local assets); fall
    // back to whatever icon the TV inventory supplied.
    if (tile.iconPath !== iconPath) {
      tile.iconPath = iconPath;
      tile.iconLoaded = false;
      image.removeAttribute('src');
    }
    if (tile.iconLoaded && image.complete) {
      if (!image.naturalWidth) image.onerror();
      else if (image.onload) image.onload();
    }
    if (tiles[focusedTile] === tile) {
      updateAmbient(tile.color);
    }
  }
  function loadTileIcon(tile) {
    if (tile.add || tile.iconLoaded) return;
    tile.iconLoaded = true;
    tile.image.src = tile.iconPath;
  }
  function loadVisibleIcons() {
    tiles.forEach(function (tile, index) {
      var top = tileTop(index) - scrollOffset;
      if (rowFor(index) === 0 || (!layout.tvos || layout.grid) &&
          top < 1080 + layout.rowPitch && top + layout.cardHeight > -layout.rowPitch) loadTileIcon(tile);
    });
  }
  function rowFor(index) {
    return Math.floor(index / columnCount);
  }
  function tileLeft(index) {
    return HomeUI.positionFor(layout, index).left;
  }
  function tileTop(index) {
    return HomeUI.positionFor(layout, index).top;
  }
  function layoutTiles(gridToggle) {
    tiles.forEach(function (e, t) {
      if (!gridToggle) tilesContainer.appendChild(e.el);
      // Position via transform so layout is never touched on updates.
      e.el.style.transform = "translate3d(" + tileLeft(t) + "px," + tileTop(t) + "px,0)";
      e.el.classList.toggle("dock", 0 === rowFor(t));
    });
    var dockBand = getElement("dockBand"),
      dockCount = Math.min(columnCount, tiles.length);
    dockBand.style.display = dockCount ? "block" : "none";
    dockBand.style.left = (layout.tvos ? 40 : tileLeft(0) - 28) + "px";
    dockBand.style.top = layout.dockTop + "px";
    dockBand.style.width = (layout.tvos ? 1824 : (dockCount - 1) * columnWidth + layout.cardWidth + 56) + "px";
    dockBand.style.height = layout.dockHeight + "px";
    // Tile positions changed, so any cached top-button geometry is stale.
    topButtonRects = null;
    if (!gridToggle) loadVisibleIcons();
  }
  function currentHeaderBottom() {
    if (headerBottom === null) {
      var header = document.querySelector("header");
      headerBottom = header.offsetTop + header.offsetHeight;
    }
    return headerBottom;
  }
  // Widgets are decorative tvOS-style surfaces fed by WidgetData (Home Assistant
  // in production, a fake provider in the browser preview). They are not part
  // of the remote-focus grid and never intercept input.
  var widgets = null;
  var stopWidgetWatch = null;
  var widgetRefreshGeneration = 0;
  function ensureWidgets() {
    if (HomeUI.preferences().appearance !== 'tvos' || typeof window.WidgetData === 'undefined' || !HomeUI.createWidgets || widgets) return;
    widgets = HomeUI.createWidgets(window.WidgetData);
    startupMark('widgetsCreated');
    window.WidgetData.subscribe(refreshWidgets);
  }
  function refreshWidgets() {
    if (stopWidgetWatch) stopWidgetWatch();
    stopWidgetWatch = null;
    var generation = ++widgetRefreshGeneration;
    if (!widgets || typeof window.WidgetData === 'undefined') return;
    var preferences = HomeUI.preferences();
    widgets.show(preferences.appearance === 'tvos' && preferences.widgetsVisible);
    widgets.update(null);
    if (document.hidden || preferences.appearance !== 'tvos' || !preferences.widgetsVisible) return;
    afterRender(function () {
      if (generation !== widgetRefreshGeneration) return;
      stopWidgetWatch = window.WidgetData.watch(function (snap) {
        if (generation !== widgetRefreshGeneration) return;
        widgets.update(snap);
        startupMark('widgetDataFirst');
      });
    });
  }
  function tileBackground(hex) {
    var rgb = parseHexColor(hex);
    if (!rgb) {
      return "#2c2c2e";
    }
    var hsv = rgbToHsv(rgb);
    return hsv[1] < .15 && (hsv[2] > .85 || hsv[2] < .1) ? "#2c2c2e" : "rgb(" + rgb.join(",") + ")";
  }
  function parseHexColor(hex) {
    var match = /^#?([0-9a-f]{6})$/i.exec(hex || "");
    if (!match) {
      return null;
    }
    var value = parseInt(match[1], 16);
    return [value >> 16 & 255, value >> 8 & 255, 255 & value];
  }
  function rgbToHsv(rgb) {
    var red = rgb[0] / 255,
      green = rgb[1] / 255,
      blue = rgb[2] / 255,
      maximum = Math.max(red, green, blue),
      delta = maximum - Math.min(red, green, blue),
      hue = 0;
    return delta && (hue = maximum === red ? (green - blue) / delta % 6 : maximum === green ? (blue - red) / delta + 2 : (red - green) / delta + 4, (hue *= 60) < 0 && (hue += 360)), [hue, maximum ? delta / maximum : 0, maximum];
  }
  function hsvToRgb(hsv) {
    var hue = hsv[0],
      saturation = hsv[1],
      value = hsv[2],
      chroma = value * saturation,
      secondary = chroma * (1 - Math.abs(hue / 60 % 2 - 1)),
      offset = value - chroma;
    return (hue < 60 ? [chroma, secondary, 0] : hue < 120 ? [secondary, chroma, 0] : hue < 180 ? [0, chroma, secondary] : hue < 240 ? [0, secondary, chroma] : hue < 300 ? [secondary, 0, chroma] : [chroma, 0, secondary]).map(function (e) {
      return Math.round(255 * (e + offset));
    });
  }
  // Focus follows both remote navigation and Magic Remote hover.
  function focusTile(index) {
    if (tiles.length) {
      index = Math.max(0, Math.min(index, tiles.length - 1));
      setFocusZone("grid");
      tiles[focusedTile] && tiles[focusedTile].el.classList.remove("focused");
      focusedTile = index;
      refreshVisibleTiles();
      loadTileIcon(tiles[index]);
      tiles[index].el.classList.add("focused");
      var row = rowFor(index);
      if (layout.tvos && layout.grid !== (row > 0)) {
        layout.grid = row > 0;
        tilesContainer.classList.add("regrid");
        layoutTiles(true);
        tilesContainer.offsetWidth;
        requestAnimationFrame(function () {
          tilesContainer.classList.remove("regrid");
        });
      }
      var top = tileTop(index);
      scrollOffset = HomeUI.scrollFor(layout, index, scrollOffset, !!moveState);
      loadVisibleIcons();
      stage.style.transform = "translate3d(0," + -scrollOffset + "px,0)";
      document.body.classList.toggle("app-grid", layout.tvos && scrollOffset > 0);
      document.body.classList.toggle("scrolled", layout.dockTop - scrollOffset < currentHeaderBottom() + 24);
      shelf.update(layout.tvos && row === 0, layout.tvos);
      dockGlass.update(layout.tvos, layout.grid, HomeUI.preferences().reducedEffects);
      if (layout.tvos) return;
      var glassWidth = layout.focusScale * layout.cardWidth + layout.glassPadding,
        glassHeight = layout.focusScale * layout.cardHeight + layout.glassPadding,
        glassLeft = tileLeft(index) + layout.cardWidth / 2 - glassWidth / 2,
        glassTop = top + layout.cardHeight / 2 - glassHeight / 2;
      focusGlass.style.width = glassWidth + "px";
      focusGlass.style.height = glassHeight + "px";
      focusGlass.style.transform = "translate3d(" + glassLeft + "px," + glassTop + "px,0)";
      focusGlassVisible || (focusGlass.style.transition = "none", focusGlass.offsetWidth, focusGlass.style.transition = "", focusGlass.style.opacity = "1", focusGlassVisible = true);
      0 === row ? function (e) {
        var t = e.app.title;
        heroTitle.style.top = (layout.tileBase - layout.heroOffset) + "px";
        heroVisible ? heroTitle.textContent !== t && (heroTitle.style.opacity = "0", heroTitle.style.transform = "translateX(-24px)", clearTimeout(heroTitle.swap), heroTitle.swap = setTimeout(function () {
          heroTitle.textContent = t;
          heroTitle.style.transition = "none";
          heroTitle.style.transform = "translateX(24px)";
          heroTitle.offsetWidth;
          heroTitle.style.transition = "";
          heroTitle.style.transform = "none";
          heroTitle.style.opacity = "1";
        }, 120)) : (heroTitle.textContent = t, heroTitle.style.transform = "none", heroTitle.style.opacity = "1", heroVisible = true);
        updateAmbient(e.color);
      }(tiles[index]) : heroVisible && (heroVisible = false, heroTitle.style.opacity = "0");
      updateAmbient(tiles[index].color);
    }
  }
  function updateAmbient(rgb) {
    if (rgb && !layout.tvos) {
      var color = rgb.join(",");
      if (color !== ambientColor) {
        ambientColor = color;
        var nextLayer = ambientLayers[1 - ambientIndex];
        nextLayer.style.background = "radial-gradient(circle 1190px at 32% 42%, rgba(" + color + ",0.36) 0%, rgba(" + color + ",0.15) 50%, rgba(" + color + ",0) 100%)";
        nextLayer.style.opacity = "1";
        ambientLayers[ambientIndex].style.opacity = "0";
        ambientIndex = 1 - ambientIndex;
      }
    }
  }
  function focusTopButton(index) {
    setFocusZone("top");
    document.body.classList.remove("scrolled");
    topButtons[focusedTopButton].classList.remove("focused");
    focusedTopButton = Math.max(0, Math.min(index, layout.tvos ? (churchVisible() ? 4 : 3) : 2));
    topButtons[focusedTopButton].classList.add("focused");
    // The church shortcut sits beside the clock widget, so keep the widgets on screen.
    if (focusedTopButton === 4) {
      document.body.classList.remove('controls-open');
      statusControl.expanded(false);
    }
  }
  function churchVisible() {
    return !topButtons[4].classList.contains('church-off');
  }
  function setFocusZone(zone) {
    document.body.classList.toggle('controls-open', layout.tvos && zone === 'top');
    statusControl.expanded(layout.tvos && zone === 'top');
    if (zone === 'grid') statusControl.reset();
    focusZone !== zone && ("top" === focusZone && topButtons[focusedTopButton].classList.remove("focused"), "grid" === focusZone && (tiles[focusedTile] && tiles[focusedTile].el.classList.remove("focused"), focusGlassVisible = false, focusGlass.style.opacity = "0"), focusZone = zone);
  }
  function updateClock() {
    var now = new Date(),
      hour = now.getHours();
    for (var idx = 0; idx < greetings.length; idx++) if (hour < greetings[idx][0]) {
      getElement("greeting").textContent = greetings[idx][1];
      break;
    }
    headerBottom = null;
    if (window.HomeI18n) {
      getElement("clock").textContent = HomeI18n.formatTime(now);
      getElement("ampm").textContent = "";
      getElement("date").textContent = HomeI18n.formatDate(now);
    } else {
      getElement("clock").textContent = (hour % 12 || 12) + ":" + ("0" + now.getMinutes()).slice(-2);
      getElement("ampm").textContent = hour < 12 ? "am" : "pm";
      getElement("date").textContent = weekdays[now.getDay()] + "  " + now.getDate() + " " + months[now.getMonth()];
    }
    statusControl.update(getElement('clock').textContent + getElement('ampm').textContent);
    if (focusZone === 'top' && focusedTopButton === 4 && !churchVisible()) focusTile(focusedTile);
  }
  function activateTopButton(index) {
    if (index === 4) {
      launchApp('com.webos.app.browser', 'Kerkdienst', {target: 'https://kerkdienstgemist.nl/stations/1341-Nieuwe-Kerk-Utrecht-Wittevrouwen-'});
      return;
    }
    if (index === 3) {
      if (!layout.tvos || moveState || pickerOpen || undoState || focusZone === 'inputs') return;
      if (!HomeUI.setPreference('widgetsVisible', !HomeUI.preferences().widgetsVisible)) {
        showToast(tr("Couldn't save changes"));
        return;
      }
      focusTile(focusedTile);
      return;
    }
    0 === index ? function () {
      if (inputsPanel.innerHTML = "", inputRows = [], (window.TV_APPS && TV_APPS.inputs || []).forEach(function (e) {
        addInputRow("M18,7V4c0,-1.1 -0.9,-2 -2,-2H8C6.9,2 6,2.9 6,4v3H5v6l3,6v3h8v-3l3,-6V7H18zM8,4h8v3h-2V5h-1v2h-2V5h-1v2H8V4z", e.label, e.appId);
      }), CONFIG.liveTvApp && (inputRows.length && addInputSeparator(), addInputRow("M21,6h-7.59l3.29,-3.29L16,2l-4,4l-4,-4l-0.71,0.71L10.59,6H3c-1.1,0 -2,0.89 -2,2v12c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.89 2,-2V8C23,6.89 22.1,6 21,6zM21,20H3V8h18V20zM9,10v8l7,-4L9,10z", tr("Live TV"), CONFIG.liveTvApp)), inputRows.length) {
        var e = topButtons[0].getBoundingClientRect();
        inputsPanel.style.left = e.left + "px";
        inputsPanel.style.top = e.bottom + 20 + "px";
        inputsPanel.style.minWidth = Math.max(e.width, 300) + "px";
        inputsPanel.classList.remove("hidden");
        topButtons[focusedTopButton].classList.remove("focused");
        focusZone = "inputs";
        focusInput(0);
      } else {
        showToast(tr("No inputs found"));
      }
    }() : 1 === index ? openNetworkSettings() : window.RenewalPanel.open();
  }
  function addInputSeparator() {
    var separator = document.createElement("div");
    separator.className = "separator";
    inputsPanel.appendChild(separator);
  }
  function addInputRow(iconPath, label, appId) {
    var element = document.createElement("div");
    element.className = "inputRow";
    element.innerHTML = ht('<svg viewBox="0 0 24 24"><path d="') + iconPath + '"/></svg>';
    element.appendChild(document.createTextNode(label));
    var index = inputRows.length;
    element.addEventListener("mouseover", function () {
      focusInput(index);
    });
    element.addEventListener("click", function () {
      closeInputs();
      launchApp(appId, label);
    });
    element.appId = appId;
    element.label = label;
    inputRows.push(element);
    inputsPanel.appendChild(element);
  }
  function focusInput(index) {
    inputRows[focusedInput] && inputRows[focusedInput].classList.remove("focused");
    focusedInput = Math.max(0, Math.min(index, inputRows.length - 1));
    inputRows[focusedInput].classList.add("focused");
  }
  function closeInputs() {
    inputsPanel.classList.add("hidden");
    focusZone = "none";
    focusTopButton(0);
  }
  function moveTile(index) {
    index < 0 || index >= tiles.length - 1 || index === focusedTile || (tiles.splice(index, 0, tiles.splice(focusedTile, 1)[0]), focusedTile = index, layoutTiles(), focusTile(index));
  }
  function finishMoving(commit) {
    var item = moveState.item;
    if (commit && !saveScreen()) {
      return;
    }
    if (!commit) {
      tiles = moveState.snapshot;
    }
    moveState = null;
    item.el.classList.remove("moving");
    document.body.classList.remove("editing");
    hideSelected = false;
    hideButton.hidden = true;
    editHint.hidden = true;
    layoutTiles();
    focusTile(tiles.indexOf(item));
  }
  // Short OK launches on release; holding OK enters tile editing instead.
  var okPressed = false,
    okHoldTimer = null;
  function restoreFocus() {
    if (window.HomeHelper && window.HomeHelper.isOpen && window.HomeHelper.isOpen()) return;
    cancelHold();
    closePicker();
    dismissUndo();
    moveState && finishMoving(false);
    updateClock();
    "inputs" === focusZone && inputsPanel.classList.add("hidden");
    topButtons.forEach(function (e) {
      e.classList.remove("focused");
    });
    focusZone = "none";
    focusTile(focusedTile);
  }
  document.addEventListener("keyup", function (event) {
    if (window.RenewalPanel && window.RenewalPanel.isOpen()) {
      okPressed = false;
      return;
    }
    if (event.keyCode === KEY_OK && (okPressed = false, okHoldTimer)) {
      clearTimeout(okHoldTimer);
      okHoldTimer = null;
      var tile = tiles[focusedTile];
      "grid" === focusZone && tile && !moveState && activateTile(tile);
    }
  });
  document.addEventListener("keydown", function (event) {
    var key = event.keyCode;
    if (key !== KEY_OK && okHoldTimer) {
      cancelHold();
    }
    if (key === KEY_OK && okPressed) {
      event.preventDefault();
    } else {
      if (key === KEY_OK && (okPressed = true), moveState) {
        if (37 === key) {
          moveTile(focusedTile - 1);
        } else if (39 === key) {
          moveTile(focusedTile + 1);
        } else if (38 === key) {
          moveTile(focusedTile - columnCount);
        } else if (40 === key) {
          if (rowFor(focusedTile) >= rowFor(tiles.length - 2)) {
            selectHide();
          } else {
            moveTile(Math.min(focusedTile + columnCount, tiles.length - 2));
          }
        } else if (key === KEY_OK) {
          finishMoving(true);
        } else {
          if (key !== KEY_BACK && 27 !== key) {
            return;
          }
          finishMoving(false);
        }
      } else if ("inputs" === focusZone) {
        if (38 === key) {
          if (0 === focusedInput) {
            closeInputs();
          } else {
            focusInput(focusedInput - 1);
          }
        } else if (40 === key) {
          focusInput(focusedInput + 1);
        } else if (key === KEY_OK) {
          var input = inputRows[focusedInput];
          closeInputs();
          launchApp(input.appId, input.label);
        } else {
          if (key !== KEY_BACK && 27 !== key && 37 !== key && 39 !== key) {
            return;
          }
          closeInputs();
        }
      } else if ("top" === focusZone) {
        if (37 === key) {
          focusTopButton(focusedTopButton - 1);
        } else if (39 === key) {
          focusTopButton(focusedTopButton + 1);
        } else if (40 === key) {
          focusTile(0 === rowFor(focusedTile) ? focusedTile : 0);
        } else if (38 === key && focusedTopButton === 4) {
          focusTopButton(2);
        } else if (key === KEY_OK) {
          activateTopButton(focusedTopButton);
        } else if (layout.tvos && (key === KEY_BACK || key === 27)) {
          focusTile(focusedTile);
        } else if (key !== KEY_BACK) {
          return;
        }
      } else {
        var column = focusedTile % columnCount,
          lastIndex = tiles.length - 1;
        if (37 === key) {
          column > 0 && focusTile(focusedTile - 1);
        } else if (39 === key) {
          column < columnCount - 1 && focusedTile < lastIndex && focusTile(focusedTile + 1);
        } else if (38 === key) {
          0 === rowFor(focusedTile) ? focusTopButton(layout.tvos ? (focusedTile < 2 && churchVisible() ? 4 : 2) : (tileCenter = tileLeft(focusedTile) + layout.cardWidth / 2, nearestButton = 0, nearestDistance = 1 / 0, (topButtonRects || (topButtonRects = topButtons.slice(0, 3).map(function (e) {
            var n = e.getBoundingClientRect();
            return n.left + n.width / 2;
          }))).forEach(function (center, t) {
            var a = Math.abs(center - tileCenter);
            a < nearestDistance && (nearestDistance = a, nearestButton = t);
          }), nearestButton)) : focusTile(focusedTile - columnCount);
        } else if (40 === key) {
          rowFor(focusedTile) < rowFor(lastIndex) && focusTile(Math.min(focusedTile + columnCount, lastIndex));
        } else if (key === KEY_OK) {
          okHoldTimer = setTimeout(function () {
            okHoldTimer = null;
            beginMoving(tiles[focusedTile]);
          }, 600);
        } else if (key !== KEY_BACK) {
          return;
        }
      }
      var tileCenter, nearestButton, nearestDistance;
      event.preventDefault();
    }
    startupMark('firstHandledKey');
  });
  var lastWheel = 0;
  getElement('viewport').addEventListener('wheel', function (event) {
    if (!layout.tvos || !event.deltaY || moveState || pickerOpen || undoState || focusZone !== 'grid' ||
        (window.RenewalPanel && window.RenewalPanel.isOpen())) return;
    event.preventDefault();
    var now = Date.now(), row = rowFor(focusedTile), lastRow = rowFor(tiles.length - 1);
    if (now - lastWheel < 220 || (event.deltaY < 0 && row === 0) || (event.deltaY > 0 && row === lastRow)) return;
    lastWheel = now;
    focusTile(event.deltaY > 0 ? Math.min(focusedTile + columnCount, tiles.length - 1) : focusedTile - columnCount);
  }, false);
  topButtons.forEach(function (e, t) {
    e.addEventListener("mouseover", function () {
      "inputs" !== focusZone && !moveState && !pickerOpen && !undoState && focusTopButton(t);
    });
    e.addEventListener("click", function () {
      if (!moveState && !pickerOpen && !undoState) {
        activateTopButton(t);
      }
    });
  });
  document.addEventListener("webOSRelaunch", restoreFocus);
  document.addEventListener("visibilitychange", function () {
    document.hidden || restoreFocus();
  });
  var previousPreferences = HomeUI.preferences();
  HomeUI.subscribe(function (preferences) {
    ensureWidgets();
    var widgetPreferencesChanged = preferences.appearance !== previousPreferences.appearance ||
      preferences.widgetsVisible !== previousPreferences.widgetsVisible;
    var layoutUnchanged = preferences.appearance === previousPreferences.appearance &&
      preferences.reducedEffects === previousPreferences.reducedEffects;
    previousPreferences = preferences;
    if (layoutUnchanged) {
      if (widgetPreferencesChanged) refreshWidgets();
      return;
    }
    topButtonRects = null;
    headerBottom = null;
    var previousZone = focusZone;
    cancelHold();
    closePicker();
    dismissUndo();
    if (moveState) finishMoving(false);
    clearTimeout(heroTitle.swap);
    heroVisible = false;
    heroTitle.style.opacity = "0";
    layout = HomeUI.layoutFor(preferences.appearance, CONFIG.columns);
    columnCount = layout.columns;
    columnWidth = layout.columnWidth;
    scrollOffset = 0;
    focusGlassVisible = false;
    focusGlass.style.opacity = "0";
    layoutTiles();
    focusZone = "none";
    focusTile(focusedTile);
    if (previousZone === "top") focusTopButton(focusedTopButton);
    if (widgets) widgets.show(preferences.appearance === 'tvos' && preferences.widgetsVisible);
    if (widgetPreferencesChanged) refreshWidgets();
  });
  initializeApps();
  updateClock();
  ensureWidgets();
  refreshWidgets();
  if (widgets) widgets.show(layout.tvos && HomeUI.preferences().widgetsVisible);
  var clockTimer = setInterval(updateClock, 1e4);
  document.addEventListener("visibilitychange", function () {
    refreshWidgets();
    if (document.hidden) {
      clearInterval(clockTimer);
    } else {
      updateClock();
      clearInterval(clockTimer);
      clockTimer = setInterval(updateClock, 1e4);
    }
  });
  afterRender(function () {
    refreshInventory();
    if (layout.tvos) setTimeout(function () {
      tiles.forEach(function (tile, index) { if (index < columnCount * 3) loadTileIcon(tile); });
    }, 3000);
    callLuna("luna://com.palm.connectionmanager/getStatus", {
      subscribe: true
    }, function (e) {
      if (false !== e.returnValue || e.wifi || e.wired) {
        var t = "Wi-Fi";
        e.wired && "connected" === e.wired.state ? t = tr("Ethernet") : e.wifi && "connected" === e.wifi.state ? t = e.wifi.ssid || "Wi-Fi" : false === e.isInternetConnectionAvailable && (t = tr("Offline"));
        getElement("wifiLabel").textContent = t;
      }
    });
  });
  focusZone = "none";
  focusTile(0);
  if (layout.tvos) {
    tiles.forEach(function (tile, index) { if (index) tile.el.classList.add('tile-entering'); });
    setTimeout(function () { tiles.forEach(function (tile) { tile.el.classList.remove('tile-entering'); }); }, 180);
  }
  window.RootLauncherRendered = true;
  if (window.HomeStartupReady) window.HomeStartupReady();
  if (window.HomeStartup) window.HomeStartup.paintProxy();
}();
