// Compile classic webOS scripts separately: bundling their UMD wrappers would
// change their globals. A single ES5 core-js bundle runs before all app scripts.
const fs = require('node:fs');
const path = require('node:path');
const babel = require('@babel/core');
const acorn = require('acorn');
const postcss = require('postcss');
const presetEnv = require('postcss-preset-env');
const doiuse = require('doiuse');
const html = require('parse5');
const {bundleHomeUI, isModule} = require('./bundle-home-ui.cjs');
const targets = require('../package.json').browserslist;
const root = path.resolve(__dirname, '..');
const polyfillsName = 'compat-polyfills.js';

function javascript(code, filename) {
  // Already-compatible scripts keep their bytes and global-script semantics.
  try { acorn.parse(code, {ecmaVersion: 5}); return code; } catch (_) {}
  const output = babel.transformSync(code, {
    filename, cwd: root, configFile: false, babelrc: false, sourceType: 'script',
    presets: [[require.resolve('@babel/preset-env'), {
      targets, forceAllTransforms: true, modules: false, useBuiltIns: false, bugfixes: true
    }]]
  }).code;
  acorn.parse(output, {ecmaVersion: 5});
  return output + '\n';
}

function themeVariants(code, filename) {
  const tree = postcss.parse(code, {from: filename});
  const defaults = {};
  const palettes = new Map();
  tree.walkRules(rule => {
    const definitions = rule.nodes.filter(node => node.type === 'decl' && node.prop.startsWith('--'));
    if (!definitions.length) return;
    for (const selector of rule.selectors) {
      const theme = selector.match(/^html\.(theme-[\w-]+)$/);
      if (selector !== 'html' && !theme) continue;
      const palette = theme ? palettes.get(theme[1]) || {} : defaults;
      for (const declaration of definitions) palette[declaration.prop] = declaration.value;
      if (theme) palettes.set(theme[1], palette);
    }
  });
  // Scope complete rules consistently: cloning only variable declarations would
  // raise their specificity above literal overrides in focus and other states.
  const rules = [];
  tree.walkRules(rule => {rules.push(rule);});
  for (const rule of rules) {
    let parent = rule.parent;
    while (parent && !(parent.type === 'atrule' && /(?:^|-)keyframes$/.test(parent.name))) parent = parent.parent;
    if (parent) continue;
    const declarations = (rule.nodes || []).filter(node => node.type === 'decl' &&
      !node.prop.startsWith('--'));
    if (!declarations.length) continue;
    for (const [theme, overrides] of palettes) {
      const palette = {...defaults, ...overrides};
      const variant = rule.clone({selector: rule.selectors.map(selector =>
        /^html(?=[\s.#[:>+~]|$)/.test(selector) ? selector.replace(/^html/, 'html.' + theme) :
          'html.' + theme + ' ' + selector).join(', ')});
      variant.removeAll();
      for (const declaration of declarations) variant.append(declaration.clone({
        value: declaration.value.replace(/var\(\s*(--[\w-]+)\s*\)/g,
          (reference, name) => Object.hasOwn(palette, name) ? palette[name] : reference)
      }));
      rule.after(variant);
    }
  }
  return tree.toString();
}

async function stylesheet(code, filename) {
  // First, compile CSS custom properties (variables) for Chrome 38 compatibility
  // Stage 0 + explicit feature enables custom-properties transformation
  const compiled = await postcss([
    presetEnv({browsers: targets, stage: 0, preserve: false,
      features: {
        'custom-properties': { preserve: false },
        'logical-properties-and-values': true,
        'hexadecimal-alpha-notation': true
      }})
  ]).process(themeVariants(code, filename), {from: filename, map: false});

  // Values are now literals. Discard unsupported palette definitions, also making
  // repeated compilation a no-op rather than generating another set of variants.
  compiled.root.walkDecls(/^--/, declaration => declaration.remove());
  compiled.root.walkRules(rule => {if (!rule.nodes.length) rule.remove();});

  const unsupported = [];
  compiled.root.walkDecls(/^(overflow-wrap|word-wrap)$/, declaration => {
    if (declaration.value === 'anywhere') unsupported.push(filename + ': ' + declaration.prop + ': anywhere requires a legacy break-word value');
  });
  await postcss([doiuse({browsers: targets, onFeatureUsage: usage => {
    // Ignore css-variables since we transform them via preset-env stage 0
    if (usage.feature === 'css-variables') return;
    // Allow legacy overflow values
    if (usage.feature === 'css-overflow' && /^overflow(?:-[xy])?$/.test(usage.usage.prop) &&
        /^(auto|hidden|scroll|visible)$/.test(usage.usage.value)) return;
    unsupported.push(usage.message);
  }})])
    .process(compiled.css, {from: filename, map: false});
  if (unsupported.length) throw Error(filename + ': unsupported CSS after PostCSS:\n' + unsupported.join('\n'));
  return compiled.root.toString();
}

async function document(code, filename) {
  const tree = html.parse(code);
  let head, hasPolyfills = false;
  async function visit(node) {
    if (node.tagName === 'head') head = node;
    const attrs = node.attrs || [];
    const source = attrs.find(attr => attr.name === 'src');
    if (node.tagName === 'script' && source && source.value === polyfillsName) hasPolyfills = true;
    if (node.tagName === 'style') {
      for (const text of node.childNodes) text.value = await stylesheet(text.value, filename + '.style.css');
    }
    for (const attr of attrs) {
      if (attr.name === 'style') {
        const css = await stylesheet('.inline{' + attr.value + '}', filename + '.attribute.css');
        attr.value = postcss.parse(css).first.nodes.map(node => node.toString()).join(';');
      }
    }
    if (node.tagName === 'script' && !source) {
      const type = attrs.find(attr => attr.name === 'type');
      if (type && type.value === 'module') throw Error(filename + ': use classic scripts, not unbundled ES modules');
      if (!type || /^(text|application)\/javascript$/.test(type.value)) {
        for (const text of node.childNodes) text.value = javascript(text.value, filename + '.inline.js');
      }
    }
    for (const child of node.childNodes || []) await visit(child);
    if (node.content) await visit(node.content);
  }
  await visit(tree);
  if (!hasPolyfills) {
    const script = html.parseFragment('<script src="' + polyfillsName + '"></script>').childNodes[0];
    script.parentNode = head;
    head.childNodes.unshift(script);
  }
  return html.serialize(tree);
}

async function compile(files) {
  const output = {...files};
  const homeUI = await bundleHomeUI(files);
  if (homeUI) {
    for (const name of Object.keys(output)) if (isModule(name)) delete output[name];
    output['home-ui.js'] = javascript(homeUI.code, 'home-ui.js');
    output['home-ui-LICENSE.txt'] = homeUI.license;
  }
  for (const [name, code] of Object.entries(files)) {
    if (name === polyfillsName) continue;
    if (homeUI && (isModule(name) || name === 'home-ui.js')) continue;
    if (name.endsWith('.js')) output[name] = javascript(code, name);
    if (name.endsWith('.css')) output[name] = await stylesheet(code, name);
    if (name.endsWith('.html')) output[name] = await document(code, name);
  }
  if (Object.keys(files).some(name => name.endsWith('.html'))) {
    output[polyfillsName] = fs.readFileSync(require.resolve('core-js-bundle/minified.js'), 'utf8');
    acorn.parse(output[polyfillsName], {ecmaVersion: 5});
    output['compat-LICENSE.txt'] = fs.readFileSync(require.resolve('core-js-bundle/LICENSE'), 'utf8') + '\n' +
      fs.readFileSync(path.join(path.dirname(require.resolve('@babel/core/package.json')), 'LICENSE'), 'utf8');
  }
  return output;
}

exports.compile = compile;
if (require.main === module) {
  let input = '';
  process.stdin.setEncoding('utf8');
  process.stdin.on('data', chunk => input += chunk);
  process.stdin.on('end', () => compile(JSON.parse(input)).then(output => process.stdout.write(JSON.stringify(output)))
    .catch(error => {console.error(error.message); process.exitCode = 1;}));
}
