var total_env = 1;
var opt_empty = '<option></option>'

$(document).ready(function() {

    $('[data-toggle="tooltip"]').tooltip();

    $.ajax({
        url: "/autocomplete/environment/",
        dataType: "json",
        success: function(dataenv) {
            if (dataenv.errors.length > 0) {
                alert(dataenv.errors);
            } else {
                localStorage.setItem("environment_list", JSON.stringify(dataenv.list));
            }
	}});

    fillEnvironmentField("#envs", "environment_list", "rangevlans");

    $('#btn_channel_env').click(function() {

        let addBlockId = total_env = total_env + 1;

        let addBlockRow = document.createElement('div');
        $(addBlockRow).addClass('form-row-cadvlan');
        $(addBlockRow).attr('id','form_env_vlans_' + addBlockId);

        let addBlockElemSw = document.createElement('div');
        $(addBlockElemSw).addClass('form-group');
        $(addBlockElemSw).appendTo($(addBlockRow));

        let labelEquip = document.createElement('Label');
        $(labelEquip).addClass('form-control-label');
        $(labelEquip).attr('for', 'channel_number' + addBlockId);
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
        $(addBlockElemInt).addClass('form-group');
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
        $(addBlockButton).appendTo($(addBlockRow));

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

function interfaceTrunk() {

    let checkBox = document.getElementById("trunk");
    let envsDiv = document.getElementById("more_envs");

    if (checkBox.checked == true){
        envsDiv.style.display = "flex";
        envsDiv.style.flexDirection = "column";
    }
}

function interfaceAccess() {

    let checkBox = document.getElementById("access");
    let envsDiv = document.getElementById("more_envs");

    if (checkBox.checked == true){
        envsDiv.style.display = "none";
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
