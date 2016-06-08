	var oldPortVip;

    var opt_empty = '<option></option>'

	$("#page_tab").tabs();

	$("#btn_sav").button({ icons: {primary: "ui-icon-disk"} });

	$("#btn_can").button({ icons: {primary: "ui-icon-cancel"} }).click(function(){
		location.href = "{% url vip-request.list %}";
	});

    $("#idPort").live("keyup", function(e){
        $(this).val($(this).val().replace(/[^0-9]+/g,''));
	});

	$(".numbersOnly").live('focus', function(){
        $(this).attr("style", "width: 35px; height: 14px;");
		oldPortVip = $(this).val();
	});
	
	$(".numbersOnly").live('focusout', function(){
        $(this).attr("style", "width: 35px; height: 14px;");
		var this_element = $(this);
        var tableEditing = this_element.parents("#tablePoolMembers");

		$(this).next().click(function(){
			if (!check_port_vip(this_element)){
				return false;
			}

            var newPortVIp = this_element.val();

            check_port_vip(this_element);

            update_pools_new_vip(tableEditing, oldPortVip, newPortVIp);
		});
	});
	
	$('.numbersOnly').live("keydown", function(e){

          $(this).attr("style", "width: 35px; height: 14px;");

    	  if(e.keyCode == 9 || e.keyCode == 13){

            var this_element = $(this);
            var tableEditing = this_element.parents("#tablePoolMembers");

			if (!check_port_vip($(this))){
				
				e.preventDefault();
	    		label = $(this).parent().parent().parent().next().find('.editable');
	      		label.click();
				return false;
			}else{


	    		label = $(this).parent().parent().parent().next().find('.editable');
	      		$(this).next().click();
	      		label.click();

                var newPortVIp = $(this).val();

                check_port_vip(this_element);

	      		update_pools_new_vip(tableEditing, oldPortVip, newPortVIp);

	      		return false;
			}

			      	  	
    	  }
	}).live("keyup", function(e){ 
        $(this).val($(this).val().replace(/[^0-9]+/g,''));
	});

	
	// Check if port vip is duplicated
	function check_port_vip(element){
        var elementName = element.parent().parent().next().attr('name');
		if( elementName == 'ports_vip' || element.hasClass("numbersOnly")){

			is_valid = true;
			
			if (oldPortVip != element.val()){
				$("input[name=ports_vip]").each(function(){
					if ($(this).val() == element.val()){
						is_valid = false;
					}
				});
			}
			
			if (element.val() == "" && oldPortVip != ""){
				element.val(oldPortVip);
				alert('Deve-se preencher todos os campos de portas.');
				return false;
			}
				
			
			if (!is_valid){
				element.val(oldPortVip);
				alert('Porta Vip já cadastrada.');
				return false;
			}
			
			return true;
		}
		return true;
	}

	
	$("select[name=step_finality]").change(function(){
		$.ajax({
			data: { finality: $(this).val(), token: $("#id_token").val() },
			url: "{% if external %}{% url vip-request.client.ajax.external %}{% else %}{% url vip-request.client.ajax %}{% endif %}",
			dataType: 'text',
			success: function(data, textStatus, xhr) {
			
				if (xhr.status == 278) {
                    window.location = xhr.getResponseHeader('Location');
                }
				else if (xhr.status == 203) {
                    alert(data);
                }
				else {
                    $("select[name=step_client]").html(opt_empty + data);

                    $("select[name=step_environment]").empty().select2(select2_basic);
                    options_reset()
                }
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}	
		});
		
	});
	
	
	$("select[name=step_client]").live("change", function(){  
		$.ajax({
			data: { client: $(this).val(), finality: $('select[name=step_finality]').val(),  token: $("#id_token").val() },
			url: "{% if external %}{% url vip-request.environment.ajax.external %}{% else %}{% url vip-request.environment.ajax %}{% endif %}",
			dataType: 'text',
			success: function(data, textStatus, xhr) {
				if (xhr.status == 278) {
                    window.location = xhr.getResponseHeader('Location');
                }
				else if (xhr.status == 203) {
                    alert(data);
                }
				else {
                    $("select[name=step_environment]").html(opt_empty + data).select2(select2_basic);

                    options_reset()

                }
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}	
		});
		
	});
	
	$("select[name=step_environment]").live("change", function(){
		var id_environment_vip = $('select[name=step_environment] option:selected').attr("attr");

		$.ajax({
			data: { environment_vip: id_environment_vip, id_vip: '{{id_vip}}', token: $("#id_token").val() },
			url: "{% if external %}{% url vip-request.options.ajax.external %}{% else %}{% url vip-request.options.ajax %}{% endif %}",
			dataType: 'json',
			success: function(data, textStatus, xhr) {

				if (xhr.status == 278) {
                    alert(xhr.status);
                    window.location = xhr.getResponseHeader('Location');
                }
				else if (xhr.status == 203) {
                    alert(data);
                }
				else {

                    $("#id_caches").html(opt_empty+data.caches).select2(select2_basic);
                    $("#id_persistence").html(opt_empty+data.persistence).select2(select2_basic);
                    $("#id_trafficreturn").html(opt_empty+data.trafficreturn).select2(select2_basic);
                    $("#id_timeout").html(opt_empty+data.timeout).select2(select2_basic);
                    $("#id_l4_protocol").html(opt_empty+data.l4_protocol).select2(select2_basic);
                    $("#id_l7_protocol").html(opt_empty+data.l7_protocol).select2(select2_basic);
                    $("#id_l7_rule").html(opt_empty+data.l7_rule).select2(select2_basic);

                    $("#id_environment_vip").val(id_environment_vip);

					loadPools(id_environment_vip);
				}
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}
	
		})
	});
	

	function loadPools(envVipId){

        $.ajax({

            beforeSend: function(){
                $(".loading").show();
            },
            data: {environment_vip_id : envVipId, token: $("#id_token").val()},
            url: "{% if external %}{% url vip-request.external.load.options.pool %}{% else %}{% url vip-request.load.options.pool %}{% endif %}",
            success: function(data, textStatus, xhr) {
                if (xhr.status == 200){
                    $("select#id_pools").empty();
                    $("select#id_pools").html(data);
                }
                else if (xhr.status == 203) {
                    alert(data);
                }

            },
            error: function (error) {
                message = jQuery.parseJSON(error.responseText);
                addMessage(message);
            }
        })
        .done(function(){
            $(".loading").hide();
        });
	}
	
	function update_pools_new_vip(tableEditing, old_port_vip, porta_vip) {
		
		var oldPortVip = parseInt(old_port_vip);
		var newPortVip = parseInt(porta_vip);

        if (oldPortVip != newPortVip) {

            $("label:contains("+oldPortVip+")", tableEditing).html(newPortVip);
            $("input:hidden[value="+oldPortVip+"]", tableEditing).val(newPortVip);
            $("strong:contains("+oldPortVip+")", tableEditing).html(newPortVip);

        }
        else {
            return false;
        }

    }

    function options_reset(){
        $("#id_timeout").empty().select2(select2_basic);
        $("#id_caches").empty().select2(select2_basic);
        $("#id_persistence").empty().select2(select2_basic);
        $("#id_trafficreturn").empty().select2(select2_basic);
        $("#id_l4_protocol").empty().select2(select2_basic);
        $("#id_l7_protocol").empty().select2(select2_basic);
        $("#id_l7_rule").empty().select2(select2_basic);
        $("#id_pools").empty().select2(select2_basic);
        
        $("#id_environment_vip").val('');
    
        $("#table_real tbody tr").remove();
    }