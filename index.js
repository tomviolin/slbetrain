(function() {

	// $ = document.querySelector.bind(document); // $ is a shorthand for document.querySelector

	bdy = $("body")[0];
	headline = bdy.appendChild(document.createElement("p"));
	headline.classList.add("title");
	headline.innerHTML=("FISH IDENTIFICATION TRAINING");
	$.ajax("/slbetrain/cgi-bin/getconts.cgi", {
		"complete": function(data) {
			console.log(data);
			jdata = data.responseJSON;
			for (var i=0; i<jdata.length; i++) {
				var d=bdy.appendChild(document.createElement("div"));
				d.classList.add("trainbox");
				jdi = jdata[i][0]+'';
				hiresjpg = jdi.replace(".gif",".jpg").replace("conts","jpg").replace("_sfs","_sf2");
				d.innerHTML=('<div class="imgflip"><img style="z-index:1" class="flipper sample" src="/slbetrain/trains/'+hiresjpg+'">'
								+ '<img style="z-index:0" class="flipper sampgif" src="/slbetrain/trains/'+jdata[i][0]+'"></div>'
					+'<div class="btstrip">'
						+'<button class="train yes" style="float:left" data-train="'+jdata[i][1]+'">YES</button>'
						+'<button class="train no" style="float:right" data-train="'+jdata[i][1]+'">NO</button>'

				);
			}
		}
	});


})();
