import { h } from 'nano-jsx/lib/core.js';

export function createTileView(app) {
  const element = <div class="item" data-app-id={app.id} role="button" aria-label={app.title}>
    <div class="card"><img alt="" draggable="false" /></div>
    <div class="name">{app.title}</div>
  </div>;
  return { element, card: element.querySelector('.card'), image: element.querySelector('img') };
}

export function createAddView(title) {
  return <div class="item add-app" role="button" aria-label={title}>
    <div class="card"><svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 10v28M10 24h28" /></svg></div>
    <div class="name">{title}</div>
  </div>;
}
