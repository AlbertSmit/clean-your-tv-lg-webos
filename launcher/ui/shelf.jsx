import { h } from 'nano-jsx/lib/core.js';

export function createShelf() {
  const element = <section id="homeShelf" aria-hidden="true">
    <div class="shelf-backdrop" />
    <div class="shelf-backdrop-soft" />
    <div class="shelf-shade" />
    <div class="shelf-copy"><img class="shelf-mark" src="assets/shelf-mark.svg" alt="" draggable="false" /></div>
  </section>;
  document.body.insertBefore(element, document.getElementById('viewport'));
  return {
    update(visible, enabled) {
      if (enabled) {
        var backdrop = element.querySelector(visible ? '.shelf-backdrop' : '.shelf-backdrop-soft');
        var image = visible ? 'cinema-backdrop.jpg' : 'cinema-backdrop-shelf.jpg';
        if (!backdrop.style.backgroundImage) backdrop.style.backgroundImage = "url('assets/" + image + "')";
      }
      element.classList.toggle('shelf-visible', visible);
    }
  };
}
