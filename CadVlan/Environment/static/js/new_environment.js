var total_env = 1;

$(document).ready(function() {

    $('[data-toggle="tooltip"]').tooltip();

    autocompleteAjax ("/autocomplete/environment/", "env_list")
    fillEnvironmentField("father_env", "env_list");

    autocompleteAjax ("/autocomplete/environment/dc/", "router_env_list")
    fillEnvironmentField("router_env", "router_env_list");

    autocompleteAjax ("/autocomplete/environment/l3/", "l3_env_list")
    fillEnvironmentField("fisic_env", "l3_env_list");

    autocompleteAjax ("/autocomplete/environment/logic/", "logic_env_list")
    fillEnvironmentField("logic_env", "logic_env_list");

    autocompleteAjax ("/autocomplete/vrf/", "vrf_list")
    fillEnvironmentField("vrf", "vrf_list");

    $('#more_range').click(function() {

        let addBlockId = total_env = total_env + 1;

        let addBlockRow = document.createElement('div');
        $(addBlockRow).addClass('form-row-cadvlan');
        $(addBlockRow).attr('id','rangevlans_' + addBlockId);

        let addBlockElemSw = document.createElement('div');
        $(addBlockElemSw).addClass('form-group');
        $(addBlockElemSw).appendTo($(addBlockRow));

        let addBlockElemField = document.createElement('div');
        $(addBlockElemField).addClass('field-group');
        $(addBlockElemField).appendTo($(addBlockElemSw));

        let addBlockElemButton = document.createElement('div');
        $(addBlockElemButton).addClass('field-group');
        $(addBlockElemButton).appendTo($(addBlockElemSw));

        let labelInt = document.createElement('Label');
        $(labelInt).addClass('form-control-label');
        $(labelInt).attr('for', 'vlan_range_' + addBlockId);
        labelInt.innerHTML = "Range de Vlan " + addBlockId;
        $(labelInt).appendTo($(addBlockElemField));

        let inputInt = document.createElement('input');
        $(inputInt).addClass('form-control');
        $(inputInt).attr('type','text');
        $(inputInt).attr('id','vlan_range_' + addBlockId);
        $(inputInt).attr('name','vlan_range');
        $(inputInt).attr('placeholder','MIN-MAX');
        $(inputInt).appendTo($(addBlockElemField));

        let addBlockButton = document.createElement('button');
        $(addBlockButton).addClass('btn btn-social-bottom btn-responsive channel');
        $(addBlockButton).attr('type', 'button');
        $(addBlockButton).attr('style', 'margin-bottom: 0px;');
        $(addBlockButton).attr('id','btn_remove_envs' + addBlockId);
        $(addBlockButton).attr('name', addBlockId);
        $(addBlockButton).attr('data-toggle', 'tooltip');
        $(addBlockButton).attr('title','Remover.');
        addBlockButton.addEventListener( 'click', function(){
            let Ids = this.name;
            let elementId = "rangevlans_".concat(Ids);
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

        $(addBlockRow).appendTo($('#div_more_range'));

    });

});

function fillEnvironmentField(envFieldId, storageName) {

    let jsonEnv = JSON.parse(localStorage.getItem(storageName));
    let envField = document.getElementById(envFieldId);

    $.each(jsonEnv, function(){
        $(envField).append($("<option />").val(this.id).text(this.name));
    })
}

function autocompleteAjax(url, object) {
    $.ajax({
        url: url,
        dataType: "json",
        success: function(data) {
            if (data.errors.length > 0) {
                alert(data.errors);
            } else {
                localStorage.setItem(object, JSON.stringify(data.list));
            }
	}});
}

function envACL() {

    let checkBox = document.getElementById("acl_option");
    let envsDiv = document.getElementById("acl_info");

    if (checkBox.checked == true){
        envsDiv.style.display = "flex";
        envsDiv.style.flexDirection = "column";
    } else {
        envsDiv.style.display = "none";
    }
}
