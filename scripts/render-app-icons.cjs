// Optional authoring tool: requires Sharp; generated images are checked in.
const sharp = require('sharp');
const path = require('node:path');
const fs = require('node:fs/promises');
const root = path.resolve(__dirname, '..');
const jobs = {
  home: [['launcher/brand-v2-icon.png', 80], ['launcher/brand-v2-largeIcon.png', 130], ['launcher/icon.png', 80]],
  helper: [['native/app/brand-v2-icon.png', 80], ['native/app/brand-v2-largeIcon.png', 130], ['native/app/icon.png', 80]],
  updater: [['updater-app/icon.png', 80], ['updater-app/largeIcon.png', 130]],
  'home-root': [['root-edition/assets/home.png', 80], ['root-edition/assets/home-large.png', 130]],
  'updater-root': [['root-edition/assets/updater.png', 80], ['root-edition/assets/updater-large.png', 130]],
  installer: [['assets/icons/installer.png', 1024], ['assets/icons/installer-256.png', 256]],
};

async function main() {
  for (const [name, targets] of Object.entries(jobs)) {
    for (const [destination, size] of targets) {
      const output = path.join(root, destination);
      await fs.mkdir(path.dirname(output), { recursive: true });
      await sharp(path.join(root, 'assets/icons', name + '.svg'), { density: 576 })
        .resize(size, size).png().toFile(output);
    }
  }
  // ICO supports PNG-compressed entries. Include several native Windows sizes.
  const sizes = [16, 32, 48, 256];
  const images = await Promise.all(sizes.map(size => sharp(path.join(root, 'assets/icons/installer.svg'), { density: 576 })
    .resize(size, size).png().toBuffer()));
  const header = Buffer.alloc(6 + 16 * sizes.length);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(sizes.length, 4);
  let offset = header.length;
  images.forEach((png, i) => {
    const entry = 6 + i * 16;
    header[entry] = header[entry + 1] = sizes[i] === 256 ? 0 : sizes[i];
    header.writeUInt16LE(1, entry + 4);
    header.writeUInt16LE(32, entry + 6);
    header.writeUInt32LE(png.length, entry + 8);
    header.writeUInt32LE(offset, entry + 12);
    offset += png.length;
  });
  await fs.writeFile(path.join(root, 'assets/icons/installer.ico'), Buffer.concat([header, ...images]));
  for (const [source, output] of [['logo-light.svg', 'readme-logo.png'], ['logo-dark.svg', 'readme-logo-dark.png']]) {
    await sharp(path.join(root, 'assets/brand', source), { density: 144 })
      .resize(1440).png().toFile(path.join(root, 'assets/brand', output));
  }
}

main().catch(error => { console.error(error); process.exitCode = 1; });
