/* Local, per-document startup timings. No storage, payloads or uploads. */
(function (root) {
  'use strict';
  var names = ['firstJS', 'languageReply', 'languageReady', 'profileGateStart',
    'profileGateComplete', 'profileGateBlocked', 'appStart', 'gridCreated',
    'inventoryRefreshStart', 'inventoryRefreshComplete', 'firstPaintProxy',
    'firstHandledKey', 'widgetsCreated', 'widgetDataFirst'];
  var clock = root.performance && typeof root.performance.now === 'function' ?
    function () { return root.performance.now(); } : function () { return Date.now(); };
  var start = clock(), marks = {firstJS: 0}, paintScheduled = false;
  function mark(name) {
    if (names.indexOf(name) < 0 || Object.prototype.hasOwnProperty.call(marks, name)) return;
    marks[name] = Math.max(0, clock() - start);
  }
  root.HomeStartup = {
    mark: mark,
    snapshot: function () {
      var copy = {};
      Object.keys(marks).forEach(function (name) { copy[name] = marks[name]; });
      return copy;
    },
    // Two frame callbacks are only a rendering opportunity, never proof of paint.
    paintProxy: function () {
      if (paintScheduled) return;
      paintScheduled = true;
      function frame(callback) {
        if (root.requestAnimationFrame) root.requestAnimationFrame(callback);
        else root.setTimeout(callback, 16);
      }
      frame(function () { frame(function () { mark('firstPaintProxy'); }); });
    }
  };
}(window));
