"""Issue #68: legacy web engines must receive real static Outfit outlines."""
import re
import runpy
import struct
import unittest
from pathlib import Path

from cytv import package
from scripts.tv_web_build import compile_web

ROOT = Path(__file__).resolve().parents[2]
WEIGHTS = (300, 400, 500, 700)


def tables(data):
    """Read the SFNT directory without adding a font library to normal tests."""
    count = struct.unpack_from('>H', data, 4)[0]
    result = {}
    for i in range(count):
        tag, _, offset, length = struct.unpack_from('>4sIII', data, 12 + i * 16)
        result[tag] = data[offset:offset + length]
    return result


class LegacyOutfitTests(unittest.TestCase):
    def check_faces(self, files):
        css = files['style.css'].decode()
        faces = {}
        for body in re.findall(r'@font-face\s*\{([^}]+)\}', css):
            if not re.search(r"font-family:\s*['\"]Outfit['\"]", body):
                continue
            weight = re.search(r'font-weight:\s*([^;]+)', body).group(1).strip()
            self.assertRegex(weight, r'^[1-9]00$', 'legacy engines cannot select a variable weight range')
            url = re.search(r"url\(['\"]?([^)'\"]+)", body).group(1)
            self.assertNotIn(int(weight), faces)
            faces[int(weight)] = url
        self.assertEqual(set(faces), set(WEIGHTS))
        source = tables((ROOT / 'launcher/fonts/outfit.ttf').read_bytes())
        outlines = set()
        for weight, url in faces.items():
            with self.subTest(weight=weight, url=url):
                font = tables(files[url])
                self.assertNotIn(b'fvar', font, 'axis defaults would render Thin on old webOS')
                self.assertNotIn(b'gvar', font)
                self.assertEqual(struct.unpack_from('>H', font[b'OS/2'], 4)[0], weight)
                self.assertEqual(font[b'cmap'], source[b'cmap'], 'retain all original glyph mappings')
                self.assertNotEqual(font[b'glyf'], source[b'glyf'], 'bake weight into actual outlines')
                outlines.add(font[b'glyf'])
        self.assertEqual(len(outlines), len(WEIGHTS), 'weights must not all contain the same Thin outlines')
        self.assertIn('fonts/OFL.txt', files)

    def test_no_root_package_contains_static_faces(self):
        builder = runpy.run_path(str(ROOT / 'scripts/build-cytv.py'))
        raw = builder['pack_app'](builder['tracked_files']('launcher'),
                                  builder['tracked_files']('renewal-service'))
        prefix = 'usr/palm/applications/com.gathin.tvhome/'
        self.check_faces({name[len(prefix):]: data for name, data in package.data_files(raw).items()
                          if name.startswith(prefix)})

    def test_compiled_root_package_inventory(self):
        prepare = runpy.run_path(str(ROOT / 'root-edition/preview.py'))['prepare']
        self.check_faces(compile_web(prepare()))
