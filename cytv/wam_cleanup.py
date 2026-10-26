"""Explicit Root maintenance for four fixed WAM folders; no Python on TV needed."""
import re
import shlex

from .errors import UserError
from .python_runtime import _run

ERROR = 'WAM cleanup could not be verified. Close TV apps and inspect storage before retrying; some selected files may already have been removed.'
SCRIPT = r'''
'use strict';
var fs = require('fs'), crypto = require('crypto');
var BASE = '/var/lib/wam/Default';
var OWNER = 0;
var MOUNTINFO = '/proc/self/mountinfo';
var FOLDERS = ['Session Storage', 'Cache', 'Code Cache', 'GPUCache'];
function fail() { throw new Error('unsafe'); }
function info(path) {
    var s = fs.lstatSync(path);
    if (s.uid !== OWNER || (s.mode & 18) || s.isSymbolicLink() ||
        (!s.isDirectory() && !s.isFile()) || (s.isFile() && s.nlink !== 1)) fail();
    return s;
}
function signature(s) { return [s.dev,s.ino,s.mode,s.uid,s.gid,s.size,s.mtime.getTime(),s.ctime.getTime()].join(':'); }
try {
    if (Number(process.versions.node.split('.')[0]) < 8) fail();
    var parent = info(BASE);
    if (!parent.isDirectory() || fs.realpathSync(BASE) !== BASE) fail();
    var mounts = fs.readFileSync(MOUNTINFO, 'utf8').trim().split('\n').map(function (line) {
        var fields = line.split(' ');
        if (fields.length < 10) fail();
        return fields[4].replace(/\\(040|011|012|134)/g, function (_, octal) { return String.fromCharCode(parseInt(octal, 8)); });
    });
    var nodes = [], bytes = 0, digest = crypto.createHash('sha256');
    function visit(path, depth) {
        if (depth > 64 || nodes.length >= 100000) fail();
        var s = info(path);
        if (s.dev !== parent.dev || mounts.indexOf(path) >= 0) fail();
        var sig = signature(s);
        nodes.push({path:path, sig:sig, identity:[s.dev,s.ino,s.mode,s.uid,s.gid].join(':'), dir:s.isDirectory()});
        digest.update(JSON.stringify([path,sig]));
        if (s.isDirectory()) fs.readdirSync(path).sort().forEach(function (name) { visit(path + '/' + name, depth + 1); });
        else bytes += s.size;
        if (!Number.isSafeInteger(bytes)) fail();
    }
    FOLDERS.forEach(function (name) {
        var path = BASE + '/' + name;
        try { fs.lstatSync(path); } catch (e) { if (e.code === 'ENOENT') return; throw e; }
        visit(path, 0);
    });
    var hash = digest.digest('hex');
    if (process.argv[1] === 'probe') {
        process.stdout.write('CYTV_WAM_READY ' + hash + ' ' + bytes);
    } else if (process.argv[1] === 'clean' && process.argv[2] === hash) {
        nodes.reverse().forEach(function (item) {
            // Recheck each inode immediately before touching it; never follow links.
            var s = info(item.path);
            if (s.dev !== parent.dev || fs.realpathSync(item.path) !== item.path) fail();
            if (item.dir ? [s.dev,s.ino,s.mode,s.uid,s.gid].join(':') !== item.identity : signature(s) !== item.sig) fail();
            if (item.dir) fs.rmdirSync(item.path); else fs.unlinkSync(item.path);
        });
        process.stdout.write('CYTV_WAM_CLEARED');
    } else fail();
} catch (e) {
    process.stdout.write('CYTV_WAM_REFUSED');
    process.exitCode = 1;
}
'''


def _command(action, token='-'):
    script = r'''
ancestors /var/lib/wam/Default
unset NODE_OPTIONS NODE_PATH
node_path=$(command -v node)
node_real=$(readlink -f "$node_path")
[ -f "$node_real" ] && [ -x "$node_real" ] && safe_mode "$node_real"
ancestors "${node_real%/*}"
'''
    return script + '"$node_real" -e ' + shlex.quote(SCRIPT) + ' ' + shlex.quote(action) + ' ' + shlex.quote(token)


def inspect(remote):
    try:
        reply = _run(remote, _command('probe'), timeout=60)
        match = re.fullmatch(r'CYTV_WAM_READY ([a-f0-9]{64}) ([0-9]{1,16})', reply)
        if match and int(match[2]) <= 2**53 - 1:
            return {'token': match[1], 'bytes': int(match[2])}
    except (UserError, OSError):
        pass
    raise UserError('WAM cleanup is unavailable: the fixed folders, root ownership, safe tools or unchanged storage could not be verified.') from None


def clean(remote, token):
    if not isinstance(token, str) or not re.fullmatch('[a-f0-9]{64}', token):
        raise UserError(ERROR)
    try:
        if _run(remote, _command('clean', token), timeout=120) == 'CYTV_WAM_CLEARED': return
    except (UserError, OSError):
        pass
    raise UserError(ERROR) from None


def reboot(remote):
    script = r'''
reboot_path=$(command -v reboot)
reboot_real=$(readlink -f "$reboot_path")
[ -f "$reboot_real" ] && [ -x "$reboot_real" ] && safe_mode "$reboot_real"
ancestors "${reboot_real%/*}"
ancestors "${reboot_path%/*}"
"$reboot_path"
'''
    try:
        _run(remote, script, timeout=30)
    except (UserError, OSError):
        # Disconnect is expected but does not prove reboot. Never submit it again.
        pass
