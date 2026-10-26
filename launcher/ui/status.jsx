import { h } from 'nano-jsx/lib/core.js';

export function createStatus(onOpen) {
  const title = window.HomeI18n ? window.HomeI18n.t('Home settings') : 'Home settings';
  const time = <span class="status-time" />;
  function open() { if (onOpen() === false) element.blur(); }
  const element = <button type="button" id="homeStatus" aria-label={title} aria-expanded="false" aria-controls="topButtons" onClick={open} onFocus={open}>
    {time}<span class="status-avatar" aria-hidden="true"><span class="avatar-head" /><span class="avatar-body" /></span>
  </button>;
  document.body.appendChild(element);
  return {
    update(value) { time.textContent = value.replace(/^0(?=\d:)/, '').replace(/\s+/g, ' '); },
    expanded(value) { element.setAttribute('aria-expanded', String(value)); },
    reset() { element.blur(); }
  };
}
