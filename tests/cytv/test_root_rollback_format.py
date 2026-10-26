import hashlib
import importlib.util
import io
from pathlib import Path
import tarfile
import unittest
from cytv import package


class RootRollbackFormatTests(unittest.TestCase):
    def test_personalized_root_is_accepted_by_real_updater_validator(self):
        app = package.ROOT_APP
        prefix = 'usr/palm/applications/' + app + '/'
        files = {prefix+'appinfo.json': ('{"id":"'+app+'","version":"0.1.3","type":"web","main":"index.html"}').encode(),
                 prefix+'index.html': b'<html></html>',
                 'usr/palm/packages/'+app+'/packageinfo.json': ('{"id":"'+app+'","app":"'+app+'","version":"0.1.3","services":[]}').encode()}
        raw, expected = package.personalize(package.ipk(app,'0.1.3',files), app, {'apps':[{'id':'youtube'}], 'inputs':[]})
        path = Path(__file__).resolve().parents[2] / 'root-edition/updater/package.py'
        spec = importlib.util.spec_from_file_location('root_updater_package_check', path)
        validator = importlib.util.module_from_spec(spec); spec.loader.exec_module(validator)
        actual = validator.inspect_package(raw, {'version':'0.1.3','size':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
        self.assertEqual(actual, {name:hashlib.sha256(data).hexdigest() for name,data in expected.items()})

    def test_personalization_preserves_execution_and_normalizes_other_mode_bits(self):
        for app in (package.ROOT_APP,'com.gathin.tvhome'):
            with self.subTest(app=app):
                prefix='usr/palm/applications/'+app+'/'
                files={prefix+'startup.sh':b'#!/bin/sh\nexit 0\n',prefix+'config.js':b'config'}
                original=package.read_ar(package.ipk(app,'1.0.0',files))
                stream=io.BytesIO()
                with tarfile.open(fileobj=stream,mode='w:gz') as archive:
                    for name,raw in files.items():
                        member=tarfile.TarInfo(name);member.size=len(raw)
                        member.mode=0o4751 if name.endswith('startup.sh') else 0o2640
                        archive.addfile(member,io.BytesIO(raw))
                original['data.tar.gz']=stream.getvalue()
                personalized,_=package.personalize(package.ar(original),app,{'apps':[{'id':'org.example.video'}]})
                with tarfile.open(fileobj=io.BytesIO(package.read_ar(personalized)['data.tar.gz'])) as archive:
                    self.assertEqual(archive.getmember(prefix+'startup.sh').mode,0o755)
                    self.assertEqual(archive.getmember(prefix+'config.js').mode,0o644)
                    self.assertEqual(archive.getmember(prefix+'apps.js').mode,0o644)
                if app==package.ROOT_APP:package.verify_root_rollback_format(personalized)

    def test_no_root_still_contains_parent_directories(self):
        app='com.gathin.tvhome'
        raw,_=package.personalize(package.ipk(app,'1.3.1',{'usr/palm/applications/'+app+'/index.html':b'home'}),app,{'apps':[{'id':'youtube'}]})
        with tarfile.open(fileobj=io.BytesIO(package.read_ar(raw)['data.tar.gz']),mode='r:gz') as archive:
            self.assertTrue(any(item.isdir() for item in archive))

    def test_root_preflight_accepts_secure_owned_leaf_directories(self):
        raw=package.ipk(package.ROOT_APP,'0.1.3',{'usr/palm/applications/'+package.ROOT_APP+'/index.html':b'home'})
        package.verify_root_rollback_format(raw)
        fixed,_=package.personalize(raw,package.ROOT_APP,{'apps':[{'id':'youtube'}]})
        package.verify_root_rollback_format(fixed)
        with tarfile.open(fileobj=io.BytesIO(package.read_ar(fixed)['data.tar.gz'])) as archive:
            dirs=[entry for entry in archive if entry.isdir()]
        self.assertTrue(dirs);self.assertTrue(all(len(Path(entry.name).parts)>=4 and entry.mode==0o755 for entry in dirs))
