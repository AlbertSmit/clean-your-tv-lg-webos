#!/usr/bin/env python3
"""Build only the launcher (home app) IPK from current source, for dev sideload."""
import json
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# build-cytv.py is a script (hyphenated name), not an importable module.
ns = runpy.run_path(str(ROOT / 'scripts/build-cytv.py'))
tracked_files = ns['tracked_files']
pack_app = ns['pack_app']

launcher = {n: b for n, b in tracked_files('launcher').items() if n != 'apps.js'}
launcher['config.js'] = b'window.CONFIG = {columns:5,dockApps:[],hiddenApps:["com.gathin.tvhome","com.local.nativehome"]};\n'
launcher['apps.js'] = b'window.TV_APPS = {apps:[],inputs:[]};\n'
renewal = {n: b for n, b in tracked_files('renewal-service').items() if not n.startswith('state/')}

ipk = pack_app(launcher, renewal)
version = json.loads(launcher['appinfo.json'])['version']
out = ROOT / 'dist' / ('com.gathin.tvhome_' + version + '_all.ipk')
out.write_bytes(ipk)
print('wrote', out, out.stat().st_size, 'bytes')
