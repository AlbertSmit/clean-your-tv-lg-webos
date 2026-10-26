/* Synthetic TV filesystem/process fixture; never touches a real runtime slot. */
'use strict';
var assert=require('assert'),fs=require('fs'),os=require('os'),path=require('path'),vm=require('vm'),crypto=require('crypto');
var runtimeSource=fs.readFileSync(path.join(__dirname,'../runtime.js'),'utf8');
var PIN='4a71641c8d5536175e404a961624e8656eba30e97b5026f6bd7dc31e4bbeaaea';
function remove(folder){if(!fs.existsSync(folder))return;fs.readdirSync(folder).forEach(function(entry){var full=path.join(folder,entry);if(fs.lstatSync(full).isDirectory())remove(full);else fs.unlinkSync(full);});fs.rmdirSync(folder);}
async function rejects(promise){var failed=false;try{await promise;}catch(error){failed=true;}assert(failed,'expected rejection');}
function digest(raw){return crypto.createHash('sha256').update(raw).digest('hex');}
function fixture(){
    var base=fs.mkdtempSync(path.join(fs.realpathSync(os.tmpdir()),'cytv-node-offline-')),root=path.join(base,'payload'),runtimeBase=path.join(base,'private');fs.mkdirSync(root);
    var calls=[],system=false,space=true,platform='linux',arch='arm',machine='armv7l',badOwner=null;
    var files={},runtimeFiles={};
    var binding={schema:1,archive_sha256:PIN,files:{'bin/python3.13':digest('candidate')}};
    runtimeFiles['bin/python3.13']={sha256:digest('candidate'),size:9,mode:493};
    var bindraw=JSON.stringify(binding);runtimeFiles['.cytv-runtime.json']={sha256:digest(bindraw),size:Buffer.byteLength(bindraw),mode:420};
    function write(name,raw){fs.writeFileSync(path.join(root,name),raw);files[name]={sha256:digest(raw),size:Buffer.byteLength(raw)};}
    write('runtime.tar.gz','verified normalized archive');write('runtime-binding.json',bindraw);
    write('runtime-provenance.json',JSON.stringify({sha256:PIN,normalized_sha256:files['runtime.tar.gz'].sha256}));
    write('runtime-bootstrap.json',JSON.stringify({shell:'FIXED SHELL\n',smoke:'SMOKE',inspect_probe:'INSPECT',system_probe:'SYSTEM',promote:'PROMOTE'}));
    var manifest={schema:1,files:files,runtime:{archive_sha256:PIN,files:runtimeFiles,max_unpacked:160*1024*1024,max_files:12000,required_space:320*1024*1024}};
    function save(){fs.writeFileSync(path.join(root,'manifest.json'),JSON.stringify(manifest));}save();
    var fakefs=Object.create(fs);
    fakefs.lstatSync=function(name){var st=(name==='/var'||name==='/var/lib'||name==='/bin'||name==='/usr'||name==='/usr/bin')?fs.lstatSync(base):(name==='/bin/sh'||name==='/usr/bin/python3')?fs.lstatSync(path.join(root,'runtime.tar.gz')):fs.lstatSync(name);st.uid=name===badOwner?1000:0;st.mode&=~18;return st;};
    fakefs.fstatSync=function(fd){var st=fs.fstatSync(fd);st.uid=0;st.mode&=~18;return st;};
    fakefs.realpathSync=function(name){return (name==='/bin/sh'||name==='/usr/bin/python3')?name:fs.realpathSync(name);};
    var elf=Buffer.alloc(40);elf.write('7f454c46',0,'hex');elf[4]=1;elf[5]=1;elf.writeUInt16LE(40,18);elf[39]=5;
    fakefs.openSync=function(name,flags){return name==='/bin/sh'?999:fs.openSync(name,flags);};
    fakefs.readSync=function(fd,buffer){if(fd===999){elf.copy(buffer);return 40;}return fs.readSync.apply(fs,arguments);};
    fakefs.closeSync=function(fd){if(fd!==999)fs.closeSync(fd);};
    function exec(executable,args,options,callback){
        calls.push({executable:executable,args:args});
        if(executable==='/usr/bin/python3') return callback(system?null:new Error('missing'),system?(args.indexOf('SMOKE')>=0?'CYTV_RUNTIME_SMOKE':'CYTV_SYSTEM_PYTHON'):'');
        if(executable==='/bin/sh'){
            var script=args[1];
            if(script.indexOf('uname -m')>=0){var kernels=script.match(/case \"\$\(uname -m\)\" in ([a-z0-9|]+)\)/);var accepted=kernels&&kernels[1].split('|').indexOf(machine)>=0;return callback(accepted?null:new Error('unsupported machine'),accepted?'CYTV_MACHINE_READY':'');}
            if(script.indexOf('df -Pk')>=0)return callback(space?null:new Error('space'),space?'CYTV_SPACE_READY':'');
            if(script.indexOf('mktemp -d')>=0){var stage=path.join(runtimeBase,'.stage-123456789abc');fs.mkdirSync(stage);return callback(null,stage);}
            if(script.indexOf('tar -xzf')>=0){var tree=path.join(runtimeBase,'.stage-123456789abc/tree');fs.mkdirSync(tree);fs.mkdirSync(path.join(tree,'bin'));fs.writeFileSync(path.join(tree,'bin/python3.13'),'candidate');fs.chmodSync(path.join(tree,'bin/python3.13'),493);fs.writeFileSync(path.join(tree,'.cytv-runtime.json'),bindraw);return callback(null,'');}
            if(script.indexOf('rm -rf')>=0){var stage2=path.join(runtimeBase,'.stage-123456789abc');if(fs.existsSync(stage2))remove(stage2);return callback(null,'');}
        }
        if(args.indexOf('PROMOTE')>=0){fs.renameSync(args[args.length-2],args[args.length-1]);return callback(null,'CYTV_RUNTIME_PROMOTED');}
        if(args.indexOf('SMOKE')>=0)return callback(null,'CYTV_RUNTIME_SMOKE');
        if(args.indexOf('INSPECT')>=0)return callback(null,'CYTV_SYSTEM_PYTHON');
        callback(new Error('Unexpected operation'));
    }
    var sandbox={require:function(name){if(name==='fs')return fakefs;if(name==='child_process')return {execFile:exec};return require(name);},process:{geteuid:function(){return 0;},platform:platform,arch:arch},Promise:Promise,Buffer:Buffer,module:{exports:{}}};
    vm.runInNewContext(runtimeSource.replace("'/var/lib/clean-your-tv-python'",JSON.stringify(runtimeBase)),sandbox);
    return {root:root,manifest:manifest,save:save,calls:calls,api:sandbox.module.exports,base:base,runtimeBase:runtimeBase,setMachine:function(value){machine=value;},setSystem:function(){system=true;},setSpace:function(){space=false;},setArch:function(){sandbox.process.arch='x64';},badOwner:function(name){badOwner=name;},clean:function(){remove(base);}};
}
async function rejection(change){var f=fixture();try{change(f);await rejects(f.api.prepare(f.root));assert.strictEqual(f.calls.filter(function(c){return c.args.join(' ').indexOf('mktemp -d')>=0;}).length,0);assert(f.calls.every(function(c){return c.executable==='/usr/bin/python3'||c.executable==='/bin/sh';}),'preflight failure must not execute a candidate');}finally{f.clean();}}
(async function(){
    for(var mutate of [function(f){fs.unlinkSync(path.join(f.root,'runtime.tar.gz'));},function(f){fs.writeFileSync(path.join(f.root,'extra'),'x');},function(f){fs.appendFileSync(path.join(f.root,'runtime.tar.gz'),'x');},function(f){fs.writeFileSync(path.join(f.root,'runtime.tar.gz'),'x'.repeat(27));},function(f){fs.unlinkSync(path.join(f.root,'runtime.tar.gz'));fs.symlinkSync('runtime-binding.json',path.join(f.root,'runtime.tar.gz'));},function(f){f.manifest.files['../escape']={sha256:'0'.repeat(64),size:1};f.save();},function(f){f.manifest.runtime.archive_sha256='0'.repeat(64);f.save();},function(f){f.setArch();},function(f){f.setSpace();},function(f){f.badOwner(path.join(f.root,'runtime.tar.gz'));}])await rejection(mutate);
    await rejection(function(f){f.setMachine('armv6l');});
    await rejection(function(f){f.setSystem();f.setArch();});
    await rejection(function(f){f.setSystem();f.setMachine('armv6l');});
    for(var machine of ['armv7l','armv8l','aarch64']){var supported=fixture();try{supported.setMachine(machine);assert.strictEqual((await supported.api.inspect(supported.root)).privateRuntimeRequired,true);assert(!fs.existsSync(supported.runtimeBase));}finally{supported.clean();}}
    var native64=fixture();try{native64.setMachine('aarch64');native64.setSystem();assert.strictEqual((await native64.api.inspect(native64.root)).python,'/usr/bin/python3');assert(!fs.existsSync(native64.runtimeBase));}finally{native64.clean();}
    var f=fixture();try{var state=await f.api.inspect(f.root);assert.strictEqual(state.privateRuntimeRequired,true);assert(!fs.existsSync(f.runtimeBase));assert(f.calls.every(function(c){return c.args.indexOf('SMOKE')<0 && c.args.join(' ').indexOf('mktemp -d')<0;}));var selected=await f.api.prepare(f.root);assert.strictEqual(selected,path.join(f.runtimeBase,PIN,'bin/python3.13'));assert(!fs.existsSync(path.join(f.runtimeBase,'.stage-123456789abc')));var count=f.calls.length;assert.strictEqual((await f.api.inspect(f.root)).python,selected);assert(f.calls.slice(count).every(function(c){return c.args.indexOf('SMOKE')<0;}));}finally{f.clean();}
    f=fixture();try{f.setSystem();assert.strictEqual(await f.api.prepare(f.root),'/usr/bin/python3');assert(!fs.existsSync(f.runtimeBase));}finally{f.clean();}
    f=fixture();try{f.setSystem();f.setArch();assert.strictEqual((await f.api.inspect(f.root,true)).python,'/usr/bin/python3');assert(!fs.existsSync(f.runtimeBase));assert(f.calls.every(function(c){return c.executable==='/usr/bin/python3';}));}finally{f.clean();}
    console.log('Offline runtime: corruption, ownership, ABI, space, read-only inspect, system skip, staging/promotion/readback passed');
})().catch(function(error){console.error(error);process.exitCode=1;});
