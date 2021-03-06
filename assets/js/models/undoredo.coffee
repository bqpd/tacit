window.tacit ?= {}

class UndoRedo
    constructor: (@project) ->
        @pointer = -1
        @project.actionQueue ?= []
        @log()

    log: ->
        @project.onChange()
        structure = new tacit.Structure(@project.easel.pad.sketch.structure)
        structure.solve()

        clock = document.getElementById("timer")
        tickfn = ->
            limit = 60 * (if window.tutorial then 20.99 else 12.99)
            t = limit - (Date.parse(new Date()) - Date.parse(project.starttime))/1000
            itstopped = Math.abs(project.last_t-t) > 1
            console.log t
            project.last_t = t
            fractions = t % 1
            t  -= fractions
            seconds = t % 60
            minutes = (t-seconds)/60
            seconds--
            if t < 0
                if window.log.search("ran out of time") == -1
                    return
            if t < 1
                $("#export-btn").click()
                window.log += "# ran out of time at "+new Date().toLocaleString()+" \n"
            else if t >= 0
                if seconds < 10
                    seconds = "0" + seconds
                if minutes >= 1
                    clock.innerHTML =  ' | ' + minutes + ' minutes';
                else
                    clock.innerHTML = " | " + minutes + ':' + seconds;
            return itstopped

        if tickfn()
            console.log "restarting clock"
            setInterval(tickfn, 1000)

        if !@project.actionQueue[@pointer]? or @project.actionQueue[@pointer].strucstr != structure.strucstr
            window.log ?= ""
            window.log += "# at #{new Date().toLocaleString()}, a new structure of weight #{structure.lp.obj} with #{project.easel.pad.sketch.structure.nodeList.length} nodes and #{project.easel.pad.sketch.structure.beamList.length} beams was created by the #{project.easel.currentTool.name} tool\n" + structure.strucstr + "\n"
            @project.actionQueue = @project.actionQueue.slice(0,@pointer+1)
            @project.actionQueue.push(structure)
            @pointer = @project.actionQueue.length-1


    undo: ->
        if @pointer - 1 >= 0
            if window.triggers.undo?
                window.triggers.undo()
            @pointer -= 1
            structure = new tacit.Structure(@project.actionQueue[@pointer])
            @project.easel.pad.load(structure)
            @project.easel.pad.sketch.feapad = window.feapadpad
            @project.easel.pad.sketch.updateDrawing()
            @project.easel.pad.sketch.dragline.attr("x1", 0).attr("x2", 0)
                                              .attr("y1", 0).attr("y2", 0)
            @project.easel.currentTool.drawStart = false
            window.log += "# at #{new Date().toLocaleString()}, a new structure of weight #{structure.lp.obj} with #{project.easel.pad.sketch.structure.nodeList.length} nodes and #{project.easel.pad.sketch.structure.beamList.length} beams was created by the undo tool\n" + structure.strucstr + "\n"

    redo: ->
        if @pointer + 1 < @project.actionQueue.length
            @pointer += 1
            @project.easel.pad.load(@project.actionQueue[@pointer])
            @project.easel.pad.sketch.feapad = window.feapadpad
            @project.easel.pad.sketch.updateDrawing()
            window.log += "# at #{new Date().toLocaleString()}, a new structure of weight #{structure.lp.obj} with #{project.easel.pad.sketch.structure.nodeList.length} nodes and #{project.easel.pad.sketch.structure.beamList.length} beams was created by the redo tool\n" + structure.strucstr + "\n"

window.tacit.UndoRedo = UndoRedo
