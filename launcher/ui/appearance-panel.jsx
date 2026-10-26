import { h } from 'nano-jsx/lib/core.js';
import { preferences, setPreference } from './preferences.js';

export function mountAppearance(container) {
  const tr = text => window.HomeI18n ? window.HomeI18n.t(text) : text;
  const message = <p class="appearance-error" role="status" />;
  function select(key, value) {
    message.textContent = setPreference(key, value) ? '' : tr("Couldn't save changes. Please try again.");
    refresh();
  }
  const existing = <button type="button" data-appearance="existing" onClick={() => select('appearance', 'existing')}>{tr('Existing')}</button>;
  const tvos = <button type="button" data-appearance="tvos" onClick={() => select('appearance', 'tvos')}>tvOS</button>;
  const effects = <button type="button" role="switch" onClick={() => select('reducedEffects', !preferences().reducedEffects)}>{tr('Reduce effects')}</button>;
  function refresh() {
    const state = preferences();
    existing.setAttribute('aria-pressed', String(state.appearance === 'existing'));
    tvos.setAttribute('aria-pressed', String(state.appearance === 'tvos'));
    effects.setAttribute('aria-checked', String(state.reducedEffects));
  }
  container.appendChild(<section class="appearance-panel" aria-labelledby="appearanceHeading">
    <h3 id="appearanceHeading">{tr('Home screen')}</h3>
    <div class="renewal-actions appearance-options">{existing}{tvos}{effects}</div>
    {message}
  </section>);
  refresh();
}
