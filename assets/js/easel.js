// Generated by CoffeeScript 1.4.0
(function() {
  var Easel, dist, print, _ref;

  print = function(o) {
    return console.log(o);
  };

  dist = function(a, b) {
    var ai, i;
    return sqrt(sum((function() {
      var _i, _len, _results;
      _results = [];
      for (i = _i = 0, _len = a.length; _i < _len; i = ++_i) {
        ai = a[i];
        _results.push(sqr(ai - (b ? b[i] : 0)));
      }
      return _results;
    })()));
  };

  if ((_ref = this.tacit) == null) {
    this.tacit = {};
  }

  Easel = (function() {

    function Easel(project, toolbarLoc, padLoc, padHeight, padWidth, structure) {
      var padHtmlRect;
      this.project = project;
      if (structure == null) {
        structure = null;
      }
      padHtmlRect = d3.select(padLoc).node().getBoundingClientRect();
      if (padWidth == null) {
        padWidth = htmlRect.width;
      }
      if (padHeight == null) {
        padHeight = htmlRect.height;
      }
      this.pad = new tacit.Pad(this, padLoc, padHeight, padWidth, structure);
    }

    Easel.prototype.currentTool = {
      mouseDown: function(easel, eventType, mouseLoc, object) {
        var node, pos;
        if (eventType !== "node") {
          pos = {
            x: mouseLoc[0],
            y: mouseLoc[1]
          };
          node = new easel.pad.sketch.structure.Node(pos);
          node.force.y = -1;
          easel.pad.sketch.redraw();
        } else {
          pos = {
            x: object.x,
            y: object.y
          };
        }
        easel.pad.sketch.dragline.attr("x1", pos.x).attr("x2", pos.x).attr("y1", pos.y).attr("y2", pos.y);
        return easel.currentTool.dragStart = pos;
      },
      mouseUp: function(easel, eventType, mouseLoc, object) {
        var node, pos;
        if (eventType !== "node") {
          pos = {
            x: mouseLoc[0],
            y: mouseLoc[1]
          };
          node = new easel.pad.sketch.structure.Node(pos);
          node.force.y = -1;
        } else {
          pos = {
            x: object.x,
            y: object.y
          };
        }
        if (pos !== easel.currentTool.dragStart) {
          new easel.pad.sketch.structure.Beam(easel.currentTool.dragStart, pos);
          easel.pad.sketch.dragline.attr("x1", pos.x).attr("x2", pos.x).attr("y1", pos.y).attr("y2", pos.y);
          easel.pad.sketch.redraw();
        }
        return easel.currentTool.dragStart = null;
      },
      mouseMove: function(easel, eventType, mouseLoc, object) {
        if (easel.currentTool.dragStart) {
          easel.pad.sketch.dragline.attr("x2", mouseLoc[0]).attr("y2", mouseLoc[1]);
          if (easel.pad.sketch.reposition != null) {
            return easel.pad.sketch.reposition();
          }
        }
      }
    };

    return Easel;

  })();

  this.tacit.Easel = Easel;

}).call(this);
