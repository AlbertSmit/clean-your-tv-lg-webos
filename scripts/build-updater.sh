#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${ARES_PACKAGE:=ares-package}"
python3 - <<'PYCLEAN'
from pathlib import Path
import shutil
p=Path('build/updater-service')
if p.exists(): shutil.rmtree(p)
PYCLEAN
mkdir -p build/updater-service/state dist
cp updater-service/*.js updater-service/*.json updater-service/*.pem build/updater-service/
cp launcher/user-data.js build/updater-service/user-data.js
touch build/updater-service/state/.keep
"$ARES_PACKAGE" updater-app build/updater-service -o dist
python3 scripts/fix-updater-data.py dist/com.cleanyourtv.updater_0.1.0_all.ipk

python3 - <<'PYSUM'
from pathlib import Path
import hashlib
p=Path('dist')
(p/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(p.glob('*.ipk'))))
PYSUM
