"""Issue-ready diagnostics built from allowlisted metadata, never raw logs."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import traceback
import uuid

from . import __version__
from .state import private_write
from .terminal import console
from .errors import TVConnectionError

ISSUE_URL = 'https://github.com/Razdva122/clean-your-tv-lg-webos/issues/new'
KERNEL_ARCHES = ('armv7l', 'armv7', 'armv8l', 'aarch64', 'arm64', 'x86_64', 'i686', 'unknown')


def create_report(store, action, profile, phase, error=None, tv_info=None):
    pending = store.pending(profile) if profile else None
    report = {
        'schema': 1, 'cytv_version': __version__,
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'desktop': {'os': platform.system(), 'architecture': platform.machine(), 'python': platform.python_version()},
        'action': action, 'edition': profile.get('edition') if profile else None,
        'phase': phase,
        'error_type': type(error).__name__ if error else None,
        'pending': {k: pending.get(k) for k in ('action', 'stage')} if pending else None,
        'trace': [{'file': Path(frame.filename).name, 'function': frame.name, 'line': frame.lineno}
                  for frame in traceback.extract_tb(error.__traceback__)[-12:]] if error else [],
        'tv': {k: tv_info[k] for k in ('modelName', 'firmwareVersion', 'sdkVersion') if tv_info and k in tv_info},
        'privacy': 'No addresses, SSH identities, exception text, credentials, app inventory, environment or raw TV logs are collected.',
    }
    if isinstance(error, TVConnectionError):
        report['connection'] = {'protocol': 'ssap', 'close_code': error.close_code, 'reason_code': error.reason_code}
    for name, allowed in (('kernel_arch', KERNEL_ARCHES),
                          ('userland_abi', ('arm32', 'arm64', 'other', 'unknown'))):
        if tv_info and name in tv_info:
            report['tv'][name] = tv_info[name] if tv_info[name] in allowed else 'unknown'
    if tv_info and type(tv_info.get('arm32_supported')) is bool:
        report['tv']['arm32_supported'] = tv_info['arm32_supported']
    path = store.root / 'reports' / ('diagnostic-' + uuid.uuid4().hex[:12] + '.json')
    private_write(path, json.dumps(report, indent=2).encode())
    return path


def suggest_issue(write, store, action, profile, phase, error, tv_info=None):
    write = console(write)
    write.heading('Need help? Open an issue')
    write(ISSUE_URL)
    try:
        path = create_report(store, action, profile, phase, error, tv_info)
        write.heading('Attach this diagnostic report')
        write.raw('  ' + str(path.resolve()))
    except (OSError, ValueError):
        write('Could not save a diagnostic file. Include cytv ' + __version__ + ', your desktop OS, edition and failed step: ' + phase + '.')
    write('')
    write('Include your steps, expected/actual result and TV model/firmware.')
    write('Review the report. Do not attach keys or your profile folder.')
