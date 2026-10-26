const assert = require('node:assert/strict');
const path = require('node:path');
const browserslist = require('browserslist');
const {ESLint} = require('eslint');

const root = path.resolve(__dirname, '..');

(async () => {
  assert.deepEqual(browserslist(undefined, {path: root}), ['chrome 38'],
    'the shared Browserslist configuration must resolve to Chrome 38');

  const eslint = new ESLint({cwd: root});
  const productionPaths = [
    'launcher/compat-regression.js',
    'launcher/ui/compat-regression.jsx',
    'root-edition/ui/compat-regression.js',
    'updater-app/compat-regression.js'
  ];
  for (const filePath of productionPaths) {
    const [unsupported] = await eslint.lintText(
      'if (window.enabled) { fetch("/data"); new AbortController(); }', {filePath});
    assert.equal(unsupported.errorCount, 2,
      filePath + ': unsupported browser APIs inside ordinary conditionals must fail');
    for (const api of ['fetch', 'AbortController']) {
      assert(unsupported.messages.some(message => message.ruleId === 'compat/compat' &&
        message.severity === 2 && message.message.includes(api) && message.message.includes('Chrome 38')),
      filePath + ': missing Chrome 38 compatibility error for ' + api);
    }

    const [supported] = await eslint.lintText(
      'var request = new XMLHttpRequest(); request.open("GET", "/data"); request.send();', {filePath});
    assert.deepEqual(supported.messages, [], filePath + ': XMLHttpRequest must remain available');
  }

  const [modernSource] = await eslint.lintText(`
    import {h} from 'nano-jsx/lib/core.js';
    export const Card = ({items}) => {
      const copy = {...Object.assign({}, items?.[0] ?? {})};
      const values = Array.from(new Set([copy.title])).includes('Home');
      return <article>{Promise.resolve(values)}</article>;
    };
  `, {filePath: 'launcher/ui/compat-regression.jsx'});
  assert.deepEqual(modernSource.messages, [],
    'bundled JSX, transformed syntax and packaged core-js built-ins must be accepted');

  for (const filePath of [
    'native/service/service.js',
    'tests/compat-regression.cjs',
    'preview/compat-regression.js',
    'scripts/compat-regression.cjs',
    'root-edition/ui/test-firmware-browser.js'
  ]) {
    const config = await eslint.calculateConfigForFile(filePath);
    assert(!config?.rules?.['compat/compat'],
      filePath + ': host tools and Node services must not receive browser compatibility rules');
  }
  console.log('PASS ESLint Chrome 38 compatibility configuration');
})().catch(error => {console.error(error); process.exitCode = 1;});
