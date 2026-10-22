const assert = require('node:assert/strict');
const fs = require('fs'), vm = require('vm');
function setup() {
 const calls=[], visibility=[], messages=[], timers=new Map(); let id=0;
 const document={hidden:false,addEventListener(){}};
 const window={setHelperResumeVisible:v=>visibility.push(v),helperResumeMessage:m=>messages.push(m)};
 function PalmServiceBridge(){this.cancel=()=>{};this.call=(uri,data)=>calls.push({uri,data:JSON.parse(data),reply:r=>this.onservicecallback(JSON.stringify(r))});}
 vm.runInNewContext(fs.readFileSync(__dirname+'/../launcher/helper-control.js','utf8'),{window,document,PalmServiceBridge,setTimeout:f=>{timers.set(++id,f);return id},clearTimeout:i=>timers.delete(i),setInterval(){}});
 return {calls,visibility,messages,window,timers};
}
let t=setup();
assert.equal(t.calls.length,1); assert.match(t.calls[0].uri,/\/registerServerStatus$/);
t.calls[0].reply({connected:false}); assert.equal(t.visibility.at(-1),true);
assert.equal(t.calls.length,1,'status must never resume automatically');
t.window.HelperControl.resume(); t.window.HelperControl.resume();
assert.equal(t.calls.length,2,'ignore duplicate presses');
assert.equal(t.calls[1].data.id,'com.local.nativehome');
assert.equal(t.calls[1].data.params.nativeHomeAuto,undefined,'explicit manual resume');
t.calls[1].reply({returnValue:false}); assert.equal(t.visibility.at(-1),true);
t.window.HelperControl.resume(); t.calls[2].reply({returnValue:true});
assert.equal(t.visibility.at(-1),true,'launch acceptance does not prove emergency state cleared');
t.calls[3].reply({connected:true}); assert.equal(t.visibility.at(-1),false);
t=setup(); t.calls[0].reply({returnValue:false}); assert.equal(t.calls.length,1);
assert.equal(t.visibility.at(-1),false,'unknown status must not imply stopped');
t.window.HelperControl.resume(); assert.equal(t.calls.length,1,'unknown status cannot enable recovery');
t=setup(); for(const f of [...t.timers.values()])f(); assert.equal(t.calls.length,1,'timeouts cannot trigger resume');
console.log('PASS: explicit resume only, duplicates suppressed, failure/timeout safe, status confirmed');
