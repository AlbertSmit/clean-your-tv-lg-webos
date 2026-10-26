const fs = require('node:fs');
const path = require('node:path');
const {compile} = require('./compile-tv-web.cjs');
(async () => {
  for (const directory of ['launcher', 'root-edition/ui', 'updater-app']) {
    const files = {};
    function collect(current, prefix = '') {
      for (const entry of fs.readdirSync(current, {withFileTypes: true})) {
        const name = prefix + entry.name;
        if (entry.isDirectory()) collect(path.join(current, entry.name), name + '/');
        else if (/\.(js|jsx|css|html)$/.test(name)) files[name] = fs.readFileSync(path.join(current, entry.name), 'utf8');
      }
    }
    collect(directory);
    await compile(files);
    console.log('PASS TV web compatibility:', directory);
  }
})().catch(error => {console.error(error.message); process.exitCode = 1;});
