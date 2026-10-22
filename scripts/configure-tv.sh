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
STATE=/media/developer/apps/usr/palm/applications/com.local.nativehome/state
# @webos-tools/cli 3.x offers ares-push only for the ose/apollo profiles, and
# `ares-novacom --run` does not deliver stdin to the TV, so send each file base64-encoded
# in the command. The remote command always exits 0 so a failure never echoes it (and the
# key) back; the size check below confirms the copy instead.
push() {
  ares-novacom -d "$DEVICE" --run "umask $3; echo $(base64 < "$1" | tr -d '\n') | base64 -d > $STATE/$2 && chmod $4 $STATE/$2; exit 0" >/dev/null
  [ "$(ares-novacom -d "$DEVICE" --run "wc -c < $STATE/$2 2>/dev/null || echo 0" | tail -n 1 | tr -d ' ')" = "$(wc -c < "$1" | tr -d ' ')" ] \
    || { echo "Copying $2 to the TV failed."; exit 1; }
}
push build/setup/ssap-key.json ssap-key.json 027 640
push build/setup/apps.json apps.json 022 644
EIM=$(ares-novacom -d "$DEVICE" --run "luna-send-pub -n 1 luna://com.webos.service.eim/addDevice '{\"appId\":\"com.gathin.tvhome\",\"pigImage\":\"\",\"mvpdIcon\":\"\"}'" 2>&1 | grep -v '^\[Info\]' || true)
echo "EIM response: ${EIM:-<none>}"
if grep -q '"returnValue" *: *true' <<<"$EIM"; then
  echo 'Early input restoration registered. Now launch Home Helper explicitly.'
else
  echo 'WARNING: EIM registration not confirmed (no returnValue:true). Startup will rely on the'
  echo 'guarded fallback: LG Home first, then the launcher. See docs/COMPATIBILITY.md.'
  echo 'Now launch Home Helper explicitly.'
fi
