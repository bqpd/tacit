// Generated by CoffeeScript 1.4.0
(function() {
  var Suggestions, dummyEasel, r, _ref;

  if ((_ref = window.tacit) == null) {
    window.tacit = {};
  }

  r = function() {
    return 2 * Math.random() - 1;
  };

  dummyEasel = (function() {

    function dummyEasel(suggestions, i) {
      this.suggestions = suggestions;
      this.i = i;
      null;
    }

    dummyEasel.prototype.mouseDown = function(easel, eventType, mouseLoc, object) {
      var _this = this;
      console.log(this.i);
      this.suggestions.project.easel.pad.load(this.suggestions.pads[this.i].sketch.structure);
      this.suggestions.project.easel.pad.sketch.onChange = function() {
        return _this.suggestions.update(_this.suggestions.project.easel.pad.sketch.structure);
      };
      this.suggestions.project.easel.pad.sketch.updateDrawing();
      return false;
    };

    dummyEasel.prototype.mouseUp = function(easel, eventType, mouseLoc, object) {
      return false;
    };

    dummyEasel.prototype.mouseMove = function(easel, eventType, mouseLoc, object) {
      return false;
    };

    return dummyEasel;

  })();

  Suggestions = (function() {

    function Suggestions(project, htmlLoc) {
      var i, structure, _i,
        _this = this;
      this.project = project;
      this.htmlLoc = htmlLoc;
      this.project.easel.pad.sketch.onChange = function() {
        return _this.update(_this.project.easel.pad.sketch.structure);
      };
      structure = new tacit.Structure(this.project.easel.pad.sketch.structure);
      this.pads = [];
      for (i = _i = 1; _i <= 3; i = ++_i) {
        this.pads.push(new tacit.Pad(new dummyEasel(this, i), this.htmlLoc, 200, 225, structure));
      }
      this.update(structure);
    }

    Suggestions.prototype.mutate = function(structure) {
      var delta, dg, node, _i, _len, _ref1, _results;
      _ref1 = structure.nodeList;
      _results = [];
      for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
        node = _ref1[_i];
        dg = 200 * r() * structure.nodeList.length / structure.lp.obj;
        delta = {
          x: node.grad.x * dg * !node.fixed.x,
          y: node.grad.y * dg * !node.fixed.y,
          z: node.grad.z * dg * !node.fixed.z
        };
        _results.push(node.move(delta));
      }
      return _results;
    };

    Suggestions.prototype.update = function(structure) {
      var pad, _i, _len, _ref1, _results;
      _ref1 = this.pads;
      _results = [];
      for (_i = 0, _len = _ref1.length; _i < _len; _i++) {
        pad = _ref1[_i];
        structure = new tacit.Structure(structure);
        structure.solve();
        this.mutate(structure);
        pad.load(structure);
        pad.sketch.nodeSize = 0;
        pad.sketch.rect.attr("fill", "transparent");
        pad.sketch.showforce = false;
        _results.push(pad.sketch.updateDrawing());
      }
      return _results;
    };

    return Suggestions;

  })();

  window.tacit.Suggestions = Suggestions;

}).call(this);
