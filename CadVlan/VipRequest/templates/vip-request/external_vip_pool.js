$("#dialog_pool").dialog({
        height: 650,
        width: 580,
        modal: true,
        autoOpen: false,
        draggable: false,
        resizable: true,
        buttons: {
            "Gravar": function(ev){

                var el = $('input:radio:checked[name=environment][attr],input:hidden[name=environment_vip]');                
                var envVipId = el.attr('attr') == undefined ? el.val() : el.attr('attr');

                var $this = $(this);
                var form =  $("#add_form_vip_pool");
                var formData = form.serialize() + '&' + $.param({ 'environment_vip': envVipId, 'token': $("#id_token").val() });

                $.ajax({ 
                    type: "POST",
                    url: form.attr('action'),
                    data: formData,
                    success: function(data){
                        var data_json = jQuery.parseJSON(data);

                        var envVipId = $('input:hidden[name=environment_vip]').val();
                        $.ajax({
                            data: {environment_vip_id : envVipId,
                                   token: $("#id_token").val()},
                            url: "{% url vip-request.external.load.options.pool %}",
                            success: function(data) {
                                $("select#id_pools").html(data);
                                $("select#id_pools").val(data_json.id);
                            },
                            error: function (error) {
                                message = jQuery.parseJSON(error.responseText);
                                addMessage(message);
                            }
                        });

                        $this.dialog("close");
                        alert(data_json.message);
                    },
                    error: function (error) {
                        message = jQuery.parseJSON(error.responseText);
                        addMessageModal(message);
                    }
                });
            },
            "Cancelar": function(error) {
                var $this = $(this);
                $this.dialog("close");
            }
        }
});

$("#btn_copy").button({ icons: {primary: "ui-icon-copy"} }).live("click", function(){

    var poolId = $("#id_pools").val();

    if (poolId !=  0 && poolId != null){

        $.ajax({
                data: { 
                    pool_id: poolId,
                    is_copy: 1,
                    token: $("#id_token").val()
                },
                url: "{% url vip-request.external.load.pool %}",
                success: function(data) {
                                                    
                    $("#content_pool").empty();
                    $("#content_pool").html(data);
                    $("#id_equip_name").removeAttr('disabled');
                    $("#btn_new_real").removeAttr('disabled');
                    $("#add_form_vip_pool").append($("#id_token"));
                    $("#dialog_pool").dialog("open");

                    autocomplete_external("{% url equipment.autocomplete.ajax.external %}", true, "id_equip_name", false);
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
        $.ajax({
                data: {env_vip_id: envVipId, token: $("#id_token").val()},
                url: "{% url vip-request.external.load.new.pool %}",
                success: function(data) {
                    $("#content_pool").html(data);
                    $("#id_equip_name").removeAttr('disabled');
                    $("#btn_new_real").removeAttr('disabled');
                    $("#add_form_vip_pool").append($("#id_token"));
                    $("#dialog_pool").dialog("open");

                    autocomplete_external("{% url equipment.autocomplete.ajax.external %}", true, "id_equip_name", false);
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

    if ($("input:hidden[value="+portVip+"]").length > 0){
        alert('Porta Vip já cadastrada.');
        return false;
    }

    if (poolId !=  0 && poolId != null){

        $.ajax({
            data: { 
                pool_id: poolId, token: $("#id_token").val()
            },
            url: "{% url vip-request.external.members.items %}",
            success: function(data) {
                $("#divMembers").append(data);
                $(".tablePoolMembers:last-child .portVip").html(portVip);
                $(".tablePoolMembers:last-child .ports_vip").val(portVip);
                $(".tablePoolMembers:last-child .portVip").editableTable();
                $("#idPort").val('');
                $('#id_pools').prop('selectedIndex', 0);
            },
            error: function (error) {
                message = jQuery.parseJSON(error.responseText);
                   addMessage(message);
            }
        });
    }
});

$("span[id^=editPool]").live("click", function(){
    var obj = $(this).parents();

    var poolId = obj.find("#idsPool").val();

    if (poolId !=  0 && poolId != null){

        $.ajax({
                data: {
                    pool_id: poolId,
                    is_copy: 0,
                    token: $("#id_token").val()
                },
                url: "{% url vip-request.external.load.pool %}",
                success: function(data) {
                    $("#content_pool").empty();
                    $("#content_pool").html(data);
                    $("#id_equip_name").removeAttr('disabled');
                    $("#btn_new_real").removeAttr('disabled');
                    $("#dialog_pool").dialog("open");
                    autocomplete_external("{% url equipment.autocomplete.ajax.external %}", true, "id_equip_name", false);
                },
                error: function (error) {
                    message = jQuery.parseJSON(error.responseText);
                    addMessage(message);
                }
        });

    }
});

$("span[id^=removePool]").live("click", function(){
    var $this = $(this);
    $this.parents("table:first").remove();
});

$("#btn_new_real").live("click", function(){
    var val_equip_name = $.trim($('#id_equip_name').val());
    if ( val_equip_name != '' ) {
        $.ajax({
            data: { id_environment: $('#id_environment').val(), equip_name: val_equip_name, token: $("#id_token").val() },
            url: "{% url pool.modal.ips.ajax.external %}",
            success: function(data, textStatus, xhr) {
                $('#content-ip').html(data);
                $("#dialog_ip").dialog("open");
            }
        });
    }
});

$('#btn_new_expect').live("click", function(){
    var expect_string = $.trim($('#expect_string').val());
    var id_environment = $('#id_environment').val();

    if(expect_string) {
        $.ajax({
                data: { 'expect_string': expect_string,
                        'id_environment': id_environment,
                        'token': $("#id_token").val() },
                url: "{% url pool.add.healthcheck.expect.external %}",
                success: function(data, xhr) {

                    $('#msg_new_health_check').fadeIn(1000);
                    $("#id_expect").append('<option value="'+data['expect_string']+'">'+data['expect_string']+'</option>');
                    $("#msg_new_health_check").html('<td></td><td style="color: #0073EA;font-weight: bold;padding-left: 5px;">'+data['mensagem']+'</td>');
                    $("#msg_new_health_check").delay(15000).fadeOut('slow');
                    $("#id_expect option:last").attr('selected', 'selected');
                    $("#btn_new_expect").button({ icons: {primary: "ui-icon-disk"} });
                    $("#expect_string").val('');
                }
            });
    }
});

$('#id_environment').live("change", function(){
    $('#id_health_check').html('<option value="">-</option>');

    var environmentId = this.value;

    if (environmentId != ''){
        $("#id_equip_name, #btn_new_real").prop('disabled', '');

        $.ajax({
                data: {'id_environment': environmentId,
                       'token': $("#id_token").val()},
                url: "{% url pool.ajax.get.opcoes.pool.by.ambiente.external %}",
                success: function(data, xhr) {
                    for (var i = 0; i < data.length; i++) {
                        $('#id_health_check').append('<option value="'+data[i]['opcao_pool']['description']+'">'+data[i]['opcao_pool']['description']+'</option>');
                    }
                }
            });
    }else{
        $("#id_equip_name, #btn_new_real").prop('disabled', 'disabled');
    }
});