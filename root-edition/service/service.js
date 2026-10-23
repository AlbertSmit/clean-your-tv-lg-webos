'use strict';
var Service = require('webos-service');
var execFile = require('child_process').execFile;
var service = new Service('com.cleanyourtv.root.preview.service');
var runtime = '/var/lib/clean-your-tv-root/runtime/cli.py';
var handlers = require('./handlers')(function (command, transaction) {
  return new Promise(function (resolve, reject) {
    if (process.getuid() !== 0) return reject(new Error('Root recovery service required'));
    if (['boot', 'status', 'restore', 'enable', 'confirm'].indexOf(command) === -1) return reject(new Error('Unknown operation'));
    var executable = command === 'boot' ? '/bin/sh' : '/usr/bin/python3';
    var args = command === 'boot' ? [__dirname + '/boot-recover.sh'] : [runtime, command];
    if (command === 'confirm') args.push(transaction);
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
// Activity registration belongs to the root installer, not the web service.
