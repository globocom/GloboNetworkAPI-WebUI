	$("#page_tab").tabs();
	
	$("#btn_sav").button({ icons: {primary: "ui-icon-disk"} });
	
	$("#btn_can").button({ icons: {primary: "ui-icon-cancel"} }).click(function(){
		location.href = "{% url vip-request.list %}";
	});
	
	$("#btn_new_excpect").button({ icons: {primary: "ui-icon-disk"} }).live("click", function(){  
		
		$("#err_new_healthcheck").html("");
		
		$.ajax({
			data: { excpect_new:  $("#id_excpect_new").val(),  token: $("#id_token").val() },
			url: "{% if external %}{% url vip-request.add.healthcheck.ajax.external %}{% else %}{% url vip-request.add.healthcheck.ajax %}{% endif %}",
			dataType: "json",
			success: function(data, textStatus, xhr) {
			
				if (xhr.status == "278")
					window.location = xhr.getResponseHeader('Location');
					
				else if (xhr.status == "203")
					alert(data);
				
				else {
				
					$("#id_excpect").html(data.healthcheck);
					$("#add_new_healthcheck").html(data.form);
					$("#msg_new_healthcheck").html(data.msg);
					$("#msg_new_healthcheck").delay(15000).animate({ opacity: 'toggle', height: 'toggle' }, "slow");
					$("#btn_new_excpect").button({ icons: {primary: "ui-icon-disk"} });
					
				}
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}	
		});
		
	});
	
	$("#btn_new_real").button({ icons: {primary: "ui-icon-disk"} }).live("click", function(){
		
		if ( $('#id_equip_name').val() != '' ) {
			$.ajax({
				data: { id_environment: $('#id_environment').val(), equip_name: $('#id_equip_name').val(), token: $("#id_token").val() },
				url: "{% if external %}{% url pool.modal.ips.ajax.external %}{% else %}{% url pool.modal.ips.ajax %}{% endif %}",
				success: function(data, textStatus, xhr) {
				    $('#content-ip').html(data);
					$("#dialog_ip").dialog("open");
				},
				error: function (xhr, error, thrown) {
					location.reload();
				}	
			});
		}
	});
	
	$("#dialog_ip").dialog({
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
	
	
	if ( $("#id_environment_vip").val() == '' ) {
		$("#id_equip_name").attr('disabled', 'disabled');
		$("#btn_new_real").attr('disabled', 'disabled');
	}
	
	$("#btn_new_port").button({ icons: {primary: "ui-icon-disk"} }).live("click", function(){  
		$('#table_ports tbody').append("<tr class='remove_port'><td><label class='editable'></label> <input type='hidden' name='ports_vip' value='-'></td><td><label class='editable'></label> <input type='hidden' name='ports_real' value='-'></td><td><span class='ui-icon ui-icon-closethick' style='cursor: pointer;'></span></td></tr>");
		$('.editable').editableTable();
	});
	
	var port_vip;
	
	$(".numbersOnly").live('focus', function(){
		port_vip = $(this).val();
	});
	
	$(".numbersOnly").live('focusout', function(){

		this_element = $(this); 
		$(this).next().click(function(){
			if (!check_port_vip(this_element)){
				return false;
			}
			update_port_vips(this_element);
		});
	});
	
	// Update port vips values in table 'Reals'
	function update_port_vips(element){
		if(element.parent().parent().next().attr('name') == 'ports_vip'){
			new_port_vip = element.val();
			      	  
			$("input[name=ports_vip_reals]").each(function(){
	  			if ($(this).val() == port_vip){
	  				if (new_port_vip == ''){
		  				$(this).val('-');
	  				}else{
	  					$(this).val(new_port_vip);
	  				}
	  				$(this).parent().find('label').text(new_port_vip);
	  			}
	  		});		
		}
	}
	
	// Check if port vip is duplicated
	function check_port_vip(element){
		if(element.parent().parent().next().attr('name') == 'ports_vip'){
			is_valid = true;
			
			if (port_vip != element.val()){
				$("input[name=ports_vip]").each(function(){
					if ($(this).val() == element.val()){
						is_valid = false;
					}
				});
			}
			
			if (element.val() == "" && port_vip != ""){
				element.val(port_vip);
				alert('Deve-se preencher todos os campos de portas.');
				return false;
			}
				
			
			if (!is_valid){
				element.val(port_vip);
				alert('Porta Vip já cadastrada.');
				return false;
			}
			
			return true;
		}
		return true;
	}	
	$('.numbersOnly').live("keydown", function(e){
      	  if(e.keyCode == 9 || e.keyCode == 13){
	
			if (!check_port_vip($(this))){
				
				e.preventDefault();
	    		label = $(this).parent().parent().parent().next().find('.editable');
	      		label.click();
				return false;
			}else{
	      	  	update_port_vips($(this));
	      	  	
	    		label = $(this).parent().parent().parent().next().find('.editable');
	      		$(this).next().click();
	      		label.click();
	      		return false;
			}
			      	  	
      	  }
	}).live("keyup", function(e){ 
          $(this).val($(this).val().replace(/[^0-9]+/g,''));
	});
	
	$('#table_ports tbody tr span').live("click", function(){  
		
		port_vip_value = $(this).parents().find('input=[name=ports_vip]').val(); 

		if (confirm('Deseja realmente excluir a(s) Portas selecionada(s)?')){ 
		
			$("input[name=ports_vip_reals]").each(function(){
				if ($(this).val() == port_vip_value){
					$(this).parents(".remove_port").remove();
				}
			});
			
			$(this).parents(".remove_port").remove();
			return false;
		}
	});
	
	$('#table_real tbody tr span').live("click", function(){  
		if (confirm('Deseja realmente excluir o(s) Real selecionado(s)?')){ 
		$(this).parents(".remove_port").remove();
		return false;
		}
	});

			
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
		
	if ( $("input[name=healthcheck_type]:checked'").val() == "HTTP" ) {
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