#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
: "${ARES_PACKAGE:=ares-package}"
python3 - <<'PYCLEAN'
from pathlib import Path
import shutil
for p in (Path('build/updater-service'), Path('dist/updater-setup')):
    if p.exists(): shutil.rmtree(p)
PYCLEAN
mkdir -p build/updater-service dist
cp updater-service/*.js updater-service/*.json build/updater-service/
cp updater-service/release-public.pem build/updater-service/
cp launcher/user-data.js build/updater-service/user-data.js
"$ARES_PACKAGE" updater-app build/updater-service -o dist

mkdir -p dist/updater-setup/scripts/lib dist/updater-setup/updater-service
cp scripts/update-permissions.cjs dist/updater-setup/scripts/
cp scripts/lib/update-permissions.cjs dist/updater-setup/scripts/lib/
cp updater-service/permissions.js dist/updater-setup/updater-service/
cp docs/UPDATES.md dist/updater-setup/README.md

python3 - <<'PYSUM'
from pathlib import Path
import hashlib
p=Path('dist')
(p/'SHA256SUMS').write_text(''.join(hashlib.sha256(f.read_bytes()).hexdigest()+'  '+f.name+'\n' for f in sorted(p.glob('*.ipk'))))
PYSUM
