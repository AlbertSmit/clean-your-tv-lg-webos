const path = require('node:path');
const {execFileSync} = require('node:child_process');

module.exports = function compiledLauncher() {
  if (process.env.TV_WEB_DIR) return path.resolve(process.env.TV_WEB_DIR);
  const root = path.resolve(__dirname, '..');
  const output = path.join(root, 'build/browser-launcher');
  execFileSync('python3', ['scripts/tv_web_build.py', '--input', 'launcher', '--output', output], {cwd: root});
  return output;
};
