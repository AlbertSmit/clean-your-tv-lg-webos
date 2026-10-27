"""Use the verified bundled runtime's permission code without replacing retained code."""
import ast
import hashlib
import json
from pathlib import Path


def program(bundle, enable=True):
    bundle=Path(bundle)
    manifest=json.loads((bundle/'bundle.json').read_bytes())
    source=bundle/'runtime/cli.py'
    if source.is_symlink() or hashlib.sha256(source.read_bytes()).hexdigest()!=manifest.get('files',{}).get('runtime/cli.py'):
        raise ValueError('Firmware permission source integrity mismatch')
    raw=source.read_text();tree=ast.parse(raw)
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='firmware_access']
    if len(functions)!=1 or type(enable) is not bool:raise ValueError('Unsupported firmware permission source')
    return ast.get_source_segment(raw,functions[0])+'\nimport json\nprint(json.dumps(firmware_access(enable='+repr(enable)+')))\n'
