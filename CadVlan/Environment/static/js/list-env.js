$(document).ready(function() {

	oTable = $("#envtable").DataTable({
		"aaSorting": [],
		"bJQueryUI": true,
		"sPaginationType": "full_numbers",
		"aoColumnDefs": [{ "bSortable": false, "aTargets": [ 4, 5] }]
	});

});

function format ( d ) {
    // `d` is the original data object for the row
    let network = "";

    if (d.configs.length==0) {
        network = "-"
    } else {
        for (net of d.configs) {
            network = network + '<p style="margin:0px;">'+net.network+'('+net.subnet_mask+')</p>'
        }
    }

    return '<tr id='+d.id+'>'+
            '<td onclick=childrenChildrenInfo('+d.id+
            ') data-children='+d.children+
            ' id=clickable'+d.id+'>'+d.id+'</td>'+
            '<td onclick=childrenChildrenInfo('+d.id+
            ') data-children='+d.children+
            ' id=clickable'+d.id+'>'+d.name+'</td>'+
            '<td onclick=childrenChildrenInfo('+d.id+
            ') data-children='+d.children+
            ' id=clickable'+d.id+'>'+d.vrf+'</td>'+
            '<td>'+network+'</td>'+
            '<td><div style="border: 1px solid #0D84A5;border-radius:3px;width: 20px;height: 20px;">'+
            '<a href="/environment/form/'+d.id+
            '" class="material-icons" style="font-size:20px;vertical-align:middle;color:#0D84A5">'+
            'edit</a></td>'+
            '<td><div style="border: 1px solid #0D84A5;border-radius:3px;width: 20px;height: 20px;">'+
            '<a href="/environment/remove/'+d.id+
            '" class="material-icons" style="font-size:20px;vertical-align:middle;color:#0D84A5">'+
            'delete</a></td>'+
            '</tr>';
}

function childrenInfo(envId) {
    let clickable = "clickable" + envId
    let dataChildren = document.getElementById(clickable);
    let children = dataChildren.getAttribute("data-children");
    let child;
    console.log(children)
    let childrenJson = JSON5.parse(children);
    let tr = document.getElementById(envId)
    let row = oTable.row(tr);


    for (child of childrenJson) {
        row.child(format(child)).show();
    }
}

function childrenChildrenInfo(envId) {
    let clickable = "clickable" + envId
    let dataChildren = document.getElementById(clickable);
    let childrenJson = dataChildren.getAttribute("data-children");
    let child;
    console.log(childrenJson)
    let tr = document.getElementById(envId)
    let row = oTable.row(tr);

    for (child of childrenJson) {
        row.child(format(child)).show();
    }
}

//function newRow(childrenJson, row){
//    for (child of childrenJson) {
//        row.child(format(child)).show();
//        if (child.children) {
//            let table = document.getElementById("envtable");
//            let tr = document.getElementById(child.id)
//            let row = oTable.row(tr);
//            newRow(child.children, row);
//        }
//    }
//}