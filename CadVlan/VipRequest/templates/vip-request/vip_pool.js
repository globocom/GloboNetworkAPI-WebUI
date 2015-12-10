
function loadPoolMembers(poolId, portVip){
    if (poolId !=  0 && poolId != null){
        var tokenId = $("#id_token").val();
        $.ajax({
            url: "{% url vip-request.members.items %}",
            data: {
                pool_id: poolId,
                token: tokenId
            },
            success: function(data, textStatus, xhr) {
                if(xhr.status == 200) {
                    $("#divMembers").append(data);
                    $(".tablePoolMembers:last-child .portVip").html(portVip);
                    $(".tablePoolMembers:last-child .ports_vip").val(portVip);
                    $(".tablePoolMembers:last-child .portVip").editableTable();
                    $("#idPort, #id_pools").val('');
                }
                else if(xhr.status == 203){
                   alert(data);
                }
            },
            error: function (error) {
                message = jQuery.parseJSON(error.responseText);
                addMessage(message);
            }
        });
    }
}

function loadOptionsPool(poolId){
    var envVipId = $('input:hidden[name=environment_vip]').val();
    var tokenId = $("#id_token").val();

    $.ajax({
        url: "{% url vip-request.load.options.pool %}",
        data: {
            environment_vip_id: envVipId,
            token: tokenId
        },
        success: function (data) {
            $("select#id_pools").html(data);

            if (poolId){
                $("select#id_pools").val(poolId);
            }
        },
        error: function (error) {
            message = jQuery.parseJSON(error.responseText);
            addMessage(message);
        }
    });
}

function buildContentNewPool(data) {
    $("#content_pool").html(data);
    $("#id_equip_name, #btn_new_real").prop('disabled', false);
    $("#dialog_pool").dialog("open");

    openDialog(function(idPool){
        loadOptionsPool(idPool);
    });

    autocomplete("{% url equipment.autocomplete.ajax %}", true, "id_equip_name", false);
}

function buildContentEditPool(data) {
    $("#content_pool").html(data);
    $("#id_equip_name, #btn_new_real").prop('disabled', false);
    $("#dialog_pool").dialog("open");

    openDialog(function(idPool){
        var objTable = $('#tablePoolMembers_'+idPool);
        var portVip =   objTable.find('[name="ports_vip"]').val();

        objTable.remove();

        loadPoolMembers(idPool, portVip);
        loadOptionsPool(false);
    });

    autocomplete("{% url equipment.autocomplete.ajax %}", true, "id_equip_name", false);
}

function openDialog(callback) {
    $("#dialog_pool").dialog({
            height: 650,
            width: 580,
            modal: true,
            draggable: false,
            resizable: true,
            buttons: {
                "Gravar": function(ev){

                    var el = $('input:radio:checked[name=environment][attr],input:hidden[name=environment_vip]');
                    var envVipId = el.attr('attr') == undefined ? el.val() : el.attr('attr');
                    var idToken = $("#id_token").val();

                    var $this = $(this);
                    var form =  $("#add_form_vip_pool");
                    var formData = form.serialize() + '&' + $.param({'environment_vip': envVipId, 'token': idToken});

                    $.ajax({
                        type: "POST",
                        url: form.attr('action'),
                        data: formData,
                        success: function(data, textStatus, xhr){
                            if (xhr.status == 200) {
                                if (callback){
                                    callback(data.id);
                                }
                                $this.dialog("close");
                                alert(data.message);
                            }else if(xhr.status == 203){
                                alert(data);
                            }
                        },
                        error: function (error) {
                            message = jQuery.parseJSON(error.responseText);
                            addMessageModal(message);
                        }
                    });
                },
                "Cancelar": function() {
                    var $this = $(this);
                    $this.dialog("close");
                }
            }
    });
}

$("#btn_copy").button({ icons: {primary: "ui-icon-copy"} }).live("click", function(){

    var poolId = $("#id_pools").val();

    if (poolId !=  0 && poolId != null){
        var tokenId = $("#id_token").val();
        $.ajax({
                url: "{% url vip-request.load.pool %}",
                data: { 
                    pool_id: poolId,
                    is_copy: 1,
                    token: tokenId
                },
                url: "{% url vip-request.load.pool %}",
                success: function(data, textStatus, xhr) {

                    if (xhr.status == 200) {
                        buildContentNewPool(data);
                    }
                    else if(xhr.status == 203){
                        alert(data);
                    }
                },
                error: function (error) {
                    message = jQuery.parseJSON(error.responseText);
                    addMessage(message);
                }
        });

    }
});

$("#btn_new_pool").button({ icons: {primary: "ui-icon-document"} }).click(function(){

    var envVipId = $('input:hidden[name=environment_vip]').val();

    if(envVipId && envVipId !=  0 && envVipId != null){
        var tokenId = $("#id_token").val();
        $.ajax({
                url: "{% url vip-request.load.new.pool %}",
                data: {
                    env_vip_id: envVipId,
                    token: tokenId
                },
                success: function(data, textStatus, xhr) {

                    if (xhr.status == 200) {
                        buildContentNewPool(data);
                    }
                    else if(xhr.status == 203){
                       alert(data);
                    }
                },
                error: function (error) {
                    message = jQuery.parseJSON(error.responseText);
                    addMessage(message);
                }
        });
    }
});

$("#btn_add_pool").button({ icons: {primary: "ui-icon-plus"} }).live("click", function(){

    var poolId = $("#id_pools").val();
    var portVip = $("#idPort").val().trim();

    if(isNaN(portVip)){
        alert('Porta Vip deve ser um número.');
        $("#idPort").val('');
        return false;
    }

    if(portVip.length == 0){
        alert('Deve-se preencher o campo de porta.');
        return false;
    }

    loadPoolMembers(poolId, portVip);
});

$("span[id^=editPool]").live("click", function(){
    var obj = $(this).parents();

    var poolId = obj.find("#idsPool").val();

    if (poolId !=  0 && poolId != null){
        var tokenId = $("#id_token").val();
        $.ajax({
                url: "{% url vip-request.load.pool %}",
                data: {
                    pool_id: poolId,
                    is_copy: 0,
                    token: tokenId
                },
                success: function(data,textStatus, xhr) {

                    if(xhr.status == 200) {
                        buildContentEditPool(data);
                    }
                    else if(xhr.status == 203){
                       alert(data);
                    }
                },
                error: function (error) {
                    message = jQuery.parseJSON(error.responseText);
                    addMessage(message);
                }
        });

    }
});

$("span[id^=removePool]").live("click", function(){
    $(this).parents("table:first").remove();
});

$("#btn_new_real").live("click", function(){
    var val_equip_name = $.trim($('#id_equip_name').val());
    if ( val_equip_name != '' ) {
        $.ajax({
            url: "{% url pool.modal.ips.ajax %}",
            data: {
                id_environment: $('#id_environment').val(),
                equip_name: val_equip_name,
                token: $("#id_token").val()
            },
            success: function(data, textStatus, xhr) {
                if(xhr.status == 200) {
                    $('#content-ip').html(data);
                    $("#dialog_ip").dialog("open");
                }
                else if(xhr.status == 203){
                   alert(data);
                }
            }
        });
    }
});

$('#btn_new_expect').live("click", function(){
    var expect_string = $.trim($('#expect_string').val());
    var id_environment = $('#id_environment').val();

    if(expect_string) {
        var tokenId = $("#id_token").val();
        $.ajax({
                url: "{% url pool.add.healthcheck.expect %}",
                data: {
                    'expect_string': expect_string,
                    'id_environment': id_environment,
                    'token': tokenId
                },
                success: function(data, textStatus, xhr) {

                    if(xhr.status == 200) {
                        $('#msg_new_health_check').fadeIn(1000);
                        $("#id_expect").append('<option value="' + data['expect_string'] + '">' + data['expect_string'] + '</option>');
                        $("#msg_new_health_check").html('<td></td><td style="color: #0073EA;font-weight: bold;padding-left: 5px;">' + data['mensagem'] + '</td>');
                        $("#msg_new_health_check").delay(15000).fadeOut('slow');
                        $("#id_expect option:last").attr('selected', 'selected');
                        $("#btn_new_expect").button({ icons: {primary: "ui-icon-disk"} });
                        $("#expect_string").val('')
                    }
                    else if(xhr.status == 203){
                       alert(data);
                    }
                }
            });
    }
});

$('#id_environment').live("change", function(){
    $('#id_health_check').html('<option value=""> - </option>');

    var environmentId = this.value;

    if (environmentId != ''){
        $("#id_equip_name, #btn_new_real").prop('disabled', false);
        var tokenId = $("#id_token").val();
        $.ajax({
                url: "{% url pool.ajax.get.opcoes.pool.by.ambiente %}",

                data: {
                    'id_environment': environmentId,
                    'token': tokenId
                },
                success: function(data, textStatus, xhr) {
                    if(xhr.status == 200) {
                        for (var i = 0; i < data.length; i++) {
                            $('#id_health_check').append('<option value="' + data[i]['opcao_pool']['description'] + '">' + data[i]['opcao_pool']['description'] + '</option>');
                        }
                    }
                    else if(xhr.status == 203){
                       alert(data);
                    }
                }
            });
    }else{
        $("#id_equip_name, #btn_new_real").prop('disabled', true);
    }
});