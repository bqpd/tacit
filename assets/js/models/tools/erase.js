// Generated by CoffeeScript 1.4.0
(function() {
  var eraseTool, _base, _ref, _ref1;

  if ((_ref = window.tacit) == null) {
    window.tacit = {};
  }

  if ((_ref1 = (_base = window.tacit).tools) == null) {
    _base.tools = {};
  }

  eraseTool = {
    allowPan: true,
    name: "erase",
    mouseDown: function(easel, eventType, mouseLoc, object) {
      var idx, selection;
      this.allowPan = false;
      this.dragging = true;
      if (eventType !== "background") {
        if (eventType === "node") {
          selection = easel.pad.sketch.selectedNodes;
        } else {
          selection = easel.pad.sketch.selectedLinks;
        }
        idx = selection.indexOf(object);
        if (idx === -1) {
          selection.push(object);
        } else {
          selection.splice(idx, 1);
        }
        if (eventType === "node") {
          easel.pad.sketch.selectedNodes = selection;
        } else {
          easel.pad.sketch.selectedLinks = selection;
        }
        return easel.pad.sketch.slowDraw();
      }
    },
    mouseUp: function(easel, eventType, mouseLoc, object) {
      var link, node, _i, _j, _len, _len1, _ref2, _ref3;
      this.mouseDown(easel, eventType, mouseLoc, object);
      this.allowPan = true;
      this.dragging = false;
      _ref2 = easel.pad.sketch.selectedNodes;
      for (_i = 0, _len = _ref2.length; _i < _len; _i++) {
        node = _ref2[_i];
        node["delete"]();
      }
      _ref3 = easel.pad.sketch.selectedLinks;
      for (_j = 0, _len1 = _ref3.length; _j < _len1; _j++) {
        link = _ref3[_j];
        link["delete"]();
      }
      easel.pad.sketch.selectedLinks = [];
      easel.pad.sketch.selectedNodes = [];
      return easel.pad.sketch.updateDrawing();
    },
    mouseMove: function(easel, eventType, mouseLoc, object) {
      var idx, selection;
      if (this.dragging) {
        if (eventType !== "background") {
          if (eventType === "node") {
            selection = easel.pad.sketch.selectedNodes;
          } else {
            selection = easel.pad.sketch.selectedLinks;
          }
          idx = selection.indexOf(object);
          if (idx === -1) {
            selection.push(object);
          }
          if (eventType === "node") {
            easel.pad.sketch.selectedNodes = selection;
          } else {
            easel.pad.sketch.selectedLinks = selection;
          }
          return easel.pad.sketch.quickDraw();
        }
      }
    }
  };

  window.tacit.tools.erase = eraseTool;

}).call(this);
