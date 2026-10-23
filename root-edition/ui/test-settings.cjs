const assert=require('assert'),vm=require('vm'),fs=require('fs');
const elements=[],listeners={},calls=[];let selected,exitCount=0,resolveExit;
class Element {
 constructor(tag){this.tag=tag;this.children=[];this.hidden=false;this.disabled=false;elements.push(this);}
 appendChild(e){this.children.push(e);}
 setAttribute(){}
 focus(){selected=this;}
}
const document={body:new Element('body'),activeElement:{focus(){selected='previous';}},createElement:t=>new Element(t),addEventListener:(n,f)=>{listeners[n]=f;}};
let updateOptions;
const context={window:{RootUpdates:{open:o=>{updateOptions=o;}}},document,Promise,setTimeout,clearTimeout,createRootExit:()=>()=>{exitCount++;return new Promise(r=>{resolveExit=r;});},PalmServiceBridge:class{call(uri,p){calls.push(uri);this.onservicecallback('{"returnValue":true}');}cancel(){}}};
vm.runInNewContext(fs.readFileSync(__dirname+'/root-settings.js','utf8'),context);
const panel=context.window.RenewalPanel;
function key(code){let prevented=false,stopped=false;listeners.keydown({keyCode:code,preventDefault(){prevented=true;},stopImmediatePropagation(){stopped=true;}});return {prevented,stopped};}
(async()=>{
 panel.open();assert(panel.isOpen());assert.strictEqual(calls.length,1);
 const buttons=elements.filter(e=>e.tag==='button');assert.strictEqual(selected,buttons[1]);
 key(40);key(40);assert.strictEqual(selected,buttons[3]);key(13);assert.strictEqual(exitCount,0);
 key(461);assert(!panel.isOpen());assert.strictEqual(selected,'previous');
 panel.open();key(40);key(40);key(13);key(13);assert.strictEqual(exitCount,1);
 key(13);assert.strictEqual(exitCount,1);key(461);assert(panel.isOpen());
 resolveExit();await new Promise(r=>setImmediate(r));assert(!panel.isOpen());assert.strictEqual(selected,'previous');
 assert.deepStrictEqual(key(40),{prevented:false,stopped:false});
 panel.open();buttons[3].onclick();assert.strictEqual(buttons[3].textContent,'Confirm return');
 buttons[1].onclick();assert(!panel.isOpen());updateOptions.onClose();
 await new Promise(r=>setImmediate(r));
 assert.strictEqual(buttons[3].textContent,'Return to LG Home','Leaving for updates must cancel the previous exit confirmation');
 buttons[3].onclick();assert.strictEqual(exitCount,1,'Return must ask for confirmation again');key(461);
 console.log('PASS Root settings remote focus, confirmation, Back, duplicate and busy handling');
})().catch(e=>{console.error(e);process.exit(1);});
