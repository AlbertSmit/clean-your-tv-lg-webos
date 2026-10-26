'use strict';
module.exports = function (uid, execute) {
  var busy = false;
  function valid(payload, key, values) {
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return false;
    var keys = Object.keys(payload);
    return key ? keys.length === 1 && keys[0] === key && values.indexOf(payload[key]) >= 0 : keys.length === 0;
  }
  function handler(key, values, command) {
    return async function (payload) {
      if (uid() !== 0 || !valid(payload, key, values)) return {returnValue:false,errorCode:'invalid'};
      // Disabling policy and status must remain available during a reset.
      var mutating = command === 'recover';
      if (mutating && busy) return {returnValue:false,errorCode:'busy'};
      if (mutating) busy = true;
      try {
        return await execute(command === 'recover' ? payload.operation :
          command === 'configure' ? payload.enabled ? 'enable' : 'disable' : 'status');
      } catch (_) { return {returnValue:false,errorCode:'unavailable'}; }
      finally { if (mutating) busy = false; }
    };
  }
  return {
    audioRecoveryStatus:handler(null, null, 'status'),
    setAudioRecoveryEnabled:handler('enabled', [true, false], 'configure'),
    recoverAudio:handler('operation', ['restart-earc', 'restore-hdmi', 'restore-setting'], 'recover')
  };
};
