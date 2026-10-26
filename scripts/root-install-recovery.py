#!/usr/bin/env python3
"""Internal reviewed-source Root cancellation tool. Never installs or activates.

Build a fresh Root Updater code bundle first. No action runs by default; inspect
only stages trusted temporary code and reads. remove needs the reviewed proof;
reconcile only archives host pending history after fresh device verification.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shlex
import sys
import uuid

PROJECT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PROJECT))
from cytv import state


def reconcile(store, profile, identifier, candidate, proof, inspect):
    pending=store.pending(profile)
    if (profile['edition']!='root' or not isinstance(pending,dict)
            or pending.get('action')!='install' or pending.get('product_operation')!=identifier):
        raise ValueError('matching_original_host_pending_required')
    disposition=inspect(identifier,candidate)
    if (not isinstance(disposition,dict) or disposition.get('operation')!=identifier
            or disposition.get('state')!='cancelled-and-removed' or disposition.get('lease_terminal') is not True
            or disposition.get('proof_sha256')!=proof or disposition.get('home_changed') is not False):
        raise ValueError('verified_device_cancellation_required')
    if store.pending(profile)!=pending:raise ValueError('host_pending_changed')
    # Preserve the original unresolved host request and honest cancellation,
    # before retiring the active pending file. No install-success receipt.
    history=store.recovery(profile,'cancelled-root-install')
    state.private_write(history,json.dumps(dict(action='cancelled-root-install',stage='verified',
                                              previous=pending,disposition=disposition),sort_keys=True).encode())
    store.finish(profile)
    return disposition


def code_inventory(bundle):
    # Local source is trusted; the complete generated inventory pins every byte
    # uploaded to the temporary device interpreter search path.
    sys.path.insert(0,str(PROJECT/'root-edition'))
    from updater.bootstrap import verify_bundle
    from updater.store import encode
    manifest=verify_bundle(bundle)
    module=(PROJECT/'root-edition/cancel_install.py').read_bytes()
    pin=hashlib.sha256(encode(dict(bundle=manifest,recovery_sha256=hashlib.sha256(module).hexdigest()))).hexdigest()
    return manifest,module,pin


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('digest','inspect','remove','reconcile'))
    parser.add_argument('--code-bundle',required=True,type=Path)
    parser.add_argument('--operation')
    parser.add_argument('--candidate')
    parser.add_argument('--code-sha256')
    parser.add_argument('--proof-sha256')
    args=parser.parse_args()
    manifest,module,pin=code_inventory(args.code_bundle)
    if args.action=='digest':print(pin);return
    for field,length in (('operation',32),('candidate',64),('code_sha256',64)):
        if not isinstance(getattr(args,field),str) or not re.fullmatch('[a-f0-9]{'+str(length)+'}',getattr(args,field)):
            parser.error('--'+field.replace('_','-')+' is required')
    if args.code_sha256!=pin:raise ValueError('reviewed_local_recovery_code_changed')
    if args.action in ('remove','reconcile') and (not isinstance(args.proof_sha256,str) or not re.fullmatch('[a-f0-9]{64}',args.proof_sha256)):
        parser.error('remove/reconcile requires --proof-sha256 from reviewed inspect')
    store=state.Store();profiles=[p for p in store.profiles() if p['edition']=='root' and (store.pending(p) or {}).get('product_operation')==args.operation]
    if len(profiles)!=1:raise ValueError('exactly_one_matching_saved_root_profile_required')
    profile=profiles[0]
    from cytv.transport import SSH
    from cytv.operations import Installer
    def secret(_):raise RuntimeError('saved_automatic_authentication_required')
    with store.lock(profile):
        remote=SSH.connect(profile,store.device_dir(profile),secret,lambda *_:False)
        try:
            installer=Installer(remote,store,profile,args.code_bundle.parent,{},progress=lambda *_:None)
            stage='/tmp/cytv-recovery-'+uuid.uuid4().hex
            remote.run('umask 077; mkdir '+shlex.quote(stage))
            finished=False
            try:
                for directory in sorted({str(PurePosixPath(n).parent) for n in manifest['files']}-{'.'}):
                    remote.run('mkdir -p '+shlex.quote(stage+'/'+directory))
                for name in (*manifest['files'],'bundle.json'):
                    remote.upload(stage+'/'+name,(args.code_bundle/name).read_bytes(),mode=0o600)
                remote.upload(stage+'/cancel_install.py',module,mode=0o600)
                def invoke(action,identifier,candidate):
                    command=[installer._python(),'-B',stage+'/cancel_install.py',action,'--operation',identifier,'--candidate',candidate,'--code-sha256',pin]
                    if action=='remove':command+=['--proof-sha256',args.proof_sha256]
                    return json.loads(remote.run(installer._python_command(command),timeout=180))
                if args.action=='reconcile':
                    result=reconcile(store,profile,args.operation,args.candidate,args.proof_sha256,lambda identifier,candidate:invoke('inspect',identifier,candidate))
                else:result=invoke(args.action,args.operation,args.candidate)
                finished=True
                print(json.dumps(result,sort_keys=True))
            finally:
                # Only this invocation's newly created trusted staging tree.
                if finished:remote.run('rm -rf -- '+shlex.quote(stage))
        finally:remote.close()


if __name__=='__main__':main()
