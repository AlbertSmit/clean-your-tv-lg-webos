const assert=require('assert'),fs=require('fs'),vm=require('vm');
assert(fs.existsSync(__dirname+'/root-updates.js'),'Root update dialog is missing');
const tick=()=>new Promise(r=>setImmediate(r));
function harness({recovery=false,unavailable=false,delayed=false}={}){
 const elements=[],listeners=[],calls=[],timers=[],pending=[];let focus='previous',tx=null,captures=0,offer={installed:{version:'0.0.1'},candidate:{version:'0.0.2',notes:'Release notes'},canInstall:true};
 class E{constructor(tag){this.tag=tag;this.children=[];this.hidden=false;elements.push(this);}appendChild(e){this.children.push(e);}setAttribute(){}focus(){focus=this;}removeChild(e){this.children.splice(this.children.indexOf(e),1);}}
 const document={body:new E('body'),activeElement:{focus(){focus='previous';}},createElement:t=>new E(t),addEventListener:(name,f)=>listeners.push(f)};
 let confirmation;const window={HomeI18n:{t:s=>s,confirm:(options,accept)=>{confirmation={options,accept};}},ROOT_VERSION:'0.0.1',RenewalPanel:{open(){calls.push(['settings']);}}};if(!recovery)window.RootProfile={capture:async()=>{captures++;return {snapshot:true};}};
 const context={window,document,Promise,setTimeout:f=>{timers.push(f);return timers.length;},clearTimeout(){},PalmServiceBridge:class{cancel(){}call(uri,raw){const method=uri.split('/').pop(),p=JSON.parse(raw);assert(uri.startsWith('luna://com.cleanyourtv.root.updater.service/'));calls.push([method,p]);let result;
 if(method==='check')result=offer;if(method==='status')result=tx;if(method==='install')result=tx={id:'install-tx',phase:'preparing'};if(method==='confirm')result=tx={id:'new-tx',phase:'complete',oldRoute:{active:true}};if(method==='reconcile')result=tx;if(method==='rollback')result=tx={id:'old',phase:'rolling-back'};
 const reply=()=>this.onservicecallback(JSON.stringify(unavailable?{returnValue:false,errorText:'Service does not exist'}:{returnValue:true,result}));if(delayed&&method==='status')pending.push(reply);else reply();}}};
 vm.runInNewContext(fs.readFileSync(__dirname+'/root-updates.js','utf8'),context);
 const api=window.RootUpdates;const buttons=()=>elements.filter(e=>e.tag==='button'&&!e.hidden);const button=label=>buttons().find(b=>b.textContent===label);
 return {get confirmation(){return confirmation;},api,calls,timers,elements,buttons,button,resolve:()=>pending.splice(0).forEach(f=>f()),get focus(){return focus;},get captures(){return captures;},setTx:t=>tx=t,key(code){listeners.forEach(f=>f({keyCode:code,preventDefault(){},stopImmediatePropagation(){}}));}};
}
(async()=>{
 let h=harness();h.api.open();await tick();assert.strictEqual(h.calls.filter(c=>c[0]==='check').length,1);assert(!h.button('Try again'));assert(h.button('Update'));assert(h.button('Update').disabled===false);assert.strictEqual(h.captures,0);
 h.button('Update').onclick();await tick();assert.equal(h.confirmation.options.action,'Install update');assert.strictEqual(h.captures,0);h.confirmation.accept();await tick();assert.strictEqual(h.captures,1);assert.strictEqual(h.calls.filter(c=>c[0]==='install').length,1);
 h.confirmation.accept();await tick();assert.strictEqual(h.calls.filter(c=>c[0]==='install').length,1);
 h.key(461);assert.strictEqual(h.focus,'previous');
 h=harness();h.api.confirmLaunch({transaction:'new-tx',version:'0.0.2'});await tick();h.button('Confirm working update').onclick();await tick();assert(h.calls.some(c=>c[0]==='confirm'&&c[1].transaction==='new-tx'&&c[1].version==='0.0.2'));assert(h.calls.some(c=>c[0]==='status'));assert(h.elements.some(e=>String(e.textContent).includes('Update complete')));assert(h.button('Root mode settings'));
 h=harness({recovery:true});h.setTx({id:'old',phase:'recovery-required',installEvidence:{terminal:null}});h.api.open({recovery:true});await tick();assert(!h.button('Update'));assert(h.button('Recover status'));assert(!h.button('Roll back'));h.key(40);assert(!h.focus.disabled);h.key(461);assert.strictEqual(h.focus,'previous');assert.strictEqual(h.captures,0);
 h=harness({recovery:true});h.setTx({id:'old',phase:'recovery-required',installEvidence:{terminal:{success:false}}});h.api.open({recovery:true});await tick();assert(h.button('Roll back'));h.button('Roll back').onclick();await tick();assert(!h.calls.some(c=>c[0]==='rollback'));assert.equal(h.confirmation.options.action,'Restore previous Home');h.confirmation.accept();await tick();assert(h.calls.some(c=>c[0]==='rollback'));assert.strictEqual(h.captures,0);
 h=harness();h.setTx({id:'old',phase:'recovery-required',installEvidence:{terminal:{success:false}}});h.api.open();await tick();assert(h.button('Roll back'));
 h=harness({unavailable:true});h.api.open();await tick();assert(h.elements.some(e=>String(e.textContent).includes('one-time computer setup')));
 h=harness({delayed:true});h.api.open();h.key(461);assert.strictEqual(h.focus,'previous');h.resolve();await tick();assert.strictEqual(h.focus,'previous');
 console.log('PASS Root updates explicit install, duplicate prevention, transaction health, status polling, recovery, remote focus and Back');
})().catch(e=>{console.error(e);process.exit(1);});
