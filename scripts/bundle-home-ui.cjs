const fs = require('node:fs');
const path = require('node:path');
const esbuild = require('esbuild');

const entry = 'ui/index.jsx';
const isModule = name => /^ui\/.*\.(js|jsx)$/.test(name);

async function bundleHomeUI(files) {
  if (!Object.hasOwn(files, entry)) return null;
  const result = await esbuild.build({
    entryPoints: [entry], bundle: true, write: false, format: 'iife', logLevel: 'silent',
    platform: 'browser', target: 'es2015', jsxFactory: 'h',
    plugins: [{name: 'supplied-home-ui', setup(build) {
      build.onResolve({filter: /.*/, namespace: 'home-ui'}, args => {
        if (/^nano-jsx\/lib\/core(?:\.js)?$/.test(args.path)) {
          return {path: require.resolve('nano-jsx/lib/core.js')};
        }
        if (!args.path.startsWith('.')) throw Error('Unsupported Home UI import: ' + args.path);
        const name = path.posix.normalize(path.posix.join(path.posix.dirname(args.importer), args.path));
        const found = [name, name + '.js', name + '.jsx'].find(candidate => isModule(candidate) && Object.hasOwn(files, candidate));
        if (!found) throw Error('Missing supplied Home UI module: ' + name);
        return {path: found, namespace: 'home-ui'};
      });
      build.onResolve({filter: /^ui\/index\.jsx$/}, () => ({path: entry, namespace: 'home-ui'}));
      build.onLoad({filter: /.*/, namespace: 'home-ui'}, args => ({
        contents: files[args.path], loader: args.path.endsWith('.jsx') ? 'jsx' : 'js'
      }));
    }}]
  });
  return {
    code: result.outputFiles[0].text,
    license: fs.readFileSync(require.resolve('nano-jsx/LICENSE'), 'utf8')
  };
}

exports.bundleHomeUI = bundleHomeUI;
exports.isModule = isModule;
