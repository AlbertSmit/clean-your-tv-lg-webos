"""Chinese UI must carry usable glyphs in the actual TV packages."""
import runpy
import struct
import json
import subprocess
import unittest
from pathlib import Path
from test_tv_fonts import tables
from cytv import package
from cytv.translations import MESSAGES
from scripts.tv_web_build import compile_web

ROOT = Path(__file__).resolve().parents[2]


def cmap(data):
    table = tables(data)[b'cmap']
    result = set()
    for i in range(struct.unpack_from('>H', table, 2)[0]):
        _, _, offset = struct.unpack_from('>HHI', table, 4 + 8 * i)
        fmt = struct.unpack_from('>H', table, offset)[0]
        if fmt == 4:
            count = struct.unpack_from('>H', table, offset + 6)[0] // 2
            ends = struct.unpack_from('>' + str(count) + 'H', table, offset + 14)
            starts = struct.unpack_from('>' + str(count) + 'H', table, offset + 16 + 2 * count)
            deltas = struct.unpack_from('>' + str(count) + 'h', table, offset + 16 + 4 * count)
            ranges = offset + 16 + 6 * count
            for segment, (start, end, delta) in enumerate(zip(starts, ends, deltas)):
                distance = struct.unpack_from('>H', table, ranges + 2 * segment)[0]
                for code in range(start, end + 1):
                    glyph = struct.unpack_from('>H', table, ranges + 2 * segment + distance + 2 * (code - start))[0] if distance else code
                    if glyph and ((glyph + delta) & 0xffff):
                        result.add(code)
        elif fmt == 12:
            for j in range(struct.unpack_from('>I', table, offset + 12)[0]):
                start, end, _ = struct.unpack_from('>III', table, offset + 16 + 12 * j)
                result.update(range(start, end + 1))
    return result


class ChineseFontTests(unittest.TestCase):
    def check_fonts(self, files):
        script = """
const fs=require('fs'),vm=require('vm'),catalogs={};
const ctx={HomeI18n:{add(values){for(const [code,map] of Object.entries(values))Object.assign(catalogs[code]||(catalogs[code]={}),map);}}};ctx.window=ctx;
for(const file of ['launcher/catalogs.js','root-edition/ui/root-locales.js'])vm.runInNewContext(fs.readFileSync(file,'utf8'),ctx);
process.stdout.write(JSON.stringify(catalogs));
"""
        catalogs = json.loads(subprocess.check_output(['node', '-e', script], cwd=ROOT))
        for name, code, label in [('SC', 'zh-Hans', '简体中文'), ('TC', 'zh-Hant', '繁體中文')]:
            text = ''.join(catalogs[code].values()) + ''.join(values[code] for values in MESSAGES.values())
            text += label + '年月日星期上午下午'
            required = {ord(c) for c in text if 0x3000 <= ord(c) <= 0x9fff or 0xff00 <= ord(c) <= 0xffef}
            data = files['fonts/NotoSans%s.ttf' % name]
            self.assertNotIn(b'fvar', tables(data), 'old TV engines need static fonts')
            self.assertEqual(struct.unpack_from('>H', tables(data)[b'OS/2'], 4)[0], 400)
            self.assertFalse(required - cmap(data), 'regenerate Chinese font subset after adding translations')
            self.assertIn('fonts/NotoSans%s-OFL.txt' % name, files)

    def test_no_root_packaged_chinese_glyphs(self):
        builder = runpy.run_path(str(ROOT / 'scripts/build-cytv.py'))
        raw = builder['pack_app'](builder['tracked_files']('launcher'), builder['tracked_files']('renewal-service'))
        prefix = 'usr/palm/applications/com.gathin.tvhome/'
        self.check_fonts({name[len(prefix):]: data for name, data in package.data_files(raw).items() if name.startswith(prefix)})

    def test_root_packaged_chinese_glyphs(self):
        prepare = runpy.run_path(str(ROOT / 'root-edition/preview.py'))['prepare']
        self.check_fonts(compile_web(prepare()))
