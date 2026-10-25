'use strict';
const assert=require('assert'),vm=require('vm'),fs=require('fs'),crypto=require('crypto'),path=require('path');
const state='/var/lib/clean-your-tv-root',pin='4a71641c8d5536175e404a961624e8656eba30e97b5026f6bd7dc31e4bbeaaea';
const executable='/var/lib/clean-your-tv-python/'+pin+'/bin/python3.13',slot=path.dirname(path.dirname(executable));
const digest=raw=>crypto.createHash('sha256').update(raw).digest('hex');
let files={};
const fakeFs={lstatSync(name){
 if((name===state+'/python-launcher'||name===state+'/python-runtime.json')&&!files[name]){let e=Error();e.code='ENOENT';throw e;}
 const file=Object.prototype.hasOwnProperty.call(files,name);
 return {uid:0,mode:file?0o100700:0o40755,nlink:1,size:file?Buffer.byteLength(files[name]):0,isSymbolicLink:()=>false,isFile:()=>file,isDirectory:()=>!file};
},readFileSync(name,encoding){return encoding?files[name]:Buffer.from(files[name]);}};
const source=fs.readFileSync(__dirname+'/service.js','utf8');
const select=vm.runInNewContext(source+';pythonCommand', {require(name){
 if(name==='webos-service')return function(){this.register=function(){};};
 if(name==='./handlers')return ()=>({});
 if(name==='child_process')return {execFile(){throw Error('unexpected spawn');}};
 if(name==='fs')return fakeFs;
 return require(name);
},__dirname,process});
assert.equal(select(),'/usr/bin/python3');
files[executable]='verified-python';
files[slot+'/.cytv-runtime.json']=JSON.stringify({schema:1,archive_sha256:pin,files:{'bin/python3.13':digest(files[executable])}});
files[state+'/python-runtime.json']=JSON.stringify({schema:1,executable,archive_sha256:pin,inventory_sha256:digest(files[slot+'/.cytv-runtime.json'])});
files[state+'/python-launcher']='#!/bin/sh\nunset PYTHONHOME PYTHONPATH\nexport PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1\nexec '+executable+' "$@"\n';
assert.equal(select(),state+'/python-launcher');
files[state+'/python-launcher']='#!/bin/sh\nexec /tmp/evil "$@"\n';
assert.throws(select,/invalid-python-launcher/);
delete files[state+'/python-launcher'];
assert.throws(select);
console.log('Root service Python binding selection passed');
