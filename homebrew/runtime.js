/* Node 8 backend: fixed offline Python bootstrap; no browser command surface. */
'use strict';
var fs = require('fs'), path = require('path'), crypto = require('crypto'), cp = require('child_process');
var BASE = '/var/lib/clean-your-tv-python';
var PIN = '4a71641c8d5536175e404a961624e8656eba30e97b5026f6bd7dc31e4bbeaaea';
var MAX = 160 * 1024 * 1024, COUNT = 12000;
function fail(message) { throw new Error(message); }
function safeName(name) {
    if (typeof name !== 'string' || name.length > 512 || !/^[A-Za-z0-9_+.,@=/-]+$/.test(name) || name.split('/').some(function (p) { return !p || p === '.' || p === '..'; })) fail('Unsafe payload path');
    return name;
}
function owned(name, directory) {
    var s = fs.lstatSync(name);
    if (s.uid !== 0 || (s.mode & 18) || s.isSymbolicLink() || (directory ? !s.isDirectory() : !s.isFile() || s.nlink !== 1)) fail('Unsafe root-owned path: ' + name);
    return s;
}
function ancestors(name) {
    name = path.resolve(name);
    while (true) { owned(name, true); var parent = path.dirname(name); if (parent === name) return; name = parent; }
}
function json(name) {
    if (owned(name, false).size > 4 * 1024 * 1024) fail('Oversized payload manifest');
    return JSON.parse(fs.readFileSync(name, 'utf8'));
}
function hash(name, expected) {
    return new Promise(function (resolve, reject) {
        var flags = fs.constants.O_RDONLY | (fs.constants.O_NOFOLLOW || 0) | (fs.constants.O_NONBLOCK || 0);
        fs.open(name, flags, function (error, fd) {
            if (error) return reject(error);
            var before;
            try {
                before = fs.fstatSync(fd);
                if (!before.isFile() || before.nlink !== 1 || before.uid !== 0 || (before.mode & 18) || before.size !== expected.size) fail('Payload size or ownership mismatch');
            } catch (e) { fs.closeSync(fd); return reject(e); }
            var h = crypto.createHash('sha256'), bytes = 0;
            var stream = fs.createReadStream(name, { fd: fd, autoClose: true });
            stream.on('data', function (chunk) { bytes += chunk.length; h.update(chunk); if (bytes > expected.size) stream.destroy(new Error('Payload grew during verification')); });
            stream.on('error', reject);
            stream.on('end', function () {
                try {
                    var after = owned(name, false);
                    if (bytes !== expected.size || h.digest('hex') !== expected.sha256 || before.ino !== after.ino || before.dev !== after.dev || before.mtime.getTime() !== after.mtime.getTime()) fail('Payload hash or binding mismatch');
                    resolve();
                } catch (e) { reject(e); }
            });
        });
    });
}
function walk(root, expected) {
    ancestors(root);
    var seen = {}, dirs = {}, total = 0, names = Object.keys(expected);
    names.forEach(function (name) {
        safeName(name); var r = expected[name];
        if (!r || !Number.isSafeInteger(r.size) || r.size < 0 || !/^[0-9a-f]{64}$/.test(r.sha256)) fail('Invalid file record');
        var parent = path.posix.dirname(name);
        while (parent !== '.') { dirs[parent] = true; parent = path.posix.dirname(parent); }
    });
    function visit(folder, prefix) {
        fs.readdirSync(folder).sort().forEach(function (entry) {
            var name = prefix + entry, full = path.join(folder, entry); safeName(name);
            var s = fs.lstatSync(full);
            if (s.isDirectory()) {
                if (!dirs[name]) fail('Unexpected payload directory');
                owned(full, true); visit(full, name + '/');
            } else {
                owned(full, false);
                if (!Object.prototype.hasOwnProperty.call(expected, name)) fail('Unexpected payload file');
                seen[name] = true; total += s.size;
            }
        });
    }
    visit(root, '');
    if (Object.keys(seen).length !== names.length) fail('Missing payload file');
    // Sequential streaming keeps memory and descriptor usage bounded on the TV.
    return names.reduce(function (promise, name) { return promise.then(function () { return hash(path.join(root, name), expected[name]); }); }, Promise.resolve()).then(function () { return total; });
}
function run(executable, args, marker) {
    return new Promise(function (resolve, reject) {
        cp.execFile(executable, args, { timeout: 90000, maxBuffer: 65536, env: { PATH: '/usr/sbin:/usr/bin:/sbin:/bin', LC_ALL: 'C' } }, function (error, stdout) {
            if (error || (marker && stdout.trim() !== marker)) return reject(new Error('Verified runtime operation failed'));
            resolve(stdout.trim());
        });
    });
}
function quote(value) { return "'" + value.replace(/'/g, "'\\''") + "'"; }
function shell(bootstrap, script) { return run('/bin/sh', ['-c', bootstrap.shell + script]); }
function abi() {
    if (process.platform !== 'linux' || process.arch !== 'arm') fail('Private Python requires ARMv7 little-endian soft-float EABI5 Linux');
    // /bin/sh can be the distribution's expected symlink; validate its real target.
    var executable = fs.realpathSync('/bin/sh'); ancestors(path.dirname(executable)); owned(executable, false);
    var fd = fs.openSync(executable, 'r'), header = Buffer.alloc(40);
    try { if (fs.readSync(fd, header, 0, 40, 0) !== 40) fail('Unknown Linux ABI'); } finally { fs.closeSync(fd); }
    if (header.toString('hex', 0, 4) !== '7f454c46' || header[4] !== 1 || header[5] !== 1 || header.readUInt16LE(18) !== 40 || (header[37] & 4) || header[39] !== 5) fail('Unsupported ARM ABI; private Python was not installed');
}
function verifiedPayload(root) {
    root = path.resolve(root); ancestors(root);
    var manifest = json(path.join(root, 'manifest.json'));
    if (manifest.schema !== 1 || !manifest.runtime || manifest.runtime.archive_sha256 !== PIN || manifest.runtime.max_unpacked !== MAX || manifest.runtime.max_files !== COUNT || !Number.isSafeInteger(manifest.runtime.required_space) || manifest.runtime.required_space < 320 * 1024 * 1024) fail('Invalid runtime binding');
    var expected = manifest.files;
    if (!expected || Object.keys(expected).length > COUNT * 3 || expected['manifest.json']) fail('Invalid payload inventory');
    // Manifest is trusted by the installed package ownership boundary, never UI input.
    expected['manifest.json'] = { size: owned(path.join(root, 'manifest.json'), false).size, sha256: crypto.createHash('sha256').update(fs.readFileSync(path.join(root, 'manifest.json'))).digest('hex') };
    return walk(root, expected).then(function () {
        var binding = json(path.join(root, 'runtime-binding.json')), provenance = json(path.join(root, 'runtime-provenance.json'));
        var files = manifest.runtime.files;
        if (!files || Object.keys(files).length > COUNT || binding.schema !== 1 || binding.archive_sha256 !== PIN || provenance.sha256 !== PIN || provenance.normalized_sha256 !== expected['runtime.tar.gz'].sha256) fail('Runtime provenance mismatch');
        var total = 0;
        Object.keys(files).forEach(function (name) {
            safeName(name); var record = files[name];
            if (!record || !Number.isSafeInteger(record.size) || record.size < 0 || !/^[0-9a-f]{64}$/.test(record.sha256) || (record.mode !== 420 && record.mode !== 493)) fail('Invalid runtime file metadata');
            total += record.size;
            if (name !== '.cytv-runtime.json' && binding.files[name] !== files[name].sha256) fail('Runtime inventory binding mismatch');
        });
        if (!files['.cytv-runtime.json'] || files['.cytv-runtime.json'].sha256 !== expected['runtime-binding.json'].sha256 || files['.cytv-runtime.json'].size !== expected['runtime-binding.json'].size || Object.keys(files).length !== Object.keys(binding.files).length + 1 || total > MAX || !files['bin/python3.13'] || !(files['bin/python3.13'].mode & 73)) fail('Invalid runtime inventory');
        var bootstrap = json(path.join(root, 'runtime-bootstrap.json'));
        ['shell', 'smoke', 'inspect_probe', 'system_probe', 'promote'].forEach(function (key) { if (typeof bootstrap[key] !== 'string' || !bootstrap[key]) fail('Missing fixed runtime bootstrap'); });
        return { root: root, manifest: manifest, bootstrap: bootstrap };
    });
}
function inspectInternal(payloadRoot) {
    return Promise.resolve().then(function () {
        if (!process.geteuid || process.geteuid() !== 0) fail('Root execution is required');
        return verifiedPayload(payloadRoot);
    }).then(function (context) {
        var systemSafe = Promise.resolve().then(function () {
            var executable = fs.realpathSync('/usr/bin/python3');
            ancestors(path.dirname(executable)); owned(executable, false);
            return run('/usr/bin/python3', ['-I', '-B', '-c', context.bootstrap.inspect_probe], 'CYTV_SYSTEM_PYTHON');
        });
        return systemSafe.then(function () {
            return { python: '/usr/bin/python3', privateRuntimeRequired: false, context: context };
        }, function () {
            abi(); ancestors('/var/lib');
            var slot = BASE + '/' + PIN;
            if (fs.existsSync(BASE)) ancestors(BASE);
            if (fs.existsSync(slot) || (function () { try { fs.lstatSync(slot); return true; } catch (e) { if (e.code !== 'ENOENT') throw e; return false; } }())) {
                return walk(slot, context.manifest.runtime.files).then(function () {
                    return run(slot + '/bin/python3.13', ['-I', '-B', '-c', context.bootstrap.inspect_probe], 'CYTV_SYSTEM_PYTHON');
                }).then(function () { return { python: slot + '/bin/python3.13', privateRuntimeRequired: false, context: context }; });
            }
            return shell(context.bootstrap, "ancestors /var/lib\navailable=$(df -Pk /var/lib | awk 'END {print $4}')\ncase \"$available\" in ''|*[!0-9]*) exit 1;; esac\n[ \"$available\" -ge " + Math.ceil(context.manifest.runtime.required_space / 1024) + " ] || exit 1\nprintf CYTV_SPACE_READY\n").then(function (result) {
                if (result !== 'CYTV_SPACE_READY') fail('Insufficient storage; private Python needs at least 320 MiB free');
                return { python: null, privateRuntimeRequired: true, requiredSpace: context.manifest.runtime.required_space, context: context };
            }, function () { fail('Private Python needs safe system tools and at least 320 MiB free in /var/lib'); });
        });
    });
}
function removeStage(bootstrap, stage) {
    if (!stage || !new RegExp('^' + BASE + '/\\.stage-[A-Za-z0-9]{6,32}$').test(stage)) return Promise.resolve();
    return shell(bootstrap, 'ancestors ' + quote(stage) + '\nrm -rf ' + quote(stage) + '\n').catch(function () { /* Preserve untrusted drift for diagnosis. */ });
}
function prepare(payloadRoot) {
    var context, stage;
    return inspectInternal(payloadRoot).then(function (state) {
        if (state.python) return run(state.python, ['-I', '-B', '-c', state.context.bootstrap.smoke], 'CYTV_RUNTIME_SMOKE').then(function () { return state.python; });
        context = state.context;
        // No product lease here: candidate Python takes the existing immutable-slot promotion lock.
        // The caller must acquire the shared product lease and re-inspect before product mutations.
        if (!fs.existsSync(BASE)) fs.mkdirSync(BASE, 493);
        ancestors(BASE);
        return shell(context.bootstrap, 'ancestors ' + quote(BASE) + '\nstage=$(mktemp -d ' + quote(BASE + '/.stage-XXXXXXXXXXXX') + ')\nprintf "%s" "$stage"\n').then(function (created) {
            if (!new RegExp('^' + BASE + '/\\.stage-[A-Za-z0-9]{6,32}$').test(created)) fail('Unsafe runtime staging result');
            stage = created;
            return hash(path.join(context.root, 'runtime.tar.gz'), context.manifest.files['runtime.tar.gz']);
        }).then(function () {
            return shell(context.bootstrap, 'ancestors ' + quote(stage) + '\nmkdir -m 755 ' + quote(stage + '/tree') + '\ntar -xzf ' + quote(path.join(context.root, 'runtime.tar.gz')) + ' -C ' + quote(stage + '/tree') + '\n');
        }).then(function () { return walk(stage + '/tree', context.manifest.runtime.files); }).then(function () {
            return run(stage + '/tree/bin/python3.13', ['-I', '-B', '-c', context.bootstrap.smoke], 'CYTV_RUNTIME_SMOKE');
        }).then(function () {
            return run(stage + '/tree/bin/python3.13', ['-I', '-B', '-c', context.bootstrap.promote, BASE, stage + '/tree', BASE + '/' + PIN]);
        }).then(function (result) {
            if (result !== 'CYTV_RUNTIME_PROMOTED' && result !== 'CYTV_RUNTIME_EXISTS') fail('Runtime promotion failed');
            return walk(BASE + '/' + PIN, context.manifest.runtime.files);
        }).then(function () {
            return run(BASE + '/' + PIN + '/bin/python3.13', ['-I', '-B', '-c', context.bootstrap.smoke], 'CYTV_RUNTIME_SMOKE');
        }).then(function () { return BASE + '/' + PIN + '/bin/python3.13'; });
    }).then(function (python) { return context ? removeStage(context.bootstrap, stage).then(function () { return python; }) : python; }, function (error) {
        return (context ? removeStage(context.bootstrap, stage) : Promise.resolve()).then(function () { throw error; });
    });
}
function inspect(payloadRoot) {
    return inspectInternal(payloadRoot).then(function (state) {
        return { python: state.python, privateRuntimeRequired: state.privateRuntimeRequired,
            requiredSpace: state.requiredSpace || 0 };
    });
}
module.exports = { inspect: inspect, prepare: prepare };
