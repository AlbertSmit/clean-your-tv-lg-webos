const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const source=fs.readFileSync('launcher/i18n.js','utf8');
const metrics=fs.readFileSync('launcher/startup-metrics.js','utf8');
const cacheKey='tvhome.system-language.v1';
function load(options={}){
 const saved={'tvhome.language':options.preference||'auto',[cacheKey]:options.cache};
 let bridge,timer,reloads=0,ready=0,applies=0,writes=0,now=0,writeFailed=false,readbackFailed=false,readbackMismatch=false;
 const root={navigator:{language:'fr-FR'},performance:{now:()=>now},
  document:{documentElement:{},addEventListener(){},querySelectorAll(){applies++;return [];}},
  localStorage:{getItem(key){if(key===cacheKey&&(options.readFailed||readbackFailed))throw Error('read');return key===cacheKey&&readbackMismatch?'de':saved[key]||null;},
   setItem(key,value){writes++;if(writeFailed)throw Error('write');saved[key]=value;}},
  location:{reload(){reloads++;}},setTimeout(callback,delay){assert.equal(delay,1200);timer=callback;return 1;},clearTimeout(){}};
 if(!options.noBridge)root.PalmServiceBridge=function(){bridge=this;this.cancel=()=>{};this.call=(uri,raw)=>{
  assert.equal(uri,'luna://com.webos.settingsservice/getSystemSettings');assert.equal(JSON.parse(raw).key,'localeInfo');
  if(options.callFailed)throw Error('call');
 };};
 root.window=root;vm.runInNewContext(metrics,root);vm.runInNewContext(source,root);root.HomeI18n.ready(()=>ready++);
 return {root,saved,reply(value){now=50;bridge.onservicecallback(JSON.stringify({returnValue:true,settings:{localeInfo:{locales:{UI:value}}}}));},
  raw(value){now=50;bridge.onservicecallback(value);},timeout(){now=1200;timer();},
  failWrite(){writeFailed=true;},failReadback(){readbackFailed=true;},mismatchReadback(){readbackMismatch=true;},
  ready:()=>ready,reloads:()=>reloads,applies:()=>applies,writes:()=>writes};
}
for(const cache of [undefined,'de-DE','auto','xx','']){
 const h=load({cache});assert.equal(h.ready(),0,'invalid/missing cache retains language gate');
 h.reply('de-DE');assert.equal(h.ready(),1);assert.equal(h.root.HomeI18n.language(),'de');assert.equal(h.saved[cacheKey],'de');
 assert.equal(h.root.HomeStartup.snapshot().languageReady,50);
}
for(const ui of ['pt-PT','pt_BR','de-AT','ja-JP']){
 const expected=ui.indexOf('pt')===0?'pt-BR':ui==='de-AT'?'de':'en';
 const h=load();h.reply(ui);assert.equal(h.root.HomeI18n.language(),expected);assert.equal(h.saved[cacheKey],expected);
}
const warm=load({cache:'de'});assert.equal(warm.ready(),1);assert.equal(warm.root.HomeI18n.language(),'de');
assert.equal(warm.root.HomeStartup.snapshot().languageReady,0);assert.equal(warm.root.HomeStartup.snapshot().languageReply,undefined);
warm.reply('de-AT');assert.equal(warm.reloads(),0);assert.equal(warm.applies(),0);assert.equal(warm.writes(),0,'unchanged canonical cache avoids synchronous storage writes');
assert.equal(warm.root.HomeStartup.snapshot().languageReply,50);assert.equal(warm.root.HomeStartup.snapshot().languageReady,0);
for(const ui of ['ko-KR','ja-JP']){
 const h=load({cache:'de'});h.reply(ui);assert.equal(h.reloads(),1);assert.equal(h.saved[cacheKey],ui==='ko-KR'?'ko':'en');
 assert.equal(h.root.HomeI18n.language(),'de','warm UI remains coherent until new document');assert.equal(h.root.document.documentElement.lang,'de');assert.equal(h.applies(),0);
 h.reply('fr');h.timeout();assert.equal(h.reloads(),1,'duplicate callback and late timeout are ignored');
 assert.equal(h.saved[cacheKey],ui==='ko-KR'?'ko':'en');
}
for(const cache of [undefined,'de'])for(const raw of [
 '{',JSON.stringify({returnValue:false}),JSON.stringify({returnValue:true}),
 JSON.stringify({returnValue:true,settings:{localeInfo:{locales:null}}}),
 ...[null,{},[],12,'','  ','de DE'].map(UI=>JSON.stringify({returnValue:true,settings:{localeInfo:{locales:{UI}}}}))
]){
 const h=load({cache});h.raw(raw);assert.equal(h.ready(),1);assert.equal(h.root.HomeI18n.language(),cache||'fr');
 assert.equal(h.saved[cacheKey],cache);assert.equal(h.reloads(),0);
}
for(const options of [{noBridge:true},{callFailed:true}])for(const cache of [undefined,'de']){
 const h=load({...options,cache});assert.equal(h.ready(),1);assert.equal(h.root.HomeI18n.language(),cache||'fr');assert.equal(h.reloads(),0);
}
for(const cache of [undefined,'de']){
 const h=load({cache});h.timeout();assert.equal(h.ready(),1);assert.equal(h.root.HomeI18n.language(),cache||'fr');
 assert.equal(h.root.HomeStartup.snapshot().languageReply,undefined);h.reply('ko');assert.equal(h.reloads(),0);assert.equal(h.saved[cacheKey],cache);
 assert.equal(h.root.HomeI18n.language(),cache||'fr','late reply cannot change selected language');
}
const blockedRead=load({cache:'de',readFailed:true});assert.equal(blockedRead.ready(),0);blockedRead.reply('ko');assert.equal(blockedRead.root.HomeI18n.language(),'ko');
for(const failure of ['failWrite','failReadback','mismatchReadback']){
 const h=load({cache:'de'});h[failure]();h.reply('ko');assert.equal(h.reloads(),0);assert.equal(h.root.HomeI18n.language(),'de');assert.equal(h.applies(),0);
}
for(const cache of [undefined,'de']){
 const h=load({cache});assert.equal(h.root.HomeI18n.setLanguage('ru'),true);assert.equal(h.reloads(),1);
 h.reply('ko');assert.equal(h.reloads(),1);assert.equal(h.root.HomeI18n.language(),'ru');assert.equal(h.saved['tvhome.language'],'ru');assert.equal(h.saved[cacheKey],cache);
}
const explicit=load({cache:'de',preference:'ru'});assert.equal(explicit.ready(),1);assert.equal(explicit.root.HomeI18n.language(),'ru');
console.log('PASS bounded cold/warm system locale cache, canonicalization, storage failures and preference races');
