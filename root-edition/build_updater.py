#!/usr/bin/env python3
"""Build a separate Root Updater and its explicit one-time host setup bundle."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
UPDATER_FILES=('core.py','store.py','profile.py','device.py','package.py','cli.py','fetch.js','bridge.js','luna.py','bootstrap.py')
SUPPORT=('observed_install.py','installer_status.py','provision.py','deploy.py','setup.py','system_permissions.py','activity.py','startup_hook.py')
APP='com.cleanyourtv.root.updater'


def source(path):
    if any(p.is_symlink() for p in (path,*path.parents)) or not path.is_file():raise ValueError('Missing or indirect updater source')
    return path.read_bytes()


def build(output):
    output=Path(output).absolute()
    if '..' in output.parts or any(p.is_symlink() for p in (output,*output.parents)):raise ValueError('Indirect build output')
    spec=importlib.util.spec_from_file_location('root_ipk_builder',ROOT/'build.py')
    builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
    code={'updater/'+name:source(ROOT/'updater'/name) for name in UPDATER_FILES}
    code.update({name:source(ROOT/name) for name in SUPPORT})
    code['updater/release-public.pem']=source(ROOT.parent/'updater-service/release-public.pem')
    code['service.js']=source(ROOT/'updater/service.js')
    code['run-updater.py']=b'from updater.cli import entry\nentry()\n'
    code['services.json']=(json.dumps({'id':APP+'.service','services':[{'name':APP+'.service'}]})+'\n').encode()
    code['package.json']=(json.dumps({'name':APP+'.service','version':'0.1.0','main':'service.js'})+'\n').encode()
    code['setup-updater.py']=source(ROOT/'setup_updater.py')
    files={}
    prefix='usr/palm/applications/'+APP+'/'
    app={'id':APP,'version':'0.1.0','vendor':'Clean Your TV','type':'web','main':'index.html','title':'Root Updater','icon':'icon.png','largeIcon':'icon.png','noSplashOnLaunch':True,'disableBackHistoryAPI':True,'requiredPermissions':[]}
    files[prefix+'appinfo.json']=(json.dumps(app)+'\n').encode()
    files[prefix+'icon.png']=source(ROOT.parent/'launcher/brand-v2-icon.png')
    files[prefix+'root-settings.css']=source(ROOT/'ui/root-settings.css')
    files[prefix+'root-updates.js']=source(ROOT/'ui/root-updates.js')
    files[prefix+'index.html']=b'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=1920"><title>Root Updater</title><link rel="stylesheet" href="root-settings.css"></head><body style="background:#10121a;color:white"><script src="root-updates.js"></script><script>RootUpdates.open({recovery:true});</script></body></html>\n'
    sp='usr/palm/services/'+APP+'.service/'
    files[sp+'service.js']=b"'use strict';require('/var/lib/clean-your-tv-root-updater/code/service.js');\n"
    files[sp+'package.json']=code['package.json'];files[sp+'services.json']=code['services.json']
    files['usr/palm/packages/'+APP+'/packageinfo.json']=(json.dumps({'id':APP,'version':'0.1.0','app':APP,'services':[APP+'.service']})+'\n').encode()
    control=('Package: '+APP+'\nVersion: 0.1.0\nSection: misc\nPriority: optional\nArchitecture: all\nMaintainer: Clean Your TV\nDescription: Independent Root application updater and recovery\n').encode()
    code['root-updater.ipk']=builder.ar({'debian-binary':b'2.0\n','control.tar.gz':builder.tgz({'control':control}),'data.tar.gz':builder.tgz(files)})
    output.mkdir(exist_ok=False)
    for name,raw in code.items():
        target=output/name;target.parent.mkdir(exist_ok=True);target.write_bytes(raw)
    (output/'bundle.json').write_text(json.dumps({'schema':1,'files':{name:hashlib.sha256(raw).hexdigest() for name,raw in sorted(code.items())}},indent=2)+'\n')
    return output/'root-updater.ipk'


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    print(build(parser.parse_args().output))
