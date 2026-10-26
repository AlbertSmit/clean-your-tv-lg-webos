#!/usr/bin/env python3
"""Build a reproducible complete offline bootstrap from verified component bundles."""
import argparse
import hashlib
import json
import importlib.util
from pathlib import Path
import shutil
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from cytv import package, python_runtime
from homebrew.payload import checked_bundle, inventory, read_file, validate_runtime

IDENTITIES={'root':'com.cleanyourtv.root.preview','root-updater':'com.cleanyourtv.root.updater','supervisor':'com.cleanyourtv.system.updater'}

def build_payload(root_bundle, root_updater_bundle, supervisor_bundle, runtime_archive, output):
    output=Path(output).absolute()
    if '..' in output.parts or any(p.is_symlink() for p in (output,*output.parents)): raise ValueError('Unsafe output')
    inputs=dict(zip(IDENTITIES,(root_bundle,root_updater_bundle,supervisor_bundle)))
    components={}; versions={}; package_names={}
    for key,root in inputs.items():
        root=Path(root);components[key]=checked_bundle(root)
        ipks=[n for n in components[key] if n.endswith('.ipk')]
        if len(ipks)!=1: raise ValueError('Expected one component package')
        package_names[key]=ipks[0]
        files=package.data_files(read_file(root/ipks[0]))
        app=IDENTITIES[key]
        info=json.loads(files['usr/palm/applications/'+app+'/appinfo.json'])
        if info.get('id')!=app: raise ValueError('Component identity mismatch')
        versions[key]=info['version']
    # Shared protocol/binding sources must come from the same component baseline.
    for name in ('installation.py','observed_install.py','installer_status.py','startup_hook.py','python_binding.py','python_boot.js'):
        hashes={components[key].get(name,{}).get('sha256') for key in inputs}
        if len(hashes)!=1 or None in hashes: raise ValueError('Mismatched component baseline: '+name)
    # Reuse each component's authoritative inventory contract, including required files.
    project=Path(__file__).resolve().parents[1]
    sys.path.insert(0,str(project/'root-edition'))
    from deploy import verify_bundle as verify_root
    from updater.bootstrap import verify_bundle as verify_updater
    verify_root(root_bundle);verify_updater(root_updater_bundle)
    spec=importlib.util.spec_from_file_location('homebrew_supervisor_setup',project/'system-updater/setup.py')
    setup=importlib.util.module_from_spec(spec);spec.loader.exec_module(setup)
    setup.verify_bundle(supervisor_bundle)
    raw=python_runtime._verified_bytes(Path(runtime_archive))
    output.mkdir()
    try:
        for key,root in inputs.items():
            for name in components[key]:
                target=output/key/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(read_file(Path(root)/name))
        spec=importlib.util.spec_from_file_location('homebrew_supervisor_builder',Path(__file__).resolve().parents[1]/'system-updater/build.py')
        supervisor=importlib.util.module_from_spec(spec);spec.loader.exec_module(supervisor)
        supervisor.prepare_baseline(output,'root',output/'baseline')
        binding=python_runtime.normalize_to_file(raw,output/'runtime.tar.gz')
        runtime_files=validate_runtime(output/'runtime.tar.gz',binding)
        (output/'runtime-binding.json').write_text(json.dumps(binding,sort_keys=True,separators=(',',':')))
        provenance={'url':python_runtime.URL,'sha256':python_runtime.SHA256,'size':python_runtime.SIZE,
                    'license':'Python-2.0; included runtime LICENSE and component licenses',
                    'normalized_sha256':hashlib.sha256(read_file(output/'runtime.tar.gz')).hexdigest()}
        if not any(n=='LICENSE' or n.endswith('/LICENSE') for n in runtime_files): raise ValueError('Runtime license missing')
        (output/'runtime-provenance.json').write_text(json.dumps(provenance,sort_keys=True,separators=(',',':')))
        (output/'runtime.js').write_bytes(read_file(Path(__file__).with_name('runtime.js')))
        bootstrap={'shell':python_runtime._SHELL,'smoke':python_runtime.SMOKE,'inspect_probe':python_runtime._PROBE_BODY.split('with tempfile.TemporaryDirectory')[0]+"\nprint('CYTV_SYSTEM_PYTHON')\n",'system_probe':python_runtime.SYSTEM_PROBE,'promote':python_runtime._PROMOTE}
        (output/'runtime-bootstrap.json').write_text(json.dumps(bootstrap,sort_keys=True,separators=(',',':')))
        manifest={'schema':1,'files':inventory(output),'components':components,'versions':versions,'packages':package_names,
                  'runtime':{'archive_sha256':python_runtime.SHA256,'files':runtime_files,
                             'max_unpacked':python_runtime.MAX_UNPACKED,'max_files':python_runtime.MAX_FILES,
                             'required_space':320*1024*1024}}
        (output/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,separators=(',',':'))+'\n')
        return output/'manifest.json'
    except BaseException:
        shutil.rmtree(output);raise

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('root-bundle','root-updater-bundle','supervisor-bundle','runtime-archive','output'): parser.add_argument('--'+name,type=Path,required=True)
    print(build_payload(**vars(parser.parse_args())))
