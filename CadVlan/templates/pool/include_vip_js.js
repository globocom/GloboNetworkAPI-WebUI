	
	if ($('#id_environment').val() != 0 ){

		$.ajax({
			data: { id_environment: $('#id_environment').val(), token: $("#id_token").val() },
			url: "{% url pool.ajax.get.opcoes.pool.by.ambiente %}",
			success: function(data, xhr) {
				$('#id_healthcheck').html('');
				
				{% if healthcheck.healthcheck_type %}
				$('#id_healthcheck').append('<option value="{{ healthcheck.healthcheck_type }}">{{ healthcheck.healthcheck_type }}</option>');
				{% endif %}

				if ($('#id_healthcheck').val() == 'HTTP' || $('#id_healthcheck').val() == 'HTTPS') {
					$("#table_healthcheck").show();
				} else {
					$("#table_healthcheck").hide();
				}
	
				for (var i = 0; i < data.length; i++) {
					$('#id_healthcheck').append('<option value="'+data[i]['opcao_pool']['description']+'">'+data[i]['opcao_pool']['description']+'</option>');
				}	
			},
			error: function (xhr, error, thrown) {
				location.reload();
			}	
		});
	}

	$("#page_tab").tabs();

	$("#table_healthcheck").hide();
	
	$("#btn_sav").button({ icons: {primary: "ui-icon-disk"} });
	
	$("#btn_can").button({ icons: {primary: "ui-icon-cancel"} }).click(function(){
		location.href = "{% url vip-request.list %}";
	});

	$("#btn_new_expect").button({ icons: {primary: "ui-icon-disk"} });
	
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
	
	
	$('#table_real tbody tr span').die("click");
	
	$('#table_real tbody tr span').live("click", function(e){

		if (confirm('Deseja realmente excluir o(s) Real selecionado(s)?')){ 
		$(this).parents(".remove_port").remove();
		return false;
		}
	});


	$('#btn_new_expect').click(function(){
		$.ajax({
				data: { 'expect_string': $('#expect_string').val(), 'id_environment': $('#id_environment').val(), token: $("#id_token").val() },
				url: "{% url pool.add.healthcheck.expect %}",
				success: function(data, xhr) {

					$('#msg_new_healthcheck').fadeIn(1000);
					$("#id_expect").append('<option value="'+data['expect_string']+'">'+data['expect_string']+'</option>');
					$("#msg_new_healthcheck").html('<td></td><td style="color: #0073EA;font-weight: bold;padding-left: 5px;">'+data['mensagem']+'</td>');
					$("#msg_new_healthcheck").delay(15000).fadeOut('slow');
					$("#id_expect option:last").attr('selected', 'selected');
					$("#btn_new_expect").button({ icons: {primary: "ui-icon-disk"} });

				},
				error: function (xhr, error, thrown) {
					location.reload();
				}	
			});
	});


	$('#id_environment').live("change", function(){
		
		var environmentId = $('#id_environment').val();
		
		if (environmentId != 0){
			
			$.ajax({
					data: { id_environment: environmentId},
					url: "{% url pool.ajax.get.opcoes.pool.by.ambiente %}",
					success: function(data, xhr) {
	
						$('#id_healthcheck').html('<option value="">-</option>');
	
						for (var i = 0; i < data.length; i++) {
							$('#id_healthcheck').append('<option value="'+data[i]['opcao_pool']['description']+'">'+data[i]['opcao_pool']['description']+'</option>');
						}	
					},
					error: function (xhr, error, thrown) {
						location.reload();
					}	
				});
		}

	});
			
	$("#id_healthcheck").live("change", function(){
		if ($(this).val() == 'HTTP' || $(this).val() == 'HTTPS') {
			$("#table_healthcheck").show();
		} else {
			$("#table_healthcheck").hide();
		}
	});
			
	$("#id_balancing").live("change", function(){
		if ( $(this).val().toLowerCase() == "weighted".toLowerCase())
			$('.weighted').show();
		else{
			$('input[name=weight]').val('0');
			$("label[for=weighted]").text('Click para editar.');
			$('.weighted').hide();
		}
	});

function verifyWeight() {
    if ( $("#id_balancing").val() != null &&  $("#id_balancing").val().toLowerCase() == "weighted".toLowerCase()){
        $('.weighted').show();
    }else{
        $('.weighted').hide();
    }
}
