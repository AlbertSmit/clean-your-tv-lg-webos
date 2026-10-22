import io
from pathlib import Path
import subprocess
import tarfile
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

class PackageTests(unittest.TestCase):
    def test_archive_members_and_state_permissions(self):
        payload = io.BytesIO()
        names = ['usr/palm/applications/com.local.nativehome/state',
                 'usr/palm/services/com.local.nativehome.service/state']
        with tarfile.open(fileobj=payload, mode='w:gz') as archive:
            for name in names:
                entry = tarfile.TarInfo(name); entry.type = tarfile.DIRTYPE
                entry.mode = 0o775; archive.addfile(entry)
            entry = tarfile.TarInfo('usr/palm/example.txt'); entry.size = 5
            archive.addfile(entry, io.BytesIO(b'hello'))
        members = [('debian-binary', b'2.0\n'), ('control.tar.gz', b'odd'), ('data.tar.gz', payload.getvalue())]
        raw = bytearray(b'!<arch>\n')
        for name, data in members:
            header = f'{name+"/":<16}{0:<12}{0:<6}{0:<6}{"100644":<8}{len(data):<10}`\n'.encode()
            raw += header + data + (b'\n' if len(data)%2 else b'')
        with tempfile.TemporaryDirectory() as tmp:
            package = Path(tmp)/'test.ipk'; package.write_bytes(raw)
            subprocess.run(['python3', str(ROOT/'scripts/fix-package-data.py'), str(package)], check=True, capture_output=True)
            data = package.read_bytes(); self.assertEqual(data[:8], b'!<arch>\n')
            offset=8; found={}
            while offset < len(data):
                header=data[offset:offset+60]; self.assertEqual(header[58:], b'`\n')
                size=int(header[48:58]); name=header[:16].decode().strip().rstrip('/')
                found[name]=data[offset+60:offset+60+size]
                self.assertEqual(len(found[name]), size)
                offset += 60+size+(size%2)
            self.assertEqual(offset, len(data))
            self.assertEqual(list(found), [name for name,_ in members])
            self.assertEqual(found['debian-binary'], b'2.0\n')
            self.assertEqual(found['control.tar.gz'], b'odd')
            with tarfile.open(fileobj=io.BytesIO(found['data.tar.gz']), mode='r:gz') as archive:
                for name in names:
                    entry=archive.getmember(name)
                    self.assertEqual((entry.uid,entry.gid,entry.mode), (5999,5000,0o770))
                    self.assertEqual((entry.uname,entry.gname), ('prisoner','jailer'))
                self.assertEqual(archive.extractfile('usr/palm/example.txt').read(), b'hello')

if __name__ == '__main__': unittest.main()
