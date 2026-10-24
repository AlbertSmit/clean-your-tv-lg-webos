(window.HomeI18n?HomeI18n.ready:function(callback){callback();})(function(){
(function(){
 'use strict';
 function tr(s,p){return window.HomeI18n?HomeI18n.t(s,p):s.replace(/\{(\w+)\}/g,function(m,k){return p&&p[k]!==undefined?p[k]:m;});}function ht(s){return window.HomeI18n?HomeI18n.html(s):s;}
 var panel=document.createElement('section');panel.id='renewalPanel';panel.className='hidden';panel.setAttribute('role','dialog');panel.setAttribute('aria-label',tr('Home settings'));
 panel.setAttribute('aria-modal','true');
 panel.innerHTML=ht('<div class="renewal-card"><div class="settings-heading"><h2>Home settings</h2><span class="settings-edition">No-root Edition</span></div><p>Manage Home, software updates and your TV.</p><section class="settings-section"><h3>Your Home screen</h3><p>Choose where Home and return from apps take you.</p><p id="homeRoutingStatus" class="settings-status" aria-live="polite">Checking Home control…</p><div class="renewal-actions home-routing-actions"><button id="homeRoutingToggle" class="home-routing-switch" role="switch" aria-checked="false" disabled>Change Home</button><div class="home-visit-action"><button id="homeVisit" class="home-visit-button" aria-describedby="homeVisitHint">Open LG Home</button><p id="homeVisitHint" class="home-visit-hint">This button opens LG Home once. Your Home screen choice and settings stay saved.</p></div></div></section><section class="settings-section"><h3>Developer Mode auto-renewal (Beta)</h3><p>Developer Mode keeps Home installed. Auto-renewal tries to extend its session while your TV is on and online.</p><p class="renewal-warning">Beta: renewal is not yet verified on no-root TVs. Keep checking the timer in the Developer Mode app.</p><div id="renewalStatus" aria-live="polite">Checking auto-renewal…</div><div class="renewal-actions"><button id="renewalToggle">Turn on auto-renewal</button><button id="renewalCheck">Check session</button><button id="renewalDiagnostics" aria-expanded="false" aria-controls="renewalDetails">Show diagnostics</button></div><pre id="renewalDetails" class="hidden"></pre></section><section class="settings-section"><h3>Language</h3><div class="renewal-actions"><button id="homeLanguage">Language</button></div></section><section class="settings-section"><h3>Updates and TV</h3><p>Update Home or open LG settings for picture, sound and network.</p><div class="renewal-actions settings-links"><button id="renewalUpdates">Software updates</button><button id="renewalTV">TV settings</button></div></section><div class="settings-footer"><p>Hold Back for 1.2 seconds to open LG Home. Your settings stay saved.</p><div class="renewal-actions"><button id="renewalClose">Back to Home</button></div></div></div>');
 document.body.appendChild(panel);
 var status=document.getElementById('renewalStatus'),toggle=document.getElementById('renewalToggle'),check=document.getElementById('renewalCheck'),details=document.getElementById('renewalDetails');
 var previous;
 var buttons=Array.prototype.slice.call(panel.querySelectorAll('button')),index=0,state=null,busy=false;
 var checkingUpdates=false;
 function checkUpdates(){
  if(checkingUpdates||!window.HomeUpdates||!window.HomeUpdates.rpc)return;
  checkingUpdates=true;
  window.HomeUpdates.rpc('check',{},function(offer){
   checkingUpdates=false;if(!offer)return;
   var available=offer.state==='available'||offer.state==='helper-update-required';
   var button=document.getElementById('renewalUpdates');
   button.setAttribute('data-update-available',String(available));
   button.setAttribute('aria-label',tr(available?'Software updates. Update available.':'Software updates'));
  });
 }
 function openNow(){return !panel.classList.contains('hidden');}
 function focus(i){var direction=i<index?-1:1;for(var n=0;n<buttons.length;n++,i+=direction){var j=(i+buttons.length*2)%buttons.length;if(!buttons[j].disabled){index=j;buttons[index].focus();return;}}}
 function rpc(method,callback){
  var bridge,done=false,timer=setTimeout(function(){finish(null);},45000);
  function finish(r){if(done)return;done=true;clearTimeout(timer);if(bridge)try{bridge.cancel();}catch(_){}callback(r);}
  try{bridge=new PalmServiceBridge();bridge.onservicecallback=function(raw){try{finish(JSON.parse(raw));}catch(_){finish(null);}};bridge.call('luna://com.gathin.tvhome.renewal/'+method,'{}');}catch(_){finish(null);}
 }
 var homeToggle=document.getElementById('homeRoutingToggle'),homeVisit=document.getElementById('homeVisit'),homeStatus=document.getElementById('homeRoutingStatus'),homeEnabled=null,homeBusy=false;
 function homeRPC(method,payload,callback){
  var b,done=false,t=setTimeout(function(){finish({returnValue:false});},10000);
  function finish(r){if(done)return;done=true;clearTimeout(t);if(b)try{b.cancel();}catch(_){}callback(r);}
  try{b=new PalmServiceBridge();b.onservicecallback=function(raw){try{finish(JSON.parse(raw));}catch(_){finish({returnValue:false});}};b.call('luna://com.gathin.tvhome.renewal/'+method,JSON.stringify(payload));}catch(_){finish({returnValue:false});}
 }
 function renderHome(r){
  homeBusy=false;homeVisit.disabled=false;
  if(!r||r.returnValue!==true||typeof r.enabled!=='boolean'){
   homeEnabled=null;homeToggle.disabled=true;homeStatus.textContent=tr('Home Helper unavailable. Open Home Helper, then reopen settings.');return;
  }
  homeEnabled=r.enabled;homeToggle.disabled=false;homeToggle.setAttribute('aria-checked',String(homeEnabled));
  homeStatus.textContent=homeEnabled?tr('Home and return from apps open Clean Your TV.'):tr('Home and return from apps open LG Home.');
  if(openNow())focus(index);
 }
 function refreshHome(){homeToggle.disabled=true;homeRPC('homeStatus',{},renderHome);}
 homeToggle.onclick=function(){
  if(homeBusy||homeEnabled===null)return;homeBusy=true;homeToggle.disabled=true;homeVisit.disabled=true;homeStatus.textContent=tr('Changing Home control…');
  homeRPC('setHomeControl',{enabled:!homeEnabled},function(r){
   if(r.returnValue===true)renderHome(r);
   else homeRPC('homeStatus',{},function(status){renderHome(status);homeStatus.textContent=tr('Change was not confirmed. Check the switch and try again.');});
  });
 };
 homeVisit.onclick=function(){
  if(homeBusy)return;homeBusy=true;homeVisit.disabled=true;
  homeRPC('openLGHome',{},function(r){homeBusy=false;homeVisit.disabled=false;
   if(r.returnValue===true)close();else homeStatus.textContent=tr('Could not open LG Home. Check Home Helper and try again.');
  });
 };
 function date(v){return typeof v==='number'?(window.HomeI18n?HomeI18n.formatDateTime(v):new Date(v).toLocaleString()):tr('Not yet');}
 var labels={healthy:tr('Session checked'),renewed:tr('Renewal confirmed'),retry:tr('Connection failed — retry scheduled'),unverified:tr('LG response could not confirm renewal'),expired:tr('Session expired — open Developer Mode'),unavailable:tr('No readable Developer Mode session'), 'session-changed':tr('Session changed — retry scheduled'),'storage-error':tr('Could not save state'),'internal-error':tr('Check failed')};
 function render(){
  toggle.textContent=state&&state.enabled?tr('Turn off auto-renewal'):tr('Turn on auto-renewal');
  check.disabled=busy||!state||!state.enabled;toggle.disabled=busy||!state;
  if(!state)return;
  var last=state.last||{};
  var text=state.enabled?tr('Auto-renewal enabled (Beta)'):tr('Auto-renewal off');
  if(last.status)text+='\n'+(labels[last.status]||tr('Check pending'));
  if(typeof last.remainingSeconds==='number')text+=' · '+tr('{hours} hours remaining (estimate)',{hours:Math.floor(Math.max(0,last.remainingSeconds-(Date.now()-last.checkedAt)/1000)/3600)});
  text+='\n'+tr('Last checked: {date}',{date:date(last.checkedAt)})+'\n'+tr('Last confirmed renewal: {date}',{date:date(state.lastRenewedAt)});
  if(state.error==='disable-not-saved')text+='\n'+tr('Disable could not be saved. Retry before restarting the service.');
  if(state.error)text+='\n'+tr('Setup error: {error}. Use Developer Mode manually.',{error:state.error});
  status.textContent=text;if(openNow())focus(index);
 }
 function action(method){if(busy)return;busy=true;status.textContent=tr('Working…');toggle.disabled=true;check.disabled=true;
  rpc(method,function(r){busy=false;if(!r||r.returnValue!==true){state=null;status.textContent=tr('Service unavailable. Install the complete Home package and try again. Manage your Developer Mode timer manually.');toggle.disabled=true;check.disabled=true;if(openNow())focus(index);return;}state=r.state;render();});
 }
 toggle.onclick=function(){if(state)action(state.enabled?'disable':'enable');};
 check.onclick=function(){action('check');};
 document.getElementById('renewalDiagnostics').onclick=function(){
  var last=state&&state.last||{};
  details.textContent=tr('Share this with your TV model and firmware at:')+'\ngithub.com/Razdva122/clean-your-tv-lg-webos/issues\n'+JSON.stringify({launcher:'1.2.0',beta:true,enabled:!!(state&&state.enabled),status:last.status||'not-checked',checkedAt:last.checkedAt||null,remainingSeconds:typeof last.remainingSeconds==='number'?last.remainingSeconds:null,lastRenewedAt:state&&state.lastRenewedAt||null,error:state&&state.error||null},null,2);
  details.classList.toggle('hidden');
  this.textContent=details.classList.contains('hidden')?tr('Show diagnostics'):tr('Hide diagnostics');
  this.setAttribute('aria-expanded',String(!details.classList.contains('hidden')));
 };
 function close(){panel.classList.add('hidden');if(previous&&previous.focus)previous.focus();}
 document.getElementById('renewalClose').onclick=close;
 document.getElementById('homeLanguage').onclick=function(){if(window.HomeI18n)HomeI18n.openLanguagePicker();};
 document.getElementById('renewalUpdates').onclick=function(){panel.classList.add('hidden');window.HomeUpdates.open({onClose:function(){panel.classList.remove('hidden');focus(buttons.indexOf(document.getElementById('renewalUpdates')));checkUpdates();}});};
 document.getElementById('renewalTV').onclick=function(){close();try{var b=new PalmServiceBridge();b.onservicecallback=function(){b.cancel();};b.call('luna://com.webos.applicationManager/launch',JSON.stringify({id:'com.palm.app.settings',params:{}}));}catch(_){}};
 buttons.forEach(function(b,i){b.onfocus=function(){index=i;};b.addEventListener('mouseover',function(){focus(i);});});
 document.addEventListener('keydown',function(e){if(!openNow())return;var k=e.keyCode;
  if([9,37,38,39,40,13,461,27].indexOf(k)<0)return;
  e.preventDefault();e.stopImmediatePropagation();
  if(k===461||k===27)close();else if(k===13){if(!e.repeat)buttons[index].click();}else focus(index+(k===37||k===38||(k===9&&e.shiftKey)?-1:1));
 },true);
 window.RenewalPanel={isOpen:openNow,open:function(){if(openNow())return;previous=document.activeElement;panel.classList.remove('hidden');details.classList.add('hidden');document.getElementById('renewalDiagnostics').textContent=tr('Show diagnostics');document.getElementById('renewalDiagnostics').setAttribute('aria-expanded','false');focus(0);action('status');refreshHome();checkUpdates();}};
 // No session request, token access or scheduler setup happens on launcher startup.
}());

});
