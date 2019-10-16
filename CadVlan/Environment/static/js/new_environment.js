var total_env = 1;

$(document).ready(function() {

    $('[data-toggle="tooltip"]').tooltip();

    autocompleteAjax ("/autocomplete/environment/", "father_env")
    autocompleteAjax ("/autocomplete/dc/", "router_env")
    autocompleteAjax ("/autocomplete/l3/", "fisic_env")
    autocompleteAjax ("/autocomplete/logic/", "logic_env")
    autocompleteAjax ("/autocomplete/vrf/", "vrf")

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

function autocompleteAjax(url, envFieldId) {
    $.ajax({
        url: url,
        async: false,
        dataType: "json",
        success: function(data) {
            if (data.errors.length > 0) {
                alert(data.errors);
            } else {
                let envField = document.getElementById(envFieldId);

                $.each(data.list, function(){
                    $(envField).append($("<option />").val(this.id).text(this.name));
                })
            }
	}});
}

function display_more_range() {

    let addBlockRow = document.createElement('div');
    $(addBlockRow).addClass('form-row-cadvlan');
    $(addBlockRow).attr('id','div_more_vlan_range');

    let addBlockGroup = document.createElement('div');
    $(addBlockGroup).addClass('form-group');
    $(addBlockGroup).appendTo($(addBlockRow));

    let addBlockField = document.createElement('div');
    $(addBlockField).addClass('field-group');
    $(addBlockField).appendTo($(addBlockGroup));

    let inputEquip = document.createElement('input');
    $(inputEquip).addClass('form-control');
    $(inputEquip).attr('id','more_vlan_range');
    $(inputEquip).attr('name','vlan_range2');
    $(inputEquip).attr('placeholder','MIN-MAX');
    $(inputEquip).attr('required');
    $(inputEquip).appendTo($(addBlockField));

    let addBlockField2 = document.createElement('div');
    $(addBlockField2).addClass('field-group');
    $(addBlockField2).appendTo($(addBlockGroup));

    let addBlockButton = document.createElement('button');
    $(addBlockButton).addClass('btn btn-social-bottom btn-responsive channel');
    $(addBlockButton).attr('type', 'button');
    $(addBlockButton).attr('id','remove_more_range');
    $(addBlockButton).attr('data-toggle', 'tooltip');
    $(addBlockButton).attr('title','Remover extra range.');
    addBlockButton.addEventListener( 'click', function(){
        let node = document.getElementById('div_more_vlan_range');
        if (node.parentNode) {
            node.parentNode.removeChild(node);
        }
        let bttAddId = document.getElementById("btt_more_range");
        bttAddId.disabled = false;
        } );
    $(addBlockButton).appendTo($(addBlockField2));

    let addBlockI = document.createElement('i');
    $(addBlockI).addClass('material-icons');
    $(addBlockI).attr('style', 'color:#FFD17C;font-size:15px;left:50%;');
    addBlockI.innerHTML = "delete";
    $(addBlockI).appendTo($(addBlockButton));

    let divId = document.getElementById("range_vlans");
    $(addBlockRow).appendTo($(divId));

    let bttAddId = document.getElementById("btt_more_range");
    bttAddId.disabled = true;
}