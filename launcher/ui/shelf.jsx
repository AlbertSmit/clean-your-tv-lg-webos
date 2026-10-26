import { h } from 'nano-jsx/lib/core.js';

export function createShelf() {
  const element = <section id="homeShelf" aria-hidden="true">
    <div class="shelf-backdrop" />
    <div class="shelf-backdrop-soft" />
    <div class="shelf-shade" />
    <div class="shelf-copy"><div class="shelf-title">Sundown</div></div>
  </section>;
  document.body.insertBefore(element, document.getElementById('viewport'));
  return {
    update(visible) {
      element.classList.toggle('shelf-visible', visible);
    }
  };
}
