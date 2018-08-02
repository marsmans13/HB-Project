$(document).ready(function () {
	$("[id*=show-tracks]").hide();
	$("p [id*=plBtn]").on('click', function() {
		let btn = $(this).html();
		if (btn == "-") {
			$(this).html("+");
		}
		else {
			$(this).html("-");
		}
		let id = $(this).attr("id");
		let thisDiv = "#show-tracks-" + id;
		$(thisDiv).toggle();
		// $(this).html("-");
	});
});

$(document).ready(function () {
	$("[id*=delete-track]").hide();
	$("[id*=menu-track]").on('click', function() {
		let id = $(this).attr("id");
		let thisDiv = "#delete-" + id.substring(5);
		$(thisDiv).toggle();
	})

	// --------Need to store in database and set current time here-------

	$("audio").on('click', function() {
		let cTime = $(this)[0].currentTime;
		console.log(cTime);
		let audioSrc = $(this).attr("src");
		localStorage.setItem(audioSrc, cTime);
		console.log(audioSrc);

		let savedTime = localStorage.getItem(audioSrc);
		// localStorage.removeItem("track-item");
		// console.log("Storage" + ": " + savedTime);
		let trackId = $(this).attr("id");
		console.log(trackId);
	});

	// ------------------------------------------------------------------

	$("[id*=re]").on('click', function() {
		let reId = $(this).attr("id");
		let trackId = reId.substring(3);
		try {
			$("#" + trackId)[0].currentTime -= 10;
		}
		catch {
			null;
		}
	});
	$("[id*=ff]").on('click', function() {
		let ffId = $(this).attr("id");
		let trackId = ffId.substring(3);
		try {
			$("#" + trackId)[0].currentTime += 30;
		}
		catch {
			null;
		}
	});
});


$(document).ready(function () {
	$("#edit-form").hide();
	$("#edit-btn").on('click', function() {
		$("#edit-form").toggle();
	});
});


$(document).ready(function () {
	$("#playlist-form").hide();
	$("#show-playlist-form").on('click', function() {
		$("#playlist-form").toggle();
	});
});