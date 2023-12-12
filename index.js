
const PAGESIZE = 80;

// check if SSL is enabled; if not, redirect to SSL
if (window.location.protocol != "https:") {
	window.location.href = "https://"+window.location.host+window.location.pathname;
}
var user="tomh";
// implement simple user auth: if there is a cookie, use it, otherwise prompt for a username
// check if user/password authenticates with ldap server. if so, set cookie and proceed, otherwise prompt again
// if user is authenticated, show the training page
// if user is not authenticated, show the login page

function login() {
	user = $("input#user")[0].value;
	pass = $("input#pass")[0].value;
	$.ajax({
		url: "/slbetrain/cgi-bin/login.cgi?user="+user+"&pass="+pass,
		complete: function(data) {
			console.log(data);
			if (data.responseJSON['status'] == "ok") {
				// set cookie
				document.authtoken = data.responseJSON['token'];
				document.cookie = "authuser="+user;
				document.logintime = new Date();

				// show training page
				// updateBody();
				$("div#login")[0].style.display = "none";
				$("div#root")[0].style.display = "block";
				$("div#root")[0].style.opacity = 1;
				$("div#root")[0].style.zIndex = 1;
				$("div#root")[0].style.position = "relative";
				$("div#root")[0].style.top = 0;
				$("div#root")[0].style.left = 0;
			} else {
				// show error
				$("div#login")[0].style.display = "block";
				$("div#root")[0].style.display = "none";
				$("div#login")[0].style.opacity = 1;
				$("div#login")[0].style.zIndex = 1;
				$("div#login")[0].style.position = "relative";
				$("div#login")[0].style.top = 0;
				$("div#login")[0].style.left = 0;
			}
		}
	});
}



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


function chose(recid, yesno) {
	console.log("chose "+recid+" "+yesno);
	switch (yesno) {
		case "yes":
			leftAnim = "125%";
			direction = "left";
			break;
		case "no":
			leftAnim = "-125%";
			direction = "right";
			break;
		default:
			return;
	}

	var targ_imgflip = $("div.imgflip[data-recid="+recid+"]")[0];
	var targ_trainbox = $("div.trainbox[data-recid="+recid+"]")[0];
	var targ_btnstrip = $("div.btnstrip[data-recid="+recid+"]")[0];
	console.log("about to animate "+direction);
	$(targ_imgflip).animate({left:leftAnim,opacity:0},500);
	console.log("about to animate fadeout");
	$(targ_btnstrip).animate({opacity:0},500);
	$(targ_trainbox).animate({opacity:0},500,function() {
		console.log("completed the animation");
		console.log("sending user choice");
		$.ajax({
			url: "/slbetrain/cgi-bin/user_chose.cgi?recid="+recid+"&user="+user+"&choice="+yesno,
			complete: function(data) {
				console.log("completed the processing of user choice");
				console.log(data);
				console.log("removing "+recid);
				var targ_trainbox = $("div.trainbox[data-recid="+recid+"]")[0];
				$(targ_trainbox).remove();
				console.log("removed "+recid);
			}
		});
	});
}


// read "user" cookie
function readCookie(name) {
    var allcookies = document.cookie;
    console.log("All Cookies : " + allcookies );
    // Get all the cookies pairs in an array
    cookiearray = allcookies.split(';');
    // Now take key value pair out of this array
    for(var i=0; i<cookiearray.length; i++) {
        cname = cookiearray[i].split('=')[0];
        cvalue = cookiearray[i].split('=')[1];
        console.log ("Key is : " + cname + " and Value is : " + cvalue);
	if (cname == name) {
		return cvalue;
	}

    }
}

window._x_startAt = 0;
window._x_maxAt = 0;
function updateBody() {
	//user = readCookie('authuser');
	if (false) { // (user == null) {
		// show login page
		$("div#login")[0].style.display = "block";
		$("div#root")[0].style.display = "none";
		$("div#login")[0].style.opacity = 1;
		$("div#login")[0].style.zIndex = 1;
		$("div#login")[0].style.position = "relative";
		$("div#login")[0].style.top = 0;
		$("div#login")[0].style.left = 0;
		return;
	}
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
				d.setAttribute("data-recid",jdata[i]['recid']);
				jdi = jdata[i][0]+'';
				hiresjpg = jdi.replace(".gif",".jpg").replace("conts","jpg").replace("_sfs","_sf2");
				d.innerHTML=(`
				<div class="imgflip" data-recid="${jdata[i]['recid']}">
					<img style="z-index:1" class="sample" data-recid="${jdata[i]['recid']}" src="data:image/jpg;base64,${jdata[i]['still_context']}">
					<img style="z-index:0" class="sampgif" data-recid="${jdata[i]['recid']}" src="data:image/gif;base64,${jdata[i]['animated_context']}">
				</div>
				<div class="btnstrip" data-recid="${jdata[i]['recid']}">
					<button class="train no" onclick="chose(${jdata[i]['recid']},'no')"><img src="fish_no.png"></button>
					<button class="train yes" onclick="chose(${jdata[i]['recid']},'yes')"><img src="fish_yes.png"</button>
				</div>`
				);
			}
			$("div.imgflip").swipe({
				swipeLeft:function(e) {
					console.log("swiped left!");
					console.log(e);
					chose(e.target.attributes['data-recid'].value, "no");
					e.preventDefault();
				},
				swipeRight:function(e) {
					console.log("swiped right!");
					console.log(e);
					chose(e.target.attributes['data-recid'].value, "yes");
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

