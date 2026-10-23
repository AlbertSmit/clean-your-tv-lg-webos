'use strict';
var fs=require('fs'),Service=require('webos-service'),claim=require('./boot-state').claim;
var service=new Service('com.local.nativehome.service');
var statePath=__dirname+'/state/startup-state.json',name='com.local.nativehome.boot';
function read(){try{return JSON.parse(fs.readFileSync(statePath,'utf8'));}catch(e){return {enabled:false};}}
function save(state){fs.writeFileSync(statePath+'.tmp',JSON.stringify(state));fs.renameSync(statePath+'.tmp',statePath);}
function boot(){return require('./boot-state').identity(fs.readFileSync('/proc/sys/kernel/random/boot_id','utf8').trim(),fs.readFileSync('/proc/stat','utf8'));}
function call(uri,args,cb){service.call(uri,args,function(m){cb(m.payload);});}
function complete(message,result){
 fs.writeFileSync('/tmp/nativehome-boot-callback.json',JSON.stringify({time:Date.now(),result:result,activity:message.payload.$activity}));
 if(message.payload.$activity&&message.activity)service.activityManager.complete(message.activity,{restart:true},function(a){fs.writeFileSync('/tmp/nativehome-boot-complete.json',JSON.stringify({time:Date.now(),activity:a}));message.respond({returnValue:true,result:result});});
 else message.respond({returnValue:true,result:result});
}
service.register('status',function(m){try{m.respond({returnValue:true,state:read(),boot:boot(),blocked:blocked(),callback:readDebug('/tmp/nativehome-boot-callback.json'),complete:readDebug('/tmp/nativehome-boot-complete.json')});}catch(e){m.respond({returnValue:false,errorText:String(e)});}});
service.register('disable',function(m){try{save({enabled:false});call('luna://com.palm.activitymanager/cancel',{activityName:name},function(r){m.respond({returnValue:true,cancel:r});});}catch(e){m.respond({returnValue:false,errorText:String(e)});}});
service.register('enable',function(m){try{save({enabled:true,boot:boot(),schema:3});m.respond({returnValue:true});}catch(e){m.respond({returnValue:false,errorText:String(e)});}});
service.register('tick',function(m){try{
 if(blocked()){complete(m,{blocked:true});return;}
 var next=claim(read(),boot(),blocked());if(!next){complete(m,{skipped:true});return;}
 // Persist before launching: a crash or watchdog exit must never create a restart loop.
 next.schema=3;next.claimedAt=Date.now();save(next);
 call('luna://com.webos.applicationManager/launch',{id:'com.local.nativehome',params:{nativeHomeAuto:true}},function(r){next.launch=r;save(next);complete(m,r);});
}catch(e){complete(m,{returnValue:false,errorText:String(e)});}});

function readDebug(p){try{return JSON.parse(fs.readFileSync(p,'utf8'));}catch(e){return null;}}

function blocked(){try{fs.statSync('/media/developer/apps/usr/palm/applications/com.local.nativehome/state/blocked');return true;}catch(e){return e.code!=='ENOENT';}}

var inventoryPending=null;
service.register('listApps',function(message){
 if(!inventoryPending)inventoryPending=require('./app-inventory')();
 var request=inventoryPending;
 request.then(function(apps){if(inventoryPending===request)inventoryPending=null;message.respond({returnValue:true,apps:apps});},function(){if(inventoryPending===request)inventoryPending=null;message.respond({returnValue:false,errorText:'App inventory unavailable'});});
});
