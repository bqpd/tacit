// Generated by CoffeeScript 1.4.0
(function() {
  var UndoRedo, _ref;

  if ((_ref = window.tacit) == null) {
    window.tacit = {};
  }

  UndoRedo = (function() {

    function UndoRedo(project) {
      var _base, _ref1;
      this.project = project;
      this.pointer = -1;
      if ((_ref1 = (_base = this.project).actionQueue) == null) {
        _base.actionQueue = [];
      }
      this.log();
    }

    UndoRedo.prototype.log = function() {
      var structure, _ref1;
      this.project.onChange();
      structure = new tacit.Structure(this.project.easel.pad.sketch.structure);
      structure.solve();
      if (!(this.project.actionQueue[this.pointer] != null) || this.project.actionQueue[this.pointer].strucstr !== structure.strucstr) {
        if ((_ref1 = window.log) == null) {
          window.log = "";
        }
        window.log += ("# at " + (new Date().toLocaleString()) + ", a new structure of weight " + structure.lp.obj + "\n") + structure.strucstr + "\n";
        this.project.actionQueue = this.project.actionQueue.slice(0, this.pointer + 1);
        this.project.actionQueue.push(structure);
        return this.pointer = this.project.actionQueue.length - 1;
      }
    };

    UndoRedo.prototype.undo = function() {
      var structure;
      if (this.pointer - 1 >= 0) {
        window.log += "\n# undo";
        this.pointer -= 1;
        structure = new tacit.Structure(this.project.actionQueue[this.pointer]);
        this.project.easel.pad.load(structure);
        this.project.easel.pad.sketch.feapad = window.feapadpad;
        this.project.easel.pad.sketch.updateDrawing();
        this.project.easel.pad.sketch.dragline.attr("x1", 0).attr("x2", 0).attr("y1", 0).attr("y2", 0);
        return this.project.easel.currentTool.drawStart = false;
      }
    };

    UndoRedo.prototype.redo = function() {
      if (this.pointer + 1 < this.project.actionQueue.length) {
        window.log += "\n# redo";
        this.pointer += 1;
        this.project.easel.pad.load(this.project.actionQueue[this.pointer]);
        this.project.easel.pad.sketch.feapad = window.feapadpad;
        return this.project.easel.pad.sketch.updateDrawing();
      }
    };

    return UndoRedo;

  })();

  window.tacit.UndoRedo = UndoRedo;

}).call(this);
