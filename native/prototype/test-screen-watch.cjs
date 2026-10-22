const fs=require('fs'),vm=require('vm'),a=require('node:assert/strict'),{EventEmitter}=require('events');
const source=fs.readFileSync(require.resolve('../app/screen-watch'),'utf8');
function setup(withPower){
 let seq=0,timers=new Map(),logs=[],events=[],power=[],resets=0;
 class WS extends EventEmitter{
  constructor(url,opts){super();this.url=url;this.sent=[];WS.last=this;}
  send(v){this.sent.push(JSON.parse(v));}
  terminate(){if(!this.ended){this.ended=true;this.emit('close',1006);}}
  ping(){this.pings=(this.pings||0)+1;}
 }
 const sandbox={module:{exports:{}},require(n){return n==='fs'?{readFileSync:()=>'{"key":"private-test-key"}'}:n==='os'?{networkInterfaces:()=>({lo:[{internal:true,family:'IPv4',address:'127.0.0.1'}],wlan:[{internal:false,family:'IPv4',address:'192.0.2.50'}]})}:WS;},setTimeout(f,ms){timers.set(++seq,{f,ms});return seq;},clearTimeout(i){timers.delete(i);},setInterval(f,ms){timers.set(++seq,{f,ms,interval:true});return seq;},clearInterval(i){timers.delete(i);}};
 vm.runInNewContext(source,sandbox);
 let watcher=sandbox.module.exports('/state',x=>logs.push(x),x=>events.push(x),()=>resets++,withPower?x=>power.push(x):undefined);
 return {watcher,WS,logs,events,power,timers,resets:()=>resets};
}
let t=setup(),s=t.WS.last;
a.equal(s.url,'wss://192.0.2.50:3001');s.emit('open');
a.equal(s.sent[0].payload['client-key'],'private-test-key');
s.emit('message',JSON.stringify({type:'registered'}));
a.equal(s.sent[1].type,'subscribe');
s.emit('message',JSON.stringify({id:'foreground',type:'response',payload:{appId:'app'}}));
a.deepEqual(t.events,['app']);
a.equal([...t.timers.values()].filter(x=>x.interval).length,1);
t.watcher.close();s.emit('message',JSON.stringify({id:'foreground',payload:{appId:'com.webos.app.home'}}));
a.deepEqual(t.events,['app']);a.equal(t.timers.size,0);
a.equal(JSON.stringify(t.logs).includes('private-test-key'),false);
t=setup();s=t.WS.last;s.emit('message',JSON.stringify({type:'error',error:'401 insufficient permissions'}));a.equal(t.timers.size,0);
t=setup();s=t.WS.last;s.terminate();a.equal([...t.timers.values()][0].ms,10000);
console.log('PASS: local endpoint, registration, subscription, stop, key redaction, permanent error, reconnect');

t=setup(true);s=t.WS.last;s.emit('message',JSON.stringify({type:'registered'}));
a.equal(s.sent[1].id,'power');
s.emit('message',JSON.stringify({id:'power',type:'response',payload:{returnValue:true,state:'Active Standby'}}));
a.equal(t.power[0].state,'Active Standby');
s.emit('message',JSON.stringify({id:'power',type:'error',error:'403 access denied'}));a.equal(s.ended,undefined);
t.watcher.close();s.emit('message',JSON.stringify({id:'power',payload:{state:'Active'}}));a.equal(t.power.length,1);
console.log('PASS: power subscription, isolated permission failure, stopped power callback');
