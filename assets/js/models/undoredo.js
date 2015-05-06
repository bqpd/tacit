// Generated by CoffeeScript 1.9.2
(function() {
  var UndoRedo;

  if (window.tacit == null) {
    window.tacit = {};
  }

  UndoRedo = (function() {
    function UndoRedo(project) {
      var base;
      this.project = project;
      this.pointer = -1;
      if ((base = this.project).actionQueue == null) {
        base.actionQueue = [];
      }
      this.log();
    }

    UndoRedo.prototype.log = function() {
      var structure;
      this.project.onChange();
      this.project.actionQueue = this.project.actionQueue.slice(0, this.pointer + 1);
      structure = new tacit.Structure(this.project.easel.pad.sketch.structure);
      structure.solve();
      if ((this.project.actionQueue[this.pointer] == null) || this.project.actionQueue[this.pointer].LPstring() !== structure.LPstring()) {
        this.project.actionQueue.push(structure);
      }
      return this.pointer = this.project.actionQueue.length - 1;
    };

    UndoRedo.prototype.undo = function() {
      if (this.pointer - 1 >= 0) {
        this.pointer -= 1;
        this.project.easel.pad.load(this.project.actionQueue[this.pointer]);
        return this.project.easel.pad.sketch.updateDrawing();
      }
    };

    UndoRedo.prototype.redo = function() {
      if (this.pointer + 1 < this.project.actionQueue.length) {
        this.pointer += 1;
        this.project.easel.pad.load(this.project.actionQueue[this.pointer]);
        return this.project.easel.pad.sketch.updateDrawing();
      }
    };

    return UndoRedo;

  })();

  window.tacit.UndoRedo = UndoRedo;

}).call(this);
