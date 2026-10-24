#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${ZIG:=zig}"
: "${ARES_PACKAGE:=ares-package}"
command -v "$ZIG" >/dev/null || { echo 'Install Zig 0.14.1 or set ZIG to its executable.'; exit 1; }
python3 - <<'PYBUILD'
from pathlib import Path
import shutil
for p in [Path('build/native-app'),Path('build/native-service')]:
 if p.exists(): shutil.rmtree(p)
p=Path('launcher/apps.js')
if not p.exists(): p.write_text('window.TV_APPS = {apps: [], inputs: []};\n')
PYBUILD
mkdir -p build/native-app/state build/native-service/state dist
baseline=$(python3 - <<'PYPIN'
import json, runpy
from pathlib import Path
info = json.loads(Path('native/app/appinfo.json').read_text())
raw = runpy.run_path('scripts/build-cytv.py')['helper_baseline'](info['version'])
if raw is not None:
    Path('dist', info['id'] + '_' + info['version'] + '_arm.ipk').write_bytes(raw)
    print('published')
PYPIN
)
if [[ "$baseline" != published ]]; then
# Stage from a clean set of public sources; never package local runtime state.
cp native/app/*.js native/app/*.json native/app/*.png build/native-app/
cp -R native/app/vendor build/native-app/
cp native/service/*.js native/service/*.json build/native-service/
touch build/native-app/state/.keep build/native-service/state/.keep
"$ZIG" cc -target arm-linux-musleabi -Os -static -s native/app/detach.c -o build/native-app/detach
"$ZIG" cc -target arm-linux-musleabi -Os -static -s native/prototype/relay.c native/prototype/filter.c -o build/native-app/relay
"$ZIG" cc -target arm-linux-musleabi -Os -static -s native/app/resume.c -o build/native-app/resume
"$ARES_PACKAGE" build/native-app build/native-service -o dist
# Repair the package just built, even when older releases remain in dist/.
helper=$(python3 -c 'import json; a=json.load(open("build/native-app/appinfo.json")); print("dist/"+a["id"]+"_"+a["version"]+"_arm.ipk")')
python3 scripts/fix-package-data.py "$helper"
fi
python3 scripts/tv_web_build.py --input launcher --output build/home-app
"$ARES_PACKAGE" build/home-app renewal-service -o dist
python3 - <<'PY'
from pathlib import Path
import hashlib
p=Path('dist');(p/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(p.glob('*.ipk'))))
PY
