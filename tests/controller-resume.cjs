const fs=require('fs'),vm=require('vm'),a=require('node:assert/strict'),E=require('events');
function run(baseline){let now=1000,interval,watch,worker;const calls=[],logs=[],timeouts=[];
 function Service(){this.register=()=>{};this.activityManager={create(){}};this.call=(uri,p,cb)=>{if(uri.endsWith('/launch'))calls.push(p.id);cb({payload:{returnValue:true,state:{enabled:true,schema:3}}});};}
 const fakefs={existsSync:()=>false,writeFileSync(){},chmodSync(){},unlinkSync(){},readFileSync:()=> '{}',appendFileSync:(p,s)=>logs.push(JSON.parse(s))};
 const child=()=>{let c=new E();c.pid=12;c.stdout=new E();c.stderr=new E();c.stdin=new E();c.stdin.write=()=>{};c.stdin.end=()=>{};return c;};
 const context={console,Buffer,require(name){if(name==='fs')return fakefs;if(name==='child_process')return{spawn(){return worker=child()}};if(name==='/usr/lib/node_modules/webos-service')return Service;if(name==='./screen-watch')return(d,l,fg,reset,power)=>{watch={fg,reset,power};return{close(){}}};if(name==='./resume-policy')return require('../native/app/resume-policy');return require('../native/app/'+name.slice(2));},process:{argv:['node','app','{"nativeHomeAuto":true}'],pid:1,getuid:()=>5431,hrtime:()=>[Math.floor(now/1000),(now%1000)*1e6],on(){},exit(){throw Error('unexpected exit')}},setTimeout(fn,ms){timeouts.push({fn,ms});return 1},clearTimeout(){},setInterval(fn){interval=fn;return 2},clearInterval(){}};
 let code=fs.readFileSync(require('path').join(__dirname,'../native/app/native.js'),'utf8');if(baseline)code=code.replace('!shouldResumeLaunch(lastForeground)','false');vm.runInNewContext(code,context);
 timeouts.find(t=>t.ms===0).fn();worker.stdout.emit('data',Buffer.from('READY\n'));
 watch.fg('com.gathin.tvhome');watch.power({state:'Active'});interval();const before=calls.length;
 watch.power({state:'Active Standby'});watch.fg('com.webos.app.cpcover');watch.fg('');watch.fg('com.gathin.tvhome');watch.power({state:'Active'});now+=400;interval();
 return{extra:calls.length-before,logs};
}
a.equal(run(true).extra,1);
a.equal(run(false).extra,0);
console.log('PASS: controller replay reproduces duplicate in baseline, suppresses it in candidate');
