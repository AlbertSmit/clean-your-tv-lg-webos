const assert=require('assert'),vm=require('vm'),fs=require('fs'),crypto=require('crypto'),path=require('path');
const keys=crypto.generateKeyPairSync('rsa',{modulusLength:2048});
function signed(home,release){const m={schema:1,home,release,helper:'0.6.13',url:`https://github.com/Razdva122/clean-your-tv-lg-webos/releases/download/${release}/com.gathin.tvhome_${home}_all.ipk`,sha256:'a'.repeat(64),notes:'Test'};const b=Buffer.from(JSON.stringify(m));return {payload:b.toString('base64'),signature:crypto.sign('RSA-SHA256',b,keys.privateKey).toString('base64')};}
const envelope=signed('1.2.1','v0.8.1');envelope.previous=signed('1.2.0','v0.8.0');
const profile={schema:1,inventory:{apps:[],inputs:[]},config:{columns:5,dockApps:[],hiddenApps:[]},settings:{}};
let methods={},disk={},calls=[],corrupt=false;
const store={read:n=>{if(corrupt&&n==='profile')throw Error('corrupt');return disk[n]||null;},write:(n,v)=>{disk[n]=JSON.parse(JSON.stringify(v));}};
function Service(){this.register=(n,fn)=>{methods[n]=fn;};this.call=(uri,p,cb)=>{calls.push({uri,p});setImmediate(()=>{
 if(uri.endsWith('/checkRoot'))cb({payload:{returnValue:true}});
 else if(uri.endsWith('/getAppInfo'))cb({payload:{returnValue:true,appInfo:{id:p.id,version:p.id==='com.gathin.tvhome'?'1.2.0':'0.6.13'}}});
 else if(uri.endsWith('/pauseForUpdate'))cb({payload:{returnValue:true,state:{enabled:false,updatePause:{id:p.id,wasEnabled:false,confirmed:true}}}});
 else if(uri.endsWith('/resumeAfterUpdate'))cb({payload:{returnValue:true,state:{enabled:false,completedUpdate:p.id}}});
 else if(uri.endsWith('/status'))cb({payload:{returnValue:true,state:{enabled:false}}});
 else if(uri.endsWith('/install')){cb({payload:{statusText:'Downloading…'}});cb({payload:{returnValue:true,finished:true}});}
 else throw Error(uri);
 });return {cancel:()=>{}};};}
const dir=path.resolve('updater-service');
const context={require:n=>n==='webos-service'?Service:n==='fs'?{readFileSync:()=>keys.publicKey.export({type:'spki',format:'pem'})}:n==='./storage'?()=>store:n==='./transport'?{get:async()=>JSON.stringify(envelope)}:require(path.join(dir,n)),__dirname:dir,Promise,setTimeout,clearTimeout};
vm.runInNewContext(fs.readFileSync(dir+'/service.js','utf8'),context);
function request(name,p={},id='com.gathin.tvhome'){return new Promise(resolve=>methods[name]({payload:p,ls2Message:{applicationID:()=>id},respond:resolve}));}
(async()=>{
 assert.equal((await request('check',{},'other.app')).returnValue,false);assert.equal(calls.length,0);
 const offered=await request('check');assert.equal(offered.result.canInstall,true);
 corrupt=true;assert.equal((await request('install',{version:'1.2.1',profile})).returnValue,false);assert(!calls.some(x=>x.uri.endsWith('/install')));
 corrupt=false;const installed=await request('install',{version:'1.2.1',profile});assert.equal(installed.result.status,'awaiting-launch');
 const args=calls.find(x=>x.uri.endsWith('/install')).p;assert.equal(args.id,'com.gathin.tvhome');assert.equal(args.ipkHash,'a'.repeat(64));assert.equal(args.subscribe,true);assert.deepEqual(disk.profile,profile);
 console.log('PASS service identity, signed offer, backup failure and streamed installer wiring');
})().catch(e=>{console.error(e);process.exit(1);});
