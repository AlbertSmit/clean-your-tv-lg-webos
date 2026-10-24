(window.HomeI18n && window.HomeI18n.ready ? window.HomeI18n.ready : function(callback){callback();})(function(){
(function(){'use strict';var buttons=[document.getElementById('refresh'),document.getElementById('restore'),document.getElementById('open')],index=0,busy=false;
function tr(source,params){return window.HomeI18n ? window.HomeI18n.t(source,params) : source.replace(/\{(\w+)\}/g,function(_,key){return params[key];});}
function state(code){var names={preparing:'Preparing','pausing-renewal':'Pausing renewal','renewal-recovery':'Renewal recovery','restoring-renewal':'Restoring renewal',installing:'Installing','awaiting-launch':'Awaiting launch',complete:'Complete','rolling-back':'Rolling back','rolled-back':'Rolled back','recovery-required':'Recovery required',aborted:'Aborted'};return names[code]?tr(names[code])+' ('+code+')':code;}
function text(t){document.getElementById('status').textContent=tr(t);}
if(window.HomeI18n){document.title=tr('Home Updater');window.HomeI18n.apply(document.body);}
function call(method,payload,cb){var b=new PalmServiceBridge(),done=false,t=setTimeout(function(){finish(null);},190000);function finish(r){if(done)return;done=true;clearTimeout(t);try{b.cancel();}catch(_){}cb(r);}
b.onservicecallback=function(raw){try{var r=JSON.parse(raw);finish(r.returnValue===true?r.result:null);}catch(_){finish(null);}};b.call('luna://com.cleanyourtv.updater.service/'+method,JSON.stringify(payload));}
function refresh(){if(busy)return;buttons[1].textContent=tr('Restore previous Home');buttons[1].disabled=true;call('reconcile',{},function(s){text(s?tr('Update state: {status}',{status:state(s.status)}):'No transaction, or recovery service is unavailable.');buttons[1].disabled=!s||['awaiting-launch','complete'].indexOf(s.status)<0;});}
document.addEventListener('webOSRelaunch',refresh);
document.addEventListener('visibilitychange',function(){if(!document.hidden)refresh();});
buttons[0].onclick=refresh;
buttons[1].onclick=function(){if(busy||buttons[1].disabled)return;window.HomeI18n.confirm({title:'Restore previous Home?',message:'Restore the signed previous Home package. Home Helper will remain unchanged.',action:'Restore previous Home'},function(){if(busy||buttons[1].disabled)return;busy=true;buttons[1].disabled=true;text('Restoring… Keep the TV on.');call('rollback',{},function(s){busy=false;text(s?tr('Recovery state: {status}',{status:state(s.status)}):'Outcome unknown. Do not retry installation; inspect the transaction first.');});});};
buttons[2].onclick=function(){var b=new PalmServiceBridge();b.onservicecallback=function(){b.cancel();};b.call('luna://com.webos.applicationManager/launch',JSON.stringify({id:'com.gathin.tvhome'}));};
document.addEventListener('keydown',function(e){if([37,38,39,40,13].indexOf(e.keyCode)<0)return;e.preventDefault();if(e.keyCode===13){if(!e.repeat)buttons[index].click();return;}var step=e.keyCode===37||e.keyCode===38?-1:1;for(var n=0;n<buttons.length;n++){index=(index+step+buttons.length)%buttons.length;if(!buttons[index].disabled){buttons[index].focus();break;}}});buttons.forEach(function(b,i){b.onfocus=function(){index=i;};b.onmouseover=function(){index=i;b.focus();};});buttons[0].focus();text('Reading status…');refresh();}());

});
