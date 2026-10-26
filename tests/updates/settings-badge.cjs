const assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const tick=()=>new Promise(resolve=>setImmediate(resolve));
function harness(root){
 const ids={},buttons=[],pending=[],calls=[],homePending=[],rpcCalls=[];let focused;
 class E{
  constructor(tag){this.tag=tag;this.attrs={};this.children=[];this.className='';this.hidden=false;if(tag==='button')buttons.push(this);this.classList={toggle:(n,on)=>{const has=this.className.split(' ').includes(n);if(on===undefined)on=!has;if(on&&!has)this.className+=' '+n;else if(!on)this.className=this.className.split(' ').filter(x=>x!==n).join(' ');},contains:n=>this.className.split(' ').includes(n),add:n=>{this.className+=' '+n;},remove:n=>{this.className=this.className.split(' ').filter(x=>x!==n).join(' ');}};}
  set innerHTML(html){for(const match of html.matchAll(/<(button|p|div|pre|span)\b[^>]*id="([^"]+)"[^>]*>/g)){const e=new E(match[1]);ids[match[2]]=e;this.children.push(e);}}
  appendChild(e){this.children.push(e);}setAttribute(k,v){this.attrs[k]=v;}addEventListener(){}focus(){focused=this;document.activeElement=this;if(this.onfocus)this.onfocus();}querySelectorAll(){return buttons;}
 }
 const document={body:new E('body'),activeElement:{focus(){}},createElement:t=>new E(t),getElementById:id=>ids[id],addEventListener(){}};
 const updates={open(){},rpc(method,payload,callback){calls.push(method);assert.equal(method,'check');return root?new Promise((resolve,reject)=>pending.push({resolve,reject})):pending.push(callback);}};
 const window=root?{RootUpdates:updates}:{HomeUpdates:updates};
 const context={window,document,Promise,setTimeout:()=>1,clearTimeout(){},createRootExit:()=>async()=>{},PalmServiceBridge:class{cancel(){}call(uri){rpcCalls.push(uri);if(!root&&uri.endsWith('/homeStatus')){homePending.push(value=>this.onservicecallback(JSON.stringify(value)));return;}this.onservicecallback(JSON.stringify({returnValue:true,result:{returnValue:true,result:{intent:{phase:'disabled'}}},state:{enabled:false}}));}}};
 vm.runInNewContext(fs.readFileSync(root?'root-edition/ui/root-settings.js':'launcher/renewal-panel.js','utf8'),context);
 return {panel:window.RenewalPanel,calls,rpcCalls,routing:()=>ids.homeRoutingToggle,routingStatus:()=>ids.homeRoutingStatus,replyHome:value=>homePending.shift()(value),button:()=>root?buttons.find(b=>b.textContent==='Software updates'):ids.renewalUpdates,close:()=>root?buttons.find(b=>b.textContent==='Back to Home').onclick():ids.renewalClose.onclick(),reply:value=>{const done=pending.shift();if(root)done.resolve(value);else done(value);},fail:()=>{const done=pending.shift();if(root)done.reject(Error('offline'));else done(null);},focus:()=>focused};
}
(async()=>{
 const home=harness(false);
 home.panel.open();
 assert.equal(home.routing().hidden,true,'a pending status must not appear off');
 home.replyHome({returnValue:true,enabled:true});
 assert.equal(home.routing().hidden,false);
 assert.equal(home.routing().disabled,false);
 assert.equal(home.routing().attrs['aria-checked'],'true');
 for(const reply of [{returnValue:false,errorText:'Home Helper data unavailable'},null,{returnValue:true,enabled:'false'}]){
  if(!home.routing().disabled)home.routing().focus();home.close();home.panel.open();
  assert.notEqual(home.focus(),home.routing(),'hiding the routing switch must preserve visible focus');
  assert.equal(home.routing().hidden,true,'rechecking must not show the previous choice as current');
  home.replyHome(reply);
  assert.equal(home.routing().hidden,true,'unknown status must not expose an off switch');
  assert.equal(home.routing().disabled,true);
  assert.match(home.routingStatus().textContent,/unknown/);
 }
 if(!home.routing().disabled)home.routing().focus();home.close();home.panel.open();
  assert.notEqual(home.focus(),home.routing(),'hiding the routing switch must preserve visible focus');home.replyHome({returnValue:true,enabled:false});
 assert.equal(home.routing().hidden,false,'a confirmed LG Home choice remains visible');
 assert.equal(home.routing().attrs['aria-checked'],'false');
 assert.equal(home.rpcCalls.some(uri=>uri.endsWith('/setHomeControl')||uri.includes('applicationManager')),false,'opening settings cannot change Home or launch Helper');
 for(const root of [false,true]){
  const h=harness(root);assert.equal(h.calls.length,0,'launcher startup must not check releases');
  h.panel.open();await tick();assert.equal(h.calls.length,1,'settings opening checks automatically');
  h.panel.open();assert.equal(h.calls.length,1,'already-open settings must not check twice');
  h.close();h.panel.open();await tick();assert.equal(h.calls.length,1,'coalesce an in-flight check');
  const focus=h.focus();
  h.reply(root?{canInstall:true,reason:'available'}:{state:'available',canInstall:false});await tick();
  assert.equal(h.button().attrs['data-update-available'],'true');
  assert.equal(h.button().attrs['aria-label'],'Software updates. Update available.');
  assert.equal(h.focus(),focus,'background check must not move remote focus');
  h.close();h.panel.open();await tick();assert.equal(h.calls.length,2);
  h.reply(root?{canInstall:false,reason:'current'}:{state:'newer-installed',canInstall:false});await tick();
  assert.equal(h.button().attrs['data-update-available'],'false','no newer version removes badge');
  assert.equal(h.button().attrs['aria-label'],'Software updates');
  h.close();h.panel.open();await tick();h.reply(root?{canInstall:false,reason:'missing-rollback'}:{state:'helper-update-required',canInstall:false});await tick();
  assert.equal(h.button().attrs['data-update-available'],'true','new release may require computer setup');
  h.close();h.panel.open();await tick();h.fail();await tick();
  assert.equal(h.button().attrs['data-update-available'],'true','network failure retains the last confirmed availability');
  assert(h.panel.isOpen(),'failed update checks must not block settings');
  h.close();h.panel.open();await tick();assert.equal(h.calls.length,5,'a failed request must not prevent the next settings check');h.reply(null);await tick();
 }
 console.log('PASS both settings check releases on open, show accessible badges, coalesce requests and preserve focus');
})().catch(error=>{console.error(error);process.exit(1);});
