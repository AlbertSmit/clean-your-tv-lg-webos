'use strict';
module.exports = function (execute) {
  var busy = false;
  function valid(payload, boot) {
    if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return false;
    if (Object.keys(payload).some(function (key) { return key !== '$activity' && !(boot && key === 'reason'); })) return false;
    return !boot || (payload.reason === 'activity' && payload.$activity &&
      Number.isInteger(payload.$activity.activityId) && payload.$activity.activityId > 0);
  }
  function handler(command) {
    return async function (payload) {
      if (!valid(payload, command === 'boot')) return {returnValue:false,errorText:'Invalid recovery request'};
      if (busy) return {returnValue:false,errorText:'Recovery busy'};
      busy = true;
      try { return {returnValue:true,result:await execute(command)}; }
      catch (error) { return {returnValue:false,errorText:error.message}; }
      finally { busy = false; }
    };
  }
  return {boot:handler('boot'),status:handler('status'),restore:handler('restore')};
};
