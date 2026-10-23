const vm=require('vm'),fs=require('fs'),assert=require('assert');
const ids={},listeners=[];let focus=null,reply;
function element(){const e={disabled:false,textContent:'',classList:{hidden:true,contains(){return this.hidden;},add(){this.hidden=true;},remove(){this.hidden=false;}},setAttribute(){},addEventListener(){},focus(){focus=this;},click(){if(!this.disabled&&this.onclick)this.onclick();}};
Object.defineProperty(e,'innerHTML',{set(html){this.buttons=[];for(const match of html.matchAll(/<(button|p) id="([^"]+)"([^>]*)>/g)){const child=element();child.disabled=match[3].includes('disabled');ids[match[2]]=child;if(match[1]==='button')this.buttons.push(child);}}});e.querySelectorAll=()=>e.buttons;return e;}
const ctx={document:{createElement:element,body:{appendChild(){}},getElementById:id=>ids[id],addEventListener:(name,fn)=>listeners.push(fn)},setTimeout:()=>1,clearTimeout(){},PalmServiceBridge:function(){this.call=()=>{reply=this.onservicecallback;};this.cancel=()=>{};},window:{}};
vm.runInNewContext(fs.readFileSync('launcher/update-panel.js','utf8'),ctx);ctx.window.HomeUpdates.open();assert.equal(focus,ids.updateCheck);
ids.updateCheck.click();reply(JSON.stringify({returnValue:true,result:{home:'1.2.0',candidate:{home:'1.2.0',notes:'Tooling update'},root:false,state:'current',canInstall:false}}));assert(ids.updateInstall.disabled);assert(ids.updateStatus.textContent.includes('up to date'));
let prevented=0;listeners[0]({keyCode:39,preventDefault(){prevented++;},stopImmediatePropagation(){}});assert.equal(focus,ids.updateRecovery);assert.equal(prevented,1);
listeners[0]({keyCode:37,preventDefault(){},stopImmediatePropagation(){}});assert.equal(focus,ids.updateCheck,'left must skip disabled install backwards');
listeners[0]({keyCode:461,preventDefault(){},stopImmediatePropagation(){}});listeners[0]({keyCode:39,preventDefault(){throw Error('closed panel ate key');},stopImmediatePropagation(){}});
let returned=false;ctx.window.HomeUpdates.open({onClose(){returned=true;}});ids.updateBack.click();assert(returned,'Back returns to the settings panel that opened updates');
console.log('PASS update panel no-root/current state and remote navigation');
