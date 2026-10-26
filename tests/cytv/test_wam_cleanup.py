import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from cytv import wam_cleanup as wam

@unittest.skipUnless(os.name == 'posix' and shutil.which('node'), 'Requires POSIX Node.js filesystem fixtures')
class CleanupTests(unittest.TestCase):
    def test_bootstrap_ignores_node_preload_environment(self):
        command = wam._command('probe').replace(shlex.quote(wam.SCRIPT), shlex.quote(self.script))
        prefix = 'set -eu\nsafe_mode() { return 0; }\nancestors() { return 0; }\n'
        result = subprocess.run(['/bin/sh', '-c', prefix + command],
            env=dict(os.environ, NODE_OPTIONS='--require /nonexistent-cytv-wam-preload'),
            capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('CYTV_WAM_READY', result.stdout)

    def test_reboot_preserves_busybox_applet_name(self):
        executable = self.base.parent/'busybox'
        marker = self.base.parent/'reboot-called'
        executable.write_text('#!/bin/sh\n[ "${0##*/}" = reboot ] && touch ' + str(marker) + '\n')
        executable.chmod(0o700)
        reboot_path = self.base.parent/'reboot'
        reboot_path.symlink_to(executable)
        def run(remote, script, **kwargs):
            prefix = 'set -eu\nsafe_mode() { return 0; }\nancestors() { return 0; }\n'
            prefix += 'command() { printf "%s" ' + str(reboot_path) + '; }\n'
            result = subprocess.run(['/bin/sh', '-c', prefix + script], capture_output=True, text=True, timeout=10)
            return result.stdout
        with patch.object(wam, '_run', side_effect=run):
            wam.reboot(None)
        self.assertTrue(marker.exists())

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()/'Default'
        self.base.mkdir(mode=0o700)
        self.mounts = self.base.parent/'mountinfo'
        self.mounts.write_text('1 0 0:1 / / rw - tmpfs tmpfs rw\n')
        self.script = wam.SCRIPT.replace("'/var/lib/wam/Default'", json.dumps(str(self.base))).replace('var OWNER = 0;', 'var OWNER = '+str(os.getuid())+';').replace("'/proc/self/mountinfo'",json.dumps(str(self.mounts)))
        for name in ('Session Storage','Cache','Code Cache','GPUCache','Local Storage','Service Worker','databases'):
            folder=self.base/name;folder.mkdir(mode=0o700);(folder/'data').write_bytes(b'preserve-or-delete')
        self.node = shutil.which('node')
    def run_js(self, action, token='-'):
        return subprocess.run([self.node,'-e',self.script,action,token],capture_output=True,text=True,timeout=10)
    def token(self):
        result=self.run_js('probe')
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        return result.stdout.split()[1]
    def test_only_selected_trees_removed(self):
        token=self.token(); result=self.run_js('clean',token)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
        self.assertEqual(result.stdout,'CYTV_WAM_CLEARED')
        for name in ('Session Storage','Cache','Code Cache','GPUCache'):self.assertFalse((self.base/name).exists())
        for name in ('Local Storage','Service Worker','databases'):self.assertEqual((self.base/name/'data').read_bytes(),b'preserve-or-delete')
    def test_already_empty_selection_is_a_safe_noop(self):
        for name in ('Session Storage','Cache','Code Cache','GPUCache'):
            shutil.rmtree(self.base/name)
        result = self.run_js('clean', self.token())
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        self.assertTrue((self.base/'Local Storage'/'data').exists())

    def test_changed_snapshot_refuses_before_deletion(self):
        token=self.token();(self.base/'Cache'/'new').write_bytes(b'new')
        self.assertNotEqual(self.run_js('clean',token).returncode,0)
        self.assertTrue((self.base/'Session Storage'/'data').exists())
    def test_symlink_and_hardlink_refused_before_deletion(self):
        for link in ('symbolic','hard'):
            path=self.base/'Cache'/'link';target=self.base/'Local Storage'/'data'
            if link=='symbolic':path.symlink_to(target)
            else:os.link(target,path)
            self.assertNotEqual(self.run_js('probe').returncode,0)
            self.assertEqual(target.read_bytes(),b'preserve-or-delete');path.unlink()
    def test_mountpoint_and_writable_directory_refused(self):
        encoded=str(self.base/'Session Storage').replace(' ','\\040')
        self.mounts.write_text('1 0 0:1 / '+encoded+' rw - tmpfs tmpfs rw\n')
        self.assertNotEqual(self.run_js('probe').returncode,0)
        self.mounts.write_text('1 0 0:1 / / rw - tmpfs tmpfs rw\n')
        os.chmod(self.base/'Cache',0o777)
        self.assertNotEqual(self.run_js('probe').returncode,0)

if __name__=='__main__':unittest.main()
