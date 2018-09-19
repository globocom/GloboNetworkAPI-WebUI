var total_env = 1;
var totalServer = 1;

$(document).ready(function() {

	$("#btn_can").button({ icons: {primary: "ui-icon-arrowthick-1-w"} }).click(function() {
		location.href = "{% url interface.list %}?search_equipment={{ equip_name }}";
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

    $.ajax({
        url: "/autocomplete/equipment/",
        dataType: "json",
        success: function(data) {
            if (data.errors.length > 0) {
                alert(data.errors);
            } else {
                localStorage.setItem("equipment_list", JSON.stringify(data.list));
            }
	}});

    fillEnvironmentField( "#envs", "environment_list", "rangevlans");
    fillEnvironmentField( "#ch_envs", "environment_list", "ch_rangevlans");

    fillInterfaceField("#form_switch_name", "equipment_list", "form_switch_interface");

    $('#associateLink').click(function() {
        let buttonAss = document.getElementById('associate_interfaces');
        let buttonPlus = document.getElementById('associateLink');
        buttonAss.style.display = "grid";
        buttonPlus.style.backgroundColor = "#fff9ea";
    });

    $('#btn_channel_env').click(function() {

        let addBlockId = total_env = total_env + 1;

        let addBlockRow = document.createElement('div');
        $(addBlockRow).addClass('rows');
        $(addBlockRow).attr('id','form_env_vlans_' + addBlockId);

        let addBlockElemSw = document.createElement('div');
        $(addBlockElemSw).addClass('text-fields');
        $(addBlockElemSw).appendTo($(addBlockRow));

        let labelEquip = document.createElement('Label');
        $(labelEquip).addClass('form-control-label');
        $(labelEquip).attr('for', 'envs' + addBlockId);
        labelEquip.innerHTML = "Ambiente";
        $(labelEquip).appendTo($(addBlockElemSw));

        let inputEquip = document.createElement('input');
        $(inputEquip).addClass('form-control bs-autocomplete');
        $(inputEquip).attr('autocomplete','off');
        $(inputEquip).attr('type','text');
        $(inputEquip).attr('id','envs' + addBlockId);
        $(inputEquip).attr('name','environment');
        $(inputEquip).attr('placeholder','Busque pelo nome...');
        $(inputEquip).appendTo($(addBlockElemSw));

        let addBlockElemInt = document.createElement('div');
        $(addBlockElemInt).addClass('text-fields');
        $(addBlockElemInt).appendTo($(addBlockRow));

        let labelInt = document.createElement('Label');
        $(labelInt).addClass('form-control-label');
        $(labelInt).attr('for', 'rangevlans' + addBlockId);
        labelInt.innerHTML = "Range de Vlan";
        $(labelInt).appendTo($(addBlockElemInt));

        let inputInt = document.createElement('input');
        $(inputInt).addClass('form-control');
        $(inputInt).attr('type','text');
        $(inputInt).attr('id','rangevlans' + addBlockId);
        $(inputInt).attr('name','rangevlan');
        $(inputInt).attr('placeholder','Ex.: 1-10');
        $(inputInt).appendTo($(addBlockElemInt));

        let addBlockElemButton = document.createElement('div');
        $(addBlockElemButton).addClass('text-fields');
        $(addBlockElemButton).appendTo($(addBlockRow));

        let addBlockButton = document.createElement('button');
        $(addBlockButton).addClass('btn btn-social-bottom btn-responsive channel');
        $(addBlockButton).attr('type', 'button');
        $(addBlockButton).attr('id','btn_remove_envs' + addBlockId);
        $(addBlockButton).attr('name', addBlockId);
        $(addBlockButton).attr('data-toggle', 'tooltip');
        $(addBlockButton).attr('title','Remover este ambiente.');
        addBlockButton.addEventListener( 'click', function(){
            let Ids = this.name;
            let elementId = "form_env_vlans_".concat(Ids);
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

        $(addBlockRow).appendTo($('#more_envs'));

        let autocompleteId = '#envs'.concat(addBlockId);
        let vlanId = 'rangevlans'.concat(addBlockId);
        fillEnvironmentField( autocompleteId, "environment_list", vlanId);

    });

});

function removeEnvs(counter) {
    let elementId = "env_row".concat(counter);
    let node = document.getElementById(elementId);
    if (node.parentNode) {
        node.parentNode.removeChild(node);
    }
}

function removeEnvsCh(interface_id, counter) {
    let divId = interface_id + "_div_" + counter;
    let elementId = "ch_env_row".concat(divId);
    let node = document.getElementById(elementId);
    if (node.parentNode) {
        node.parentNode.removeChild(node);
    }
}

function fillInterfaceField(equipmentFieldId, storageName, interfaceFieldId) {
    $(equipmentFieldId).autocomplete({
        source: JSON.parse(localStorage.getItem(storageName)),
        minLength: 1,
        select: function(event, ui) {
            $(equipmentFieldId).val(ui.item.label);
            let url = "interface/connect/1/front/".concat(ui.item.label);
            $.ajax({
                url: url,
                type: "GET",
                success: function(data) {
                    data_list = JSON.parse(data).list;
                    var dropdown = document.getElementById(interfaceFieldId);
                    while (dropdown.length > 1) {
                        dropdown.remove(dropdown.length-1);
                    }
                    let option;
                    for (let i = 0; i < data_list.length; i++) {
                        option = document.createElement('option');
                        option.text = data_list[i].interface;
                        option.value = data_list[i].id;
                        dropdown.add(option);
                    }
                },
                error: function (xhr, error, thrown) {
                    location.reload();
                }
            });
        }
    });
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

function myFunction(interface_id) {
    let element_id = "trunk".concat(interface_id);
    let range_id = "range_vlans".concat(interface_id);
    let env_id = "envs".concat(interface_id);
    let checkBox = document.getElementById(element_id);
    let text = document.getElementById("range_vlans");

    if (checkBox.checked == true){
        document.getElementById(range_id).style.display = "block";
        document.getElementById(env_id).style.display = "block";
    } else {
        document.getElementById(range_id).style.display = "none";
        document.getElementById(env_id).style.display = "none";
    }
}

function channelTrunk(interface_id) {
    let trunk_id = "channeltrunk".concat(interface_id);
    let envsDiv = document.getElementById("more_envs");
    let checkBoxTrunk = document.getElementById(trunk_id);

    if (checkBoxTrunk.checked == true){
        envsDiv.style.display = "flex";
        envsDiv.style.flexDirection = "column";
    } else {
        envsDiv.style.display = "none";
    }
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