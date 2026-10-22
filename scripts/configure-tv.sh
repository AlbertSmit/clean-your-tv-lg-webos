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
# CLI 3.x TV profiles do not offer ares-push or stream stdin over --run.
# Never print CLI output from a command containing the encoded pairing key:
# transport failures may echo the entire command, even if remote exit is zero.
push() {
  local payload digest reply command
  payload=$(base64 < "$1" | tr -d '\n')
  digest=$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())' "$1")
  # Stage in the same directory: failed decode, chmod or verification must leave
  # the current file intact. mktemp starts private; inspect actual mode as well
  # as chmod's status before publishing with an atomic rename.
  command="umask 077
  tmp=\$(mktemp '$STATE/.upload.XXXXXX') || exit 0
  trap 'rm -f \"\$tmp\"' EXIT
  if printf '%s' '$payload' | base64 -d > \"\$tmp\" &&
     chmod '$3' \"\$tmp\" &&
     [ \"\$(stat -c %a \"\$tmp\")\" = '$3' ] &&
     [ \"\$(sha256sum \"\$tmp\" | cut -d ' ' -f 1)\" = '$digest' ] &&
     mv -f \"\$tmp\" '$STATE/$2'; then
    printf '%s\\n' 'CYTV_TRANSFER_OK'
  fi
  exit 0"
  if ! reply=$(ares-novacom -d "$DEVICE" --run "$command" 2>&1); then
    echo "Copying $2 to the TV failed (connection or command error)." >&2
    return 1
  fi
  if ! printf '%s\n' "$reply" | tr -d '\r' | grep -qx 'CYTV_TRANSFER_OK'; then
    echo "Copying $2 to the TV failed (content or permissions not verified)." >&2
    return 1
  fi
}
push build/setup/ssap-key.json ssap-key.json 640
push build/setup/apps.json apps.json 644
EIM=$(ares-novacom -d "$DEVICE" --run "luna-send-pub -n 1 luna://com.webos.service.eim/addDevice '{\"appId\":\"com.gathin.tvhome\",\"pigImage\":\"\",\"mvpdIcon\":\"\"}'" 2>&1 | grep -v '^\[Info\]' || true)
echo "EIM response: ${EIM:-<none>}"
if grep -q '"returnValue" *: *true' <<<"$EIM"; then
  echo 'Early input restoration registered. Now launch Home Helper explicitly.'
else
  echo 'WARNING: EIM registration not confirmed (no returnValue:true). Startup will rely on the'
  echo 'guarded fallback: LG Home first, then the launcher. See docs/COMPATIBILITY.md.'
  echo 'Now launch Home Helper explicitly.'
fi
