function initialize(structure) {
	window.tutorial_state = -1
	surveylink = "http://mit.co1.qualtrics.com/SE/?SID=SV_2c6MrrOdYSZiIw5"

	// initialize easel and stuff
	var height = parseInt($(window).height() - 110);
	$("#HistoryView").css("max-width", 60*Math.floor(($(window).width()-660)/60))
	var offset = window.tutorial ? 510 : 200;
	if (window.feapad)
		var width = parseInt($(window).width() - offset);
	else
		var width = parseInt($(window).width()/2 - offset/2);
	window.project = {"name": "untitled", "onChange": function(){}};
	global_weight = document.getElementById("designweight")
	preview_weight = document.getElementById("PreviewCost")
	window.project.easel = new tacit.Easel(window.project, "#PadView",
						    	height, width, structure, global_weight);
	window.project.actionQueue = [];
	sketch = project.easel.pad.sketch;
	s = sketch.structure;
	sketch.updateDrawing();

	// initialize preview
	// todo: don't hardcode preview window size
	window.preview = {"name": "untitled", "onChange": function(){}};
	window.preview.easel = new tacit.Easel(window.project, "#Preview",
						    	225, 225, structure, preview_weight);
	window.preview.easel.mouseMove = function(){return;}
	window.preview.easel.allowPan = function(){return;}

	window.db.structures_ref0.on('child_added', function(snapshot, prevChildKey) {
			latest_snapshot_0 = snapshot.val();
	    	if (window.usernum == 1) {
                updatePreview(snapshot, prevChildKey);
            }
	});

	window.db.structures_ref1.on('child_added', function(snapshot, prevChildKey) {
			latest_snapshot_1 = snapshot.val();
            if (window.usernum == 0) {
                updatePreview(snapshot, prevChildKey);
            }
	});
	var previewVersions = new tacit.Versions(window.project, false);
	window.db.events_ref0.on('child_added', function(snapshot, prevChildKey) {
            if(window.usernum == 1 && snapshot.val().type == "save") {
                structure = window.getStructureFromSnapshot(snapshot.val());
                previewVersions.updatePreviewHistory(structure);
            }
	});
	window.db.events_ref1.on('child_added', function(snapshot, prevChildKey) {
            if(window.usernum == 0 && snapshot.val().type == "save") {
                structure = window.getStructureFromSnapshot(snapshot.val());
                previewVersions.updatePreviewHistory(structure);
            }
	});
    var updatePreview = function(snapshot, prevChildKey) {
            structure = window.getStructureFromSnapshot(snapshot.val());
            window.preview.easel.pad.load(structure);
            window.preview.easel.pad.sketch.updateDrawing();
            return;
    }
  	// activate tooltips
	$('[data-toggle="tooltip"]').tooltip()

  	// make draw the default active tool
	$('.active').removeClass("active")
	$("#move-btn").addClass("active")
	project.easel.currentTool = tacit.tools.move


	$("#PadView svg").css({'cursor': 'url(assets/resources/cursor-images/pencil.png) 0 16, auto'})

/*	$(document).click(function(evt){
		if($(evt.target).is("#tutorial-btn") && $("#instructions").length == 0){
			//Add div containing temporary tutorials
			$("#Tutorial").append(
				"<div id='instructions'>" +
					"<p> <span style='color:#ff4444'>Red lines</span> indicate a beam which is being pushed in at each end (compression). </p>" +
					"<p> <span style='color:#00c7ff'>Blue lines</span> indicate a beam being pulled at each end (in tension). </p>" +
					"<p> The circles represent pinned or welded joints; beams can rotate around these joints, so a certain number of beams are needed to make a structure stable. </p>" +
					"<p> Unstable structures have only unused beams (dotted brown), while stable structures also have beams colored by their use. </p>" +
				"</div>"
				);
		} else {
			$("#instructions").remove();
			$("#tutorial-btn").removeClass("active");
			//How do I get it to look unclicked?
			evt.stopImmediatePropagation();

		}
	});
*/

	$("#PadView").on('mouseover', function() {
		if (project.easel.currentTool.name == "select"){
			$("#PadView svg").css({'cursor': 'default'})
		} else if (project.easel.currentTool.name == "move"){
			$("#PadView svg").css({'cursor': 'pointer'})
		} else if (project.easel.currentTool.name == "draw"){
			$("#PadView svg").css({'cursor': 'url(assets/resources/cursor-images/pencil.png) 0 16, auto'})
		} else if (project.easel.currentTool.name == "erase") {
			$("#PadView svg").css({'cursor': 'url(assets/resources/cursor-images/eraser.png) 6 16, auto'})
		} else if (project.easel.currentTool.name == "measure") {
			$("#PadView svg").css({'cursor': 'url(assets/resources/cursor-images/ruler.png) 6 20, auto'})
		} else if (project.easel.currentTool.name == "load") {
			$("#PadView svg").css({'cursor': 'default'})
		} else if (project.easel.currentTool.name == "thicken"){
				$("#PadView svg").css({'cursor': 'default'})
		} else {
				console.log("no tool selected");

	}
});

	var gridBox = $('input[name=grid]');
	gridBox.click(function(){
		if(gridBox.is(":checked")){
			project.easel.pad.sketch.rect.attr("fill", "url(#grid)");
        } else {
          project.easel.pad.sketch.rect.attr("fill", "transparent");

        }
      });

      var baseLineBox = $('input[name=baseLine]');
      baseLineBox.click(function(){
        if(baseLineBox.is(":checked")){
          project.easel.pad.sketch.baseLine.attr("stroke", "#3d3130");
        } else {
          project.easel.pad.sketch.baseLine.attr("stroke", "transparent");

        }
      });

	// update project name on input change
	$("#ProjectName").on("input", function(e){
		e.stopPropagation();
	    var text = $('<span style="display: none;">')
	        .html($(this).val().replace(/ /g, "&nbsp;"))
	        .appendTo(this.parentNode);
	    var w = Math.min(400, 12 + text.innerWidth());
	    text.remove();
		$("#ProjectName").width(w);
		$("#HistoryView").css("max-width", 60*Math.floor(($(window).width()-570-w)/60))
		window.project.name = $("#ProjectName").val();
		document.title = $("#ProjectName").val() + " | tacit.blue";
	})

	// unfocus the name input on enter
	$("#ProjectName").keypress(function (e) {
  		if (e.which == 13) {
   			$("#ProjectName").trigger('blur');
    		return false;
  		}
	});
	$("#export-btn").click(function() {
		if (window.tutorial)
			return nextTutorialStep();
		window.log += "# finished at "+new Date().toLocaleString()+"\n"
                firebase.database().ref(window.sessionid+"/"+window.usernum+"/"+window.problem_order+'/events/').push().set({
                    type: "finished",
                    timestamp: new Date().toLocaleString(),
                });
		if (location.hash[1] === "t" ) {
			project.easel.saveLog()
			location.hash = location.hash.substr(2)
			console.log(location.hash)
			location.reload()
		} else if (location.hash.search("x") !== -1) {
			location.hash = location.hash.substr(3)
			console.log(location.hash)
			location.reload()
		} else {
			project.easel.saveLog()
	        location.href = surveylink
		}
		})
	$("#zoom-btn").click(function() {
		if (window.triggers.zoom !== undefined)
            window.triggers.zoom()
		project.easel.pad.sketch.defaultZoom()})

	window.updateTool = function () {
		if (window.tool.autocolor) {
			$("#fea-btn").hide()
		} else {
			$("#fea-btn").show()
		}
		project.easel.pad.sketch.slowDraw()
	}

    updateTool()
	$("#fea-btn").click(function() {
		window.log += "# analyze button clicked at "+new Date().toLocaleString()+" \n"
                firebase.database().ref(window.sessionid+"/"+window.usernum+"/"+window.problem_order+'/events/').push().set({
                    type: "analyze",
                    timestamp: new Date().toLocaleString(),
                });
		project.easel.pad.sketch.fea()})

	versions = new tacit.Versions(window.project, true);
	undoredo = new tacit.UndoRedo(window.project)

	$(".notyet").removeClass("notyet")
}

window.getLatestSnapshot0 = function() {
	return latest_snapshot_0;
}

window.getLatestSnapshot1 = function() {
	return latest_snapshot_1;
}
window.getStructureFromSnapshot = function(structureData) {
	structure = new tacit.Structure;

	var nodes =[];
	for(var i = 0; i < structureData.nodes; i++) {
		var nodeData = structureData.nodeList[i];
		var node = new structure.Node({
			x: parseFloat(nodeData.x),
			y: parseFloat(nodeData.y),
			z: parseFloat(nodeData.z)
		});
		if ("fixed" in nodeData) {
			node.fixed = {
				x: (nodeData.fixed.x === "true"),
				y: (nodeData.fixed.y === "true"),
				z: (nodeData.fixed.z === "true")
			};
		} else {
			node.fixed = {
				x: true,
				y: true,
				z: true
			};
		}
		if ("force" in nodeData) {
			node.force = {
				x: parseFloat(nodeData.force.x),
				y: parseFloat(nodeData.force.y),
				z: parseFloat(nodeData.force.z)
			};
		} else {
			node.force = {
				x: 0,
				y: 0,
				z: 0
			};
		}
        node.immovable = nodeData.immovable;
		nodes.push(node);
	}
	// todo: don't hardcode starting nodes
	if (nodes.length == 0) {
		n1 = new structure.Node({x: 42, y: 72, z: 0});
		n1.immovable = true;
		n2 = new structure.Node({x: 42, y: 97, z: 0});
		n2.immovable = true;
		n3 = new structure.Node({x: 20, y: 1.65, z: 0});
		n3.immovable = true;
		n4 = new structure.Node({x: 60, y: 1.65, z: 0});
		n4.immovable = true;
	    nodes.push(n1);
		nodes.push(n2);
        nodes.push(n3);
        nodes.push(n4);
	}
    var beams = [];
    for(var i = 0; i < structureData.beams; i++) {
	    var beamData = structureData.beamList[i];
        var beam = new structure.Beam(
			{
				x: parseFloat(beamData.start_x),
				y: parseFloat(beamData.start_y),
				z: parseFloat(beamData.start_z)
			},
    	    {
				x: parseFloat(beamData.end_x),
				y: parseFloat(beamData.end_y),
				z: parseFloat(beamData.end_z)
			},
        	parseFloat(beamData.size)
        );
		beam.immovable = beamData.immovable;
        beams.push(beam);
    }

    structure.historyLength = structureData.historyLength;
    structure.lp = {obj: structureData.weight};
    return structure;
}

window.initialize = initialize;
