
function loadPoolMembers(){
    var poolId = $("#id_pools").val();
    var portVip = $("#id_port_vip").val().trim();
    var l4_protocol = $('#id_l4_protocol option:checked');
    var l7_protocol = $('#id_l7_protocol option:checked');

    if(isNaN(portVip)){
        alert('Porta Vip deve ser um número.');
        $("#id_port_vip").val('');
        return false;
    }

    if(portVip.length == 0){
        alert('Deve-se preencher o campo de porta.');
        return false;
    }

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
                    $(".tablePoolMembers:last-child .vip_port").html(portVip);
                    $(".tablePoolMembers:last-child .vip_port_l4_protocol").html(l4_protocol.html());
                    $(".tablePoolMembers:last-child .vip_port_l7_protocol").html(l7_protocol.html());
                    $(".tablePoolMembers:last-child .ports_vip_ports").val(portVip);
                    $(".tablePoolMembers:last-child .ports_vip_id").val('');
                    $(".tablePoolMembers:last-child .ports_vip_l4_protocols").val(l4_protocol.val());
                    $(".tablePoolMembers:last-child .ports_vip_l7_protocols").val(l7_protocol.val());
                    $("#id_pools, #id_l7_protocol, #id_l4_protocol").val('').select2(select2_basic);
                    $("#id_port_vip").val('')
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
    loadPoolMembers();
});


$("span[id^=removePool]").live("click", function(){
    $(this).parents("table:first").remove();
});