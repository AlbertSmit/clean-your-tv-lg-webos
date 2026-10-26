"""Installed package data accepts only the platform chain, with strict leaves."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

SOURCE=Path(__file__).parents[1]/'package_data.py'

class PackageDataTests(unittest.TestCase):
    def setUp(self):
        spec=importlib.util.spec_from_file_location('package_data_test',SOURCE)
        self.reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.reader)
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name).resolve()/'apps'
        self.owner='com.cleanyourtv.root.preview'
        self.file=self.root/'usr/palm/applications'/self.owner/'appinfo.json'
        self.file.parent.mkdir(parents=True)
        for directory in (self.root,self.root/'usr',self.root/'usr/palm',self.file.parent.parent):directory.chmod(0o777)
        self.file.parent.chmod(0o755);self.file.write_text(json.dumps({'id':self.owner,'type':'web'}));self.file.chmod(0o644)
        self.metadata=self.root/'usr/palm/packages'/self.owner/'packageinfo.json'
        self.metadata.parent.mkdir(parents=True);self.metadata.parent.chmod(0o755)
        self.metadata.parent.parent.chmod(0o777)
        self.metadata.write_text(json.dumps({'id':self.owner}));self.metadata.chmod(0o644)
    def tearDown(self):self.temp.cleanup()
    def read(self):return self.reader.read(self.file,installed=self.root,uid=os.getuid())
    def test_fixed_shared_chain_accepts_real_0777_with_0755_leaf(self):
        self.assertEqual(json.loads(self.read())['id'],self.owner)
    def test_writable_leaf_file_links_and_foreign_identity_fail(self):
        self.file.parent.chmod(0o777)
        with self.assertRaises(ValueError):self.read()
        self.file.parent.chmod(0o755);self.file.chmod(0o666)
        with self.assertRaises(ValueError):self.read()
        self.file.chmod(0o644);other=self.file.with_name('hardlink');os.link(self.file,other)
        with self.assertRaises(ValueError):self.read()
        other.unlink();self.file.rename(other);self.file.symlink_to(other.name)
        with self.assertRaises((ValueError,OSError)):self.read()
    def test_leaf_replacement_during_read_fails_binding(self):
        original=os.read;switched=[]
        def race(fd,count):
            raw=original(fd,count)
            if not switched:
                switched.append(True);old=self.file.parent.with_name('old');self.file.parent.rename(old)
                self.file.parent.mkdir();self.file.write_text('{"id":"foreign"}')
            return raw
        with patch.object(self.reader.os,'read',side_effect=race):
            with self.assertRaises(ValueError):self.read()
    def test_generic_writable_ancestor_is_rejected(self):
        self.file.parent.parent.chmod(0o755)
        # A directory below the allowlisted package leaf is never a shared exception.
        nested=self.file.parent/'nested';nested.mkdir();nested.chmod(0o777)
        path=nested/'appinfo.json';path.write_text('{}')
        with self.assertRaises(ValueError):self.reader.read(path,installed=self.root,uid=os.getuid())
    def test_symlink_at_each_platform_or_leaf_level_is_rejected(self):
        for directory in (self.root/'usr',self.root/'usr/palm',self.file.parent.parent,self.file.parent):
            old=directory.with_name(directory.name+'-saved');directory.rename(old);directory.symlink_to(old.name,target_is_directory=True)
            try:
                with self.assertRaises((ValueError,OSError)):self.read()
            finally:directory.unlink();old.rename(directory)

    def test_foreign_owner_at_each_boundary_fails(self):
        original=os.fstat
        for attacked in (self.root,self.root/'usr',self.root/'usr/palm',self.file.parent.parent,self.file.parent,self.file):
            inode=attacked.stat().st_ino
            def changed(fd):
                value=original(fd)
                if value.st_ino==inode:
                    parts=list(value);parts[4]=os.getuid()+1;return os.stat_result(parts)
                return value
            with patch.object(self.reader.os,'fstat',side_effect=changed):
                with self.assertRaises(ValueError):self.read()

    def read_as_root(self,path,owners):
        # Real fds, modes, inodes and bytes; model only platform ownership on a
        # host that cannot chown fixtures to root or the observed metadata owner.
        original_fstat,original_lstat=os.fstat,Path.lstat
        identities={(value.st_dev,value.st_ino):uid
                    for name,uid in owners.items() for value in (original_lstat(name),)}
        def ownership(info):
            values={name:getattr(info,name) for name in dir(info) if name.startswith('st_')}
            values['st_uid']=identities.get((info.st_dev,info.st_ino),0)
            return SimpleNamespace(**values)
        with patch.object(self.reader.os,'fstat',side_effect=lambda fd:ownership(original_fstat(fd))), \
             patch.object(Path,'lstat',lambda path:ownership(original_lstat(path))):
            return self.reader.read(path,installed=self.root,uid=0)

    def test_fixed_package_metadata_container_uid501_accepts_strict_root_owned_leaf_and_file(self):
        for owner in (0,501):
            with self.subTest(container_uid=owner):
                raw=self.read_as_root(self.metadata,{self.metadata.parent.parent:owner})
                self.assertEqual(json.loads(raw)['id'],self.owner)

    def test_metadata_uid_exception_rejects_other_owners_and_every_noncontainer_path(self):
        container=self.metadata.parent.parent
        for owner in (500,502,1000):
            with self.subTest(container_uid=owner),self.assertRaises(ValueError):
                self.read_as_root(self.metadata,{container:owner})
        for path in (self.root,self.root/'usr',self.root/'usr/palm',
                     self.file.parent.parent,self.file.parent,self.file,
                     self.metadata.parent,self.metadata):
            target=self.file if path in (self.file.parent.parent,self.file.parent,self.file) else self.metadata
            with self.subTest(foreign_path=path),self.assertRaises(ValueError):
                self.read_as_root(target,{container:501,path:501})

    def test_uid501_metadata_container_does_not_allow_symlinks(self):
        container=self.metadata.parent.parent;old=container.with_name('packages-saved')
        container.rename(old);container.symlink_to(old.name,target_is_directory=True)
        with self.assertRaises((ValueError,OSError)):
            self.read_as_root(self.metadata,{old:501})

    def assert_metadata_replacement_rejected(self,directory):
        original_read=os.read;original=self.metadata.read_bytes();switched=[]
        def replace(fd,count):
            raw=original_read(fd,count)
            if not switched:
                switched.append(True);directory.rename(directory.with_name(directory.name+'-saved'))
                self.metadata.parent.mkdir(parents=True);self.metadata.parent.chmod(0o755)
                self.metadata.write_bytes(original);self.metadata.chmod(0o644)
            return raw
        with patch.object(self.reader.os,'read',side_effect=replace),self.assertRaises(ValueError):
            self.read_as_root(self.metadata,{self.metadata.parent.parent:501})
        self.assertTrue(switched,'the metadata read reached the replacement race')

    def test_uid501_metadata_container_replacement_is_detected(self):
        self.assert_metadata_replacement_rejected(self.metadata.parent.parent)

    def test_uid501_metadata_own_leaf_replacement_is_detected(self):
        self.assert_metadata_replacement_rejected(self.metadata.parent)
