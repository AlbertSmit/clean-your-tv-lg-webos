#!/usr/bin/env python3
"""Shared Root product lifecycle. Package journals retain terminal evidence.

Request IDs are data, never commands. A repeated request only reads its durable
record; even a dead worker cannot authorize replay of an uncertain submission.
"""
import re

BUNDLED_FILES=('install_driver.py','install_device.py','system_setup.py','root_package.py','app-inventory.js',
 'cleanup_root_updater.py','cleanup_system_updater.py','cleanup_legacy_permissions.py','cleanup_app_permissions.py','cleanup_root_archive.py',
 'system_updater/__init__.py','system_updater/core.py','system_updater/device.py','system_updater/support/__init__.py',
 'system_updater/support/package.py','system_updater/support/store.py','system_updater/support/profile.py','system_updater/support/luna.py')
from installation import Busy, Ownership, _optional_record, pending_journals, read_journal


def operation_id(value):
    if not isinstance(value,str) or not re.fullmatch('[0-9a-f]{32}',value):
        raise ValueError('invalid_operation_uuid')
    return value


class _Recorded(Exception):
    def __init__(self,record): self.record=record


class Coordinator:
    def __init__(self, device, ownership=None, read=read_journal):
        self.read=read
        self.device=device
        self.ownership=ownership if ownership is not None else Ownership()
        self.store=self.ownership.store

    def status(self, identifier):
        identifier=operation_id(identifier)
        value=_optional_record(self.store,'request-'+identifier)
        if value is None:
            return dict(operation=identifier,stage='unknown',state='unknown',code='unknown_operation')
        if (not isinstance(value,dict) or value.get('operation')!=identifier
                or value.get('action') not in ('install','remove')
                or value.get('state') not in ('pending','complete','recovery_required')):
            raise ValueError('unknown_product_operation')
        return value

    def inspect(self):
        return self.device.inspect()

    def restore(self):
        # Emergency restoration must work even while another operation is retained.
        return self.device.restore()

    def _run(self, identifier, action, perform):
        identifier=operation_id(identifier)
        previous=self.status(identifier)
        if previous['state']!='unknown':
            if previous['action']!=action: raise ValueError('operation_action_conflict')
            return previous
        def check():
            existing=self.status(identifier)
            if existing['state']!='unknown': raise _Recorded(existing)
            pending_journals('product',self.read)
        try:
            with self.ownership.operation('product', 'product.json', check=check) as lease:
                # Check under the lock too: two clients can race their first status.
                previous=self.status(identifier)
                if previous['state']!='unknown': return previous
                record=dict(operation=identifier,action=action,stage='reserved',state='pending',code='operation_pending',home_changed=False)
                submission=_optional_record(self.store,'submission-'+identifier)
                if submission is not None: record['candidate_sha256']=submission['candidate_sha256']
                def checkpoint(stage):
                    record['stage']=stage
                    self.store.write('request-'+identifier,record)
                    self.ownership.stage(lease,stage)
                self.device.operation=lease
                self.device.ownership=self.ownership
                checkpoint('reserved')
                try:
                    result=perform(checkpoint)
                    record.update(stage='complete',state='complete',code='verified',result=result)
                    self.store.write('request-'+identifier,record)
                    self.ownership.stage(lease,'complete',terminal=True)
                except Exception as error:
                    if hasattr(self.device,'log'): self.device.log(error)
                    # Diagnostic detail belongs in worker stderr/private logs only.
                    record.update(state='recovery_required',code='installation_requires_recovery')
                    self.store.write('request-'+identifier,record)
                return record
        except _Recorded as existing:
            if existing.record['action']!=action: raise ValueError('operation_action_conflict')
            return existing.record

    def install(self, identifier, payload, migrate=False, prepare_supervisor=False):
        operation_id(identifier)
        if type(migrate) is not bool or type(prepare_supervisor) is not bool:
            raise ValueError('invalid_install_options')
        # Validate payload/runtime readiness before taking the product lease. A
        # replay never re-enters preflight, provisioning, or package submission.
        previous=self.status(identifier)
        if previous['state']!='unknown':
            if previous['action']!='install': raise ValueError('operation_action_conflict')
            return previous
        options=dict(migrate=migrate,prepare_supervisor=prepare_supervisor)
        self.device.preflight(payload,options)
        def perform(checkpoint):
            state=self.device.inspect()['state']
            if state=='fresh':
                checkpoint('root-deploy')
                self.device.deploy(payload,options)
                checkpoint('root-updater')
                self.device.updater(payload,options)
            elif state!='installed':
                raise ValueError('installation_requires_recovery')
            if prepare_supervisor:
                checkpoint('supervisor')
                self.device.supervisor(payload,options)
            checkpoint('readback')
            return self.device.readback()
        return self._run(identifier,'install',perform)

    def remove(self, identifier):
        def perform(checkpoint):
            return self.device.remove(checkpoint)
        return self._run(identifier,'remove',perform)


def _verified_payload(payload, prepare_supervisor):
    """Copy only authoritative verified component inventories; omit runtime.

    Runtime preparation is the Node/runtime.js contract and precedes this API.
    cytv already prepares Python and must not upload an offline runtime again.
    """
    from pathlib import Path
    import deploy
    from updater.bootstrap import verify_bundle
    payload=Path(payload)
    inventories={'root':deploy.verify_bundle(payload/'root'),
                 'root-updater':verify_bundle(payload/'root-updater')}
    if prepare_supervisor:
        # verify_bundle cannot be imported before its enclosing known bundle is
        # checked. The canonical setup verifier is bundled with the coordinator.
        from system_setup import verify_bundle as verify_system
        inventories['supervisor']=verify_system(payload/'supervisor')
    return inventories


def candidate_digest(payload, inventories):
    import hashlib
    import json
    from pathlib import Path
    from deploy import checked_file
    value={name:hashlib.sha256(checked_file(Path(payload)/name,'bundle.json')).hexdigest() for name in inventories}
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def submit(identifier, payload, migrate=False, prepare_supervisor=False, action='install', candidate=None, ownership=None):
    """Persist once, snapshot trusted worker material, then detach.

    The submission receipt precedes Popen. A lost reply or a failed spawn is
    inspect-only and cannot repeat a package operation under the same ID.
    """
    import json
    import os
    import hashlib
    from pathlib import Path
    import subprocess
    import sys
    from install_device import LocalDevice
    operation_id(identifier)
    if type(migrate) is not bool or type(prepare_supervisor) is not bool: raise ValueError('invalid_install_options')
    if action not in ('install','remove'): raise ValueError('invalid_product_action')
    ownership=ownership if ownership is not None else Ownership();store=ownership.store
    with store.lock():
        existing=_optional_record(store,'submission-'+identifier)
        known=request_status(identifier,store)
        if known['state']!='unknown':
            if known.get('action')!=action: raise ValueError('operation_action_conflict')
            return known
        if existing is not None:
            if existing.get('action')!=action: raise ValueError('operation_action_conflict')
            return request_status(identifier,store)
        inventories=_verified_payload(payload,prepare_supervisor)
        actual_candidate=candidate_digest(payload,inventories)
        if candidate is not None and candidate!=actual_candidate: raise ValueError('reviewed_candidate_changed')
        device=LocalDevice();device.preflight(payload,dict(migrate=migrate,prepare_supervisor=prepare_supervisor))
        receipt=dict(operation=identifier,stage='preparing',state='pending',code='operation_pending',action=action,home_changed=False,candidate_sha256=actual_candidate)
        store.write('submission-'+identifier,receipt)
        try:
            root=Path(store.root)/('request-'+identifier)
            root.mkdir(mode=0o700)
            # Clone checked bytes, not a directory tree whose extra/link entries might
            # be executed by a later worker. The updater inventory contains all code.
            for component,manifest in inventories.items():
                for name in (*manifest['files'],'bundle.json'):
                    from deploy import checked_file
                    target=root/component/name;target.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
                    with target.open('xb') as output:
                        raw=checked_file(Path(payload)/component,name)
                        if name!='bundle.json' and hashlib.sha256(raw).hexdigest()!=manifest['files'][name]:
                            raise ValueError('worker_source_changed')
                        output.write(raw);output.flush();os.fsync(output.fileno())
                    target.chmod(0o600)
            if candidate_digest(root,inventories)!=actual_candidate: raise ValueError('worker_source_changed')
        except (OSError,ValueError):
            receipt.update(state='recovery_required',code='worker_snapshot_unavailable')
            store.write('submission-'+identifier,receipt)
            return receipt
        receipt['stage']='submitted'
        store.write('submission-'+identifier,receipt)
        args=[sys.executable,'-B',str(root/'root-updater/install_driver.py'),action,'--operation',identifier,'--payload',str(root),'--worker']
        if migrate: args.append('--migrate-packaged-home')
        if prepare_supervisor: args.append('--prepare-supervisor')
        log=root/'worker.log'
        with log.open('xb') as output:
            log.chmod(0o600)
            try:
                subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=output,stderr=output,start_new_session=True,close_fds=True,
                                 env={**{k:v for k,v in os.environ.items() if k not in ('PYTHONPATH','PYTHONHOME')},'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1'})
            except OSError:
                receipt.update(state='recovery_required',code='worker_submission_unknown')
                store.write('submission-'+identifier,receipt)
        return receipt


def request_status(identifier, store):
    from install_device import LocalDevice
    ownership=Ownership.__new__(Ownership);ownership.store=store
    status=Coordinator(LocalDevice(),ownership).status(identifier)
    if status['state']!='unknown': return status
    return _optional_record(store,'submission-'+operation_id(identifier)) or status


def main():
    import argparse
    import json
    from pathlib import Path
    from install_device import LocalDevice, checked_store
    from installation import STATE
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('inspect','install','status','restore','remove'))
    parser.add_argument('--operation')
    parser.add_argument('--payload',type=Path)
    parser.add_argument('--candidate',help='SHA-256 of the reviewed component bundle manifests')
    parser.add_argument('--migrate-packaged-home',action='store_true')
    parser.add_argument('--prepare-supervisor',action='store_true')
    parser.add_argument('--worker',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    if args.action in ('install','remove','status'): operation_id(args.operation)
    if args.action not in ('install','inspect') and (args.migrate_packaged_home or args.prepare_supervisor): parser.error('install options require install')
    device=LocalDevice()
    if args.action in ('inspect','status','restore'):
        ownership=Ownership.__new__(Ownership);ownership.store=checked_store(STATE)
    else: ownership=Ownership()
    coordinator=Coordinator(device,ownership)
    try:
        if args.action=='install':
            if args.payload is None: parser.error('install requires a verified local payload')
            if args.worker:
                result=coordinator.install(args.operation,args.payload,migrate=args.migrate_packaged_home,prepare_supervisor=args.prepare_supervisor)
            else:
                result=submit(args.operation,args.payload,migrate=args.migrate_packaged_home,prepare_supervisor=args.prepare_supervisor,candidate=args.candidate)
        elif args.action=='remove':
            if args.worker: result=coordinator.remove(args.operation)
            else:
                if args.payload is None: parser.error('remove requires a verified local payload')
                result=submit(args.operation,args.payload,action='remove',candidate=args.candidate)
        elif args.action=='status': result=request_status(args.operation,ownership.store)
        elif args.action=='inspect':
            inspected=device.inspect()
            result=dict(operation=None,stage='inspect',state=inspected['state'],code='inspected',installation=inspected)
            if args.payload:
                result['candidate_sha256']=candidate_digest(args.payload,_verified_payload(args.payload,args.prepare_supervisor))
        else: result=dict(operation=None,stage='restore',state='complete',code='restored',result=coordinator.restore())
    except Exception as error:
        device.log(error)
        result=dict(operation=args.operation,stage='blocked',state='recovery_required',code='operation_requires_recovery',home_changed=False)
        if args.action in ('install','remove'):
            result['action']=args.action
            if _optional_record(ownership.store,'request-'+args.operation) is None:
                ownership.store.write('request-'+args.operation,result)
    print(json.dumps(result,sort_keys=True),flush=True)


if __name__=='__main__': main()
