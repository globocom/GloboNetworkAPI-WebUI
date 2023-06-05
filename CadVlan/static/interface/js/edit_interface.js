function myFunction(interface_id) {
    "use strict";
    var element_id = "trunk".concat(interface_id),
        range_id = "range_vlans".concat(interface_id),
        env_id = "envs".concat(interface_id),
        checkBox = document.getElementById(element_id),
        text = document.getElementById("range_vlans");
    if (checkBox.checked == true) {
        document.getElementById(range_id).style.display = "block";
        document.getElementById(env_id).style.display = "block";
    } else {
        document.getElementById(range_id).style.display = "none";
        document.getElementById(env_id).style.display = "none";
    }
}

$(document).ready(function () {
	$("#dialog-form").dialog({
		width: 600,
		modal: true,
		autoOpen: false,
		draggable: false,
		resizable: false
	});
	$("#page_tab").tabs();

	$("#btn_can").button({ icons: {primary: "ui-icon-arrowthick-1-w"} }).click(function () {
		location.href = "{% url interface.list %}?search_equipment={{ equip_name }}";
	});

	$(".btn_close").button(
		{ icons: {primary: "ui-icon-close"}, text: false }
	).hover(
		function () {
			var num = $(this).attr("lang");
			$(".line_" + num).css("background-color", "red");
		},
		function () {
			var num = $(this).attr("lang");
			$(".line_" + num).css("background-color", "black");
		}
	);

	$("#connect0").click(function (event) {
	    console.log('back');
		event.preventDefault();
		var url0 = "/interface/connect/" + $(this).attr("href") + $(this).attr("lang") + "/0/";
		console.log(url0);
		$.ajax({
			url: url0,
			type: "GET",
			complete: function (xhr, status) {
				if (xhr.status == "500") {
					$("#dialog-form").dialog("close");
					location.reload();
				} else if (xhr.status == "278" || xhr.status == "302") {
					$("#dialog-form").dialog("close");
					window.location = xhr.getResponseHeader('Location');
				} else if (xhr.status == "200") {
					$("#dialog-form").html(xhr.responseText);
					$("#dialog-form").dialog("open");
				} else {
					$("#dialog-form").dialog("close");
				}
			}
		});
	});

	$("#connect1").click(function (event) {
		console.log('front');
		event.preventDefault();
		var url1 = "/interface/connect/" + $(this).attr("href") + $(this).attr("lang") + "/0/";
		console.log(url1);
		$.ajax({
			url: url1,
			type: "GET",
			complete: function (xhr, status) {
				if (xhr.status == "500") {
					$("#dialog-form").dialog("close");
					location.reload();
				} else if (xhr.status == "278" || xhr.status == "302") {
					$("#dialog-form").dialog("close");
					window.location = xhr.getResponseHeader('Location');
				} else if (xhr.status == "200") {
					$("#dialog-form").html(xhr.responseText);
					$("#dialog-form").dialog("open");
				} else {
					$("#dialog-form").dialog("close");
				}
			}
		});
	});

});