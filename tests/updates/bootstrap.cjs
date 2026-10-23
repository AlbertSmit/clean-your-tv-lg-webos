const assert=require('assert'),vm=require('vm'),fs=require('fs'),data=require('../../launcher/user-data');
const profile={schema:1,inventory:{apps:[{id:'app',title:'App',icon:'data:image/png;base64,YQ=='}],inputs:[]},config:{columns:5,dockApps:[],hiddenApps:[]},settings:{'tvhome.order':'old'}};
const map=new Map([[data.key,JSON.stringify(profile)],['tvhome.order','new']]);
const storage={getItem:k=>map.has(k)?map.get(k):null,setItem:(k,v)=>map.set(k,v)};
let scripts=[];const context={HomeData:data,localStorage:storage,window:null,CONFIG:{},TV_APPS:{apps:[],inputs:[]},document:{createElement:()=>({}),body:{appendChild:s=>scripts.push(s)},querySelector:()=>null},setTimeout,clearTimeout};context.window=context;
vm.runInNewContext(fs.readFileSync('launcher/profile-bootstrap.js','utf8'),context);
assert.equal(map.get('tvhome.order'),'new');assert.equal(context.TV_APPS.apps[0].id,'app');assert.equal(scripts.length,1);assert.equal(scripts[0].src,'app.js');
console.log('PASS profile startup preserves live tile ordering');
// A timeout is not the same thing as a successful response containing no backup.
let timeout;
const blank={...context,TV_APPS:{apps:[],inputs:[]},localStorage:{getItem:()=>null,setItem:()=>{}},setTimeout:fn=>{timeout=fn;return 1;},clearTimeout:()=>{},PalmServiceBridge:function(){this.call=()=>{};this.cancel=()=>{};}};blank.window=blank;
vm.runInNewContext(fs.readFileSync('launcher/profile-bootstrap.js','utf8'),blank);timeout();let error;blank.HomeProfile.capture(e=>{error=e;});assert(error,'capture must fail after restore timeout');
console.log('PASS failed restore cannot become an empty replacement profile');
const renewalCalls=[];
context.PalmServiceBridge=function(){this.cancel=()=>{};this.call=(uri)=>{renewalCalls.push(uri);this.onservicecallback(JSON.stringify({returnValue:true,state:{enabled:true,last:{status:'healthy'}}}));};};
let captured,captureError;context.HomeProfile.capture((e,p)=>{captureError=e;captured=p});assert(!captureError);assert(captured);assert.equal(captured.renewal.enabled,false);assert(renewalCalls.every(uri=>uri.endsWith('/status')));
console.log('PASS enabled renewal permits profile capture without changing its preference');
// Restoring an explicit preference to auto must reload even if both currently
// resolve to English, so the TV system locale can be queried on the new startup.
let pref='en',reloads=0,restoreScript;
const restoring={...context,TV_APPS:{apps:[],inputs:[]},CONFIG:{},
 localStorage:{getItem:()=>null,setItem:(k,v)=>{if(k==='tvhome.language')pref=v;}},
 HomeI18n:{ready:cb=>cb(),preference:()=>pref,refresh:()=> 'en'},location:{reload:()=>reloads++},
 document:{...context.document,body:{appendChild:s=>{restoreScript=s;}}},
 PalmServiceBridge:function(){this.cancel=()=>{};this.call=uri=>{if(uri.endsWith('/restore'))this.onservicecallback(JSON.stringify({returnValue:true,result:{...profile,settings:{'tvhome.language':'auto'}}}));};}};
restoring.window=restoring;
vm.runInNewContext(fs.readFileSync('launcher/profile-bootstrap.js','utf8'),restoring);
assert.equal(pref,'auto');assert.equal(reloads,1,'restore must reinitialize TV auto-detection');
console.log('PASS restored language preference reinitializes automatic TV locale');
