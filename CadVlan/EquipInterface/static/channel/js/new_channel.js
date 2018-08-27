var total_sw = 1;
var total_env = 1;

$(document).ready(function() {

    $('[data-toggle="tooltip"]').tooltip();

    $('#btn_channel_sw').click(function() {

        var addBlockId = total_sw = total_sw + 1;

        var addBlockRow = document.createElement('div');
        $(addBlockRow).addClass('form-row-cadvlan');
        $(addBlockRow).attr('id','form_sw_div_' + addBlockId);

        var addBlockElemSw = document.createElement('div');
        $(addBlockElemSw).addClass('form-group');
        $(addBlockElemSw).appendTo($(addBlockRow));

        var labelEquip = document.createElement('Label');
        $(labelEquip).addClass('form-control-label');
        $(labelEquip).attr('for', 'form_switch_name' + addBlockId);
        labelEquip.innerHTML = "Nome do Switch";
        $(labelEquip).appendTo($(addBlockElemSw));

        var inputEquip = document.createElement('input');
        $(inputEquip).addClass('form-control');
        $(inputEquip).attr('required', 'required');
        $(inputEquip).attr('type','text');
        $(inputEquip).attr('name','switchname');
        $(inputEquip).attr('placeholder','Busque pelo nome...');
        $(inputEquip).appendTo($(addBlockElemSw));

        var addBlockElemInt = document.createElement('div');
        $(addBlockElemInt).addClass('form-group');
        $(addBlockElemInt).appendTo($(addBlockRow));

        var labelInt = document.createElement('Label');
        $(labelInt).addClass('form-control-label');
        $(labelInt).attr('for', 'form_switch_interface' + addBlockId);
        labelInt.innerHTML = "Interface";
        $(labelInt).appendTo($(addBlockElemInt));

        var inputInt = document.createElement('input');
        $(inputInt).addClass('form-control');
        $(inputInt).attr('required', 'required');
        $(inputInt).attr('type','text');
        $(inputInt).attr('name','switchInt');
        $(inputInt).appendTo($(addBlockElemInt));

        var addBlockButton = document.createElement('button');
        $(addBlockButton).addClass('btn btn-social-bottom btn-responsive channel');
        $(addBlockButton).attr('type', 'button');
        $(addBlockButton).attr('id','btn_remove' + addBlockId);
        $(addBlockButton).attr('name', addBlockId);
        $(addBlockButton).attr('data-toggle', 'tooltip');
        $(addBlockButton).attr('title','Remover este equipamento.');
        addBlockButton.addEventListener( 'click', function(){
            var Ids = this.name;
            var elementId = "form_sw_div_".concat(Ids);
            var node = document.getElementById(elementId);
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        } );
        $(addBlockButton).appendTo($(addBlockRow));

        var addBlockI = document.createElement('i');
        $(addBlockI).addClass('material-icons');
        $(addBlockI).attr('style', 'color:#FFD17C;font-size:15px;left:50%;');
        addBlockI.innerHTML = "delete";
        $(addBlockI).appendTo($(addBlockButton));

        $(addBlockRow).appendTo($('#sw_content'));
    });

    $('#btn_channel_env').click(function() {

        var addBlockId = total_env = total_env + 1;

        var addBlockRow = document.createElement('div');
        $(addBlockRow).addClass('form-row-cadvlan');
        $(addBlockRow).attr('id','form_env_vlans_' + addBlockId);

        var addBlockElemSw = document.createElement('div');
        $(addBlockElemSw).addClass('form-group');
        $(addBlockElemSw).appendTo($(addBlockRow));

        var labelEquip = document.createElement('Label');
        $(labelEquip).addClass('form-control-label');
        $(labelEquip).attr('for', 'channel_number' + addBlockId);
        labelEquip.innerHTML = "Ambiente";
        $(labelEquip).appendTo($(addBlockElemSw));

        var inputEquip = document.createElement('input');
        $(inputEquip).addClass('form-control');
        $(inputEquip).attr('type','text');
        $(inputEquip).attr('name','environment');
        $(inputEquip).attr('placeholder','Busque pelo nome...');
        $(inputEquip).appendTo($(addBlockElemSw));

        var addBlockElemInt = document.createElement('div');
        $(addBlockElemInt).addClass('form-group');
        $(addBlockElemInt).appendTo($(addBlockRow));

        var labelInt = document.createElement('Label');
        $(labelInt).addClass('form-control-label');
        $(labelInt).attr('for', 'rangevlans' + addBlockId);
        labelInt.innerHTML = "Interface";
        $(labelInt).appendTo($(addBlockElemInt));

        var inputInt = document.createElement('input');
        $(inputInt).addClass('form-control');
        $(inputInt).attr('type','text');
        $(inputInt).attr('name','rangevlans' + addBlockId);
        $(inputInt).attr('placeholder','Ex.: 1-10');
        $(inputInt).appendTo($(addBlockElemInt));

        var addBlockButton = document.createElement('button');
        $(addBlockButton).addClass('btn btn-social-bottom btn-responsive channel');
        $(addBlockButton).attr('type', 'button');
        $(addBlockButton).attr('id','btn_remove_envs' + addBlockId);
        $(addBlockButton).attr('name', addBlockId);
        $(addBlockButton).attr('data-toggle', 'tooltip');
        $(addBlockButton).attr('title','Remover este ambiente.');
        addBlockButton.addEventListener( 'click', function(){
            var Ids = this.name;
            var elementId = "form_env_vlans_".concat(Ids);
            var node = document.getElementById(elementId);
            if (node.parentNode) {
                node.parentNode.removeChild(node);
            }
        } );
        $(addBlockButton).appendTo($(addBlockRow));

        var addBlockI = document.createElement('i');
        $(addBlockI).addClass('material-icons');
        $(addBlockI).attr('style', 'color:#FFD17C;font-size:15px;left:50%;');
        addBlockI.innerHTML = "delete";
        $(addBlockI).appendTo($(addBlockButton));

        $(addBlockRow).appendTo($('#more_envs'));
    });
});

function interfaceTrunk() {

    var checkBox = document.getElementById("trunk");
    var envsDiv = document.getElementById("more_envs");

    if (checkBox.checked == true){
        envsDiv.style.display = "flex";
        envsDiv.style.flexDirection = "column";
    }
}

function interfaceAccess() {

    var checkBox = document.getElementById("access");
    var envsDiv = document.getElementById("more_envs");

    if (checkBox.checked == true){
        envsDiv.style.display = "none";
    }
}