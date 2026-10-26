'use strict';
const assert=require('assert'),fs=require('fs'),path=require('path');
const {chromium}=require('playwright');
const vm=require('vm');
const APP=process.env.CYTV_INSTALLER_APP||path.join(__dirname,'../app'),ID='a'.repeat(32),LEASE='c'.repeat(32),SHA='b'.repeat(64);
(async()=>{
 assert(fs.existsSync(path.join(APP,'index.html')),'TV installer interface is required');
 const catalog=fs.readFileSync(path.join(APP,'i18n.js'),'utf8'),sandbox={window:{localStorage:{getItem(){return 'en';},setItem(){}},navigator:{language:'en'},document:{documentElement:{}}}};vm.runInNewContext(catalog,sandbox);
 const keys=vm.runInNewContext(catalog.match(/var keys=(\[[^;]+\]);/)[1]);keys.push('continueOriginal','resumeConfirm');for(const locale of Object.keys(sandbox.window.InstallerI18n.names)){sandbox.window.InstallerI18n.set(locale);for(const key of keys)assert.equal(typeof sandbox.window.InstallerI18n.t(key),'string',locale+': '+key);}
 const browser=await chromium.launch({headless:true,channel:process.env.BROWSER_CHANNEL||'chrome'});
 async function fixture(state,locale='en',size={width:1280,height:720}){
  const context=await browser.newContext({viewport:size,locale});
  await context.addInitScript(({state,ID,LEASE,SHA,locale})=>{
   localStorage.setItem('cytv.installer.language',locale);window.calls=[];window.model=state;window.saved=ID;
   if(state.noHbc)return;
   window.PalmServiceBridge=function(){this.cancel=function(){};this.call=function(uri,raw){
    const command=JSON.parse(raw).command;window.calls.push(command);let reply;
    if(command.includes(' status '))reply=window.model.status||{state:'pending',stage:'root-deploy',operation:ID,action:'install',lease:LEASE};
    else if(command.endsWith('prepare-runtime')){window.model={state:'fresh'};reply={state:'runtime_ready'};}
    else if(command.includes(' install ')||command.includes(' remove ')){if(window.model.loseReply){this.onservicecallback(JSON.stringify({returnValue:false}));return;}reply={state:'pending',operation:command.match(/--operation ([a-f0-9]+)/)[1],action:command.includes(' remove ')?'remove':'install'};}
    else if(command.endsWith('activate'))reply={state:'complete',code:'activated'};
    else if(command.endsWith('restore'))reply={state:'complete',code:'restored'};
    else reply={state:window.model.state,installation:{state:window.model.state,can_install:window.model.state==='fresh',can_maintain:window.model.state==='installed',versions:window.model.versions},candidate_sha256:SHA,active_operation:window.model.active||null,runtime:window.model.runtime};
    this.onservicecallback(JSON.stringify({returnValue:true,stdoutString:JSON.stringify(reply)}));
   };};
  },{state,ID,LEASE,SHA,locale});
  const page=await context.newPage();await page.goto('file://'+path.join(APP,'index.html'));await page.waitForSelector('[data-screen]');return {context,page};
 }
 try{
  let f=await fixture({state:'fresh'}),p=f.page;
  await p.waitForSelector('[data-screen="review"]');assert((await p.evaluate(()=>calls)).every(c=>c.includes(' inspect')),'opening inspects only');
  await p.locator('#install').focus();await p.keyboard.press('ArrowDown');assert.notEqual(await p.evaluate(()=>document.activeElement.id),'install');
  await p.locator('#install').focus();await p.keyboard.press('Enter');await p.waitForSelector('[data-screen="confirm"]');
  await p.keyboard.press('Escape');await p.waitForSelector('[data-screen="review"]');assert.equal(await p.evaluate(()=>document.activeElement.id),'install');assert((await p.evaluate(()=>calls)).every(c=>c.includes(' inspect')),'cancel never submits');
  await p.locator('#install').click();await p.locator('#confirm').click();await p.waitForSelector('[data-screen="progress"]');
  assert.equal((await p.evaluate(()=>calls)).filter(c=>c.includes(' install ')).length,1);
  await p.reload();await p.waitForSelector('[data-screen="progress"]');assert((await p.evaluate(()=>calls)).every(c=>c.includes(' inspect')||c.includes(' status ')),'reopening never resubmits');await f.context.close();
  f=await fixture({state:'recovery_required',active:{operation:ID,lease:LEASE,state:'pending',action:'remove'}});p=f.page;await p.waitForSelector('[data-screen="progress"]');assert((await p.evaluate(()=>calls)).some(c=>c.includes('--operation '+ID)));assert(!(await p.evaluate(()=>calls)).some(c=>c.includes('--operation '+LEASE)));await f.context.close();
  f=await fixture({state:'prerequisites',runtime:{privateRuntimeRequired:true,requiredSpace:335544320}});p=f.page;await p.waitForSelector('[data-screen="prerequisites"]');assert(!(await p.evaluate(()=>calls)).some(c=>c.includes('prepare-runtime')));await p.locator('#prepare').click();await p.locator('#confirm').click();await p.waitForSelector('[data-screen="review"]');assert.equal((await p.evaluate(()=>calls)).filter(c=>c.endsWith('prepare-runtime')).length,1);await f.context.close();
  f=await fixture({state:'installed',versions:{root:'1.2.3','root-updater':'2.3.4'}});p=f.page;await p.waitForSelector('[data-screen="installed"]');assert((await p.locator('#versions').textContent()).includes('1.2.3'));assert.equal(await p.locator('#install').count(),0);await p.locator('#remove').click();await p.waitForSelector('[data-screen="confirm"]');assert(!(await p.evaluate(()=>calls)).some(c=>c.includes(' remove ')));await p.keyboard.press('Escape');assert.equal(await p.evaluate(()=>document.activeElement.id),'remove');await f.context.close();
  f=await fixture({state:'fresh',loseReply:true});p=f.page;await p.waitForSelector('#install');await p.locator('#install').click();await p.locator('#confirm').click();await p.waitForSelector('[data-screen="progress"]');assert.equal((await p.evaluate(()=>calls)).filter(c=>c.includes(' install ')).length,1);assert.equal(await p.locator('#install').count(),0);await p.locator('#refresh').click();assert.equal((await p.evaluate(()=>calls)).filter(c=>c.includes(' install ')).length,1);await f.context.close();
  f=await fixture({state:'recovery_required',active:{operation:ID,state:'recovery_required',action:'install'},status:{operation:ID,state:'recovery_required',action:'install',can_resume:true}});p=f.page;await p.waitForSelector('#resume');await p.locator('#resume').click();assert(!(await p.evaluate(()=>calls)).some(c=>c.includes('--resume')));await p.locator('#confirm').click();await p.waitForSelector('[data-screen="progress"]');assert((await p.evaluate(()=>calls)).some(c=>c.endsWith('install --operation '+ 'a'.repeat(32)+' --resume')));await f.context.close();
  f=await fixture({state:'fresh',noHbc:true});p=f.page;await p.waitForSelector('[data-screen="unsupported"]');assert.equal(await p.locator('#install').count(),0);await f.context.close();
  f=await fixture({state:'installed',versions:{root:'1.2.3','root-updater':'2.3.4'},status:{state:'complete',current:false,action:'install'}});p=f.page;await p.waitForSelector('#activate');await p.evaluate(id=>localStorage.setItem('cytv.installer.operation',id),ID);await p.reload();await p.waitForSelector('[data-screen="installed"]');assert.equal(await p.locator('#install').count(),0);await f.context.close();
  for(const locale of ['en','de','es','pt-BR','fr','it','ko','hi','pl','ru'])for(const size of [{width:1280,height:720},{width:1920,height:1080}]){
   f=await fixture({state:'installed',versions:{root:'1.2.3','root-updater':'2.3.4'}},locale,size);p=f.page;await p.waitForSelector('[data-screen="installed"]');await p.evaluate(()=>document.fonts.ready);
   const metrics=await p.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth,font:parseFloat(getComputedStyle(document.querySelector('#content p')).fontSize),lang:document.documentElement.lang}));assert(metrics.scroll<=metrics.width,JSON.stringify(metrics));assert(metrics.font>=24);assert.equal(metrics.lang,locale);
   await p.locator('#remove').focus();await p.keyboard.press('ArrowDown');const rect=await p.evaluate(()=>{const r=document.activeElement.getBoundingClientRect();return {top:r.top,bottom:r.bottom};});assert(rect.top>=0&&rect.bottom<=size.height,'remote focus remains visible');
   if(process.env.CYTV_SCREENSHOTS&&['de','hi','ko'].includes(locale)){const dest=path.join(process.env.CYTV_SCREENSHOTS,locale+'-'+size.width+'.png');await p.screenshot({path:dest});console.log('SCREENSHOT',dest,JSON.stringify(metrics));}
   await f.context.close();
  }
  console.log('PASS TV UI: inspect-only reopen, durable foreign request, explicit runtime, cancellation, one submission/lost reply, installed versions, D-pad/Back/focus, ten locales at 720p/1080p');
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1;});
