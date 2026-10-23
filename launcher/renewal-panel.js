(function(){
 'use strict';
 var panel=document.createElement('section');panel.id='renewalPanel';panel.className='hidden';panel.setAttribute('role','dialog');panel.setAttribute('aria-label','Home settings');
 panel.setAttribute('aria-modal','true');
 panel.innerHTML='<div class="renewal-card"><div class="settings-heading"><h2>Home settings</h2><span class="settings-edition">No-root Edition</span></div><p>Manage Home, software updates and your TV.</p><section class="settings-section"><h3>Developer Mode auto-renewal (Beta)</h3><p>Developer Mode keeps Home installed. Auto-renewal tries to extend its session while your TV is on and online.</p><p class="renewal-warning">Beta: renewal is not yet verified on no-root TVs. Keep checking the timer in the Developer Mode app.</p><div id="renewalStatus" aria-live="polite">Checking auto-renewal…</div><div class="renewal-actions"><button id="renewalToggle">Turn on auto-renewal</button><button id="renewalCheck">Check session</button><button id="renewalDiagnostics" aria-expanded="false" aria-controls="renewalDetails">Show diagnostics</button></div><pre id="renewalDetails" class="hidden"></pre></section><section class="settings-section"><h3>Updates and TV</h3><p>Update Home or open LG settings for picture, sound and network.</p><div class="renewal-actions settings-links"><button id="renewalUpdates">Software updates</button><button id="renewalTV">TV settings</button></div></section><div class="settings-footer"><p>To return to LG Home, press Home three times within two seconds.</p><div class="renewal-actions"><button id="renewalClose">Back to Home</button></div></div></div>';
 document.body.appendChild(panel);
 var status=document.getElementById('renewalStatus'),toggle=document.getElementById('renewalToggle'),check=document.getElementById('renewalCheck'),details=document.getElementById('renewalDetails');
 var previous;
 var buttons=Array.prototype.slice.call(panel.querySelectorAll('button')),index=0,state=null,busy=false;
 function openNow(){return !panel.classList.contains('hidden');}
 function focus(i){var direction=i<index?-1:1;for(var n=0;n<buttons.length;n++,i+=direction){var j=(i+buttons.length*2)%buttons.length;if(!buttons[j].disabled){index=j;buttons[index].focus();return;}}}
 function rpc(method,callback){
  var bridge,done=false,timer=setTimeout(function(){finish(null);},45000);
  function finish(r){if(done)return;done=true;clearTimeout(timer);if(bridge)try{bridge.cancel();}catch(_){}callback(r);}
  try{bridge=new PalmServiceBridge();bridge.onservicecallback=function(raw){try{finish(JSON.parse(raw));}catch(_){finish(null);}};bridge.call('luna://com.gathin.tvhome.renewal/'+method,'{}');}catch(_){finish(null);}
 }
 function date(v){return typeof v==='number'?new Date(v).toLocaleString():'Not yet';}
 var labels={healthy:'Session checked',renewed:'Renewal confirmed',retry:'Connection failed — retry scheduled',unverified:'LG response could not confirm renewal',expired:'Session expired — open Developer Mode',unavailable:'No readable Developer Mode session', 'session-changed':'Session changed — retry scheduled','storage-error':'Could not save state','internal-error':'Check failed'};
 function render(){
  toggle.textContent=state&&state.enabled?'Turn off auto-renewal':'Turn on auto-renewal';
  check.disabled=busy||!state||!state.enabled;toggle.disabled=busy||!state;
  if(!state)return;
  var last=state.last||{};
  var text=state.enabled?'Auto-renewal enabled (Beta)':'Auto-renewal off';
  if(last.status)text+='\n'+(labels[last.status]||'Check pending');
  if(typeof last.remainingSeconds==='number')text+=' · '+Math.floor(Math.max(0,last.remainingSeconds-(Date.now()-last.checkedAt)/1000)/3600)+' hours remaining (estimate)';
  text+='\nLast checked: '+date(last.checkedAt)+'\nLast confirmed renewal: '+date(state.lastRenewedAt);
  if(state.error==='disable-not-saved')text+='\nDisable could not be saved. Retry before restarting the service.';
  if(state.error)text+='\nSetup error: '+state.error+'. Use Developer Mode manually.';
  status.textContent=text;if(openNow())focus(index);
 }
 function action(method){if(busy)return;busy=true;status.textContent='Working…';toggle.disabled=true;check.disabled=true;
  rpc(method,function(r){busy=false;if(!r||r.returnValue!==true){state=null;status.textContent='Service unavailable. Install the complete Home package and try again. Manage your Developer Mode timer manually.';toggle.disabled=true;check.disabled=true;if(openNow())focus(index);return;}state=r.state;render();});
 }
 toggle.onclick=function(){if(state)action(state.enabled?'disable':'enable');};
 check.onclick=function(){action('check');};
 document.getElementById('renewalDiagnostics').onclick=function(){
  var last=state&&state.last||{};
  details.textContent='Share this with your TV model and firmware at:\ngithub.com/Razdva122/clean-your-tv-lg-webos/issues\n'+JSON.stringify({launcher:'1.2.0',beta:true,enabled:!!(state&&state.enabled),status:last.status||'not-checked',checkedAt:last.checkedAt||null,remainingSeconds:typeof last.remainingSeconds==='number'?last.remainingSeconds:null,lastRenewedAt:state&&state.lastRenewedAt||null,error:state&&state.error||null},null,2);
  details.classList.toggle('hidden');
  this.textContent=details.classList.contains('hidden')?'Show diagnostics':'Hide diagnostics';
  this.setAttribute('aria-expanded',String(!details.classList.contains('hidden')));
 };
 function close(){panel.classList.add('hidden');if(previous&&previous.focus)previous.focus();}
 document.getElementById('renewalClose').onclick=close;
 document.getElementById('renewalUpdates').onclick=function(){panel.classList.add('hidden');window.HomeUpdates.open({onClose:function(){panel.classList.remove('hidden');focus(3);}});};
 document.getElementById('renewalTV').onclick=function(){close();try{var b=new PalmServiceBridge();b.onservicecallback=function(){b.cancel();};b.call('luna://com.webos.applicationManager/launch',JSON.stringify({id:'com.palm.app.settings',params:{}}));}catch(_){}};
 buttons.forEach(function(b,i){b.addEventListener('mouseover',function(){focus(i);});});
 document.addEventListener('keydown',function(e){if(!openNow())return;var k=e.keyCode;
  if([9,37,38,39,40,13,461,27].indexOf(k)<0)return;
  e.preventDefault();e.stopImmediatePropagation();
  if(k===461||k===27)close();else if(k===13){if(!e.repeat)buttons[index].click();}else focus(index+(k===37||k===38||(k===9&&e.shiftKey)?-1:1));
 },true);
 window.RenewalPanel={isOpen:openNow,open:function(){if(openNow())return;previous=document.activeElement;panel.classList.remove('hidden');details.classList.add('hidden');document.getElementById('renewalDiagnostics').textContent='Show diagnostics';document.getElementById('renewalDiagnostics').setAttribute('aria-expanded','false');focus(0);action('status');}};
 // No session request, token access or scheduler setup happens on launcher startup.
}());
