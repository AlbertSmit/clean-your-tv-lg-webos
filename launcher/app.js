!function(){"use strict";function tr(s,p){return window.HomeI18n?HomeI18n.t(s,p):s.replace(/\{(\w+)\}/g,function(m,k){return p&&p[k]!==undefined?p[k]:m;});}function ht(s){return window.HomeI18n?HomeI18n.html(s):s;}var e,t=Math.max(1,CONFIG.columns||4),n=1696/t,a=13,i=461,o=[[5,tr("Good night")],[12,tr("Good morning")],[17,tr("Good afternoon")],[22,tr("Good evening")],[24,tr("Good night")]],r=["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"],s=["January","February","March","April","May","June","July","August","September","October","November","December"],l=function(e){return document.getElementById(e)},c=l("stage"),u=l("tiles"),d=l("glass"),f=l("hero"),p=[l("ambientA"),l("ambientB")],m=0,v=null,h=[l("btnInputs"),l("btnWifi"),l("btnSettings")],g=l("inputsPanel"),y=[],x="grid",L=0,b=0,C=0,w=[],M=0,E=!1,k=!1,I=null,T=[];function N(e,t,n){try{var a=new PalmServiceBridge;a.onservicecallback=function(e){var i;try{i=JSON.parse(e)}catch(e){i={returnValue:!1}}n&&n(i),t&&t.subscribe||T.splice(T.indexOf(a),1)},T.push(a),a.call(e,JSON.stringify(t||{}))}catch(e){n&&n({returnValue:!1,errorText:String(e)})}}function S(e,t,n){N("luna://com.webos.applicationManager/launch",{id:e,params:n||{}},function(n){!1===n.returnValue&&O(tr("Can't open {app}",{app:t||e}))})}function O(t){var n=l("toast");n.textContent=t,n.classList.add("shown"),clearTimeout(e),e=setTimeout(function(){n.classList.remove("shown")},2200)}function launchFirst(c,i,label){var o=c[i];if(!o){O(tr("Can't open {app}",{app:label}));return;}N("luna://com.webos.applicationManager/launch",{id:o.id,params:o.params||{}},function(r){if(!1===r.returnValue)launchFirst(c,i+1,label);});}function openNetworkSettings(){launchFirst([{id:"com.webos.app.firstuse-overlay",params:{target:"network"}},{id:"com.palm.app.settings",params:{target:"network"}},{id:"com.palm.app.settings",params:{}}],0,tr("Network settings"));}var V="tvhome.order";
// App editing uses the existing grid positions and focus highlight.
var library, hideButton, editHint, picker, pickerList, pickerStatus, pickerClose;
var pickerOpen=false, pickerGeneration=0, pickerIndex=0, pickerButtons=[];
var hideSelected=false, undoState=null, undoBar, undoButton, pointerTimer=null, suppressClick=false;
function screenIds(){return y.filter(function(item){return !item.add;}).map(function(item){return item.app.id;});}
function saveScreen(hidden){
 try{library.save(screenIds(),hidden||library.hidden());return true;}
 catch(error){O(tr("Couldn't save changes. Please try again."));return false;}
}
function rebuild(focusId){
 u.innerHTML="";y=library.visible().map(createTile);
 var el=document.createElement('div');el.className='item add-app';el.setAttribute('role','button');el.setAttribute('aria-label',tr('Add app'));
 el.innerHTML=ht('<div class="card"><svg viewBox="0 0 48 48" aria-hidden="true"><path d="M24 10v28M10 24h28"/></svg></div><div class="name">Add app</div>');
 var item={add:true,app:{title:tr('Add app')},el:el,color:[100,110,125]};
 el.addEventListener('mouseover',function(){if(!I&&!pickerOpen&&!undoState)j(y.length-1);});
 el.addEventListener('click',function(){if(!I)openPicker();});u.appendChild(el);y.push(item);
 F();y.forEach(function(tile){tile.el.classList.add('shown');});
 x='none';j(Math.max(0,y.findIndex(function(tile){return tile.app.id===focusId;})));
}
function activateTile(item){if(item.add)openPicker();else S(item.app.id,item.app.title);}
function cancelHold(){clearTimeout(ee);ee=null;clearTimeout(pointerTimer);pointerTimer=null;Z=false;}
function beginMoving(item){
 if(!item||item.add||I||pickerOpen||undoState)return;
 I={item:item,snapshot:y.slice()};item.el.classList.add('moving');document.body.classList.add('editing');
 hideButton.hidden=false;editHint.hidden=false;hideButton.classList.remove('focused');hideSelected=false;j(y.indexOf(item));
}
function pointerMove(item){if(!I||item.add)return;hideSelected=false;hideButton.classList.remove('focused');Q(y.indexOf(item));}
function bindHold(item){
 item.el.addEventListener('mousedown',function(event){
  if(event.button!==0||I||pickerOpen||undoState)return;
  j(y.indexOf(item));clearTimeout(pointerTimer);suppressClick=false;
  pointerTimer=setTimeout(function(){pointerTimer=null;suppressClick=true;beginMoving(item);},600);
 });
 item.el.addEventListener('mouseleave',function(){clearTimeout(pointerTimer);pointerTimer=null;});
}
function tileClick(item){
 if(suppressClick){suppressClick=false;return;}
 if(pickerOpen||undoState)return;
 if(I){pointerMove(item);U(true);}else activateTile(item);
}
function selectHide(){if(!I)return;hideSelected=true;hideButton.classList.add('focused');hideButton.focus();}
function hideApp(){
 if(!I)return;
 var item=I.item, snapshot=I.snapshot.slice(), oldHidden=library.hidden();
 var previous=y.slice();y=y.filter(function(tile){return tile!==item;});
 if(!saveScreen(oldHidden.concat(item.app.id))){y=previous;return;}
 I=null;hideSelected=false;item.el.classList.remove('moving');document.body.classList.remove('editing');hideButton.hidden=true;editHint.hidden=true;
 item.el.remove();F();x='none';j(Math.min(L,y.length-1));
 undoState={ids:snapshot.filter(function(tile){return !tile.add;}).map(function(tile){return tile.app.id;}),hidden:oldHidden,id:item.app.id};
 undoBar.hidden=false;undoButton.focus();
}
function dismissUndo(){if(!undoState)return;undoState=null;undoBar.hidden=true;j(L);}
function undoHide(){
 if(!undoState)return;
 try{var id=undoState.id;library.save(undoState.ids,undoState.hidden);dismissUndo();rebuild(id);}
 catch(error){O(tr("Couldn't restore app. Please try again."));}
}
function closePicker(){
 if(!pickerOpen)return;
 pickerOpen=false;pickerGeneration++;picker.hidden=true;cancelHold();x='none';j(y.length-1);
}
function focusPicker(index){
 pickerIndex=Math.max(0,Math.min(index,pickerButtons.length-1));
 pickerButtons[pickerIndex].focus();pickerButtons[pickerIndex].scrollIntoView({block:'nearest'});
}
function renderPicker(apps){
 pickerList.innerHTML='';pickerButtons=[];
 apps.forEach(function(app){
  var button=document.createElement('button');button.className='app-choice';button.dataset.appId=app.id;
  var icon=document.createElement('img');icon.src=app.icon||'';icon.alt='';icon.onerror=function(){icon.style.visibility='hidden';};
  var title=document.createElement('span');title.textContent=app.title;button.appendChild(icon);button.appendChild(title);
  button.addEventListener('focus',function(){pickerIndex=pickerButtons.indexOf(button);});
  button.addEventListener('click',function(){
   try{library.add(app.id);closePicker();rebuild(app.id);O(tr('{app} added',{app:app.title}));}
   catch(error){pickerStatus.textContent=tr("Couldn't save changes. Please try again.");}
  });pickerList.appendChild(button);pickerButtons.push(button);
 });
 pickerButtons.push(pickerClose);focusPicker(0);
}
function openPicker(){
 if(I||pickerOpen)return;
 dismissUndo();cancelHold();pickerOpen=true;var generation=++pickerGeneration;
 picker.hidden=false;pickerStatus.textContent=tr('Checking installed apps…');pickerList.innerHTML='';pickerButtons=[pickerClose];focusPicker(0);_('picker');
 AppLibrary.installed(function(apps){
  if(!pickerOpen||generation!==pickerGeneration)return;
  if(apps!==null)library.refresh(apps);
  var choices=library.available();
  pickerStatus.textContent=apps===null?tr('Showing the saved list. Could not refresh apps from the TV.'):choices.length?tr('Choose an app to add to Home.'):tr('All installed apps are already on Home.');
  renderPicker(choices);
 });
}
function initializeApps(){
 library=AppLibrary.create(localStorage,window.TV_APPS&&TV_APPS.apps||[],CONFIG);
 hideButton=document.createElement('button');hideButton.id='hideApp';hideButton.hidden=true;
 hideButton.innerHTML=ht('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3l18 18M10 5.2c5.5-1 10 6.8 10 6.8a20 20 0 0 1-3 3M6 6C3.4 8 2 12 2 12s4 7 10 7c1.4 0 2.7-.4 4-1M9 9a4.2 4.2 0 0 0 6 6"/></svg><span>Hide from Home</span>');
 hideButton.addEventListener('mouseover',selectHide);hideButton.addEventListener('click',hideApp);document.body.appendChild(hideButton);
 editHint=document.createElement('div');editHint.id='editHint';editHint.hidden=true;editHint.textContent=tr('← ↑ ↓ → Move   ·   OK Place   ·   Back Cancel   ·   ↓ Below last row to hide');document.body.appendChild(editHint);
 undoBar=document.createElement('div');undoBar.id='appUndo';undoBar.hidden=true;undoBar.setAttribute('role','status');
 var message=document.createElement('span');message.textContent=tr('App hidden. Add it back with +.');undoBar.appendChild(message);
 undoButton=document.createElement('button');undoButton.textContent=tr('Undo');undoButton.addEventListener('click',undoHide);undoBar.appendChild(undoButton);document.body.appendChild(undoBar);
 picker=document.createElement('section');picker.id='appPicker';picker.hidden=true;picker.setAttribute('role','dialog');picker.setAttribute('aria-modal','true');picker.setAttribute('aria-labelledby','appPickerTitle');
 picker.innerHTML=ht('<div class="app-picker-card"><h2 id="appPickerTitle">Add app</h2><p id="appPickerStatus" role="status"></p><div id="appPickerList"></div><button id="appPickerClose">Back to Home</button></div>');
 document.body.appendChild(picker);pickerList=l('appPickerList');pickerStatus=l('appPickerStatus');pickerClose=l('appPickerClose');pickerClose.addEventListener('click',closePicker);
 document.addEventListener('mouseup',function(){clearTimeout(pointerTimer);pointerTimer=null;setTimeout(function(){suppressClick=false;},0);});
 window.addEventListener('blur',cancelHold);
 document.addEventListener('visibilitychange',function(){if(document.hidden){cancelHold();if(I)U(false);}});
 document.addEventListener('keydown',function(event){
  var key=event.keyCode;
  if(pickerOpen){
   event.preventDefault();event.stopImmediatePropagation();
   if(key===27||key===461)closePicker();
   else if(key===13&&!event.repeat)pickerButtons[pickerIndex].click();
   else if(key===38||key===37)focusPicker(pickerIndex-1);
   else if(key===40||key===39)focusPicker(pickerIndex+1);
   else if(key===9)focusPicker((pickerIndex+(event.shiftKey?-1:1)+pickerButtons.length)%pickerButtons.length);
  }else if(undoState){
   event.preventDefault();event.stopImmediatePropagation();
   if(key===13&&!event.repeat)undoHide();else if(key===27||key===461||key>=37&&key<=40)dismissUndo();
  }else if(I&&hideSelected){
   event.preventDefault();event.stopImmediatePropagation();
   if(key===13&&!event.repeat)hideApp();
   else if(key===27||key===461)U(false);
   else if(key===38){hideSelected=false;hideButton.classList.remove('focused');hideButton.blur();j(L);}
  }
 },true);
 document.addEventListener('keyup',function(event){if(pickerOpen||undoState||hideSelected){cancelHold();event.stopImmediatePropagation();}},true);
 rebuild();
}

function createTile(e){var t=document.createElement("div");t.className="item",t.dataset.appId=e.id,t.setAttribute("role","button"),t.setAttribute("aria-label",e.title);var n=document.createElement("div");n.className="card";var a=document.createElement("img"),i={app:e,el:t,card:n,color:null};a.onload=function(){!function(e,t){var n=null,a=null;try{var i=document.createElement("canvas");i.width=12,i.height=12;var o=i.getContext("2d");o.drawImage(t,0,0,12,12),n=o.getImageData(0,0,12,12).data,a=function(e){var t=e.naturalWidth,n=e.naturalHeight,a=document.createElement("canvas");a.width=t,a.height=n;var i=a.getContext("2d");i.drawImage(e,0,0);var o=i.getImageData(2,2,1,1).data;return o[3]>200?o:i.getImageData(2,Math.floor(n/2),1,1).data}(t)}catch(e){}var r=null;a&&a[3]>200?e.card.style.background="rgb("+a[0]+","+a[1]+","+a[2]+")":(e.card.classList.add("glyph"),e.card.style.background=D(e.app.iconColor),r="#2c2c2e"===D(e.app.iconColor)?null:B(e.app.iconColor)),e.color=r||(n?function(e){for(var t=null,n=-1,a=[0,0,0],i=0,o=0;o<e.length;o+=4)if(!(e[o+3]<128)){var r=[e[o],e[o+1],e[o+2]];a[0]+=r[0],a[1]+=r[1],a[2]+=r[2],i++;var s=W(r),l=s[1]*Math.min(1,1.4*s[2]);l>n&&(n=l,t=r)}if(!i)return[68,68,68];if(n<.25){var c=W([a[0]/i,a[1]/i,a[2]/i]);return c[2]=Math.max(c[2],.55),J(c)}var u=W(t);return u[1]=Math.min(1,1.1*u[1]),u[2]=Math.max(.5,u[2]),J(u)}(n):B(e.app.iconColor)),y[L]===e&&z(e.color)}(i,a)},a.onerror=function(){a.style.display="none";n.classList.add("missing-icon");n.setAttribute("data-initial",e.title.charAt(0))},a.src=e.icon||"missing-icon",n.appendChild(a),t.appendChild(n);var o=document.createElement("div");return o.className="name",o.textContent=e.title,t.appendChild(o),t.addEventListener("mouseover",function(){"inputs"===x||pickerOpen||undoState||(I?pointerMove(i):j(y.indexOf(i)))}),t.addEventListener("click",function(){tileClick(i)}),bindHold(i),u.appendChild(t),i}
function A(e){return Math.floor(e/t)}function G(e){return 112+e%t*n+(n-360)/2}function H(e){var t=A(e);return 708+292*t+(t>0?36:0)}function F(){y.forEach(function(e,t){u.appendChild(e.el),e.el.style.left=G(t)+"px",e.el.style.top=H(t)+"px",e.el.classList.toggle("dock",0===A(t))});var e=l("dockBand"),a=Math.min(t,y.length);e.style.display=a?"block":"none",e.style.left=G(0)-28+"px",e.style.top="680px",e.style.width=(a-1)*n+360+56+"px",e.style.height="258px"}function P(){y.forEach(function(e,t){e.el.classList.remove("shown"),setTimeout(function(){e.el.classList.add("shown")},60+40*Math.min(t,16))})}function D(e){var t=B(e);if(!t)return"#2c2c2e";var n=W(t);return n[1]<.15&&(n[2]>.85||n[2]<.1)?"#2c2c2e":"rgb("+t.join(",")+")"}function B(e){var t=/^#?([0-9a-f]{6})$/i.exec(e||"");if(!t)return null;var n=parseInt(t[1],16);return[n>>16&255,n>>8&255,255&n]}function W(e){var t=e[0]/255,n=e[1]/255,a=e[2]/255,i=Math.max(t,n,a),o=i-Math.min(t,n,a),r=0;return o&&(r=i===t?(n-a)/o%6:i===n?(a-t)/o+2:(t-n)/o+4,(r*=60)<0&&(r+=360)),[r,i?o/i:0,i]}function J(e){var t=e[0],n=e[1],a=e[2],i=a*n,o=i*(1-Math.abs(t/60%2-1)),r=a-i;return(t<60?[i,o,0]:t<120?[o,i,0]:t<180?[0,i,o]:t<240?[0,o,i]:t<300?[o,0,i]:[i,0,o]).map(function(e){return Math.round(255*(e+r))})}function j(e){if(y.length){e=Math.max(0,Math.min(e,y.length-1)),_("grid"),y[L]&&y[L].el.classList.remove("focused"),L=e,y[e].el.classList.add("focused");var t=H(e),n=A(e);0===n&&!I?M=0:(t-M+202+70>(I?850:1060)&&(M=t+202+70-(I?850:1060)),t-M-24<80&&(M=t-24-80)),c.style.transform="translateY("+-M+"px)";var a=document.querySelector("header"),i=a.offsetTop+a.offsetHeight;document.body.classList.toggle("scrolled",680-M<i+24);var o=1.1*360+24,r=1.1*202+24,s=G(e)+180-o/2,l=t+101-r/2;d.style.width=o+"px",d.style.height=r+"px",d.style.transform="translate("+s+"px,"+l+"px)",k||(d.style.transition="none",d.offsetWidth,d.style.transition="",d.style.opacity="1",k=!0),0===n?function(e){var t=e.app.title;f.style.top="532px",E?f.textContent!==t&&(f.style.opacity="0",f.style.transform="translateX(-24px)",clearTimeout(f.swap),f.swap=setTimeout(function(){f.textContent=t,f.style.transition="none",f.style.transform="translateX(24px)",f.offsetWidth,f.style.transition="",f.style.transform="none",f.style.opacity="1"},120)):(f.textContent=t,f.style.transform="none",f.style.opacity="1",E=!0),z(e.color)}(y[e]):E&&(E=!1,f.style.opacity="0"),z(y[e].color)}}function z(e){if(e){var t=e.join(",");if(t!==v){v=t;var n=p[1-m];n.style.background="radial-gradient(circle 1190px at 32% 42%, rgba("+t+",0.36) 0%, rgba("+t+",0.15) 50%, rgba("+t+",0) 100%)",n.style.opacity="1",p[m].style.opacity="0",m=1-m}}}function R(e){_("top"),document.body.classList.remove("scrolled"),h[b].classList.remove("focused"),b=Math.max(0,Math.min(e,h.length-1)),h[b].classList.add("focused")}function _(e){x!==e&&("top"===x&&h[b].classList.remove("focused"),"grid"===x&&(y[L]&&y[L].el.classList.remove("focused"),k=!1,d.style.opacity="0"),x=e)}function X(){var now=new Date,hour=now.getHours();for(var idx=0;idx<o.length;idx++)if(hour<o[idx][0]){l("greeting").textContent=o[idx][1];break;}if(window.HomeI18n){l("clock").textContent=HomeI18n.formatTime(now);l("ampm").textContent="";l("date").textContent=HomeI18n.formatDate(now);}else{l("clock").textContent=(hour%12||12)+":"+("0"+now.getMinutes()).slice(-2);l("ampm").textContent=hour<12?"am":"pm";l("date").textContent=r[now.getDay()]+"  "+now.getDate()+" "+s[now.getMonth()];}}function q(e){0===e?function(){if(g.innerHTML="",w=[],(window.TV_APPS&&TV_APPS.inputs||[]).forEach(function(e){K("M18,7V4c0,-1.1 -0.9,-2 -2,-2H8C6.9,2 6,2.9 6,4v3H5v6l3,6v3h8v-3l3,-6V7H18zM8,4h8v3h-2V5h-1v2h-2V5h-1v2H8V4z",e.label,e.appId)}),CONFIG.liveTvApp&&(w.length&&g.appendChild(Object.assign(document.createElement("div"),{className:"separator"})),K("M21,6h-7.59l3.29,-3.29L16,2l-4,4l-4,-4l-0.71,0.71L10.59,6H3c-1.1,0 -2,0.89 -2,2v12c0,1.1 0.9,2 2,2h18c1.1,0 2,-0.89 2,-2V8C23,6.89 22.1,6 21,6zM21,20H3V8h18V20zM9,10v8l7,-4L9,10z",tr("Live TV"),CONFIG.liveTvApp)),w.length){var e=h[0].getBoundingClientRect();g.style.left=e.left+"px",g.style.top=e.bottom+20+"px",g.style.minWidth=Math.max(e.width,300)+"px",g.classList.remove("hidden"),h[b].classList.remove("focused"),x="inputs",Y(0)}else O(tr("No inputs found"))}():1===e?openNetworkSettings():window.RenewalPanel.open()}function K(e,t,n){var a=document.createElement("div");a.className="inputRow",a.innerHTML=ht('<svg viewBox="0 0 24 24"><path d="')+e+'"/></svg>',a.appendChild(document.createTextNode(t));var i=w.length;a.addEventListener("mouseover",function(){Y(i)}),a.addEventListener("click",function(){$(),S(n,t)}),a.appId=n,a.label=t,w.push(a),g.appendChild(a)}function Y(e){w[C]&&w[C].classList.remove("focused"),C=Math.max(0,Math.min(e,w.length-1)),w[C].classList.add("focused")}function $(){g.classList.add("hidden"),x="none",R(0)}function Q(e){e<0||e>=y.length-1||e===L||(y.splice(e,0,y.splice(L,1)[0]),L=e,F(),j(e))}function U(commit){
 var item=I.item;
 if(commit&&!saveScreen())return;
 if(!commit)y=I.snapshot;
 I=null;item.el.classList.remove("moving");document.body.classList.remove("editing");
 hideSelected=false;hideButton.hidden=true;editHint.hidden=true;F();j(y.indexOf(item));
}var Z=!1,ee=null;function te(){cancelHold();closePicker();dismissUndo();I&&U(!1),X(),"inputs"===x&&g.classList.add("hidden"),h.forEach(function(e){e.classList.remove("focused")}),x="none",P(),j(L)}document.addEventListener("keyup",function(e){if(window.RenewalPanel&&window.RenewalPanel.isOpen()){Z=!1;return;}if(e.keyCode===a&&(Z=!1,ee)){clearTimeout(ee),ee=null;var t=y[L];"grid"===x&&t&&!I&&activateTile(t)}}),document.addEventListener("keydown",function(e){var n=e.keyCode;if(n!==a&&ee)cancelHold();if(n===a&&Z)e.preventDefault();else{if(n===a&&(Z=!0),I)if(37===n)Q(L-1);else if(39===n)Q(L+1);else if(38===n)Q(L-t);else if(40===n){if(A(L)>=A(y.length-2))selectHide();else Q(Math.min(L+t,y.length-2))}else if(n===a)U(!0);else{if(n!==i&&27!==n)return;U(!1)}else if("inputs"===x)if(38===n)Y(C-1);else if(40===n)Y(C+1);else if(n===a){var o=w[C];$(),S(o.appId,o.label)}else{if(n!==i&&27!==n&&37!==n&&39!==n)return;$()}else if("top"===x){if(37===n)R(b-1);else if(39===n)R(b+1);else if(40===n)j(0===A(L)?L:0);else if(n===a)q(b);else if(n!==i)return}else{var r=L%t,s=y.length-1;if(37===n)r>0&&j(L-1);else if(39===n)r<t-1&&L<s&&j(L+1);else if(38===n)0===A(L)?R((l=G(L)+180,c=0,u=1/0,h.forEach(function(e,t){var n=e.getBoundingClientRect(),a=Math.abs(n.left+n.width/2-l);a<u&&(u=a,c=t)}),c)):j(L-t);else if(40===n)A(L)<A(s)&&j(Math.min(L+t,s));else if(n===a)ee=setTimeout(function(){ee=null;beginMoving(y[L])},600);else if(n!==i)return}var l,c,u;e.preventDefault()}});h.forEach(function(e,t){e.addEventListener("mouseover",function(){"inputs"!==x&&!I&&!pickerOpen&&!undoState&&R(t)}),e.addEventListener("click",function(){if(!I&&!pickerOpen&&!undoState)q(t)})}),document.addEventListener("webOSRelaunch",te),document.addEventListener("visibilitychange",function(){document.hidden||te()}),initializeApps(),F(),X(),setInterval(X,1e4),N("luna://com.palm.connectionmanager/getStatus",{subscribe:!0},function(e){if(!1!==e.returnValue||e.wifi||e.wired){var t="Wi-Fi";e.wired&&"connected"===e.wired.state?t=tr("Ethernet"):e.wifi&&"connected"===e.wifi.state?t=e.wifi.ssid||"Wi-Fi":!1===e.isInternetConnectionAvailable&&(t=tr("Offline")),l("wifiLabel").textContent=t}}),P(),x="none",j(0);window.RootLauncherRendered=true;}();