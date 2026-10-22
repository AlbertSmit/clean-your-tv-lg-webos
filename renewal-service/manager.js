'use strict';
// A single service process owns this queue. Home interception is never called here.
module.exports=function(io){
 var state,stopped=false,queue=Promise.resolve(),generation=0;
 try{state=io.load()||{};}catch(_){state={enabled:false,error:'storage-error'};}
 state.enabled=state.enabled===true;stopped=!state.enabled;
 function status(){return JSON.parse(JSON.stringify(state));}
 function save(){io.save(state);}
 function enqueue(fn){var p=queue.then(fn).catch(function(){stopped=true;state.enabled=false;state.error='storage-error';return status();});queue=p;return p;}
 async function check(){
  if(stopped||!state.enabled)return status();
  var result=await io.run();
  if(stopped||!state.enabled)return status();
  if(result.status!=='cooldown')state.last=result;
  if(result.status==='renewed')state.lastRenewedAt=io.now();
  save();return status();
 }
 return {
  restoreHistory:function(snapshot){return enqueue(async function(){
   // Preserve diagnostics only, never import enabled=true or schedule renewal.
   if(state.enabled||state.last||!snapshot||snapshot.enabled!==false)return status();
   var allowed=['status','checkedAt','nextAt','failures','remainingSeconds'];
   if(snapshot.last&&typeof snapshot.last==='object'){
    state.last={};allowed.forEach(function(k){var v=snapshot.last[k];if((k==='status'&&typeof v==='string'&&v.length<80)||(k!=='status'&&typeof v==='number'&&Number.isFinite(v)))state.last[k]=v;});
   }
   if(typeof snapshot.lastRenewedAt==='number'&&Number.isFinite(snapshot.lastRenewedAt))state.lastRenewedAt=snapshot.lastRenewedAt;
   save();return status();
  });},
  allowed:function(){return !stopped&&state.enabled;},status:status,
  check:function(){return enqueue(check);},
  enable:function(){var ticket=++generation;return enqueue(async function(){
   state.enabled=false;state.error=null;save();
   var r=await io.schedule();
   if(!r||r.returnValue!==true){state.error='schedule-unavailable';save();return status();}
   if(ticket!==generation){await io.cancel();return status();}
   state.enabled=true;stopped=false;save();return check();
  });},
  disable:function(){generation++;stopped=true;return enqueue(async function(){
   state.enabled=false;state.error=null;var persisted=true;
   try{save();}catch(_){persisted=false;}
   var r;try{r=await io.cancel();}catch(_){r=null;}
   if(!r||!(r.returnValue===true||r.errorCode===2))state.error='cancel-unconfirmed';
   if(!persisted)state.error='disable-not-saved';
   try{save();}catch(_){state.error='disable-not-saved';}
   return status();
  });}
 };
};
