import { layoutFor, positionFor, scrollFor } from './layouts.js';
import { preferences, setPreference, subscribe, applyPreferences } from './preferences.js';
import { createTileView, createAddView } from './tile.jsx';
import { createShelf } from './shelf.jsx';
import { mountAppearance } from './appearance-panel.jsx';
import { createStatus } from './status.jsx';
import { createDockGlass } from './dock-glass.js';

applyPreferences();
window.HomeUI = {
  layoutFor, positionFor, scrollFor, preferences, setPreference, subscribe,
  createTileView, createAddView, createShelf, createStatus, createDockGlass, mountAppearance
};
