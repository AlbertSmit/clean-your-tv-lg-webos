'use strict';
module.exports=function(apps){
 var previous=null,gapSince=null;
 return {
  reset:function(){previous=null;gapSince=null;},
  next:function(id,now){
   // webOS briefly reports no foreground app between app exit and LG Home.
   // Keep that origin only for a bounded gap; any real intermediate app resets it.
   if(id===''){
    if(gapSince===null)gapSince=now;
    return false;
   }
   var redirect=id==='com.webos.app.home'&&apps.indexOf(previous)!==-1&&
    (gapSince===null||now-gapSince<=2500);
   previous=id;gapSince=null;return redirect;
  }
 };
};
