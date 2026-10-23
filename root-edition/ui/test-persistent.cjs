const assert=require('assert'),vm=require('vm'),fs=require('fs');
let phase='disabled',calls=[],buttons=[],message;
const tx='12345678-1234-1234-1234-123456789abc';
class E{constructor(tag){this.tag=tag;this.hidden=false;if(tag==='button')buttons.push(this);}appendChild(){}setAttribute(name){if(name==='aria-live')message=this;}focus(){}}
const doc={body:new E('body'),activeElement:new E('a'),createElement:t=>new E(t),addEventListener(){}};
const ctx={window:{},document:doc,Promise,setTimeout,clearTimeout,createRootExit:()=>async()=>{},PalmServiceBridge:class{
 cancel(){}call(uri,raw){const method=uri.split('/').pop(),payload=JSON.parse(raw);calls.push([method,payload]);
 if(method==='enable')phase='trial';if(method==='confirm'){assert.strictEqual(payload.transaction,tx);phase='active';}
 const value=method==='status'?{intent:{phase},journal:{transaction:tx}}:{};
 this.onservicecallback(JSON.stringify({returnValue:true,result:{returnValue:true,result:value}}));
 }}};
vm.runInNewContext(fs.readFileSync(__dirname+'/root-settings.js','utf8'),ctx);
const tick=()=>new Promise(r=>setImmediate(r));
(async()=>{
 ctx.window.RenewalPanel.open();await tick();
 assert.strictEqual(buttons[0].textContent,'Try Home control');
 buttons[0].onclick();await tick();
 assert.strictEqual(buttons[0].textContent,'Keep using Home');
 assert(message.textContent.includes('within one minute'));
 buttons[0].onclick();await tick();
 assert.strictEqual(buttons[0].textContent,'Home control is on');assert(buttons[0].disabled);
 buttons[0].onclick();await tick();
 assert.strictEqual(calls.filter(x=>x[0]==='confirm').length,1);
 console.log('PASS Root trial, transaction-bound confirmation and active status UI');
})().catch(e=>{console.error(e);process.exit(1);});
