const textures = ['assets/dock-glass-home.jpg', 'assets/dock-glass-grid.jpg'];

export function createDockGlass() {
  let enabled = false, grid = false, current = null;
  const dock = document.getElementById('dockBand');
  const texture = document.getElementById('dockTexture');

  function refresh() {
    const next = textures[grid ? 1 : 0];
    if (next !== current) {
      current = next;
      texture.style.backgroundImage = 'url("' + next + '")';
    }
    texture.style.display = enabled ? 'block' : 'none';
    dock.setAttribute('data-glass', enabled ? 'texture' : 'static');
  }

  return {
    update(tvos, appGrid, reducedEffects) {
      enabled = tvos && !reducedEffects;
      grid = appGrid;
      refresh();
    }
  };
}