// Generated by CoffeeScript 1.4.0
(function() {
  var atan2, max, moveTool, sin, sqr, sqrt, _base, _ref, _ref1,
    __slice = [].slice;

  if ((_ref = window.tacit) == null) {
    window.tacit = {};
  }

  if ((_ref1 = (_base = window.tacit).tools) == null) {
    _base.tools = {};
  }

  sqr = function(a) {
    return Math.pow(a, 2);
  };

  sqrt = function(a) {
    return Math.sqrt(a);
  };

  max = function() {
    var n;
    n = 1 <= arguments.length ? __slice.call(arguments, 0) : [];
    return Math.max.apply(Math, n);
  };

  sin = function(a) {
    return Math.sin(a);
  };

  atan2 = function(a, b) {
    return Math.atan2(a, b);
  };

  moveTool = {
    allowPan: true,
    name: "move",
    mouseDown: function(easel, eventType, mouseLoc, object) {
      var idx;
      if (eventType === "node") {
        this.selection = object;
        this.selectiontype = "node";
        this.allowPan = false;
        this.dragstart = true;
        idx = easel.pad.sketch.selectedNodes.indexOf(object);
        if (idx === -1) {
          easel.pad.sketch.selectedNodes.push(object);
        }
        return easel.pad.sketch.quickDraw();
      } else if (eventType === "beam") {
        this.selection = object;
        this.selectiontype = "beam";
        this.allowPan = false;
        this.dragstart = {
          x: mouseLoc[0],
          y: mouseLoc[1],
          size: object.size
        };
        easel.pad.sketch.selectedLinks = [this.selection];
        return easel.pad.sketch.slowDraw();
      }
    },
    mouseUp: function(easel, eventType, mouseLoc, object) {
      var idx;
      if (this.selectiontype === "node") {
        idx = easel.pad.sketch.selectedNodes.indexOf(this.selection);
        easel.pad.sketch.selectedNodes.splice(idx, 1);
        easel.pad.sketch.quickDraw();
        this.allowPan = true;
      } else if (this.selectiontype === "beam") {
        easel.pad.sketch.selectedLinks = [];
        easel.pad.sketch.slowDraw();
      }
      this.selection = null;
      this.selectiontype = null;
      return this.dragstart = null;
    },
    mouseMove: function(easel, eventType, mouseLoc, object) {
      var dist, pos, sign, xdist, ydist;
      if (this.dragstart) {
        pos = {
          x: mouseLoc[0],
          y: mouseLoc[1]
        };
        if (this.selectiontype === "node") {
          this.selection.moveto(pos);
        } else if (this.selectiontype === "beam") {
          xdist = pos.x - this.dragstart.x;
          ydist = pos.y - this.dragstart.y;
          dist = sqrt(sqr(xdist) + sqr(ydist));
          sign = sin(atan2(ydist, xdist));
          this.selection.size = max(0.5, sign * dist * 1.4 + this.dragstart.size);
        }
        return easel.pad.sketch.quickDraw();
      }
    }
  };

  window.tacit.tools.move = moveTool;

}).call(this);
