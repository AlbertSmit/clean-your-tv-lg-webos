import io, pathlib, subprocess, tarfile, tempfile, sys
p=pathlib.Path(sys.argv[1]).resolve()
raw=subprocess.check_output(['ar','p',str(p),'data.tar.gz'])
out=io.BytesIO(); changed=[]
with tarfile.open(fileobj=io.BytesIO(raw),mode='r:gz') as src,tarfile.open(fileobj=out,mode='w:gz') as dst:
 for entry in src:
  name=entry.name.rstrip('/')
  if name.endswith('/com.local.nativehome/state') or name.endswith('/com.local.nativehome.service/state'):
   assert entry.isdir()
   entry.uid=5999;entry.gid=5000;entry.uname='prisoner';entry.gname='jailer';entry.mode=0o770
   changed.append(name)
  dst.addfile(entry,src.extractfile(entry) if entry.isfile() else None)
assert len(changed)==2,changed
with tempfile.TemporaryDirectory() as d:
 q=pathlib.Path(d)/'data.tar.gz';q.write_bytes(out.getvalue())
 subprocess.run(['ar','r',str(p),str(q)],check=True)
print('Set owner prisoner:jailer and mode 0770 for data directories:',changed)
