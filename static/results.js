$(document).ready(function () {
	$("[id*=playlists]").hide();
	$("[id*=expand]").on('click', function() {
		let btn = $(this).html();
		if (btn == "-") {
			$(this).html("+");
		}
		else {
			$(this).html("-");
		}
		let id = $(this).attr("id");
		console.log("ID: " + id);
		id = id.substring(6);
		let thisDiv = "#playlists" + id;
		console.log(thisDiv);
		$(thisDiv).toggle();
	});
});

$(document).ready(function () {
	$("[id*=tracks]").hide();
	$("[id*=view]").on('click', function() {
		let id = $(this).attr("id").substring(4);
		console.log(id);
		let thisDiv = "#tracks" + id;
		console.log(thisDiv);
		$(thisDiv).toggle();
	});
});