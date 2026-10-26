/* Theme panel for Settings - adds theme selector with live preview */
(function () {
  'use strict';

  const THEMES = [
    { id: 'classic', label: 'Classic', preview: 'Default clean look' },
    { id: 'midnight', label: 'Midnight', preview: 'Deep blue, easy on eyes' },
    { id: 'pixel', label: 'Pixel', preview: 'Retro green terminal' },
    { id: 'bloom', label: 'Bloom', preview: 'Warm pink/rose accent' },
    { id: 'amber', label: 'Amber', preview: 'Warm terminal amber' }
  ];

  const STORAGE_KEY = 'cytv-theme';
  const CLASS_PREFIX = 'theme-';

  function applyTheme(themeId) {
    if (!THEMES.some(t => t.id === themeId)) themeId = 'classic';
    const html = document.documentElement;
    THEMES.forEach(t => html.classList.remove(CLASS_PREFIX + t.id));
    if (themeId !== 'classic') {
      html.classList.add(CLASS_PREFIX + themeId);
    }
    try { localStorage.setItem(STORAGE_KEY, themeId); } catch (_) {}
    updateButtonStates(themeId);
  }

  function getCurrentTheme() {
    try { return localStorage.getItem(STORAGE_KEY) || 'classic'; } catch (_) { return 'classic'; }
  }

  function updateButtonStates(activeId) {
    document.querySelectorAll('.theme-btn').forEach(btn => {
      btn.classList.toggle('selected', btn.dataset.theme === activeId);
    });
  }

  function createThemePanel() {
    const panel = document.createElement('section');
    panel.className = 'theme-panel';

    const card = document.createElement('div');
    card.className = 'theme-panel-card';
    panel.appendChild(card);

    const title = document.createElement('h2');
    title.textContent = 'Theme';
    card.appendChild(title);

    const desc = document.createElement('p');
    desc.style.cssText = 'color:var(--fg-dim);font-size:24px;margin-bottom:24px;';
    desc.textContent = 'Choose a color theme. Changes apply instantly and persist across restarts.';
    card.appendChild(desc);

    const options = document.createElement('div');
    options.className = 'theme-options';
    card.appendChild(options);

    THEMES.forEach(theme => {
      const btn = document.createElement('button');
      btn.className = 'theme-btn';
      btn.dataset.theme = theme.id;
      btn.innerHTML = `
        <div class="theme-preview" aria-hidden="true"></div>
        <span>${theme.label}</span>
        <span style="font-size:20px;font-weight:400;color:var(--fg-dim);">${theme.preview}</span>
      `;
      btn.onclick = () => applyTheme(theme.id);
      options.appendChild(btn);
    });

    const current = getCurrentTheme();
    applyTheme(current);

    return panel;
  }

  // Expose for Settings panel to mount
  window.ThemePanel = {
    mount: function (container) {
      const panel = createThemePanel();
      container.appendChild(panel);
      return panel;
    },
    applyTheme: applyTheme,
    getCurrentTheme: getCurrentTheme
  };

  // Auto-apply on load
  document.addEventListener('DOMContentLoaded', function () {
    applyTheme(getCurrentTheme());
  });
})();
