#!/usr/bin/env bash
# Run AFTER installing both packages and pairing with sync-apps.py.
set -euo pipefail
cd "$(dirname "$0")/.."
: "${TV_HOST:?Set TV_HOST to your TV address}"
DEVICE="${DEVICE:-lgtv}"
mkdir -p build/setup
python3 - <<'PY'
import json,os
from pathlib import Path
host=os.environ['TV_HOST'];keys=json.loads(Path('.lgtv-key.json').read_text());key=keys.get(host)
if not key:raise SystemExit('Run sync-apps.py and accept the pairing request first.')
s=Path('launcher/apps.js').read_text();apps=json.loads(s[s.index('{'):].rstrip().rstrip(';'))['apps']
p=Path('build/setup/ssap-key.json');p.write_text(json.dumps({'key':key}));p.chmod(0o600)
Path('build/setup/apps.json').write_text(json.dumps([a['id'] for a in apps if a['id'] not in ['com.gathin.tvhome','com.local.nativehome','com.webos.app.home']]))
PY
# ares-push uses the selected Developer Mode SSH connection.
ares-push -d "$DEVICE" build/setup/ssap-key.json /media/developer/apps/usr/palm/applications/com.local.nativehome/state/ssap-key.json
ares-push -d "$DEVICE" build/setup/apps.json /media/developer/apps/usr/palm/applications/com.local.nativehome/state/apps.json
ares-novacom -d "$DEVICE" --run 'chmod 640 /media/developer/apps/usr/palm/applications/com.local.nativehome/state/ssap-key.json'
ares-novacom -d "$DEVICE" --run "luna-send-pub -n 1 luna://com.webos.service.eim/addDevice '{\"appId\":\"com.gathin.tvhome\",\"pigImage\":\"\",\"mvpdIcon\":\"\"}'"
echo 'Check the EIM response for returnValue:true. Then launch Home Helper explicitly.'
