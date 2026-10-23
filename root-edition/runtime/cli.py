#!/usr/bin/python3
"""Isolated Root candidate: status, 60-second trial, restore, boot recovery."""
import json
import os
import sys
import device_adapter as d


def main(mode, transaction=None):
    if os.geteuid() != 0:
        raise PermissionError('Root required')
    if mode == 'confirm':
        from intent_runtime import confirm
        return confirm(transaction)
    if mode in ('enable','intent-trial'):
        from intent_runtime import start
        return start()
    if mode == 'emergency-trial':
        from emergency_trial import start
        return start()
    if mode == 'trial':
        from bounded_profile_trial import begin, spawn
        return begin(spawn)
    if mode == 'restore':
        from intent_runtime import restore
        result = restore()
        return d.main('recover') if result is None else result
    if mode == 'boot':
        from intent_runtime import boot
        result = boot()
        return d.main('boot') if result is None else result
    if mode == 'status':
        from provision import verify
        result = d.main('status')
        try:
            result['recovery'] = verify()
        except (OSError, ValueError, TypeError) as exc:
            result['recovery'] = {'integrity_verified':False,'error':str(exc)}
        result['candidate'] = d.CANDIDATE
        result['persistent_enable_available'] = result['recovery'].get('integrity_verified',False)
        from intent_runtime import coordinator
        c = coordinator()
        result['intent'] = c.store.read() if c is not None else None
        return result
    raise ValueError('Expected status, trial, emergency-trial, restore, boot, enable or confirm')


if __name__ == '__main__':
    try:
        result = main(sys.argv[1] if len(sys.argv) in (2,3) else '', sys.argv[2] if len(sys.argv) == 3 else None)
        print(json.dumps({'returnValue':True,'result':result}), flush=True)
        if isinstance(result, str) and result in ('recovering', 'conflict'):
            sys.exit(2)
    except Exception as exc:
        print(json.dumps({'returnValue':False,'error':str(exc)}), flush=True)
        sys.exit(1)
