"""Windows checkouts must produce runnable POSIX payloads without rewriting binaries."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from cytv import package

ROOT = Path(__file__).resolve().parents[2]


class WindowsPayloadTests(unittest.TestCase):
    def test_autocrlf_checkout_preserves_shell_and_binary_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            def git(*args):
                return subprocess.run(['git', '-c', 'core.autocrlf=true', *args],
                                      cwd=root, check=True, capture_output=True)
            git('init')
            attributes = ROOT / '.gitattributes'
            if attributes.exists():
                (root / '.gitattributes').write_bytes(attributes.read_bytes())
            shell = b'#!/bin/sh\nset -eu\nprintf "LF checked"\n'
            binary = b'!<arch>\n\x00\xff\r\n\x1a'
            (root / 'boot-recover.sh').write_bytes(shell)
            (root / 'published.ipk').write_bytes(binary)
            git('add', '.')
            (root / 'boot-recover.sh').unlink()
            (root / 'published.ipk').unlink()
            git('checkout-index', '--all', '--force')
            self.assertEqual((root / 'published.ipk').read_bytes(), binary)
            self.assertEqual((root / 'boot-recover.sh').read_bytes(), shell)

    def test_payload_rejects_cr_shell_scripts_even_with_valid_hashes(self):
        for ending in (b'\r\n', b'\r'):
            for nested in (False, True):
                with self.subTest(ending=ending, nested=nested), tempfile.TemporaryDirectory() as directory:
                    root = Path(directory)
                    script = b'#!/bin/sh\nset -eu' + ending
                    name = 'root.ipk' if nested else 'boot-recover.sh'
                    raw = package.ipk('com.test', '1.0.0', {'usr/palm/services/com.test/boot-recover.sh': script}) if nested else script
                    (root / name).write_bytes(raw)
                    (root / 'payload.json').write_text(json.dumps({'files': {name: hashlib.sha256(raw).hexdigest()}}))
                    with self.assertRaisesRegex(ValueError, 'POSIX.*LF'):
                        package.verify_payload(root)

    def test_payload_accepts_lf_shell_and_keeps_binary_crlf_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = {'boot-recover.sh': b'#!/bin/sh\nset -eu\n', 'image.png': b'\x89PNG\r\n\x1a\n'}
            raw = package.ipk('com.test', '1.0.0', files)
            files['root.ipk'] = raw
            for name, data in files.items():
                (root / name).write_bytes(data)
            (root / 'payload.json').write_text(json.dumps({'files': {name: hashlib.sha256(data).hexdigest() for name, data in files.items()}}))
            package.verify_payload(root)
            self.assertEqual((root / 'root.ipk').read_bytes(), raw)
            self.assertEqual(package.data_files(raw)['image.png'], b'\x89PNG\r\n\x1a\n')
