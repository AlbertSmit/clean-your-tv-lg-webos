import { h } from 'nano-jsx/lib/core.js';
import { preferences, subscribe } from './preferences.js';

export function createStatus(onOpen, onWidgetsFocus) {
  const title = window.HomeI18n ? window.HomeI18n.t('Home settings') : 'Home settings';
  const time = <span class="status-time" />;
  function open() { if (onOpen() === false) element.blur(); }
  const element = <button type="button" id="homeStatus" aria-label={title} aria-expanded="false" aria-controls="topButtons" onClick={open} onFocus={open}>
    {time}<span class="status-avatar" aria-hidden="true"><img src="assets/profile.jpg" alt="" draggable="false" /></span>
  </button>;
  const widgetsLabel = window.HomeI18n ? window.HomeI18n.t('Widgets') : 'Widgets';
  const widgetsButton = <button type="button" id="btnWidgets" class="status-widgets" role="switch" aria-label={widgetsLabel} onFocus={() => { if (onWidgetsFocus() === false) widgetsButton.blur(); }}>
    <span class="status-complications" aria-hidden="true"><i /><i /><i /><i /></span>
  </button>;
  function sync() { widgetsButton.setAttribute('aria-checked', String(preferences().widgetsVisible)); }
  document.body.appendChild(element);
  document.body.appendChild(widgetsButton);
  sync();
  subscribe(sync);
  return {
    update(value) { sync(); time.textContent = value.replace(/^0(?=\d:)/, '').replace(/\s+/g, ' '); },
    expanded(value) { sync(); element.setAttribute('aria-expanded', String(value)); },
    reset() { sync(); element.blur(); widgetsButton.blur(); }
  };
}
