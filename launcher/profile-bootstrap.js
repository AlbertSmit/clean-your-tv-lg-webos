(window.HomeI18n?HomeI18n.ready:function(callback){callback();})(function(){
(function(){
 'use strict';
 var booted=false,profileError=false;
 function rpc(method,payload,cb,service){var b,done=false;var timer=setTimeout(function(){finish(null);},2000);
  function finish(r,ok){if(done)return;done=true;clearTimeout(timer);if(b)try{b.cancel();}catch(_){}cb(r,ok===true);}
  try{b=new PalmServiceBridge();b.onservicecallback=function(raw){try{var r=JSON.parse(raw);finish(r.returnValue===true?(r.result===undefined?r.state:r.result):null,r.returnValue===true);}catch(_){finish(null);}};b.call((service||'luna://com.cleanyourtv.updater.service/')+method,JSON.stringify(payload||{}));}catch(_){finish(null);}
 }
 function boot(){if(booted)return;booted=true;var s=document.createElement('script');s.src='app.js';s.onload=function(){
  // A populated rendered grid is a startup signal, not proof of every TV feature.
  if(document.querySelector('#tiles .item'))rpc('healthy',{version:'1.2.2'},function(){});
 };document.body.appendChild(s);}
 function use(s,restore){s=HomeData.validate(s);HomeData.save(localStorage,s);if(restore){var previousLanguage=window.HomeI18n&&HomeI18n.preference();HomeData.apply(localStorage,s);if(window.HomeI18n&&(HomeI18n.refresh(),HomeI18n.preference())!==previousLanguage)window.location.reload();}window.TV_APPS=s.inventory;window.CONFIG=s.config;if(s.renewal)rpc('restoreHistory',{state:s.renewal},function(){},'luna://com.gathin.tvhome.renewal/');}
 function icon(url,cb){if(/^data:image\/(png|jpeg|webp);base64,/.test(url)){cb(null,url);return;}
  // Only packaged relative icon paths; never turn arbitrary remote content into a profile.
  if(typeof url!=='string'||url.indexOf('..')>=0||/^([a-z]+:|\/)/i.test(url)){cb(Error('icon-path'));return;}
  var x=new XMLHttpRequest();x.open('GET',url,true);x.responseType='blob';x.timeout=5000;
  x.onload=function(){if((x.status!==0&&x.status!==200)||!x.response||x.response.size>256*1024){cb(Error('icon'));return;}
   var f=new FileReader();f.onload=function(){cb(null,f.result);};f.onerror=function(){cb(Error('icon'));};f.readAsDataURL(x.response);
  };x.onerror=x.ontimeout=function(){cb(Error('icon'));};x.send();
 }
 window.HomeProfile={capture:function(cb){
  if(profileError){cb(Error('stored-profile-unreadable'));return;}
  var inventory=JSON.parse(JSON.stringify(window.TV_APPS||{apps:[],inputs:[]}));
  var s={schema:1,inventory:inventory,config:JSON.parse(JSON.stringify(CONFIG)),settings:{}};
  try{['tvhome.order','tvhome.layout','tvhome.language'].forEach(function(key){var value=localStorage.getItem(key);if(value!==null)s.settings[key]=value;});}catch(e){cb(e);return;}
  var index=0;function next(error,value){if(error){cb(error);return;}if(index>0)inventory.apps[index-1].icon=value;
   if(index<inventory.apps.length){icon(inventory.apps[index++].icon,next);return;}
   rpc('status',{},function(state){if(!state||typeof state.enabled!=='boolean'){cb(Error('renewal-state-unavailable'));return;}
    s.renewal={enabled:false};['last','lastRenewedAt','error'].forEach(function(k){if(state[k]!==undefined)s.renewal[k]=state[k];});
    try{HomeData.save(localStorage,s);cb(null,s);}catch(e){cb(e);}
   },'luna://com.gathin.tvhome.renewal/');
  }next();
 }};
 try{var saved=HomeData.load(localStorage);if(saved){use(saved);boot();return;}}catch(_){profileError=true;boot();return;}
 // Personalized packages render immediately; generic upgrades may restore from
 // the independent updater's backup before constructing the tile grid.
 if(window.TV_APPS&&TV_APPS.apps&&TV_APPS.apps.length){boot();return;}
 rpc('restore',{},function(saved,ok){if(!ok)profileError=true;if(saved)try{use(saved,true);}catch(_){profileError=true;}boot();});
}());

});
