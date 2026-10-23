const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const elements={},events={},calls=[];let status='aborted';
for(const id of ['refresh','restore','open','status'])elements[id]={disabled:false,textContent:'',focus(){}};
const document={hidden:false,getElementById:id=>elements[id],addEventListener:(name,fn)=>events[name]=fn};
function Bridge(){this.cancel=()=>{};this.call=(uri)=>{calls.push(uri);if(uri.endsWith('/reconcile'))this.onservicecallback(JSON.stringify({returnValue:true,result:{status}}));};}
// Exercise the browser fallback without HomeI18n; localized startup has its own test.
vm.runInNewContext(fs.readFileSync('updater-app/app.js','utf8'),{window:{},document,PalmServiceBridge:Bridge,setTimeout:()=>1,clearTimeout:()=>{}});
assert.equal(elements.restore.disabled,true);
status='complete';assert.equal(typeof events.webOSRelaunch,'function');events.webOSRelaunch();
assert.equal(elements.restore.disabled,false);assert.equal(elements.status.textContent,'Update state: Complete (complete)');
elements.restore.onclick();assert.equal(elements.restore.textContent,'Confirm restore');
document.hidden=true;let count=calls.length;events.visibilitychange();assert.equal(calls.length,count);
document.hidden=false;events.visibilitychange();assert.equal(elements.restore.textContent,'Restore previous Home');
elements.restore.onclick();assert.equal(calls.some(u=>u.endsWith('/rollback')),false,'returning to recovery must reset confirmation');
elements.restore.onclick();assert.equal(calls.filter(u=>u.endsWith('/rollback')).length,1);
count=calls.length;events.webOSRelaunch();assert.equal(calls.length,count,'do not reconcile during rollback');
console.log('PASS recovery refresh on relaunch/visibility, confirmation reset and busy guard');
