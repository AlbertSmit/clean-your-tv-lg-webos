const compat = require('eslint-plugin-compat');

module.exports = [
  {
    ...compat.configs['flat/recommended'],
    files: ['launcher/**/*.{js,jsx}', 'root-edition/ui/**/*.js', 'updater-app/**/*.js'],
    ignores: ['**/test-*.js'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'script',
      parserOptions: {ecmaFeatures: {jsx: true}}
    },
    settings: {
      // Babel handles syntax; the packaged core-js bundle supplies ES built-ins.
      // Browser APIs (fetch, observers, etc.) must still work on the TV itself.
      polyfills: ['es:all'],
      ignoreConditionalChecks: true
    }
  },
  {
    files: ['launcher/ui/**/*.{js,jsx}'],
    languageOptions: {sourceType: 'module'}
  }
];
