const a=require('node:assert/strict'),make=require('../app/screen-policy');
const home='com.webos.app.home',app='com.example.video';
let p=make([app]);
a.equal(p.next(home),false); // Initial LG screen is not an exit.
a.equal(p.next(app),false);
a.equal(p.next(app),false); // Internal navigation and cancelled exit.
a.equal(p.next(home),true);
a.equal(p.next(home),false); // One attempt, no launch loop.
p.next(app);p.next('com.webos.app.hdmi1');a.equal(p.next(home),false);
p.next(app);p.reset();a.equal(p.next(home),false); // Reconnect loses stale state.
p.next(app);p.next('com.gathin.tvhome');a.equal(p.next(home),false);
console.log('PASS: exit transitions, internal Back, HDMI, reconnect and duplicate events');
p.reset();p.next(app,100);p.next('',200);a.equal(p.next(home,1300),true);
p.reset();p.next(app,100);p.next('',200);p.next('',2200);a.equal(p.next(home,2800),false);
p.reset();p.next(app,100);p.next('',200);p.next('com.webos.app.hdmi1',300);a.equal(p.next(home,400),false);
console.log('PASS: bounded empty foreground gap and unrelated transitions');
