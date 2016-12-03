window.tacit ?= {}

class dummyEasel
    constructor: (@versions, @i, @project) -> null

    mouseDown: (easel, eventType, mouseLoc, object) ->
        if window.triggers.load?
            window.triggers.load()
        structure = new tacit.Structure(@versions.history[@i].sketch.structure)
        structure.solve()
        @project.actionQueue = [structure]
        undoredo.pointer = 0
        structure = new tacit.Structure(structure)
        @versions.project.easel.pad.load(structure)
        @versions.project.easel.pad.sketch.feapad = window.feapadpad
        @versions.project.easel.pad.sketch.updateDrawing()
        @versions.project.easel.pad.sketch.fea()
        @versions.project.onChange()
        window.log += "# at #{new Date().toLocaleString()}, a new structure of weight #{structure.lp.obj} with #{project.easel.pad.sketch.structure.nodeList.length} nodes and #{project.easel.pad.sketch.structure.beamList.length} beams was created by the load tool\n" + structure.strucstr + "\n"
        beams = structure.strucstr.split(/\r?\n/)
        beamObjs = []
        for beam in beams
            data = beam.split(/\|/)
            size = data[1]
            data = data[0].split(/\>\>/)
            start = data[0].split(/\,/)
            end = data[1].split(/\,/)
            immovable = (parseInt(data[2]) == "true")
            beamObjs.push
                size: size.replace /^\s+|\s+$/g, ""
                start_x: start[0].replace /^\s+|\s+$/g, ""
                start_y: start[1].replace /^\s+|\s+$/g, ""
                start_z: start[2].replace /^\s+|\s+$/g, ""
                end_x: end[0].replace /^\s+|\s+$/g, ""
                end_y: end[1].replace /^\s+|\s+$/g, ""
                end_z: end[2].replace /^\s+|\s+$/g, ""
                immovable: immovable
        nodeObjs = []
        nodes = structure.nodestr.split(/\r?\n/)
        for node in nodes
            data = node.split(/\|/)
            coordinatesData = data[0].split(" ")
            fixedData = data[1].split(" ")
            forceData = data[2].split(" ")
            immovable = (parseInt(data[3]) == "true")
            nodeObjs.push
                x: coordinatesData[0]
                y: coordinatesData[1]
                z: coordinatesData[2]
                fixed:
                    x: fixedData[0]
                    y: fixedData[1]
                    z: fixedData[2]
                force:
                    x: forceData[0]
                    y: forceData[1]
                    z: forceData[2]
                immovable: immovable
        firebase.database().ref(window.sessionid+"/"+window.usernum+"/"+window.problem_order+'/structures/').push().set
            timestamp: new Date().toLocaleString()
            weight: structure.lp.obj
            nodes: project.easel.pad.sketch.structure.nodeList.length
            beams: project.easel.pad.sketch.structure.beamList.length
            tool: "load"
            beamList: beamObjs
            nodeList: nodeObjs
        return false

    allowPan: -> false
    mouseUp: (easel, eventType, mouseLoc, object) -> false
    mouseMove: (easel, eventType, mouseLoc, object) -> false

class Versions
    constructor: (@project, newVersion) ->
        @htmlLoc = "#HistorySketchesView"
        @previewHtmlLoc = "#PreviewHistory"
        @history = []
        @newVersion(newVersion)

    newVersion: (structure, newVersion) ->
        if newVersion
            if not structure?
                structure = new tacit.Structure(@project.easel.pad.sketch.structure)
            window.log ?= ""
            window.log += "# saved at #{new Date().toLocaleString()} \n"
            @project.easel.pad.sketch.fea()
            beams = structure.strucstr.split(/\r?\n/)
            beamObjs = []
            for beam in beams
                data = beam.split(/\|/)
                size = data[1]
                data = data[0].split(/\>\>/)
                start = data[0].split(/\,/)
                end = data[1].split(/\,/)
                immovable = (parseInt(data[2]) == "true")
                beamObjs.push
                    size: size.replace /^\s+|\s+$/g, ""
                    start_x: start[0].replace /^\s+|\s+$/g, ""
                    start_y: start[1].replace /^\s+|\s+$/g, ""
                    start_z: start[2].replace /^\s+|\s+$/g, ""
                    end_x: end[0].replace /^\s+|\s+$/g, ""
                    end_y: end[1].replace /^\s+|\s+$/g, ""
                    end_z: end[2].replace /^\s+|\s+$/g, ""
                    immovable: immovable
            nodeObjs = []
            nodes = structure.nodestr.split(/\r?\n/)
            for node in nodes
                data = node.split(/\|/)
                coordinatesData = data[0].split(" ")
                fixedData = data[1].split(" ")
                forceData = data[2].split(" ")
                immovableData = (parseInt(data[3]) == "true")
                nodeObjs.push
                    x: coordinatesData[0]
                    y: coordinatesData[1]
                    z: coordinatesData[2]
                    fixed:
                        x: fixedData[0]
                        y: fixedData[1]
                        z: fixedData[2]
                    force:
                        x: forceData[0]
                        y: forceData[1]
                        z: forceData[2]
                    immovable: immovable
            structure.solve()
            firebase.database().ref(window.sessionid+"/"+window.usernum+"/"+window.problem_order+'/events/').push().set
                type: "save"
                timestamp: new Date().toLocaleString()
                nodes: nodeObjs.length
                beams: beamObjs.length
                nodeList: nodeObjs
                beamList: beamObjs
                historyLength: @history.length
                weight: structure.lp.obj
            versionObj = d3.select(@htmlLoc).append("div").attr("id", "ver"+window.usernum+"-"+@history.length).classed("ver", true)
            easel = new dummyEasel(this, @history.length, @project)
            versionObj.append("div").attr("id", "versvg"+window.usernum+"-"+@history.length).classed("versvg", true)
            easel.weightDisplay = versionObj.append("div").classed("verwd", true)[0][0]
            pad = new tacit.Pad(easel, "#versvg"+window.usernum+"-"+@history.length, 50, 50, structure)
            pad.load(structure, genhelper=false)
            pad.sketch.nodeSize = 0
            pad.sketch.showforce = false
            pad.sketch.updateDrawing()
            @history.push(pad)
            structure.solve()
            pad.sketch.fea()
            saved = Math.round(pad.sketch.structure.lp.obj/100)
            if saved <= $("#bestweight").text().substr(1)
                $("#bestweight").text("$"+saved)
                $("#bestcontainer").css("display", "")
                if window.triggers.beat?
                    window.triggers.beat()

    updatePreviewHistory: (structure) ->
        if not structure?
            structure = new tacit.Structure(@project.easel.pad.sketch.structure)
        @project.easel.pad.sketch.fea()
        previewVersionObj = d3.select("#PreviewHistory").append("div").attr("id", "ver"+window.partnernum+"-"+structure.historyLength).classed("ver", true)
        previewEasel = new dummyEasel(this, structure.historyLength, @project)
        previewVersionObj.append("div").attr("id", "versvg"+window.partnernum+"-"+structure.historyLength).classed("versvg", true)
        previewEasel.weightDisplay = previewVersionObj.append("div").classed("verwd", true)[0][0]
        previewEasel.weightDisplay.innerText = "\$"+Math.round(structure.lp.obj/100)
        previewPad = new tacit.Pad(previewEasel, "#versvg"+window.partnernum+"-"+structure.historyLength, 50, 50, structure)
        previewPad.load(structure, genhelper=false)
        previewPad.sketch.nodeSize = 0
        previewPad.sketch.showforce = false
        previewPad.sketch.updateDrawing()
        @history.push(previewPad)
        structure.solve()
        previewPad.sketch.fea()

    save: (structure) ->
        if window.triggers.save?
            window.triggers.save()
        if @project.actionQueue.length > 1 or structure?
            @newVersion(structure, true)

window.tacit.Versions = Versions
