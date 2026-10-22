"""Fix the independent updater's private writable state directory in a built IPK."""
import io
import pathlib
import sys
import tarfile
p = pathlib.Path(sys.argv[1])
b = p.read_bytes()
assert b[:8] == b'!<arch>\n'
offset = 8
out = bytearray(b[:8])
changed = 0
while offset < len(b):
    h = b[offset:offset + 60]
    assert len(h) == 60 and h[58:] == b'`\n'
    size = int(h[48:58])
    data = b[offset + 60:offset + 60 + size]
    assert len(data) == size
    if h[:16].strip().rstrip(b'/') == b'data.tar.gz':
        buf = io.BytesIO()
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as src, tarfile.open(fileobj=buf, mode='w:gz') as dst:
            for e in src:
                if e.name.rstrip('/') == 'usr/palm/services/com.cleanyourtv.updater.service/state':
                    assert e.isdir()
                    e.uid, e.gid, e.mode = 5999, 5000, 0o700
                    e.uname, e.gname = 'prisoner', 'jailer'
                    changed += 1
                dst.addfile(e, src.extractfile(e) if e.isfile() else None)
        data = buf.getvalue()
    out += h[:48] + str(len(data)).ljust(10).encode() + h[58:] + data + (b'\n' if len(data) % 2 else b'')
    offset += 60 + size + size % 2
assert changed == 1 and offset == len(b)
p.write_bytes(out)
