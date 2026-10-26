import { h } from 'nano-jsx/lib/core.js';
import { widgetLayoutFor } from './layouts.js';

const CFG_KEY = 'cytv-widgets';
const DEFAULTS = {
  enabled: { clock: true, nowPlaying: true, weather: false },
  ha: { url: '', token: '', mediaEntity: '', weatherEntity: '' }
};

function readConfig() {
  try {
    const raw = localStorage.getItem(CFG_KEY);
    if (raw) {
      const c = JSON.parse(raw);
      return {
        enabled: Object.assign({}, DEFAULTS.enabled, c.enabled || {}),
        ha: Object.assign({}, DEFAULTS.ha, c.ha || {})
      };
    }
  } catch (_) {}
  return JSON.parse(JSON.stringify(DEFAULTS));
}

function saveConfig(cfg) {
  if (window.WidgetData && window.WidgetData.save) {
    window.WidgetData.save(cfg);
    return;
  }
  try { localStorage.setItem(CFG_KEY, JSON.stringify(cfg)); } catch (_) {}
}

function fmtTime(now) {
  const f = window.HomeI18n;
  if (f && f.formatTime) {
    return { time: f.formatTime(now), ampm: '', date: f.formatDate(now) };
  }
  const hour = now.getHours(), h12 = hour % 12 || 12;
  const min = ('0' + now.getMinutes()).slice(-2);
  const weekdays = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  const months = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  return {
    time: h12 + ':' + min,
    ampm: hour < 12 ? 'am' : 'pm',
    date: weekdays[now.getDay()] + '  ' + now.getDate() + ' ' + months[now.getMonth()]
  };
}

function clockTick(clockEl, hourHand, minuteHand, dateEl) {
  const now = new Date();
  const formatted = fmtTime(now);
  hourHand.setAttribute('transform', 'rotate(' + (now.getHours() % 12 * 30 + now.getMinutes() / 2) + ' 125 125)');
  minuteHand.setAttribute('transform', 'rotate(' + now.getMinutes() * 6 + ' 125 125)');
  clockEl.setAttribute('aria-label', formatted.time + ' ' + formatted.ampm + ', ' + formatted.date);
  dateEl.textContent = window.HomeI18n && window.HomeI18n.formatDate
    ? window.HomeI18n.formatDate(now, { weekday: 'short', day: 'numeric' })
    : formatted.date.split(' ')[0].slice(0, 3) + ' ' + now.getDate();
}

function applyRect(el, rect) {
  el.style.left = rect.left + 'px';
  el.style.top = rect.top + 'px';
  el.style.width = rect.width + 'px';
  el.style.height = rect.height + 'px';
}

const WX_ICONS = {
  sunny: 'M24 14a10 10 0 1 0 0 20 10 10 0 0 0 0-20zM24 3v5M24 40v5M3 24h5M40 24h5M9 9l4 4M35 35l4 4M9 39l4-4M35 13l4-4',
  'clear-night': 'M34 34A17 17 0 0 1 15 9a18 18 0 1 0 26 23 17 17 0 0 1-7 2z',
  partlycloudy: 'M30 8a9 9 0 1 0 0 18 9 9 0 0 0 0-18zM30 1v3M43 17h4M40 6l3-3M17 6l-3-3M10 24a9 9 0 0 1 17-3 7 7 0 1 1 5 14H12a6 6 0 0 1-2-11z',
  cloudy: 'M10 18a11 11 0 0 1 21-3 10 10 0 1 1 4 19H12a8 8 0 0 1-2-16z',
  fog: 'M7 14h34M4 22h34M9 30h34M5 38h28',
  rainy: 'M10 13a10 10 0 0 1 19-2 8 8 0 1 1 4 15H12a7 7 0 0 1-2-13zM14 33l-3 7M25 33l-3 7M36 33l-3 7',
  snowy: 'M10 13a10 10 0 0 1 19-2 8 8 0 1 1 4 15H12a7 7 0 0 1-2-13zM16 33v10M11 38h10M34 33v10M29 38h10',
  windy: 'M4 15h27a6 6 0 1 0-6-6M9 24h30M4 33h27a6 6 0 1 1-6 6',
  thunderstorm: 'M10 13a10 10 0 0 1 19-2 8 8 0 1 1 4 15H12a7 7 0 0 1-2-13zM25 29l-8 10h8l-4 8 13-13h-9l4-5'
};
const WX_LABELS = {
  sunny: 'Sunny', 'clear-night': 'Clear night', partlycloudy: 'Partly cloudy',
  cloudy: 'Cloudy', fog: 'Fog', rainy: 'Rain', snowy: 'Snow', windy: 'Windy',
  thunderstorm: 'Thunderstorm'
};

export function createWidgets(dataSource) {
  let cfg = readConfig();

  const dateEl = <div class="w-clock-date"></div>;
  const clockEl = (
    <div class="glass-cell w-clock">
      <svg class="w-clock-face" viewBox="0 0 250 250" aria-hidden="true">
        <text class="w-clock-twelve" x="125" y="106" text-anchor="middle">12</text>
        <text x="46" y="170" text-anchor="middle">9</text>
        <text x="204" y="170" text-anchor="middle">3</text>
        <text x="125" y="237" text-anchor="middle">6</text>
        <line class="w-clock-hour" x1="125" y1="130" x2="125" y2="68" />
        <line class="w-clock-minute" x1="125" y1="137" x2="125" y2="35" />
        <circle class="w-clock-pivot" cx="125" cy="125" r="5" />
      </svg>
      {dateEl}
    </div>
  );

  const hourHand = clockEl.querySelector('.w-clock-hour');
  const minuteHand = clockEl.querySelector('.w-clock-minute');

  // — Weather cell —
  const musicGlyph = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>';
  const tempEl = <div class="w-wx-temp"></div>;
  const labelEl = <div class="w-wx-label"></div>;
  const metaEl = <div class="w-wx-meta"></div>;
  const wxEl = (
    <div class="glass-cell w-wx">
      <svg class="w-wx-icon" viewBox="0 0 48 48" aria-hidden="true"></svg>
      <div class="w-wx-copy">{tempEl}{labelEl}{metaEl}</div>
    </div>
  );

  const wxIconEl = wxEl.querySelector('.w-wx-icon');

  // — Now Playing cell —
  const artEl = <div class="w-np-art"></div>;
  artEl.innerHTML = '<div class="w-np-art-thumb" aria-hidden="true"></div><span class="w-np-glyph" aria-hidden="true"></span><div class="w-np-shimmer" aria-hidden="true"></div>';
  const artThumbEl = artEl.querySelector('.w-np-art-thumb');
  const artGlyphEl = artEl.querySelector('.w-np-glyph');
  artGlyphEl.innerHTML = musicGlyph;
  const artImgEl = document.createElement('img');
  artImgEl.alt = '';
  artImgEl.draggable = false;
  artImgEl.decoding = 'async';
  artImgEl.onload = function () {
    artImgEl.classList.add('loaded');
    artEl.classList.remove('loading');
  };
  artEl.appendChild(artImgEl);
  const label = window.HomeI18n ? window.HomeI18n.t('Now Playing') : 'Now Playing';
  const titleEl = <div class="w-np-title"></div>;
  const artistEl = <div class="w-np-artist"></div>;
  const textureEl = <div class="w-np-texture" aria-hidden="true"></div>;
  const npEl = (
    <div class="glass-cell w-np">
      {textureEl}
      <div class="w-np-content">
        {artEl}
        <div class="w-np-copy"><div class="w-np-label">{label}</div>{titleEl}{artistEl}</div>
        <span class="w-np-badge" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M9 18V5l12-2v13" /><circle cx="6" cy="18" r="3" /><circle cx="18" cy="16" r="3" /></svg></span>
      </div>
    </div>
  );

  const root = <aside class="widgets" aria-hidden="true">{clockEl}{wxEl}{npEl}</aside>;
  document.body.appendChild(root);

  const regions = widgetLayoutFor().regions;
  applyRect(clockEl, regions.clock);
  applyRect(wxEl, regions.weather);
  applyRect(npEl, regions.nowPlaying);
  textureEl.style.backgroundPosition = -regions.nowPlaying.left + 'px ' + -regions.nowPlaying.top + 'px';

  let visible = false;
  let snapshot = null;
  let clockTimer = null;
  function setClock(active) {
    if (active && !clockTimer) {
      clockTick(clockEl, hourHand, minuteHand, dateEl);
      clockTimer = setInterval(function () { clockTick(clockEl, hourHand, minuteHand, dateEl); }, 10000);
    } else if (!active && clockTimer) {
      clearInterval(clockTimer);
      clockTimer = null;
    }
  }

  function setWeather(snap) {
    wxEl.style.display = cfg.enabled.weather ? '' : 'none';
    if (!snap || !snap.condition) {
      wxIconEl.innerHTML = '<path d="' + WX_ICONS.cloudy + '"/>';
      tempEl.textContent = '--';
      labelEl.textContent = 'Weather';
      metaEl.textContent = '—';
      return;
    }
    wxIconEl.innerHTML = '<path d="' + (WX_ICONS[snap.condition] || WX_ICONS.cloudy) + '"/>';
    tempEl.textContent = (snap.temp != null ? Math.round(snap.temp) : '') + (snap.unit || '°');
    labelEl.textContent = WX_LABELS[snap.condition] || snap.condition;
    const parts = [];
    if (snap.high != null) parts.push('H ' + Math.round(snap.high) + '°');
    if (snap.low != null) parts.push('L ' + Math.round(snap.low) + '°');
    if (snap.humidity != null) parts.push(snap.humidity + '%');
    metaEl.textContent = parts.length ? parts.join('  ·  ') : '—';
  }

  function hasMusic(snap) {
    return !!(snap && snap.playing && snap.title);
  }

  let lastNP = null;

  function applyNowPlayingVisibility() {
    npEl.classList.toggle('w-np-hidden', !(cfg.enabled.nowPlaying && hasMusic(snapshot && snapshot.nowPlaying)));
  }

  function restartAnimation(el, cls) {
    el.classList.remove(cls);
    void el.offsetWidth;
    el.classList.add(cls);
  }

  function applyArtwork(url, thumb) {
    const has = !!(url && /^data:image\//.test(url));
    artEl.classList.toggle('has-thumb', has);
    artEl.classList.toggle('loading', has);
    const nextSrc = has ? url : '';
    if (artImgEl.getAttribute('src') !== nextSrc) {
      artImgEl.classList.remove('loaded');
      artImgEl.src = nextSrc;
    }
    artThumbEl.style.backgroundImage = has ? 'url("' + (thumb || url) + '")' : '';
  }

  function setNowPlaying(snap) {
    applyNowPlayingVisibility();
    if (!hasMusic(snap)) {
      applyArtwork(null);
      titleEl.textContent = '';
      artistEl.textContent = '';
      lastNP = null;
      return;
    }
    const changed = !lastNP ||
      lastNP.title !== snap.title ||
      lastNP.artist !== (snap.artist || '') ||
      lastNP.artwork !== snap.artwork;
    applyArtwork(snap.artwork, snap.artworkThumb);
    titleEl.textContent = snap.title;
    artistEl.textContent = snap.artist || '';
    if (changed) {
      restartAnimation(titleEl, 'w-np-animate');
      restartAnimation(artistEl, 'w-np-animate');
      restartAnimation(artEl, 'w-np-art-animate');
    }
    lastNP = { title: snap.title, artist: snap.artist || '', artwork: snap.artwork };
  }

  function update(snap) {
    snapshot = snap;
    show(visible);
    setNowPlaying(snap ? snap.nowPlaying : null);
    setWeather(snap ? snap.weather : null);
  }

  function show(nextVisible) {
    cfg = readConfig();
    visible = !!nextVisible;
    clockEl.style.display = cfg.enabled.clock ? '' : 'none';
    wxEl.style.display = cfg.enabled.weather ? '' : 'none';
    applyNowPlayingVisibility();
    root.classList.toggle('widgets-visible', visible);
    setClock(visible && !document.hidden && cfg.enabled.clock);
  }

  function setConfig(next) {
    Object.assign(cfg, next);
    saveConfig(cfg);
    update(snapshot);
    show(visible);
  }

  document.addEventListener('visibilitychange', function () { show(visible); });
  update(null);
  show(false);
  return {
    root,
    update,
    show,
    setConfig,
    config: function () { return cfg; }
  };
}

function makeField(label, key, type, cfg) {
  const input = <input type={type || 'text'} class="widget-field" spellcheck="false" />;
  input.value = cfg.ha[key] || '';
  const row = (
    <label class="widget-field-row">
      <span>{label}</span>
      {input}
    </label>
  );
  return { row, input };
}

export function mountWidgetSettings(container, opts) {
  const cfg = readConfig();
  const tr = t => window.HomeI18n ? window.HomeI18n.t(t) : t;
  const err = <p class="widget-error" role="status" />;

  function toggle(key, btn) {
    cfg.enabled[key] = !cfg.enabled[key];
    btn.setAttribute('aria-checked', String(cfg.enabled[key]));
    saveConfig(cfg);
    if (opts && opts.onChange) opts.onChange();
  }

  function makeSwitch(key, label) {
    const b = <button type="button" role="switch" class="widget-toggle" />;
    b.textContent = label;
    b.setAttribute('aria-checked', String(cfg.enabled[key]));
    b.setAttribute('aria-label', label);
    b.addEventListener('click', function () { toggle(key, b); });
    return b;
  }

  const u = makeField(tr('Home Assistant URL'), 'url', 'text', cfg);
  const t = makeField(tr('Long-lived token'), 'token', 'password', cfg);
  const m = makeField(tr('Media player entity (optional)'), 'mediaEntity', 'text', cfg);
  const w = makeField(tr('Weather entity (optional)'), 'weatherEntity', 'text', cfg);

  const sClock = makeSwitch('clock', 'Clock');
  const sNP = makeSwitch('nowPlaying', 'Now Playing');
  const sWX = makeSwitch('weather', 'Weather');

  const save = <button type="button" class="widget-save" />;
  save.textContent = tr('Save widget sources');
  save.addEventListener('click', function () {
    cfg.ha.url = u.input.value.trim();
    cfg.ha.token = t.input.value.trim();
    cfg.ha.mediaEntity = m.input.value.trim();
    cfg.ha.weatherEntity = w.input.value.trim();
    saveConfig(cfg);
    err.textContent = tr('Saved');
    if (opts && opts.onChange) opts.onChange();
  });

  const section = (
    <section class="widget-settings" aria-labelledby="widgetsHeading">
      <h3 id="widgetsHeading">{tr('Widgets')}</h3>
      <div class="renewal-actions appearance-options">{sClock}{sNP}{sWX}</div>
      <div class="widget-fields">{u.row}{t.row}{m.row}{w.row}</div>
      <div class="renewal-actions">{save}</div>
      {err}
    </section>
  );
  container.appendChild(section);
  return {
    setError: function (message) { err.textContent = message; }
  };
}
