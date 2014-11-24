	var oldPortVip;

	$("#page_tab").tabs();

	$("#btn_sav").button({ icons: {primary: "ui-icon-disk"} });

	$("#btn_can").button({ icons: {primary: "ui-icon-cancel"} }).click(function(){
		location.href = "{% url vip-request.list %}";
	});

	$("#dialog-ip").dialog({
		height: 600,
		width: 1000,
		modal: true,
		autoOpen: false,
		draggable: false,
		resizable: true,
		buttons: {
			"Voltar": function() {
				$(this).dialog("close");
			}
		}
	});
	

	$("#btn_new_port_vip").die("click");
	$("#btn_new_port_vip").button({ icons: {primary: "ui-icon-disk"} }).live("click", function(){  
		$('#table_ports tbody').append("<tr class='remove_port'><td><label class='editable'></label> <input type='hidden' class='ports_vip' name='ports_vip' value='-'></td><td><span class='ui-icon ui-icon-closethick' style='cursor: pointer;'></span></td></tr>");
		$('.editable').editableTable();
	});

	$(".numbersOnly").live('focus', function(){
		oldPortVip = $(this).val();
	});
	
	$(".numbersOnly").live('focusout', function(){
		this_element = $(this); 
		$(this).next().click(function(){
			if (!check_port_vip(this_element)){
				return false;
			}
			console.log('update');
            var porta_vip = update_port_vips(this_element);
            
            if (!oldPortVip){
            	addNews(porta_vip);
            }

            update_pools_new_vip(oldPortVip, porta_vip);
		});
	});
	
	$('.numbersOnly').live("keydown", function(e){
    	  if(e.keyCode == 9 || e.keyCode == 13){

			if (!check_port_vip($(this))){
				
				e.preventDefault();
	    		label = $(this).parent().parent().parent().next().find('.editable');
	      		label.click();
				return false;
			}else{
	      	  	var porta_vip = update_port_vips($(this));

	    		label = $(this).parent().parent().parent().next().find('.editable');
	      		$(this).next().click();
	      		label.click();
	      		
	      		if (!oldPortVip){
	            	addNews(porta_vip);
	            }
	      		update_pools_new_vip(oldPortVip, porta_vip);

	      		return false;
			}

			      	  	
    	  }
	}).live("keyup", function(e){ 
        $(this).val($(this).val().replace(/[^0-9]+/g,''));
	});

	
	// Update port vips values in table 'Reals'
	function update_port_vips(element){
		if(element.parent().parent().next().attr('name') == 'ports_vip'){
			return element.val();
		}
	}
	
	// Check if port vip is duplicated
	function check_port_vip(element){
		if(element.parent().parent().next().attr('name') == 'ports_vip'){
			is_valid = true;
			
			console.log(oldPortVip);
			
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

	$('#table_ports tbody tr span').die("click");

	$('#table_ports tbody tr span').live("click", function(){  
		
		port_vip_value = $(this).parents().find('input=[name=ports_vip]').val(); 

		if (confirm('Deseja realmente excluir a(s) Portas selecionada(s)?')){ 
		
			$("input[name=ports_vip_reals]").each(function(){
				if ($(this).val() == port_vip_value){
					$(this).parents(".remove_port").remove();
					
				}
			});
			
			$(this).parents(".remove_port").remove();
			
			$(".tablePoolMembers").each(function(){
				
				var portTable = parseInt($(this).find('.portVip:eq(0)').html().trim());
				var portToRemove = parseInt(port_vip_value.trim());

				if (portTable == portToRemove){
					$(this).remove();
				}
			});
			
			return false;
		}
	});


	if ( $("#id_environment_vip").val() == '' ) {

	}
	
	
	$("input[name=finality]").change(function(){
		$.ajax({
			data: { finality: $(this).val(), token: $("#id_token").val() },
			url: "{% if external %}{% url vip-request.client.ajax.external %}{% else %}{% url vip-request.client.ajax %}{% endif %}",
			dataType: 'text',
			success: function(data, textStatus, xhr) {
			
				if (xhr.status == "278")
					window.location = xhr.getResponseHeader('Location');
					
				else if (xhr.status == "203")
					alert(data);
				
				else
					$("#id_client_content").html(data);
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}	
		});
		
		$("#id_environment_content").html('');
		$("#id_caches").html('');
		$("#id_persistence").html('');
		$("#id_timeout").html('');
		$("#id_balancing").html('');
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
				if (xhr.status == "278")
					window.location = xhr.getResponseHeader('Location');
					
				else if (xhr.status == "203")
					alert(data);
				
				else
					$("#id_environment_content").html(data);
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}	
		});
		
		$("#id_caches").html('');
		$("#id_persistence").html('');
		$("#id_timeout").html('');
		$("#id_balancing").html('');
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
				if (xhr.status == "278")
					window.location = xhr.getResponseHeader('Location');
					
				else if (xhr.status == "203")
					alert(data.msg);
				
				else {

					$("#id_caches").html(data.caches);
					$("#id_persistence").html(data.persistence);
					$("#id_timeout").html(data.timeout);
					$("#id_balancing").html(data.balancing);
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
					if (xhr.status == "278")
						window.location = xhr.getResponseHeader('Location');
						
					else if (xhr.status == "203")
						alert(data.msg);
					
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
            success: function(data) {
                $("select#id_pools").empty();
                $("select#id_pools").html(data);
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
	
	function update_pools_new_vip(old_port_vip, porta_vip) {
		
		console.log("ANTIGA: ", old_port_vip);
		console.log("NOVA: ", porta_vip);
		
		var oldPortVip = parseInt(old_port_vip);
		var newPortVip = parseInt(porta_vip); 
        var size = $(".tablePoolMembers").size();

        for (var x = 0; x < size; x++) {
        	
            var tabela = $(".tablePoolMembers").eq(x);
            
            //Verify if the port already exist
            if (oldPortVip != newPortVip) {
                //If not, append it to the ServerPools table
            	var port= parseInt(tabela.find('.portVip').html().trim());
            	if (port == oldPortVip){
            		$("input[name=portVipToPool]", tabela).val(port);
            		tabela.find('.portVip').html(newPortVip);
            	}
            }
            else {
                return false;
            }

        }

    }
	
	 function addNews(port){
		 console.log('addNews');
		 var size = $(".tablePoolMembers").size();

	        for (var x = 0; x < size; x++) {
	        	
	        	var identifiers = getIdentifiers();

	            var tableCloned = $(".tablePoolMembers").eq(x).clone();
	            
	            tableCloned.find('.portVip').html(port);

	            $("input[name=portVipToPool]", tableCloned).val(port);
	            
	            var id = $("input:hidden", tableCloned).val() + tableCloned.find('.portVip:eq(0)').html();
	            
	            if($.inArray(id, identifiers) == -1){
	            	$(".tablesMembers").append(tableCloned);
	            	
	            }
	        }
     }
	 
	 function getIdentifiers(){
		 
		 var identifiers = [];

		 $(".tablePoolMembers").each(function(){
			
			 var id = $("input:hidden", $(this)).val() + $(this).find('.portVip:eq(0)').html();
			 
			 identifiers.push(id);

		 });
		 
		 return identifiers;
	 }