const appearanceKey = 'cytv-appearance';
const effectsKey = 'cytv-reduced-effects';
const widgetsKey = 'cytv-widgets-visible';
const listeners = [];

function read(key) {
  try { return localStorage.getItem(key); } catch (_) { return null; }
}

let appearance = read(appearanceKey) === 'tvos' ? 'tvos' : 'existing';
let reducedEffects = read(effectsKey) === 'true';
let widgetsVisible = read(widgetsKey) !== 'false';

export function preferences() {
  return { appearance, reducedEffects, widgetsVisible };
}

export function applyPreferences() {
  document.documentElement.classList.toggle('home-tvos', appearance === 'tvos');
  document.documentElement.classList.toggle('reduced-effects', reducedEffects);
}

export function setPreference(key, value) {
  if (key === 'appearance' && value !== 'existing' && value !== 'tvos') return false;
  if ((key === 'reducedEffects' || key === 'widgetsVisible') && typeof value !== 'boolean') return false;
  if (key !== 'appearance' && key !== 'reducedEffects' && key !== 'widgetsVisible') return false;
  try {
    localStorage.setItem(key === 'appearance' ? appearanceKey : key === 'widgetsVisible' ? widgetsKey : effectsKey, String(value));
  } catch (_) { return false; }
  if (key === 'appearance') appearance = value;
  else if (key === 'widgetsVisible') widgetsVisible = value;
  else reducedEffects = value;
  applyPreferences();
  listeners.forEach(listener => listener(preferences()));
  return true;
}

export function subscribe(listener) {
  listeners.push(listener);
  return () => {
    const index = listeners.indexOf(listener);
    if (index >= 0) listeners.splice(index, 1);
  };
}
