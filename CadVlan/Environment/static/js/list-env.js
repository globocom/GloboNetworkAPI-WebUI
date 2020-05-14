$(document).ready(function() {

	oTable = $("#envtable").dataTable({
		"aaSorting": [],
		"bJQueryUI": true,
		"sPaginationType": "full_numbers",
		"aoColumnDefs": [{ "bSortable": false, "aTargets": [ 4, 5] }]
	});

});

function childrenInfo() {
    var dataChildren = document.getElementById("clickable");
    var children = dataChildren.getAttribute("data-children");
    var child;
    var childrenJson = JSON5.parse(children);

    for (child of childrenJson) {
        alert(child);
    }


}
