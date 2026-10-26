const assert = require('node:assert/strict');
const vm = require('node:vm');
const {compile} = require('../scripts/compile-tv-web.cjs');
const acorn = require('acorn');
const {spawnSync} = require('node:child_process');
const postcss = require('postcss');

(async () => {
  const source = {
    'index.html': '<html><head><title>Test</title></head><body><script src="app.js"></script><script>const inline = () => 7; window.inlineResult = inline();</script></body></html>',
    'app.js': 'const app = {title: "Test"}; window.result = [app].findIndex(x => x?.title === "Test"); window.copy = Object.assign({}, app); window.includes = [1, 2].includes(2);',
    'style.css': '.viewport {position:absolute;inset:0;color:#1234}',
    'apps.js': 'window.TV_APPS = {apps: []};'
  };
  const output = await compile(source);
  assert.equal(output['apps.js'], source['apps.js'], 'compatible classic scripts must retain their bytes');
  assert(!output['home-ui.js'], 'legacy packages must not acquire a Home UI bundle');
  acorn.parse(output['app.js'], {ecmaVersion: 5});
  assert(output['index.html'].indexOf('src="compat-polyfills.js"') < output['index.html'].indexOf('src="app.js"'), 'polyfills must run before all app scripts');
  const context = vm.createContext({setTimeout, clearTimeout});
  vm.runInContext('window=this; delete Array.prototype.findIndex; delete Array.prototype.includes; delete Object.assign;', context);
  vm.runInContext(output['compat-polyfills.js'], context);
  vm.runInContext(output['app.js'], context);
  assert.equal(context.result, 0);
  assert.equal(context.copy.title, 'Test');
  assert.equal(context.includes, true);
  const inline = output['index.html'].match(/<script>([\s\S]*?)<\/script>/)[1];
  acorn.parse(inline, {ecmaVersion: 5});
  vm.runInContext(inline, context);
  assert.equal(context.inlineResult, 7, 'inline companion scripts must also be transpiled');
  assert(!/\binset\s*:/.test(output['style.css']));
  for (const edge of ['top', 'right', 'bottom', 'left']) assert(output['style.css'].includes(edge + ':0'), edge + ' must be explicit');
  assert.equal(source['app.js'].slice(0, 5), 'const', 'compilation must not mutate source inputs');
  const repeated = await compile(output);
  assert.equal((repeated['index.html'].match(/src="compat-polyfills.js"/g) || []).length, 1, 'packaging twice must not inject polyfills twice');
  await assert.rejects(() => compile({'style.css': '.row{display:flex;gap:12px}'}), /flexbox-gap|gap/, 'untransformed flex gap must block packaging');
  await assert.rejects(() => compile({'style.css': '.row{display:grid;grid-template-columns:1fr 1fr}'}), /css-grid|Grid/, 'unsupported grid must not silently reach the TV');
  await assert.rejects(() => compile({'index.html': '<head><style>.row{display:flex;gap:12px}</style></head>'}), /flexbox-gap|gap/, 'style elements must pass the same CSS gate');
  await assert.rejects(() => compile({'index.html': '<head></head><body style="display:grid"></body>'}), /css-grid|Grid/, 'style attributes must pass the same CSS gate');
  const styled = await compile({'index.html': '<head></head><body style="position:absolute;inset:0"></body>'});
  assert(!/inset\s*:/.test(styled['index.html']), 'inline inset must be transformed');
  await assert.rejects(() => compile({'style.css': '.text{overflow-wrap:anywhere}'}), /anywhere/, 'unsupported values missed by doiuse must also fail');
  await assert.rejects(() => compile({'style.css': '.row{overflow:clip}'}), /css-overflow|overflow/, 'overflow exception must not allow newer values');
  const modules = {
    'index.html': '<head></head><body><script src="home-ui.js"></script><script src="apps.js"></script></body>',
    'apps.js': source['apps.js'],
    'ui/index.jsx': "import {h, render} from 'nano-jsx/lib/core.js'; import {Card} from './card'; window.HomeUI = render(<Card title='Works' />);",
    'ui/card.jsx': "import {h} from 'nano-jsx/lib/core.js'; import {label} from './label.js'; export const Card = ({title}) => <article class='card'>{label(title)}</article>;",
    'ui/label.js': "export const label = title => ['Nano', title].flat().join(' ');"
  };
  const bundled = await compile(modules);
  acorn.parse(bundled['home-ui.js'], {ecmaVersion: 5});
  assert(!Object.keys(bundled).some(name => /^ui\//.test(name)), 'module source must not be packaged');
  assert(bundled['home-ui-LICENSE.txt'].includes('MIT'), 'Nano JSX license must ship with its code');
  assert.equal(bundled['apps.js'], modules['apps.js']);
  assert(bundled['index.html'].indexOf('src="compat-polyfills.js"') < bundled['index.html'].indexOf('src="home-ui.js"'));
  const uiContext = vm.createContext({setTimeout, clearTimeout, document: {
    createElement(tagName) {
      return {tagName, nodeType: 1, children: [], attributes: {},
        setAttribute(name, value) {this.attributes[name] = value;},
        appendChild(child) {this.children.push(child);}};
    },
    createTextNode(text) {return {nodeType: 3, textContent: text};}
  }});
  vm.runInContext('window=this; delete Array.prototype.flat; delete Object.assign;', uiContext);
  vm.runInContext(bundled['compat-polyfills.js'], uiContext);
  vm.runInContext(bundled['home-ui.js'], uiContext);
  assert.equal(uiContext.HomeUI.tagName, 'article');
  assert.equal(uiContext.HomeUI.attributes.class, 'card');
  assert.equal(uiContext.HomeUI.children[0].textContent, 'Nano Works');
  await assert.rejects(() => compile({...modules, 'ui/index.jsx': "import './missing.jsx';"}), /Missing supplied Home UI module/, 'missing modules must fail rather than read the checkout');
  await assert.rejects(() => compile({...modules, 'ui/index.jsx': "import '../apps.js';"}), /Missing supplied Home UI module/, 'modules may not import classic scripts outside ui');
  const python = spawnSync('python3', ['-c',
    "import json, sys; sys.path.insert(0, 'scripts'); from tv_web_build import compile_web; files=json.load(sys.stdin); result=compile_web({name: text.encode() for name,text in files.items()}); print(json.dumps({name: raw.decode() for name,raw in result.items()}))"
  ], {input: JSON.stringify({...modules, 'asset.txt': 'keep asset'}), encoding: 'utf8'});
  assert.equal(python.status, 0, python.stderr);
  const staged = JSON.parse(python.stdout);
  assert(!Object.keys(staged).some(name => /^ui\//.test(name)), 'Python packaging must honor deleted module keys');
  assert.equal(staged['asset.txt'], 'keep asset');
  assert(staged['home-ui.js']);
  const themed = await compile({'style.css': 'html, html.theme-classic {--bg:#000;--card:#111} html.theme-midnight {--bg:#050510;--card:#0d0d1a} html.theme-pixel {--bg:#0a1a0a;--card:#102010} html, body {background:var(--bg)} .card {background:var(--card)}'});
  const themeRules = postcss.parse(themed['style.css']);
  for (const [theme, background, card] of [['midnight', '#050510', '#0d0d1a'], ['pixel', '#0a1a0a', '#102010']]) {
    const bodyRule = themeRules.nodes.find(rule => rule.selector === 'html.theme-' + theme + ', html.theme-' + theme + ' body');
    const cardRule = themeRules.nodes.find(rule => rule.selector === 'html.theme-' + theme + ' .card');
    assert.equal(bodyRule.nodes[0].value, background, 'compiled body must follow the selected palette');
    assert.equal(cardRule.nodes[0].value, card, 'compiled card must follow the selected palette');
  }
  const states = await compile({'style.css': 'html {--border:red} html.theme-pixel {--border:green} .pill {border:2px solid var(--border)} .pill.focused {border-color:transparent;transform:scale(1.04)} .pill.disabled {border:0} @keyframes pulse {from {opacity:0} to {opacity:1}}'});
  const stateRules = postcss.parse(states['style.css']);
  const focused = stateRules.nodes.find(rule => rule.selector === 'html.theme-pixel .pill.focused');
  const disabled = stateRules.nodes.find(rule => rule.selector === 'html.theme-pixel .pill.disabled');
  assert(focused, 'literal focus declarations must receive the same palette scope as the base rule');
  assert.equal(focused.nodes.find(declaration => declaration.prop === 'border-color').value, 'transparent');
  assert.equal(disabled.nodes.find(declaration => declaration.prop === 'border').value, '0');
  assert(stateRules.nodes.indexOf(focused) > stateRules.nodes.findIndex(rule => rule.selector === 'html.theme-pixel .pill'));
  const animation = stateRules.nodes.find(rule => rule.type === 'atrule' && rule.name === 'keyframes');
  assert.deepEqual(animation.nodes.map(rule => rule.selector), ['from', 'to'], 'keyframe steps must not be scoped as element selectors');
  const statesAgain = await compile(states);
  assert.equal(statesAgain['style.css'], states['style.css'], 'theme compilation must not duplicate variants on repeated packaging');
  console.log('PASS ES5 scripts and inline scripts, missing built-ins, physical CSS offsets, polyfill ordering and idempotent HTML');
  console.log('PASS supplied ES module/JSX bundle, Nano JSX rendering, ES5 gate, module isolation, license and Python packaging');
})().catch(error => {console.error(error); process.exitCode = 1;});
