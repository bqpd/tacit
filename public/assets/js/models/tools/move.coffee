window.tacit ?= {}
window.tacit.tools ?= {}

sqr = (a) -> Math.pow(a, 2)
abs = (a) -> Math.abs(a)
sign = (a) -> Math.sign(a)
sqrt = (a) -> Math.sqrt(a)
max = (n...) -> Math.max(n...)
sin = (a) -> Math.sin(a)
atan2 = (a,b) -> Math.atan2(a,b)

moveTool =
    allowPan: true
    name: "move"
    dontSelectImmovable: true

    mouseDown: (easel, eventType, mouseLoc, object) ->
        if eventType is "node"
            if not (object.immovable? and object.immovable)
                @selection = object
                @selectiontype = "node"
                @allowPan = false
                @dragging = true
                idx = easel.pad.sketch.selectedNodes.indexOf(object)
                easel.pad.sketch.selectedNodes.push(object) if idx is -1
                easel.pad.sketch.quickDraw()
        else if eventType is "beam"
            @selection = object
            @selectiontype = "beam"
            @allowPan = false
            @dragging = {x: mouseLoc[0], y: mouseLoc[1], size:object.size}
            easel.pad.sketch.selectedLinks = [@selection]
            easel.pad.sketch.slowDraw()

    mouseUp: (easel, eventType, mouseLoc, object) ->
        if @selectiontype is "node"
            idx = easel.pad.sketch.selectedNodes.indexOf(@selection)
            easel.pad.sketch.selectedNodes.splice(idx, 1)
            easel.pad.sketch.quickDraw()
        else if @selectiontype is "beam"
            easel.pad.sketch.selectedLinks = []
            easel.pad.sketch.slowDraw()
        @selection = null
        @selectiontype = null
        @dragging = null
        @allowPan = true

    mouseMove: (easel, eventType, mouseLoc, object) ->
        if @dragging
            pos = {x: mouseLoc[0], y: mouseLoc[1]}
            if @selectiontype is "node"
                @selection.moveto(pos)
                if window.triggers.movenode?
                    window.triggers.movenode()
            else if @selectiontype is "beam"
                if window.triggers.resizebeam?
                    window.triggers.resizebeam()
                source = @selection.source
                target = @selection.target
                if source.x > target.x or (source.x is target.x and source.y < target.y)
                    tmp = source
                    source = target
                    target = tmp
                d_x = pos.x-@dragging.x
                d_y = pos.y-@dragging.y
                b_x = source.x - target.x
                b_y = source.y - target.y
                orthogonal = -(b_x*d_y - b_y*d_x)/@selection.L
                orthogonal *=  abs(orthogonal)/3
                # if b_x < 0
                    # if sign(d_y) is sign(dz_x)
                @selection.size = max(0.5, orthogonal + @dragging.size)
            easel.pad.sketch.quickDraw()

window.tacit.tools.move = moveTool
