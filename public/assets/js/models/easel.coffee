window.tacit ?= {}

`
// from stackoverflow.com/questions/3665115/create-a-file-in-memory-for-user-to-download-not-through-server
function download(filename, text) {
  var pom = document.createElement('a');
  pom.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  pom.setAttribute('download', filename);
  pom.style.display = 'none';
  document.body.appendChild(pom);
  pom.click();
  document.body.removeChild(pom);
}
`

class Easel
    constructor: (@project, padLoc, padHeight, padWidth, structure, @weightDisplay) ->
        #@toolbar = new tacit.Toolbar(this, toolbarLoc)

        padHtmlRect = d3.select(padLoc).node().getBoundingClientRect()
        padWidth ?= htmlRect.width
        padHeight ?= htmlRect.height
        @pad = new tacit.Pad(this, padLoc, padHeight, padWidth, structure)

    allowPan: -> if @currentTool.allowPan? then @currentTool.allowPan else false

    export: ->
        filename = if @project.name? then @project.name else "tacit"
        filename += ".svg"
        download(filename, d3.select(easel.pad.htmlLoc).html())

    saveLog: ->
        filename = "#{new Date().toLocaleString()}_#{window.problem_description.title}_#{window.tool.name}.txt"
        download(filename, window.log)

    mouseDown: (easel, eventType, mouseLoc, object) ->
        if easel.pad.htmlLoc == "#Preview"
            structure = null
            if window.usernum == 0
                latest_snapshot_1 = window.getLatestSnapshot1()
                console.log "click: window.latest_snapshot_1 = ", latest_snapshot_1
                structure = window.getStructureFromSnapshot(latest_snapshot_1)
            else
                latest_snapshot_0 = window.getLatestSnapshot0()
                console.log "click: window.latest_snapshot_0 = ", latest_snapshot_0
                structure = window.getStructureFromSnapshot(latest_snapshot_0)
            structure.solve()
            console.log "structure = " , structure
            @project.actionQueue = [structure]
            undoredo.pointer = 0
            structure = new tacit.Structure(structure)
            console.log "2 structure = " , structure
            structure.last_edit = (window.usernum + 1) % 2
            console.log "easel = ", easel
            easel.project.easel.pad.load(structure)
            easel.project.easel.pad.sketch.feapad = window.feapadpad
            easel.project.easel.pad.sketch.updateDrawing()
            easel.project.easel.pad.sketch.fea()
            firebase.database().ref(window.sessionid+"/"+window.usernum+"/"+window.problem_order+"/events/").push().set
                timestamp: new Date().toLocaleString()
                weight: structure.lp.obj
                nodes: easel.project.easel.pad.sketch.structure.nodeList.length
                beams: easel.project.easel.pad.sketch.structure.beamList.length
                type: "load from teammate current"
        if @currentTool?
            if @currentTool.mouseDown?
                @currentTool.mouseDown(easel, eventType, mouseLoc, object)
        if eventType in ["node", "beam"]
            @selection = object
        return false
    mouseUp: (easel, eventType, mouseLoc, object) ->
        if @currentTool?
            if @currentTool.mouseUp?
                @currentTool.mouseUp(easel, eventType, mouseLoc, object)
        undoredo.log()
        @selection = null
        return false
    mouseMove: (easel, eventType, mouseLoc, object) ->
        if @currentTool?
            if @currentTool.mouseMove?
                @currentTool.mouseMove(easel, eventType, mouseLoc, object)
        if not @currentTool.dragging
            change = false
            if (easel.pad.sketch.selectedLinks.length + easel.pad.sketch.selectedNodes.length > 0) and object isnt @selection
                change = true
                @selection = null
                easel.pad.sketch.selectedNodes = []
                easel.pad.sketch.selectedLinks = []
            if eventType is "node"
                if not (object.immovable and easel.currentTool.dontSelectImmovable)
                    if not 1 + easel.pad.sketch.selectedNodes.indexOf(object)
                        change = true
                        easel.pad.sketch.selectedNodes.push(object)
            else if eventType is "beam"
                #if not (object.immovable and easel.currentTool.dontSelectImmovable)
                if window.tool.sized_beams or project.easel.currentTool.name isnt "move"
                    if not 1 + easel.pad.sketch.selectedLinks.indexOf(object)
                        change = true
                        easel.pad.sketch.selectedLinks.push(object)
            if change and object isnt @selection
                if eventType is "node"
                    easel.project.onChange()
                    @selection = object
                easel.pad.sketch.animateSelection()
        return false

    keyDown: (easel, eventType, keyCode) ->
        if @currentTool?
            if @currentTool.keyDown?
                if @currentTool.keyDown(easel, eventType, keyCode)
                    return false
        switch d3.event.keyCode
            when 8, 46  # backspace, delete
                for node in @pad.sketch.selectedNodes
                    node.delete()
                link.delete() for link in @pad.sketch.selectedLinks
                @pad.sketch.selectedLinks = []
                @pad.sketch.selectedNodes = []
                @pad.sketch.updateDrawing()
            when 27 # esc
                if easel.currentTool is tacit.tools.draw
                    easel.currentTool.stopDrawing(easel)
            when 68 # d
                easel.currentTool = tacit.tools.draw
                `$('.active').blur();
                 $('.active').removeClass("active");
            	 $("#draw-btn").addClass("active");
                 $("#PadView svg").css({'cursor': 'url(assets/resources/cursor-images/pencil.png) 0 16, auto'});
                 `
            when 69 # e
                if d3.event.metaKey or d3.event.ctrlKey
                    $("#export-btn").click()
                else
                    easel.currentTool = tacit.tools.erase
                    `$('.active').blur();
                     $('.active').removeClass("active");
                	 $("#erase-btn").addClass("active");
                     $("#PadView svg").css({'cursor': 'url(assets/resources/cursor-images/eraser.png) 6 16, auto'});
                     `
            when 76 # l
                easel.currentTool = tacit.tools.load
                `$('.active').blur();
                 $('.active').removeClass("active");
            	 $("#load-btn").addClass("active");
                 $("#PadView svg").css({'cursor': 'default'});
                 `
            when 77 # m
                easel.currentTool = tacit.tools.move
                `$('.active').blur();
                 $('.active').removeClass("active");
            	 $("#move-btn").addClass("active");
                 $("#PadView svg").css({'cursor': 'pointer'});
                 `
            when 83 # s
                if d3.event.metaKey or d3.event.ctrlKey
                    $("#save-btn").click()
                    d3.event.preventDefault()
            when 89 # y
                if d3.event.metaKey or d3.event.ctrlKey
                    $("#redo-btn").click()
            when 90 # z
                if d3.event.metaKey or d3.event.ctrlKey
                    if d3.event.shiftKey
                        $("#redo-btn").click()
                    else
                        $("#undo-btn").click()
        return false

window.tacit.Easel = Easel
