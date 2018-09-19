var total_env = 1;
var totalServer = 1;

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

    $.ajax({
        url: "/autocomplete/environment/",
        dataType: "json",
        success: function(data) {
            if (data.errors.length > 0) {
                alert(data.errors);
            } else {
                localStorage.setItem("environment_list", JSON.stringify(data.list));
            }
	}});

});

function moreEnvsCh(interface_id, foorloopNumber) {

        totalServer = totalServer + 1 + foorloopNumber;
        let idCounter = interface_id + "_div_" + totalServer;
        let addBlockRow = document.createElement('div');
        $(addBlockRow).addClass('rows');
        $(addBlockRow).attr('id','ch_form_env_vlans_' + idCounter);

        let addBlockElemSw = document.createElement('div');
        $(addBlockElemSw).addClass('text-fields');
        $(addBlockElemSw).appendTo($(addBlockRow));

        let labelEquip = document.createElement('Label');
        $(labelEquip).addClass('form-control-label');
        $(labelEquip).attr('for', 'ch_envs' + idCounter);
        labelEquip.innerHTML = "Ambiente";
        $(labelEquip).appendTo($(addBlockElemSw));

        let inputEquip = document.createElement('input');
        $(inputEquip).addClass('form-control bs-autocomplete');
        $(inputEquip).attr('autocomplete','off');
        $(inputEquip).attr('type','text');
        $(inputEquip).attr('id','ch_envs' + idCounter);
        $(inputEquip).attr('name','environmentCh' + interface_id);
        $(inputEquip).attr('placeholder','Busque pelo nome...');
        $(inputEquip).appendTo($(addBlockElemSw));

        let addBlockElemInt = document.createElement('div');
        $(addBlockElemInt).addClass('text-fields');
        $(addBlockElemInt).appendTo($(addBlockRow));

        let labelInt = document.createElement('Label');
        $(labelInt).addClass('form-control-label');
        $(labelInt).attr('for', 'ch_rangevlans' + idCounter);
        labelInt.innerHTML = "Range de Vlan";
        $(labelInt).appendTo($(addBlockElemInt));

        let inputInt = document.createElement('input');
        $(inputInt).addClass('form-control');
        $(inputInt).attr('type','text');
        $(inputInt).attr('id','ch_rangevlans' + idCounter);
        $(inputInt).attr('name','rangevlanCh' + interface_id);
        $(inputInt).attr('placeholder','Ex.: 1-10');
        $(inputInt).appendTo($(addBlockElemInt));

        let addBlockElemButton = document.createElement('div');
        $(addBlockElemButton).addClass('text-fields');
        $(addBlockElemButton).appendTo($(addBlockRow));

        let addBlockButton = document.createElement('button');
        $(addBlockButton).addClass('btn btn-social-bottom btn-responsive channel');
        $(addBlockButton).attr('type', 'button');
        $(addBlockButton).attr('id','btn_remove_envs_ch' + idCounter);
        $(addBlockButton).attr('name', interface_id);
        $(addBlockButton).attr('data-toggle', 'tooltip');
        $(addBlockButton).attr('title','Remover este ambiente.');
        addBlockButton.addEventListener( 'click', function(){
            let Ids = this.name;
            let elementId = "ch_form_env_vlans_".concat(idCounter);
            let node = document.getElementById(elementId);
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        } );
        $(addBlockButton).appendTo($(addBlockElemButton));

        let addBlockI = document.createElement('i');
        $(addBlockI).addClass('material-icons');
        $(addBlockI).attr('style', 'color:#FFD17C;font-size:15px;left:50%;');
        addBlockI.innerHTML = "delete";
        $(addBlockI).appendTo($(addBlockButton));

        let divEnvId = "#more_envs_ch".concat(interface_id);
        $(addBlockRow).appendTo($(divEnvId));

        let autocompleteId = '#ch_envs'.concat(idCounter);
        let vlanId = 'ch_rangevlans'.concat(idCounter);
        fillEnvironmentField( autocompleteId, "environment_list", vlanId);
}

function removeEnvsCh(interface_id, counter) {
    let divId = interface_id + "_div_" + counter;
    let elementId = "ch_env_row".concat(divId);
    let node = document.getElementById(elementId);
    if (node.parentNode) {
        node.parentNode.removeChild(node);
    }
}

function fillEnvironmentField(envFieldId, storageName, vlanFieldId) {
    $(envFieldId).autocomplete({
        source: JSON.parse(localStorage.getItem(storageName)),
        minLength: 1,
        select: function(event, ui) {
            let name = ui.item.label.split('(');
            name = name[1].split(')');
            name = name[0];
            $(envFieldId).val(ui.item.label);
            let vlanField = document.getElementById(vlanFieldId);
            $(vlanField).val(name);
        }
    });
}

function serverTrunk(interface_id, type_id) {
    let serverName = "server".concat(interface_id),
        trunkName = serverName.concat('trunk')
        trunk_id = trunkName.concat(type_id),
        divId = "more_envs_ch".concat(interface_id)
        envsDiv = document.getElementById(divId)
        checkBoxTrunk = document.getElementById(trunk_id);

    if (checkBoxTrunk.checked == true){
        envsDiv.style.display = "flex";
        envsDiv.style.flexDirection = "column";
        let ids = interface_id + "_div_1"
        let ch_envId = "#ch_envs".concat(ids);
        let ch_rangID = "ch_rangevlans".concat(ids);
        fillEnvironmentField( ch_envId, "environment_list", ch_rangID);

    } else {
        envsDiv.style.display = "none";
    }
}