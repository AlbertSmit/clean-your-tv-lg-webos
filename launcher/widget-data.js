/* Widget data source. In the browser preview this runs against a fake
 * window.WidgetPreview provider; on a TV it talks to Home Assistant (HA) over
 * its WebSocket API using a long-lived access token. Network access is optional: if
 * a source is not configured, refresh() reports no data and the widgets show
 * only the clock. This module is a classic ES5 script and never touches native
 * services, so it works identically on the No-root and Root editions. */
window.WidgetData = (function () {
  'use strict';
  var KEY = 'cytv-widgets';
  var ART_CACHE_KEY = 'cytv-art-cache';
  var listeners = [];

  function artCacheRead() {
    try {
      var raw = localStorage.getItem(ART_CACHE_KEY);
      if (raw) {
        var parsed = JSON.parse(raw);
        if (parsed && typeof parsed === 'object') return parsed;
      }
    } catch (_) {}
    return {};
  }

  function artCacheWrite(box) {
    try { localStorage.setItem(ART_CACHE_KEY, JSON.stringify(box)); } catch (_) {}
  }

  function trimArtCache(box) {
    var keys = Object.keys(box).sort(function (a, b) {
      return (box[a].t || 0) - (box[b].t || 0);
    });
    var total = 0;
    for (var i = 0; i < keys.length; i++) {
      total += (box[keys[i]].src || '').length + (box[keys[i]].thumb || '').length;
    }
    var maxTotal = 3200000;
    while ((keys.length > 16 || (total > maxTotal && keys.length > 1)) && keys.length) {
      var oldest = keys.shift();
      total -= (box[oldest].src || '').length + (box[oldest].thumb || '').length;
      delete box[oldest];
    }
  }

  function defaults() {
    return {
      enabled: { clock: true, nowPlaying: true, weather: false },
      ha: { url: '', token: '', mediaEntity: '', weatherEntity: '' }
    };
  }

  function load() {
    var d = defaults();
    try {
      var raw = localStorage.getItem(KEY);
      if (raw) {
        var c = JSON.parse(raw);
        if (c.enabled) {
          d.enabled.clock = c.enabled.clock !== false;
          d.enabled.nowPlaying = c.enabled.nowPlaying !== false;
          d.enabled.weather = c.enabled.weather === true;
        }
        if (c.ha) {
          d.ha.url = typeof c.ha.url === 'string' ? c.ha.url : '';
          d.ha.token = typeof c.ha.token === 'string' ? c.ha.token : '';
          d.ha.mediaEntity = typeof c.ha.mediaEntity === 'string' ? c.ha.mediaEntity : '';
          d.ha.weatherEntity = typeof c.ha.weatherEntity === 'string' ? c.ha.weatherEntity : '';
        }
      }
    } catch (_) {}
    return d;
  }

  function save(c) {
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (_) {}
    emit();
  }

  function emit() {
    for (var i = 0; i < listeners.length; i++) {
      try { listeners[i](); } catch (_) {}
    }
  }

  function subscribe(fn) {
    listeners.push(fn);
    return function () {
      var i = listeners.indexOf(fn);
      if (i >= 0) listeners.splice(i, 1);
    };
  }

  function xhrGet(url, headers, cb) {
    try {
      var x = new XMLHttpRequest();
      x.open('GET', url, true);
      x.timeout = 8000;
      var k;
      for (k in headers) {
        if (Object.prototype.hasOwnProperty.call(headers, k)) x.setRequestHeader(k, headers[k]);
      }
      x.onload = function () {
        cb(x.status === 200 || x.status === 0 ? x.response : null);
      };
      x.onerror = x.ontimeout = function () { cb(null); };
      x.send();
    } catch (e) { cb(null); }
  }

  function pick(entities, prefix, preferred) {
    if (preferred) {
      for (var i = 0; i < entities.length; i++) {
        if (entities[i] && entities[i].entity_id === preferred) return entities[i];
      }
    }
    for (var j = 0; j < entities.length; j++) {
      if (entities[j] && typeof entities[j].entity_id === 'string' &&
          entities[j].entity_id.indexOf(prefix) === 0) return entities[j];
    }
    return null;
  }

  function text(value) {
    return typeof value === 'string' ? value.trim() : '';
  }

  function pickMusic(entities, preferred) {
    for (var i = 0; i < entities.length; i++) {
      var entity = entities[i];
      if (!entity || typeof entity.entity_id !== 'string' ||
          entity.entity_id.indexOf('media_player.') !== 0 ||
          (preferred && entity.entity_id !== preferred) || entity.state !== 'playing') continue;
      var attributes = entity.attributes || {};
      if (attributes.media_content_type === 'music' && text(attributes.media_title)) return entity;
    }
    return null;
  }

  function artworkUrl(pic, haBase) {
    if (!text(pic)) return null;
    var origin = document.createElement('a');
    origin.href = haBase.replace(/\/$/, '') + '/';
    if (origin.protocol !== 'http:' && origin.protocol !== 'https:') return null;
    var target = document.createElement('a');
    if (/^\/\//.test(pic)) target.href = origin.protocol + pic;
    else if (/^[a-z][a-z0-9+.-]*:/i.test(pic)) target.href = pic;
    else if (pic.charAt(0) === '/') target.href = origin.protocol + '//' + origin.host + pic;
    else target.href = origin.href + pic;
    if (target.protocol !== origin.protocol || target.host !== origin.host) return null;
    return target.href;
  }

  function artworkDataUrl(entity, haBase, auth, done) {
    var pic = entity && entity.attributes && entity.attributes.entity_picture;
    try {
      var url = artworkUrl(pic, haBase);
      if (!url) { done(null); return; }
      var x = new XMLHttpRequest();
      x.open('GET', url, true);
      x.responseType = 'blob';
      x.timeout = 8000;
      x.setRequestHeader('Authorization', auth);
      x.onload = function () {
        if (x.status !== 200 && x.status !== 0) { done(null); return; }
        try {
          var fr = new FileReader();
          fr.onload = function () {
            var full = fr.result;
            try {
              var img = new Image();
              img.onload = function () {
                var thumb = null;
                try {
                  var maxDim = 56;
                  var scale = Math.min(1, maxDim / Math.max(img.width, img.height));
                  var w = Math.max(1, Math.round(img.width * scale));
                  var h = Math.max(1, Math.round(img.height * scale));
                  var tinyW = Math.max(1, Math.round(w / 2.5));
                  var tinyH = Math.max(1, Math.round(h / 2.5));
                  var tiny = document.createElement('canvas');
                  tiny.width = tinyW; tiny.height = tinyH;
                  tiny.getContext('2d').drawImage(img, 0, 0, tinyW, tinyH);
                  var cv = document.createElement('canvas');
                  cv.width = w; cv.height = h;
                  var gx = cv.getContext('2d');
                  gx.imageSmoothingEnabled = true;
                  gx.imageSmoothingQuality = 'high';
                  gx.drawImage(tiny, 0, 0, w, h);
                  thumb = cv.toDataURL('image/jpeg', 0.7);
                } catch (e) {}
                done({ src: full, thumb: thumb });
              };
              img.onerror = function () { done({ src: full, thumb: null }); };
              img.src = full;
            } catch (e) {
              done({ src: full, thumb: null });
            }
          };
          fr.onerror = function () { done(null); };
          fr.readAsDataURL(x.response);
        } catch (e) { done(null); }
      };
      x.onerror = x.ontimeout = function () { done(null); };
      x.send();
    } catch (e) { done(null); }
  }

  function loadArtwork(entity, haBase, auth, done) {
    var key = artworkKey(entity);
    var box = artCacheRead();
    var hit = box[key];
    if (hit && (hit.src || hit.thumb)) {
      done({ src: hit.src || null, thumb: hit.thumb || null });
      return;
    }
    artworkDataUrl(entity, haBase, auth, function (value) {
      if (value && value.src) {
        box[key] = { src: value.src, thumb: value.thumb || null, t: Date.now() };
        trimArtCache(box);
        artCacheWrite(box);
      }
      done(value);
    });
  }

  function model(list, cfg, weatherEnabled) {
    var out = { source: 'home-assistant', weather: null, nowPlaying: null };
    var wx = pick(list, 'weather.', cfg.ha.weatherEntity);
    if (wx && weatherEnabled) {
      var w = wx.attributes || {};
      var f = (w.forecast && w.forecast[0]) || {};
      out.weather = {
        condition: wx.state,
        temp: w.temperature,
        unit: w.temperature_unit || '',
        high: f.temperature != null ? f.temperature : w.temperature_high,
        low: f.templow != null ? f.templow : w.temperature_low,
        humidity: w.humidity,
        source: w.friendly_name || 'Weather'
      };
    }
    var np = pickMusic(list, cfg.ha.mediaEntity);
    if (np) {
      var a = np.attributes || {};
      out.nowPlaying = {
        playing: true,
        title: text(a.media_title),
        artist: text(a.media_artist),
        album: text(a.media_album_name),
        source: text(a.friendly_name),
        artwork: null,
        artworkThumb: null
      };
    }
    return out;
  }

  function artworkKey(entity) {
    if (!entity) return '';
    var a = entity.attributes || {};
    return JSON.stringify([entity.entity_id, text(a.entity_picture), text(a.media_title),
      text(a.media_artist), text(a.media_album_name)]);
  }

  function snapshot(list, cfg, done, immediate, artworkLoader) {
    var out = model(list, cfg, immediate ? cfg.enabled.weather : true);
    var np = pickMusic(list, cfg.ha.mediaEntity);
    if (np && np.attributes.entity_picture) {
      var completed = false;
      (artworkLoader || loadArtwork)(np, cfg.ha.url, 'Bearer ' + cfg.ha.token, function (durl) {
        completed = true;
        if (durl) {
          out.nowPlaying.artwork = durl.src;
          out.nowPlaying.artworkThumb = durl.thumb || null;
        }
        if (done) done(out);
      });
      if (immediate && !completed && done) done(out);
      return;
    }
    if (done) done(out);
  }

  function refresh(done) {
    var cfg = load();
    if (window.WidgetPreview) {
      window.WidgetPreview.refresh(cfg, function (snap) { if (done) done(snap); });
      return;
    }
    if (!cfg.ha.url || !cfg.ha.token) { if (done) done(null); return; }
    var auth = 'Bearer ' + cfg.ha.token;
    xhrGet(cfg.ha.url.replace(/\/$/, '') + '/api/states', {
      Authorization: auth,
      Accept: 'application/json'
    }, function (response) {
      if (response === null) { if (done) done(null); return; }
      var list;
      try { list = JSON.parse(response); } catch (e) { if (done) done(null); return; }
      if (Object.prototype.toString.call(list) !== '[object Array]') { if (done) done(null); return; }
      snapshot(list, cfg, done);
    });
  }

  function watch(done) {
    var cfg = load();
    var stopped = false;
    var socket = null;
    var retry = null;
    var deadline = null;
    var heartbeat = null;
    var delay = 1000;
    var generation = 0;
    var artworkCache = null;

    function publish(value) { if (!stopped && done) done(value); }

    function disposeSocket() {
      generation++;
      clearTimeout(deadline);
      clearTimeout(heartbeat);
      deadline = null;
      heartbeat = null;
      artworkCache = null;
      if (!socket) return;
      socket.onopen = socket.onmessage = socket.onerror = socket.onclose = null;
      try { socket.close(); } catch (_) {}
      socket = null;
    }

    function disconnected(reconnect) {
      disposeSocket();
      publish(null);
      if (stopped || !reconnect || retry !== null) return;
      retry = setTimeout(function () { retry = null; connect(); }, delay);
      delay = Math.min(delay * 2, 30000);
    }

    function connect() {
      if (stopped) return;
      var states = Object.create(null);
      var queued = [];
      var initialized = false;
      var phase = 'auth';
      var signature = null;
      var nextId = 3;
      var pingId = null;

      function relevant(id) {
        return typeof id === 'string' &&
          (id.indexOf('media_player.') === 0 || id.indexOf('weather.') === 0);
      }

      function change(data) {
        if (!data || !relevant(data.entity_id)) return false;
        if (data.new_state && data.new_state.entity_id === data.entity_id) states[data.entity_id] = data.new_state;
        else delete states[data.entity_id];
        return true;
      }

      function render() {
        var list = Object.keys(states).map(function (id) { return states[id]; });
        var key = artworkKey(pickMusic(list, cfg.ha.mediaEntity));
        var nextSignature = JSON.stringify([model(list, cfg, cfg.enabled.weather), key]);
        if (signature === nextSignature) return;
        signature = nextSignature;
        var current = ++generation;
        snapshot(list, cfg, function (value) {
          if (current === generation) publish(value);
        }, true, cachedArtwork);
      }

      function cachedArtwork(entity, haBase, auth, done) {
        var key = artworkKey(entity);
        if (artworkCache && artworkCache.key === key) {
          if (artworkCache.pending) artworkCache.callbacks.push(done);
          else done(artworkCache.value);
          return;
        }
        var entry = {key: key, pending: true, value: null, callbacks: [done]};
        artworkCache = entry;
        loadArtwork(entity, haBase, auth, function (value) {
          entry.pending = false;
          entry.value = value;
          var callbacks = entry.callbacks;
          entry.callbacks = [];
          for (var i = 0; i < callbacks.length; i++) callbacks[i](value);
        });
      }

      function send(value) { socket.send(JSON.stringify(value)); }

      function schedulePing() {
        heartbeat = setTimeout(function () {
          heartbeat = null;
          if (stopped || socket !== connection) return;
          try {
            pingId = nextId++;
            send({id: pingId, type: 'ping'});
            deadline = setTimeout(function () {
              if (socket === connection) disconnected(true);
            }, 10000);
          } catch (_) { disconnected(true); }
        }, 30000);
      }

      try {
        socket = new WebSocket(cfg.ha.url.replace(/\/$/, '').replace(/^http:/i, 'ws:').replace(/^https:/i, 'wss:') + '/api/websocket');
        var connection = socket;
        deadline = setTimeout(function () { if (socket === connection) disconnected(true); }, 10000);
        socket.onerror = socket.onclose = function () { if (socket === connection) disconnected(true); };
        socket.onmessage = function (event) {
          if (stopped || socket !== connection) return;
          try {
            var message = JSON.parse(event.data);
            if (!message || typeof message.type !== 'string') { disconnected(true); return; }
            if (message.type === 'auth_invalid') { disconnected(false); return; }
            if (message.type === 'auth_required' && phase === 'auth') {
              phase = 'auth-sent';
              send({type: 'auth', access_token: cfg.ha.token});
            } else if (message.type === 'auth_ok' && phase === 'auth-sent') {
              phase = 'subscribing';
              send({id: 1, type: 'subscribe_events', event_type: 'state_changed'});
            } else if (message.type === 'result' && message.id === 1 && phase === 'subscribing') {
              if (!message.success) { disconnected(false); return; }
              phase = 'snapshot';
              send({id: 2, type: 'get_states'});
            } else if (message.type === 'result' && message.id === 2 && phase === 'snapshot') {
              if (!message.success || Object.prototype.toString.call(message.result) !== '[object Array]') {
                disconnected(true); return;
              }
              for (var i = 0; i < message.result.length; i++) {
                var entity = message.result[i];
                if (entity && relevant(entity.entity_id)) states[entity.entity_id] = entity;
              }
              for (var j = 0; j < queued.length; j++) change(queued[j]);
              queued = [];
              initialized = true;
              phase = 'watching';
              delay = 1000;
              clearTimeout(deadline);
              deadline = null;
              render();
              schedulePing();
            } else if (message.type === 'pong' && pingId !== null && message.id === pingId) {
              pingId = null;
              clearTimeout(deadline);
              deadline = null;
              schedulePing();
            } else if (message.type === 'event' && message.id === 1 &&
                message.event && message.event.event_type === 'state_changed') {
              var data = message.event.data;
              if (!data || !relevant(data.entity_id)) return;
              if (!initialized) queued.push(data);
              else if (change(data)) render();
            }
          } catch (_) { disconnected(true); }
        };
      } catch (_) { disconnected(true); }
    }

    if (window.WidgetPreview) {
      window.WidgetPreview.refresh(cfg, publish);
    } else if (!cfg.ha.url || !cfg.ha.token) {
      publish(null);
    } else {
      connect();
    }
    return function () {
      stopped = true;
      clearTimeout(retry);
      retry = null;
      disposeSocket();
    };
  }

  return { load: load, save: save, subscribe: subscribe, refresh: refresh, watch: watch };
})();
