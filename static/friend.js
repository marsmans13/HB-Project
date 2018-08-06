$(document).ready(function () {
	$("p [id*=plBtn]").html("-");
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
	$("[id*=re]").on('click', function() {
		let reId = $(this).attr("id");
		let trackId = reId.substring(3);
		// console.log(trackId);
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
		// console.log(trackId);
		try {
			$("#" + trackId)[0].currentTime += 30;
		}
		catch {
			null;
		}
	});
});