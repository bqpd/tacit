// Generated by CoffeeScript 1.4.0
(function() {
  var Pad, _ref;

  if ((_ref = this.tacit) == null) {
    this.tacit = {};
  }

  Pad = (function() {

    function Pad(easel, htmlLoc, height, width, structure) {
      this.easel = easel;
      this.htmlLoc = htmlLoc;
      this.height = height;
      this.width = width;
      this.sketch = new tacit.Sketch(this, this.htmlLoc, structure, this.height, this.width);
    }

    Pad.prototype.load = function(structure) {
      var scale, translate;
      this.sketch.svg.remove();
      translate = [this.sketch.translate[0] * this.sketch.scale, this.sketch.translate[1] * this.sketch.scale];
      scale = this.sketch.scale;
      return this.sketch = new tacit.Sketch(this, this.htmlLoc, structure, this.height, this.width);
    };

    return Pad;

  })();

  this.tacit.Pad = Pad;

}).call(this);
