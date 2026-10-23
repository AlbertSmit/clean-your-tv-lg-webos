(function(){
 'use strict';
 var URI='luna://com.cleanyourtv.updater.service/',VERSION='1.2.2';
 var panel=document.createElement('section');panel.id='updatePanel';panel.className='hidden';panel.setAttribute('role','dialog');panel.setAttribute('aria-label','Software updates');
 panel.innerHTML='<div class="renewal-card"><h2>Software updates</h2><p id="updateStatus" aria-live="polite">Checking for updates…</p><p id="updateNotes"></p><div class="renewal-actions"><button id="updateCheck" hidden>Try again</button><button id="updateInstall" disabled>Update Home</button><button id="updateRecovery">Recovery</button><button id="updateBack">Back</button></div></div>';
 document.body.appendChild(panel);
 var status=document.getElementById('updateStatus'),notes=document.getElementById('updateNotes'),install=document.getElementById('updateInstall'),check=document.getElementById('updateCheck');
 var buttons=Array.prototype.slice.call(panel.querySelectorAll('button')),index=0,offer=null,busy=false,confirmed=false,onClose=null,previous;
 function rpc(method,payload,cb){var b,done=false,timer=setTimeout(function(){finish(null);},method==='install'?190000:65000);
  function finish(r){if(done)return;done=true;clearTimeout(timer);if(b)try{b.cancel();}catch(_){}cb(r&&r.returnValue===true?r.result:null);}
  try{b=new PalmServiceBridge();b.onservicecallback=function(raw){try{finish(JSON.parse(raw));}catch(_){finish(null);}};b.call(URI+method,JSON.stringify(payload||{}));}catch(_){finish(null);}
 }
 function focus(i,direction){direction=direction||1;for(var n=0;n<buttons.length;n++,i+=direction){var j=(i+buttons.length)%buttons.length;if(!buttons[j].disabled&&!buttons[j].hidden){index=j;buttons[j].focus();return;}}}
 function show(text){status.textContent=text;}
 function checkNow(){if(busy)return;busy=true;check.hidden=true;check.disabled=true;install.disabled=true;notes.textContent='';confirmed=false;install.textContent='Update Home';show('Checking for updates…');
  rpc('check',{},function(r){busy=false;check.disabled=false;offer=r;
   if(!r||!r.candidate){check.hidden=false;show('Update service or signed release unavailable. Install the separate Home Updater package once, then retry. Your current Home is unchanged.');if(!panel.classList.contains('hidden'))focus(0);return;}
   notes.textContent=r.candidate.notes;install.disabled=!r.canInstall;
   var labels={current:'Home is up to date.','newer-installed':'Your installed Home is newer than this release.','helper-update-required':'Update Home Helper using the installation guide first.',available:r.canInstall?'A signed Home update is available.':r.root?'Update available, but a verified recovery package for your installed version is missing.':'Update available. Without root, install it from a computer using the guide.'};
   show('Installed Home '+r.home+' · Available '+r.candidate.home+'\n'+labels[r.state]);if(!panel.classList.contains('hidden'))focus(0);
  });
 }
 check.onclick=checkNow;
 install.onclick=function(){if(busy||!offer||!offer.canInstall)return;
  if(!confirmed){confirmed=true;install.textContent='Confirm update';show('Home will close during installation. Your app list and settings will be saved first. Press Confirm update to continue.');return;}
  busy=true;install.disabled=true;check.disabled=true;show('Saving apps, icons and settings…');
  window.HomeProfile.capture(function(error,profile){if(error){busy=false;check.disabled=false;show('Could not save your complete profile. Nothing was installed.');return;}
   show('Installing Home… Keep the TV on. If this screen closes, open Home again or use Home Updater for recovery.');
   rpc('install',{version:offer.candidate.home,profile:profile},function(r){busy=false;check.disabled=false;show(r?'Update state: '+r.status+'. Reopen Home when installation finishes.':'Update outcome is not confirmed. Open Home Updater → Recovery before retrying.');});
  });
 };
 document.getElementById('updateRecovery').onclick=function(){if(busy)return;rpc('reconcile',{},function(r){show(r?'Recovery state: '+r.status+'. Use Home Updater to restore the previous version if offered.':'No recovery result available. Your helper has not been changed.');});};
 function close(){panel.classList.add('hidden');if(onClose){var callback=onClose;onClose=null;callback();}else if(previous&&previous.focus)previous.focus();}
 document.getElementById('updateBack').onclick=close;
 buttons.forEach(function(b,i){b.onfocus=function(){index=i;};b.addEventListener('mouseover',function(){focus(i);});});
 document.addEventListener('keydown',function(e){if(panel.classList.contains('hidden'))return;if([9,37,38,39,40,13,461,27].indexOf(e.keyCode)<0)return;
  e.preventDefault();e.stopImmediatePropagation();if(e.keyCode===461||e.keyCode===27)close();else if(e.keyCode===13){if(!e.repeat)buttons[index].click();}else {var direction=e.keyCode===37||e.keyCode===38||(e.keyCode===9&&e.shiftKey)?-1:1;focus(index+direction,direction);}
 },true);
 window.HomeUpdates={open:function(options){previous=document.activeElement;onClose=options&&options.onClose||null;panel.classList.remove('hidden');checkNow();focus(0);},rpc:rpc,version:VERSION};
}());
