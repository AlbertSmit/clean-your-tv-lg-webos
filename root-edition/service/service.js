'use strict';
var Service = require('webos-service');
var execFile = require('child_process').execFile;
var service = new Service('com.cleanyourtv.root.preview.service');
function pythonCommand(){
 var fs=require('fs'),path=require('path'),crypto=require('crypto'),state='/var/lib/clean-your-tv-root',launcher=state+'/python-launcher',receipt=state+'/python-runtime.json';
 function present(name){try{fs.lstatSync(name);return true;}catch(e){if(e.code==='ENOENT')return false;throw e;}}
 function owned(name,file){
  var item=fs.lstatSync(name);
  if(item.uid!==0||(item.mode&18)||item.isSymbolicLink()||(file?(!item.isFile()||item.nlink!==1):!item.isDirectory()))throw Error('unsafe-python-binding');
  for(var parent=path.dirname(name);;parent=path.dirname(parent)){
   item=fs.lstatSync(parent);if(!item.isDirectory()||item.isSymbolicLink()||item.uid!==0||(item.mode&18))throw Error('unsafe-python-binding');
   if(parent===path.dirname(parent))break;
  }
  return fs.lstatSync(name);
 }
 if(!present(launcher)&&!present(receipt))return '/usr/bin/python3';
 var pin='4a71641c8d5536175e404a961624e8656eba30e97b5026f6bd7dc31e4bbeaaea',executable='/var/lib/clean-your-tv-python/'+pin+'/bin/python3.13';
 if((owned(launcher,true).mode&511)!==448||owned(receipt,true).size>65536)throw Error('unsafe-python-binding');
 var binding=JSON.parse(fs.readFileSync(receipt,'utf8'));
 if(Object.keys(binding).sort().join(',')!=='archive_sha256,executable,inventory_sha256,schema'||binding.schema!==1||binding.executable!==executable||binding.archive_sha256!==pin||!/^[a-f0-9]{64}$/.test(binding.inventory_sha256))throw Error('invalid-python-binding');
 if(fs.readFileSync(launcher,'utf8')!=='#!/bin/sh\nunset PYTHONHOME PYTHONPATH\nexport PYTHONDONTWRITEBYTECODE=1 PYTHONNOUSERSITE=1\nexec '+executable+' "$@"\n')throw Error('invalid-python-launcher');
 var inventoryPath=path.dirname(path.dirname(executable))+'/.cytv-runtime.json';
 if(owned(inventoryPath,true).size>4*1024*1024||owned(executable,true).size>256*1024*1024)throw Error('oversized-python-runtime');
 var raw=fs.readFileSync(inventoryPath),inventory=JSON.parse(raw);
 if(crypto.createHash('sha256').update(raw).digest('hex')!==binding.inventory_sha256||inventory.schema!==1||inventory.archive_sha256!==pin||!inventory.files||crypto.createHash('sha256').update(fs.readFileSync(executable)).digest('hex')!==inventory.files['bin/python3.13'])throw Error('changed-python-runtime');
 return launcher;
}

var runtime = '/var/lib/clean-your-tv-root/runtime/cli.py';
var handlers = require('./handlers')(function (command, transaction) {
  return new Promise(function (resolve, reject) {
    if (process.getuid() !== 0) return reject(new Error('Root recovery service required'));
    if (['boot', 'status', 'restore', 'enable', 'confirm'].indexOf(command) === -1) return reject(new Error('Unknown operation'));
    var executable = command === 'boot' ? '/bin/sh' : pythonCommand();
    var args = command === 'boot' ? [__dirname + '/boot-recover.sh'] : [runtime, command];
    if (command === 'confirm') args.push(transaction);
    execFile(executable, args, {timeout:command === 'restore' ? 600000 : command === 'boot' ? 120000 : 30000,maxBuffer:65536}, function (error, stdout) {
      if (error) return reject(new Error('Recovery operation failed; inspect runtime status'));
      try { resolve(JSON.parse(stdout)); } catch (_) { reject(new Error('Invalid runtime response')); }
    });
  });
});
Object.keys(handlers).forEach(function (method) {
  service.register(method, function (message) {
    handlers[method](message.payload).then(function (result) { result.root = process.getuid() === 0; message.respond(result); });
  });
});
// Activity registration belongs to the root installer, not the web service.

var inventoryPending=null;
service.register('listApps',function(message){
 if(!inventoryPending)inventoryPending=require('./app-inventory')();
 var request=inventoryPending;
 request.then(function(apps){if(inventoryPending===request)inventoryPending=null;message.respond({returnValue:true,apps:apps});},function(){if(inventoryPending===request)inventoryPending=null;message.respond({returnValue:false,errorText:'App inventory unavailable'});});
});
