
function loadPoolMembers(){
    var poolId = $("#id_pools").val();
    var portVip = $("#id_port_vip").val().trim();
    var l4_protocol = $('#id_l4_protocol option:checked');
    var l7_protocol = $('#id_l7_protocol option:checked');
    var l7_rule = $('#id_l7_rule option:checked');
    var l7_rule_value = $('#id_l7_value');
    var l7_order = $('#id_order');

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
                    new_table = $(data)

                    new_table.find(".vip_port_pool_l7_rule").html(l7_rule.html());
                    //new_table.find(".vip_port_pool_l7_value").html(l7_rule_value.val());
                    //new_table.find(".vip_port_pool_l7_ordem").html(l7_order.val());
                    new_table.find(".idsPool")
                        .attr('name', 'idsPool_'+portVip);
                    new_table.find(".ports_vip_pool_id")
                        .attr('name', 'ports_vip_pool_id_'+portVip);
                    new_table.find(".ports_vip_l7_rules")
                        .attr('name', 'ports_vip_l7_rules_'+portVip)
                        .val(l7_rule.val());
                    new_table.find(".ports_vip_l7_rules_orders")
                        .attr('name', 'ports_vip_l7_rules_orders_'+portVip)
                        .val(l7_order.val());
                    new_table.find(".ports_vip_l7_rules_values")
                        .attr('name', 'ports_vip_l7_rules_values_'+portVip)
                        .val(l7_rule_value.val());
                    if($('#id_l7_rule_check:checked').length > 0){
                        new_table.find('.l7_rule').show()
                    }
                    if($('.ports_vip_ports[value='+portVip+']').length > 0){
                        tr = new_table.find('#vip_port_pool_'+poolId)

                        table = $('.ports_vip_ports[value='+portVip+']')
                            .parents("table:first")
                            .find('tbody:first');

                        table.append(tr)

                        td = table.find('tr:first').find('td');

                        td.attr('rowspan',parseInt(td.attr('rowspan'))+1);

                    }
                    else{
                        $(new_table).find(".vip_port").html(portVip);
                        $(new_table).find(".vip_port_l4_protocol").html(l4_protocol.html());
                        $(new_table).find(".vip_port_l7_protocol").html(l7_protocol.html());
                        $(new_table).find(".ports_vip_ports").val(portVip);
                        $(new_table).find(".ports_vip_id").val('');
                        $(new_table).find(".ports_vip_l4_protocols").val(l4_protocol.val());
                        $(new_table).find(".ports_vip_l7_protocols").val(l7_protocol.val());
                        $("#divMembers").append(new_table);
                    }

                    // clear fields of pool select
                    $("#id_pools, #id_l7_protocol, #id_l4_protocol, #id_l7_rule").val('').select2(select2_basic);
                    $("#id_port_vip, #id_l7_value, #id_order").val('')
                    $('#id_l7_rule_check').removeAttr('checked')
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
    $(this).parents("table:first").parents("tr:first").remove();
    td = $(this).parents("table:first")
        .parents("tr:first")
        .parents("table:first")
        .find('tr:first')
        .find('td');
    td.attr('rowspan',parseInt(td.attr('rowspan'))-1);
});

$("span[id^=removePort]").live("click", function(){
    $(this).parents("table:first").remove();
});
