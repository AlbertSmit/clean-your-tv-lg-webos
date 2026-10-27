"""Offline 1.3 supervisor harness. Run in a fresh interpreter to isolate imports.

The public supervisor and infrastructure fixture is immutable. Candidate private
infrastructure comes from normal current builders. Small synthetic SDK packages
exercise package identity and replacement; they do not establish UI compatibility.
Only installer, TV RPC/runtime/process IO and absolute OS paths are adapted.
"""
import hashlib,importlib.util,io,json,os,shutil,subprocess,sys,tarfile,tempfile
from contextlib import ExitStack,contextmanager
from pathlib import Path
from unittest.mock import patch

PROJECT=Path(__file__).resolve().parents[2]
def sha(raw):return hashlib.sha256(raw).hexdigest()
def packed(files):
    stream=io.BytesIO()
    with tarfile.open(fileobj=stream,mode='w:gz') as archive:
        for name,raw in sorted(files.items()):
            info=tarfile.TarInfo(name);info.size=len(raw);info.mode=0o600;archive.addfile(info,io.BytesIO(raw))
    return stream.getvalue()

def sdk(app,version,label):
    from cytv.package import ipk
    prefix='usr/palm/applications/'+app+'/'
    files={prefix+'appinfo.json':json.dumps({'id':app,'version':version,'type':'web','main':'index.html','systemUpdateProtocol':1}).encode(),prefix+'index.html':label.encode(),'usr/palm/packages/'+app+'/packageinfo.json':json.dumps({'id':app,'app':app,'version':version,'services':[]}).encode()}
    return ipk(app,version,files),files

class LegacyOTA:
    def __enter__(self):
        self.stack=ExitStack();self.base=Path(self.stack.enter_context(tempfile.TemporaryDirectory())).resolve()
        fixture=PROJECT/'tests/system_updates/fixtures/public-1.3.0-supervisor.tar.gz'
        provenance=json.loads(fixture.with_suffix('.provenance.json').read_text())
        assert sha(fixture.read_bytes())==provenance['sha256']
        with tarfile.open(fixture,'r:gz') as archive:
            for member in archive:
                raw=archive.extractfile(member).read();assert sha(raw)==provenance['files'][member.name]
                path=self.base/member.name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);path.chmod(0o600)
        self.code=self.base/'clean-your-tv-system-updater/code';self.code.parent.mkdir();shutil.move(str(self.base/'supervisor'),self.code);sys.path.insert(0,str(self.code));sys.path.insert(1,str(PROJECT))
        from system_updater.device import Device
        from system_updater.core import Manager
        from system_updater.support.store import Store
        import system_updater.device as module
        self.module=module;self.Store=Store;self.Manager=Manager
        self.state=self.base/'clean-your-tv-system-updater';self.root=self.base/'clean-your-tv-root';self.updater=self.base/'clean-your-tv-root-updater';self.installed=self.base/'installed'
        self.store=Store(self.state,uid=os.getuid());self.root_store=Store(self.root,uid=os.getuid());self.up_store=Store(self.updater,uid=os.getuid())
        (self.state/'cache').mkdir();(self.updater/'cache').mkdir();(self.updater/'code').mkdir()
        self.device=Device(self.store,code=self.code,root_state=self.root,root_updater=self.updater,installed=self.installed,uid=os.getuid())
        # Child import loader changes only the LS2 filesystem and scan-services OS call.
        original_spec=importlib.util.spec_from_file_location
        def spec(name,path,*args,**kwargs):
            result=original_spec(name,path,*args,**kwargs)
            if name=='system_root_provision':
                execute=result.loader.exec_module
                def load(module):
                    execute(module);module.FILES={key:self.base/'ls2'/key for key in module.FILES};module.refresh=lambda:{'returnValue':True}
                result.loader.exec_module=load
            return result
        self.stack.enter_context(patch.object(importlib.util,'spec_from_file_location',side_effect=spec))
        self.old={name:(self.base/'infrastructure'/name).read_bytes() for name in json.loads((self.code/'infrastructure-paths.json').read_text())}
        self.new=self.build_candidate()
        assert set(self.old)==set(self.new)
        self.prior=self.release('v1.3.0','1.0.0',self.old,local=True)
        self.candidate=self.release('v1.4.0','1.1.0',self.new)
        self.sign_candidate()
        self.store.write('baseline',self.prior);self.store.write('legacy-lockdown',{'schema':1,'files':{}})
        self.store.write('infrastructure',{'schema':1,'code':{str(p.relative_to(self.code)):sha(p.read_bytes()) for p in self.code.rglob('*') if p.is_file() and '__pycache__' not in str(p)}})
        for name,raw in self.old.items():self.write(self.device._infra_path(name),raw)
        self.root_store.write('recovery-provision',{'mode':'recovery-only','files':{str(self.device._infra_path(n)):sha(b) for n,b in self.old.items() if not n.startswith('updater/')}})
        self.up_store.write('infrastructure',{'schema':1,'code':{n.split('/',1)[1]:sha(b) for n,b in self.old.items() if n.startswith('updater/')},'recovery_sha256':sha((self.root/'recovery-provision.json').read_bytes())})
        self.up_store.write('current',self.prior['components'][0])
        root_c=self.prior['components'][0];self.write(self.updater/'cache'/(root_c['sha256']+'.ipk'),self.device.cache_bytes(root_c))
        for c in self.prior['components'][:2]:self.extract(self.device.cache_bytes(c))
        self.up_store.write('installed-package',{'schema':1,'files':self.device.inspect(self.device.cache_bytes(self.prior['components'][1]),self.prior['components'][1]),'executable':[]})
        self.system_identity()
        self.snapshot_registration()
        self.off=self.root/'persistent-intent.json';self.write(self.off,b'{"version":1,"generation":17,"phase":"disabled","enabled":false,"token":"emergency-off"}');self.off_bytes=self.off.read_bytes()
        self.device._stop_service_processes=lambda target:None
        self.device.rpc=lambda uri,payload:{'returnValue':True,'root':True}
        self.device.runtime=self.runtime
        # Retain the real update guard reserve/file locking; only process/runtime response is substituted.
        self.stack.enter_context(patch('observed_install.install',side_effect=self.installer))
        self.manager=Manager(self.store,self.device)
        from installation import Ownership
        self.owner=Ownership(Store(self.base/'clean-your-tv-installation',uid=os.getuid()))
        return self
    def __exit__(self,*args):return self.stack.__exit__(*args)
    def write(self,path,raw):path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw);path.chmod(0o600)
    def extract(self,raw):
        from cytv.package import data_files
        for name,data in data_files(raw).items():self.write(self.installed/name,data)
    def build_candidate(self):
        from cytv.package import data_files
        payload=self.base/'candidate';payload.mkdir()
        for script,folder in (('root-edition/build.py','root'),('root-edition/build_updater.py','root-updater')):
            subprocess.run([sys.executable,str(PROJECT/script),'--output',str(payload/folder)],check=True)
        spec=importlib.util.spec_from_file_location('current_infrastructure_builder',PROJECT/'system-updater/build.py')
        builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        raw,hashes=builder.infrastructure(payload)
        with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as archive:
            result={member.name:archive.extractfile(member).read() for member in archive}
        assert {name:sha(data) for name,data in result.items()}==hashes
        return result
    def release(self,release,version,infrastructure,local=False):
        components=[]
        for name,app in (('root','com.cleanyourtv.root.preview'),('root-updater','com.cleanyourtv.root.updater')):
            raw,_=sdk(app,version,release);c={'name':name,'application':app,'version':version,'kind':'ipk','sha256':sha(raw),'size':len(raw)}
            if local:c['local']=True
            else:c['url']='https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/'+release+'/'+name+'.ipk'
            self.write(self.state/'cache'/c['sha256'],raw);components.append(c)
        raw=packed(infrastructure);c={'name':'root-infrastructure','version':version,'kind':'infrastructure','sha256':sha(raw),'size':len(raw)}
        if local:c.update(local=True,files={n:sha(b) for n,b in infrastructure.items()})
        else:c['url']='https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/'+release+'/infrastructure.tar.gz'
        self.write(self.state/'cache'/c['sha256'],raw);components.append(c)
        return {'schema':1,'edition':'root','release':release,'supervisor':1,'notes':'Offline legacy compatibility fixture','components':components}
    def sign_candidate(self):
        script="const c=require('crypto'),fs=require('fs'),m=fs.readFileSync(0),k=c.generateKeyPairSync('rsa',{modulusLength:2048});process.stdout.write(JSON.stringify({proof:{payload:m.toString('base64'),signature:c.sign('RSA-SHA256',m,k.privateKey).toString('base64')},key:k.publicKey.export({type:'spki',format:'pem'})}));"
        signed=json.loads(subprocess.run(['node','-e',script],input=json.dumps(self.candidate).encode(),stdout=subprocess.PIPE,check=True).stdout)
        self.write(self.code/'system_updater/release-public.pem',signed['key'].encode());self.candidate['proof']=signed['proof']
        def fetch(method,payload=None,binary=False):
            if method=='offer':return {'candidate':self.candidate}
            assert method=='verify', 'Network/download is forbidden in this offline harness'
            result=subprocess.run(['node',str(self.code/'system_updater/policy.js'),method],input=json.dumps(payload or {}).encode(),stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
            return result.stdout if binary else json.loads(result.stdout)
        self.device.fetch=fetch
    def system_identity(self):
        app='com.cleanyourtv.system.updater';raw,files=sdk(app,'1.0.0','System');c={'version':'1.0.0','sha256':sha(raw),'size':len(raw),'local':True}
        self.write(self.state/'cache'/(c['sha256']+'.ipk'),raw);self.extract(raw)
        self.store.write('bootstrap-bundle',{'schema':1,'package':{k:c[k] for k in ('sha256','size')}})
        self.store.write('installed-package',{'schema':1,'package':c,'files':{n:sha(b) for n,b in files.items()}})
        self.store.write('installed-terminal',{'completed':True,'event':{'id':app,'statusValue':30,'details':{'packageId':app,'client':'com.webos.lunasend-1','ipkFile':'/var/lib/clean-your-tv-installer/cytv-root-install-fixture/package.ipk'}}})
        self.store.write('bootstrap',{'phase':'complete'})
    def snapshot_registration(self):
        contract=json.loads((PROJECT/'tests/system_updates/fixtures/root-contract-v1.3.0.json').read_text())
        spec=importlib.util.spec_from_file_location('system_root_provision',self.updater/'code/provision.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        original={**contract['registration_original'],'client':'{}','api':'{}'};planned=module.plan(original);records={}
        for key,path in module.FILES.items():
            assert sha(planned[key])==contract['registration_sha256'][key]
            self.write(path,original[key].encode());records[str(path)]={'original':original[key],'original_sha256':sha(original[key].encode()),'installed_sha256':sha(planned[key]),'mode':0o600,'uid':os.getuid(),'gid':os.getgid()}
        self.root_store.write('ls2-provision-snapshot',{'files':records});self.planned=planned;self.ls2=module.FILES
    def installer(self,application,path,timeout,on_ready,on_accepted):
        on_ready();raw=Path(path).read_bytes();self.extract(raw)
        # A real TV package replacement can reset provisioned LS2 registrations.
        snapshot=self.root_store.read('ls2-provision-snapshot')
        for name,record in snapshot['files'].items():self.write(Path(name),record['original'].encode())
        return {'completed':True,'event':{'id':application,'statusValue':30}}
    def runtime(self,mode,transaction=None):
        if mode=='status':return {'intent':{'phase':'disabled'},'effective':{'sam_home':'com.webos.app.home','profiles':{'defaultApps':{'categories':{'home':'com.webos.app.home'}},'idleApp':{'appId':'com.webos.app.home','support':True}}}}
        if mode=='suspend-update':
            spec=importlib.util.spec_from_file_location('active_runtime_update_guard',self.root/'runtime/update_guard.py')
            guard=importlib.util.module_from_spec(spec);spec.loader.exec_module(guard)
            stage=getattr(guard,'stage_system_rollback_anchor',None)
            if stage is not None:
                guard.INSTALLED=self.installed
                before=(self.state/'transaction.json').read_bytes()
                run=subprocess.run
                def local_run(args,*a,**kw):
                    if isinstance(args,(list,tuple)) and args[0]=='/usr/bin/node':args=[shutil.which('node'),*args[1:]]
                    return run(args,*a,**kw)
                with patch.object(subprocess,'run',side_effect=local_run):stage(transaction,self.root,uid=os.getuid())
                assert (self.state/'transaction.json').read_bytes()==before, 'Rollback staging changed System journal'
            return 'restored'
        if mode in ('finish-update','abort-update'):
            self.device._guard().release(transaction,self.root,uid=os.getuid())
            return {'status':'skipped'}
        raise AssertionError('Unexpected runtime command '+mode)
    def run_until(self,phase):
        from package_identity import TransitionUnknown
        for _ in range(24):
            # Match the public worker: observe all owners before each manager leg.
            try:assert self.device.components_present()
            except TransitionUnknown:pass
            with self.product_operation():result=self.manager.run()
            if result['phase']==phase:return result
            assert result['phase'] not in ('recovery-required','aborted'),(result['phase'],result.get('error'))
        raise AssertionError(result)
    def assert_disk(self,expected,release):
        for name,data in expected.items():assert self.device._infra_path(name).read_bytes()==data,name
        self.device._root_integrity()
        for key,path in self.ls2.items():assert path.read_bytes()==self.planned[key],key
        for c in release['components']:assert self.device.verify_installed(c),c['name']
        for app in ('com.cleanyourtv.root.preview','com.cleanyourtv.root.updater','com.cleanyourtv.system.updater'):assert self.device.owner_identity(app)['id']==app
        assert self.off.read_bytes()==self.off_bytes
    @contextmanager
    def product_operation(self):
        previous=self.owner.status()
        resume=previous['id'] if previous and not previous['terminal'] else None
        with self.owner.operation('system-update','transaction.json',resume=resume) as record:
            yield
            tx=self.store.read('transaction')
            if tx:self.owner.stage(record,tx['phase'],terminal=tx['phase'] in ('complete','rolled-back','aborted') and tx.get('homeResumePhase')==tx['phase'])
    def finish_like_worker(self,tx):
        # The immutable public CLI writes these fields only after Device.finish returns.
        with self.product_operation():
            resume=self.device.finish(tx)
            tx=self.store.read('transaction');tx['homeResume']=resume;tx['homeResumePhase']=tx['phase']
            self.store.write('transaction',tx)
        return tx
    def complete_update(self,finish=True):
        snapshot={'schema':1,'inventory':{'apps':[],'inputs':[]},'config':{'columns':5,'dockApps':[],'hiddenApps':[]},'settings':{}}
        self.manager.install('root',self.candidate['release'],snapshot)
        tx=self.run_until('verifying')
        if not finish:return tx
        self.manager.healthy('root',tx['id'],'1.1.0');tx=self.run_until('complete')
        tx=self.finish_like_worker(tx)
        self.assert_disk(self.new,self.candidate)
        return tx
    def rollback(self):
        with self.product_operation():self.manager.rollback()
        tx=self.run_until('verifying-rollback');self.manager.healthy('root',tx['id'],'1.0.0');tx=self.run_until('rolled-back');tx=self.finish_like_worker(tx)
        self.assert_disk(self.old,self.prior)
        current=self.up_store.read('current');assert current['version']=='1.0.0';assert current['writer']['id']==tx['id']
        return tx
