	var oldPortVip;

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

	
	$("input[name=finality]").change(function(){
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
                    $("#id_client_content").html(data);
                }
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}	
		});
		
		$("#id_environment_content").html('');
		$("#id_caches").html('');
		$("#id_trafficreturn").html('');
		$("#id_persistence").html('');
		$("#id_timeout").html('');
		$("#id_balancing").html('');
		$("#id_servicedownaction").html('');
		$("#id_environment_vip").val('');
		$("#id_rules").html('');
		$("#id_healthcheck_type_content").html('');
		$("#table_healthcheck").hide();
		
		$("#id_filter_l7").removeAttr('disabled');
		$("#table_real tbody tr").remove();
		
	});
	
	
	$("input[name=client]").live("change", function(){  
		$.ajax({
			data: { client: $(this).val(), finality: $('input:radio[name=finality]:checked').val(),  token: $("#id_token").val() },
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
                    $("#id_environment_content").html(data);

                }
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}	
		});
		
		$("#id_caches").html('');
		$("#id_trafficreturn").html('');
		$("#id_persistence").html('');
		$("#id_timeout").html('');
		$("#id_balancing").html('');
		$("#id_servicedownaction").html('');
		$("#id_environment_vip").val('');
		$("#id_rules").html('');
		$("#id_healthcheck_type_content").html('');
		$("#table_healthcheck").hide();
		
		$("#id_filter_l7").removeAttr('disabled');
		$("#table_real tbody tr").remove();
		
	});
	
	$("input[name=environment]").live("change", function(){
		var id_environment_vip = $('input:radio[name=environment]:checked').attr("attr");

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

					$("#id_caches").html(data.caches);
					$("#id_trafficreturn").html(data.trafficreturn);
					$("#id_persistence").html(data.persistence);
					$("#id_timeout").html(data.timeout);
					$("#id_balancing").html(data.balancing);
					$("#id_servicedownaction").html(data.servicedownaction);

					$("#id_environment_vip").val(id_environment_vip);
					$("#id_rules").html(data.rules);
					$("#id_healthcheck_type_content").html(data.healthcheck_list);
					$("#table_healthcheck").hide();
					
					if ( $("#id_balancing").val() != null && $('#id_balancing').val().toLowerCase() == "weighted".toLowerCase())
						$('.weighted').show();
					else{
						$('.weighted').hide();
					}
					loadPools(id_environment_vip);
				}
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}
	
		})
	});
	
	// RULES
	
	$("#id_rules").change(function(){
		if ($(this).val())
			$.ajax({
				data: { rule_id: $(this).val(),  token: $("#id_token").val() },
				url: "{% if external %}{% url vip-request.rule.ajax.external %}{% else %}{% url vip-request.rule.ajax %}{% endif %}",
				dataType: 'json',
				success: function(data, textStatus, xhr) {
					if (xhr.status == 278) {
                        window.location = xhr.getResponseHeader('Location');
                    }
					else if (xhr.status == 203) {
                        alert(data);
                    }
					else {
						$("#id_filter_l7").val(data.rule);
					}
				},
				error: function (xhr, error, thrown) {
					location.reload();
				}	
			});
		else
			$("#id_filter_l7").val('');
	
		if ($(this).val() == '' || $(this).val() == null)
			$("#id_filter_l7").removeAttr('disabled');
		else
			$("#id_filter_l7").attr('disabled', 'disabled');
	});

	url_arr = window.location.pathname.split('/');
	
	if (isNaN(url_arr[url_arr.length - 1])){
		if ($("#id_rules").val() != '')
			$("#id_rules").change();
	}	
	else{
		if ($("#id_rules").val() != '')
			$("#id_filter_l7").attr('disabled', 'disabled');
	}		
		
	
	// RULES END
			
	$("input[name=healthcheck_type]").live("change", function(){
		if ($(this).val() == "HTTP") {
			$("#table_healthcheck").show();
		} else {
			$("#table_healthcheck").hide();
		}
	});
	
	if ( $("#id_balancing").val() != null &&  $("#id_balancing").val().toLowerCase() == "weighted".toLowerCase()){
		$('.weighted').show();
	}else{
		
		$('.weighted').hide();
	}
		
	if ( $("input[name=healthcheck_type]:checked").val() == "HTTP" ) {
		$("#table_healthcheck").show();
	} else {
		$("#table_healthcheck").hide();
	}
	
	$("#id_balancing").live("change", function(){
		if ( $(this).val().toLowerCase() == "weighted".toLowerCase())
			$('.weighted').show();
		else{
			$('input[name=weight]').val('-');
			$("label[for=weighted]").text('Click para editar.');
			$('.weighted').hide();
		}
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