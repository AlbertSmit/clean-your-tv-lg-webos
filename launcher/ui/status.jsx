import { h } from 'nano-jsx/lib/core.js';
import { preferences, subscribe } from './preferences.js';

export function createStatus(onOpen, onWidgetsFocus, onChurchFocus) {
  const title = window.HomeI18n ? window.HomeI18n.t('Home settings') : 'Home settings';
  const time = <span class="status-time" />;
  function open() { if (onOpen() === false) element.blur(); }
  const element = <button type="button" id="homeStatus" aria-label={title} aria-expanded="false" aria-controls="topButtons" onClick={open} onFocus={open}>
    {time}<span class="status-avatar" aria-hidden="true"><img src="assets/profile-avatar.jpg" alt="" draggable="false" /></span>
  </button>;
  const widgetsLabel = window.HomeI18n ? window.HomeI18n.t('Widgets') : 'Widgets';
  const widgetsButton = <button type="button" id="btnWidgets" class="status-widgets" role="switch" aria-label={widgetsLabel} onFocus={() => { if (onWidgetsFocus() === false) widgetsButton.blur(); }}>
    <span class="status-complications" aria-hidden="true"><i /><i /><i /><i /></span>
  </button>;
  const churchButton = <button type="button" id="btnChurch" class="status-church" aria-label="Kerkdienst" onFocus={() => { if (onChurchFocus() === false) churchButton.blur(); }} />;
  churchButton.innerHTML = '<span class="church-item"><span class="church-place">Nieuwe Kerk</span><span class="church-area">Wittevrouwen</span></span>';
  function churchHours(now) {
    const minutes = now.getHours() * 60 + now.getMinutes();
    return minutes >= 9 * 60 + 30 && minutes < 12 * 60;
  }
  function sync() {
    widgetsButton.setAttribute('aria-checked', String(preferences().widgetsVisible));
    churchButton.classList.toggle('church-off', !preferences().widgetsVisible || !churchHours(new Date()));
  }
  document.body.appendChild(element);
  document.body.appendChild(widgetsButton);
  document.body.appendChild(churchButton);
  sync();
  subscribe(sync);
  return {
    update(value) { sync(); time.textContent = value.replace(/^0(?=\d:)/, '').replace(/\s+/g, ' '); },
    expanded(value) { sync(); element.setAttribute('aria-expanded', String(value)); },
    reset() { sync(); element.blur(); widgetsButton.blur(); churchButton.blur(); }
  };
}
