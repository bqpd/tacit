function initialize(structure) {
	window.tutorial_state = -1
	finalsurvey = "http://mit.co1.qualtrics.com/jfe/form/SV_bOWahYvH6tOwoMB"
	intermediatesurveys = {
		"ab": "http://mit.co1.qualtrics.com/jfe/form/SV_bOWahYvH6tOwoMB",
		"mb": "http://mit.co1.qualtrics.com/jfe/form/SV_bOWahYvH6tOwoMB",
		"ob": "http://mit.co1.qualtrics.com/jfe/form/SV_bOWahYvH6tOwoMB",
		"as": "http://mit.co1.qualtrics.com/jfe/form/SV_bOWahYvH6tOwoMB",
		"ms": "http://mit.co1.qualtrics.com/jfe/form/SV_bOWahYvH6tOwoMB",
		"os": "http://mit.co1.qualtrics.com/jfe/form/SV_bOWahYvH6tOwoMB",
	}

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
	window.project.easel = new tacit.Easel(window.project, "#PadView",
						    	height, width, structure, global_weight);
	window.project.actionQueue = [];
	sketch = project.easel.pad.sketch;
	s = sketch.structure;
	sketch.updateDrawing();

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
			if (location.hash.length < 6)
	            location.href = finalsurvey
	        else
	            location.href = intermediatesurveys[location.hash.substr(4,2)]
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
		project.easel.pad.sketch.fea()})

	versions = new tacit.Versions(window.project, "#HistorySketchesView");
	undoredo = new tacit.UndoRedo(window.project)

	$(".notyet").removeClass("notyet")
}

window.initialize = initialize;
