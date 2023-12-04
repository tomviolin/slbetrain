
const PAGESIZE = 8;

function prev() {
	window._x_startAt -= PAGESIZE;
	if (window._x_startAt < 0) {
		window._x_startAt = 0;
	}
	updateBody();
}

function next() {
	window._x_startAt += PAGESIZE;
	updateBody();
}

function choseYes(recid) {
	targ = $("div[data-recid='"+recid+"']")[0];
	console.log('right');
	console.log(targ);
	$(targ).animate({left:"125%",opacity:0},500);
	$(targ.parentNode).animate({opacity:0},500, function() {
		console.log("removing "+recid);
		console.log(targ);
		targ.parentNode.remove();
	});

	return;




	$.ajax("/slbetrain/cgi-bin/chose.cgi?recid="+recid+"&yes=1", {
		"complete": function(data) {
			console.log(data);
			updateBody();
		}
	});
}

function choseNo(recid) {
	targ = $("div[data-recid='"+recid+"']")[0];
	console.log('left');
	console.log(targ);
	$(targ).animate({left:"-125%",opacity:0},500);
	$(targ.parentNode).animate({opacity:0},500, function() {
		console.log("removing "+recid);
		console.log(targ);
		targ.parentNode.remove();
	});
	return;




	$.ajax("/slbetrain/cgi-bin/chose.cgi?recid="+recid+"&no=1", {
		"complete": function(data) {
			console.log(data);
			updateBody();
		}
	});
}



window._x_startAt = 0;
window._x_maxAt = 0;
function updateBody() {

	bdy = $("div#root")[0];
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
	headline.innerHTML=("IS THIS A FISH?<br>"); //+buttonhtml);

	$.ajax("/slbetrain/cgi-bin/getconts.cgi", {
		"complete": function(data) {
			console.log(data);
			jdata = data.responseJSON;
			window._x_maxAt = jdata.length;
			for (var i=window._x_startAt; i<Math.min(jdata.length,window._x_startAt+PAGESIZE); i++) {
				var d=bdy.appendChild(document.createElement("div"));
				d.classList.add("trainbox");
				jdi = jdata[i][0]+'';
				hiresjpg = jdi.replace(".gif",".jpg").replace("conts","jpg").replace("_sfs","_sf2");
				d.innerHTML=('<div class="imgflip" data-recid="'+jdata[i]['recid']+'">'
					+'<img style="z-index:1" class="sample" data-recid="'+jdata[i]['recid']+'" src="data:image/jpg;base64,'+jdata[i]['still_context']+'">'
					+ '<img style="z-index:0" class="sampgif" data-recid="'+jdata[i]['recid']+'" src="data:image/gif;base64,'+jdata[i]['animated_context']+'"></div>'
					+'<div class="btnstrip">'
						+'<button class="train no" onclick="choseNo('+jdata[i]['recid']+')"><img src="fish_no.png"></button>'
						+'<button class="train yes" onclick="choseYes('+jdata[i]['recid']+')"><img src="fish_yes.png"</button>'
					+'</div>'
				);
			}
			$("div.imgflip").swipe({
				swipeLeft:function(e) {
					console.log("swiped left!");
					console.log(e);
					choseNo(e.target.attributes['data-recid'].value);
					//$(e.target.parentNode).animate({left:"-125%"},500);
					//e.preventDefault();
				},
				swipeRight:function(e) {
					console.log("swiped right!");
					console.log(e);
					choseYes(e.target.attributes['data-recid'].value);
					//$(e.target.parentNode).animate({left:"125%"},500);
					//e.preventDefault();
				}
			});
		}
	});

}

(function() {
	window._x_startAt = 0;
	updateBody();

})();






                










