


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

	bdy = $("body")[0];
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
				d.innerHTML=('<div class="imgflip"  id="swipe-left-right" data-mdb-touch-init="" data-mdb-event="swipe" data-mdb-treshold="100" data-mdb-touch-initialized="true"><img style="z-index:1" class="flipper sample" src="/slbetrain/trains/'+hiresjpg+'">'
								+ '<img style="z-index:0" class="flipper sampgif" src="/slbetrain/trains/'+jdata[i][0]+'"></div>'
					+'<div class="btnstrip">'
						+'<button class="train no" data-train="'+jdata[i][1]+'">NO</button>'
						+'<button class="train yes"  data-train="'+jdata[i][1]+'">YES</button>'

				);
			}
		}
	});

}

(function() {

	initMDB({ Touch });
	const swipeLeftRight = document.querySelector('#swipe-left-right');
	swipeLeftRight.addEventListener('swipeleft', (e) => {
		alert('You swiped left!');
	});
	swipeLeftRight.addEventListener('swiperight', (e) => {
		alert('You swiped right!');
	});
	window._x_startAt = 0;
	updateBody();

})();






                










