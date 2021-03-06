$("#dialog_pool").dialog({
		height: 600,
		width: 700,
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
						$this.dialog("close");
			   			addMessage(data);
					},
					error: function (error) {
						message = jQuery.parseJSON(error.responseText);
					   	addMessageModal(message);
					}
				}).done(function(){

					var envVipId = $('input:hidden[name=environment_vip]').val();

					$.ajax({
						data: {environment_vip_id : envVipId, token: $("#id_token").val()},
						url: "{% url vip-request.external.load.options.pool %}",
						success: function(data) {
							$("select#id_pools").html(data);
						},
						error: function (error) {
							message = jQuery.parseJSON(error.responseText);
						   	addMessage(message);
						}	
					});
				});
			},
			"Cancelar": function(error) {
				var $this = $(this);
				$this.dialog("close");
			}
		}
});

function loadPoolMembers(poolId, portVip){
    if (poolId !=  0 && poolId != null){
        var tokenId = $("#id_token").val();
        $.ajax({
            url: "{% url vip-request.external.members.items %}",
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
        url: "{% url vip-request.external.load.options.pool %}",
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

    autocomplete_external("{% url equipment.autocomplete.ajax.external %}", true, "id_equip_name", false);
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

    autocomplete_external("{% url equipment.autocomplete.ajax.external %}", true, "id_equip_name", false);
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
                url: "{% url vip-request.external.load.pool %}",
                data: { 
                    pool_id: poolId,
                    is_copy: 1,
                    token: tokenId
                },
                url: "{% url vip-request.external.load.pool %}",
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
                url: "{% url vip-request.external.load.new.pool %}",
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

$("#btn_add_pool").button({ icons: {primary: "ui-icon-plus"} }).click(function(){

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

    loadPoolMembers(poolId, portVip);
});

$("span[id^=editPool]").live("click", function(){
    var obj = $(this).parents();

    var poolId = obj.find("#idsPool").val();

    if (poolId !=  0 && poolId != null){
        var tokenId = $("#id_token").val();
        $.ajax({
                url: "{% url vip-request.external.load.pool %}",
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
            url: "{% url pool.modal.ips.ajax.external %}",
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


$('#id_environment').live("change", function(){
    $('#id_healthcheck').html('<option value=""> - </option>');

    var environmentId = this.value;

    if (environmentId != ''){
        $("#id_equip_name, #btn_new_real").prop('disabled', false);
        var tokenId = $("#id_token").val();
        $.ajax({
                url: "{% url pool.ajax.get.opcoes.pool.by.ambiente.external %}",

                data: {
                    'id_environment': environmentId,
                    'token': tokenId
                },
                success: function(data, textStatus, xhr) {
                    //alert(data);
                    $('#id_healthcheck').empty().select2(select2_basic);
                    if(xhr.status == 200) {
                        for (var i = 0; i < data.length; i++) {
                            if(data[i]['opcao_pool']['type']) == 'HealthCheck'){
                                $('#id_healthcheck').append('<option value="' + data[i]['opcao_pool']['description'] + '">' + data[i]['opcao_pool']['description'] + '</option>');
                            }
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