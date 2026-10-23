'use strict';
var Service = require('webos-service');
var execFile = require('child_process').execFile;
var service = new Service('com.cleanyourtv.root.preview.service');
var runtime = '/var/lib/clean-your-tv-root/runtime/cli.py';
var handlers = require('./handlers')(function (command) {
  return new Promise(function (resolve, reject) {
    if (process.getuid() !== 0) return reject(new Error('Root recovery service required'));
    if (['boot', 'status', 'restore'].indexOf(command) === -1) return reject(new Error('Unknown operation'));
    var executable = command === 'boot' ? '/bin/sh' : '/usr/bin/python3';
    var args = command === 'boot' ? [__dirname + '/boot-recover.sh'] : [runtime, command];
    execFile(executable, args, {timeout:command === 'restore' ? 600000 : 30000,maxBuffer:65536}, function (error, stdout) {
      if (error) return reject(new Error('Recovery operation failed; inspect runtime status'));
      try { resolve(JSON.parse(stdout)); } catch (_) { reject(new Error('Invalid runtime response')); }
    });
  });
});
Object.keys(handlers).forEach(function (method) {
  service.register(method, function (message) {
    handlers[method](message.payload).then(function (result) { result.root = process.getuid() === 0; message.respond(result); });
  });
});
// webos-service manages ActivityManager callback completion. Administrative
// registration is restricted to the fixed recovery activity below.
var activity = require('./activity.json');
function call(uri, payload) {
  return new Promise(function (resolve, reject) {
    service.call(uri, payload, function (reply) {
      if (!reply.payload || reply.payload.returnValue !== true) return reject(new Error('ActivityManager operation failed'));
      resolve(reply.payload);
    });
  });
}
function canonical(value) {
  if (Array.isArray(value)) return value.map(canonical);
  if (value && typeof value === 'object') {
    var result = {};
    Object.keys(value).sort().forEach(function(key){result[key] = canonical(value[key]);});
    return result;
  }
  return value;
}
function equal(a,b) { return JSON.stringify(canonical(a)) === JSON.stringify(canonical(b)); }
function owned(item) {
  return item && item.name === activity.name && item.creator &&
    item.creator.serviceId === 'com.cleanyourtv.root.preview.service' &&
    item.callback && item.callback.method === activity.callback.method &&
    equal(item.callback.params, activity.callback.params) &&
    equal(item.trigger, activity.trigger) &&
    item.type && item.type.persist === true && item.type.continuous === true && item.type.foreground === true;
}
['register','unregister'].forEach(function (method) {
  service.register(method, function (message) {
    Promise.resolve().then(async function () {
      if (process.getuid() !== 0) throw new Error('Root recovery service required');
      if (!message.payload || Object.keys(message.payload).some(function(k){return k !== '$activity';})) throw new Error('Empty request required');
      var listing = await call('luna://com.webos.service.activitymanager/list', {details:true});
      if (!Array.isArray(listing.activities)) throw new Error('Unexpected activity list');
      var matches = listing.activities.filter(function(a){return a.name === activity.name;});
      if (matches.length > 1 || (matches.length === 1 && !owned(matches[0]))) throw new Error('Activity ownership conflict');
      if (method === 'register' && !matches.length) await call('luna://com.webos.service.activitymanager/create', {activity:activity,start:true,replace:false});
      if (method === 'unregister' && matches.length) await call('luna://com.webos.service.activitymanager/cancel', {activityId:matches[0].activityId});
      var check = await call('luna://com.webos.service.activitymanager/list', {details:true});
      if (!Array.isArray(check.activities)) throw new Error('Unexpected activity list');
      var found = check.activities.filter(function(a){return a.name === activity.name;});
      if (method === 'register' ? found.length !== 1 || !owned(found[0]) : found.length !== 0) throw new Error('Activity verification failed');
      return {returnValue:true,root:true,registered:method === 'register',activityName:activity.name};
    }).then(function(result){message.respond(result);},function(error){message.respond({returnValue:false,errorText:error.message});});
  });
});
