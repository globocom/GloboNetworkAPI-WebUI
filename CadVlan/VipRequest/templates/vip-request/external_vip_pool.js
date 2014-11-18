$("#dialog_pool").dialog({
		height: 600,
		width: 1000,
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

$("#btn_copy").button({ icons: {primary: "ui-icon-copy"} }).live("click", function(){

	var poolId = $("#id_pools").val();

	if (poolId !=  0 && poolId != null){

		$.ajax({
				data: { 
					pool_id: poolId, token: $("#id_token").val()
				},
				url: "{% url vip-request.external.load.pool %}",
				success: function(data) {
													
					$("#content_pool").empty();
					$("#content_pool").html(data);
					$("#id_equip_name").removeAttr('disabled');
					$("#btn_new_real").removeAttr('disabled');
					$("#add_form_vip_pool").append($("#id_token"));
					$("#dialog_pool").dialog("open");		
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

	if (poolId !=  0 && poolId != null){

		$.ajax({
			data: { 
				pool_id: poolId, token: $("#id_token").val()
			},
			url: "{% url vip-request.external.members.items %}",
			success: function(data) {
				$(".tablesMembers").append(data);			
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