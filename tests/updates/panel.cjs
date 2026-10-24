const vm=require('vm'),fs=require('fs'),assert=require('assert');
const ids={},listeners=[];let focus=null,reply,calls=0;
function element(){const e={disabled:false,hidden:false,textContent:'',classList:{hidden:true,contains(){return this.hidden;},add(){this.hidden=true;},remove(){this.hidden=false;}},setAttribute(){},addEventListener(){},focus(){focus=this;},click(){if(!this.disabled&&this.onclick)this.onclick();}};
Object.defineProperty(e,'innerHTML',{set(html){this.buttons=[];for(const match of html.matchAll(/<(button|p) id="([^"]+)"([^>]*)>/g)){const child=element();child.disabled=match[3].includes('disabled');child.hidden=match[3].includes('hidden');ids[match[2]]=child;if(match[1]==='button')this.buttons.push(child);}}});e.querySelectorAll=()=>e.buttons;return e;}
const ctx={document:{createElement:element,body:{appendChild(){}},getElementById:id=>ids[id],addEventListener:(name,fn)=>listeners.push(fn)},setTimeout:()=>1,clearTimeout(){},PalmServiceBridge:function(){this.call=()=>{calls++;reply=this.onservicecallback;};this.cancel=()=>{};},window:{}};
vm.runInNewContext(fs.readFileSync('launcher/update-panel.js','utf8'),ctx);ctx.window.HomeUpdates.open();assert.equal(calls,1,'opening updates must check automatically');
reply(JSON.stringify({returnValue:true,result:{home:'1.2.0',candidate:{home:'1.2.0',notes:'Tooling update'},root:false,state:'current',canInstall:false}}));assert(ids.updateInstall.disabled);assert(ids.updateStatus.textContent.includes('up to date'));
let prevented=0;listeners[0]({keyCode:39,preventDefault(){prevented++;},stopImmediatePropagation(){}});assert.equal(focus,ids.updateBack);assert.equal(prevented,1);
listeners[0]({keyCode:37,preventDefault(){},stopImmediatePropagation(){}});assert.equal(focus,ids.updateRecovery,'left must skip hidden retry and disabled install');
listeners[0]({keyCode:461,preventDefault(){},stopImmediatePropagation(){}});listeners[0]({keyCode:39,preventDefault(){throw Error('closed panel ate key');},stopImmediatePropagation(){}});
let returned=false;ctx.window.HomeUpdates.open({onClose(){returned=true;}});ids.updateBack.click();assert.equal(calls,2,'reopening checks again');assert(returned,'Back returns to the settings panel that opened updates');
console.log('PASS update panel no-root/current state and remote navigation');

let confirmation,captures=0;ctx.HomeI18n=ctx.window.HomeI18n={t:s=>s,confirm:(options,accept)=>{confirmation={options,accept};}};
ctx.window.HomeProfile={capture:callback=>{captures++;callback(null,{saved:true});}};
ctx.window.HomeUpdates.open();reply(JSON.stringify({returnValue:true,result:{home:'1.2.0',candidate:{home:'1.3.0',notes:'Update'},state:'available',canInstall:true}}));
ids.updateInstall.click();assert.equal(confirmation.options.action,'Install update');assert.equal(captures,0,'opening confirmation must not capture or install');
assert.notEqual(ids.updateInstall.textContent,'Confirm update');
confirmation.accept();assert.equal(captures,1);confirmation.accept();assert.equal(captures,1,'duplicate acceptance cannot install twice');
console.log('PASS Home update requires separate confirmation and prevents duplicate install');
