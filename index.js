


function prev() {
	window._x_startAt -= 50;
	if (window._x_startAt < 0) {
		window._x_startAt = 0;
	}
	updateBody();
}

function next() {
	window._x_startAt += 50;
	updateBody();
}
window._x_startAt = 0;
window._x_maxAt = 0;
function updateBody() {

	bdy = $("div.root")[0];
	bdy.innerHTML = "";
	headline = bdy.appendChild(document.createElement("p"));
	headline.classList.add("title");
	buttonhtml = '<div class="topbtnbar">';
	if (window._x_startAt > 0) {
		disabled = "";
	} else {
		disabled = " disabled";
	}
	buttonhtml += '<button '+disabled+' class="first" onclick="window._x_startAt=0;updateBody()">|&lt;</button>';
	buttonhtml += '<button '+disabled+' class="prev" onclick="prev()">&lt;&lt;</button>';
	buttonhtml += '<button class="next" onclick="next()">&gt;&gt;</button>';
	buttonhtml += '<button class="last" onclick="window._x_startAt=window._x_maxAt;updateBody()">&gt;|</button>';
	buttonhtml += '</div>';
	headline.innerHTML=("FISH IDENTIFICATION TRAINING<br>"+buttonhtml);

	$.ajax("/slbetrain/cgi-bin/getconts.cgi", {
		"complete": function(data) {
			console.log(data);
			jdata = data.responseJSON;
			window._x_maxAt = jdata.length;
			for (var i=window._x_startAt; i<Math.min(jdata.length,window._x_startAt+50); i++) {
				var d=bdy.appendChild(document.createElement("div"));
				d.classList.add("trainbox");
				jdi = jdata[i][0]+'';
				hiresjpg = jdi.replace(".gif",".jpg").replace("conts","jpg").replace("_sfs","_sf1");
				d.innerHTML=('<div class="imgflip"><img style="z-index:1" class="flipper sample" src="/slbetrain/trains/'+hiresjpg+'">'
								+ '<img style="z-index:0" class="flipper sampgif" src="/slbetrain/trains/'+jdata[i][0]+'"></div>'
					+'<div class="btnstrip">'
						+'<button class="train no" data-train="'+jdata[i][1]+'">NO</button>'
						+'<button class="train yes"  data-train="'+jdata[i][1]+'">YES</button>'

				);
			}
			$("div.imgflip").swipe({
				swipeLeft:function(e) {
					console.log("swiped left!");
					console.log(e);
					e.preventDefault();
				},
				swipeRight:function(e) {
					console.log("swiped right!");
					console.log(e);
					e.preventDefault();
				}
			});
		}
	});

}

(function() {
	window._x_startAt = 0;
	updateBody();

})();






                










