"""Explicit Root cache maintenance through WAM, without deleting app files."""
import re

from .errors import UserError
from .python_runtime import _run

ERROR = 'WAM cache cleanup could not be verified. Some cache data may already have been cleared. Check free space before retrying; no automatic retry was attempted.'
INSPECT = r'''
ancestors /var/lib
luna_real=$(readlink -f /usr/bin/luna-send)
[ -f "$luna_real" ] && [ -x "$luna_real" ] && safe_mode "$luna_real"
ancestors "${luna_real%/*}"
ancestors /usr/bin
du_path=$(command -v du)
du_real=$(readlink -f "$du_path")
[ -f "$du_real" ] && [ -x "$du_real" ] && safe_mode "$du_real"
ancestors "${du_real%/*}"
space=$(df -Pk /var/lib)
available=$(printf '%s\n' "$space" | awk 'END {print $4}')
case "$available" in ''|*[!0-9]*) exit 1;; esac
[ "${#available}" -le 9 ]
total=0
for folder in /var/lib/wam/Default/Cache '/var/lib/wam/Default/Code Cache'; do
    if [ ! -e "$folder" ] && [ ! -L "$folder" ]; then continue; fi
    [ -d "$folder" ] && [ ! -L "$folder" ]
    [ "$(readlink -f "$folder")" = "$folder" ]
    usage=$("$du_path" -skx "$folder")
    size=$(printf '%s\n' "$usage" | awk 'END {print $1}')
    case "$size" in ''|*[!0-9]*) exit 1;; esac
    [ "${#size}" -le 9 ]
    total=$((total + size))
done
printf 'CYTV_WAM_CACHE %s %s' "$total" "$available"
'''


def inspect(remote):
    try:
        match = re.fullmatch(r'CYTV_WAM_CACHE ([0-9]{1,10}) ([0-9]{1,9})', _run(remote, INSPECT, timeout=60))
        if match:
            return {'bytes': int(match[1]) * 1024, 'available_kib': int(match[2])}
    except (UserError, OSError):
        pass
    raise UserError('WAM cache inspection is unavailable. Check root access, system tools and /var/lib space; no cleanup was requested.') from None


def clean(remote):
    try:
        # WAM owns its live caches. Never fall back to root filesystem deletion,
        # and never omit types: the platform's empty/default request means ALL.
        reply = remote.luna('com.webos.service.webappmanager/clearBrowsingData',
                            {'types': ['cache', 'codecache']}, timeout=60)
        if isinstance(reply, dict) and reply.get('returnValue') is True:
            return
    except Exception:
        # Once submitted, parser/transport failures all leave an unknown outcome.
        pass
    raise UserError(ERROR) from None
