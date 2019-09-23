$(document).ready(function() {

    let id_prefixv4 = document.getElementById("id_prefixv4");
    let id_prefixv6 = document.getElementById("id_prefixv6");
    let btn_sav = document.getElementById("btn_sav");
    let btn_can = document.getElementById("btn_can");
    let id_name = document.getElementById("id_name");
    let id_environment = document.getElementById("id_environment");
    let id_network_ipv4 = document.getElementById("id_network_ipv4");
    let id_network_ipv6 = document.getElementById("id_network_ipv6");
    let id_vlan_number = document.getElementById("id_vlan_number");
    let id_number = document.getElementById("id_number");

	$(id_prefixv4).parent().hide();
	$(id_prefixv6).parent().hide();

    $(btn_sav).button({ icons: {primary: "ui-icon-disk"} });

    $(btn_can).button({ icons: {primary: "ui-icon-cancel"} }).click(function(){
        location.href = "vlan/list/";
    });

    $(id_name).keyup(function() {
            var valor = $(this).val().replace(/[^0-9A-Za-z_-]+/g,'');
            $(this).val(valor);
     });

    $(id_name).mouseover(function() {
       $(this).attr("title","Somente letras maiúsculas e minúsculas, números, '-' e '_' são permitidos.");
    });

    get_environment_configuration_available();

    $(id_environment).change(function() {
       $(id_network_ipv4).val($('option:first', this).val());
       $(id_network_ipv6).val($('option:first', this).val());

       get_environment_configuration_available();
    });

    $(id_network_ipv4).change(function(){
        var options = $(this).children("option:selected").text();

		if (options == "Sim") {
			$(id_prefixv4).parent().show();
		} else {
			$(id_prefixv4).parent().hide();
		}
	});

    $(id_network_ipv6).change(function(){
        var options = $(this).children("option:selected").text();

		if (options == "Sim") {
			$(id_prefixv6).parent().show();
		} else {
			$(id_prefixv6).parent().hide();
		}
	});

	$(id_vlan_number).change(function(){
        var options = $(this).children("option:selected").text();

		if (options == "Sim") {
			$(id_number).parent().show();
		} else {
            $(id_number).parent().hide();
		}
    });

})

function get_environment_configuration_available() {

	var environment_id = $(id_environment).val();

    var maskv4;
    var maskv6;

	$.ajax({
		data: {environment_id: environment_id},
		url: "/vlan/form/get/available/environment/configuration/by/environment/id/",
		method: 'GET',
		success: function(data) {

			data = $.parseJSON(data);

			var network_ipv4 = '';
			var network_ipv6 = '';

			if (data.available_environment_config_ipv4 == true) {
				$(id_network_ipv4).parent().show();
			} else {
				$(id_network_ipv4).parent().hide();
			}

			if (data.available_environment_config_ipv6 == true) {
				$(id_network_ipv6).parent().show();
			} else {
				$(id_network_ipv6).parent().hide();
			}

			if (data.vlan_range == true){
			    $(id_vlan_number).parent().show();
			    $(id_number).parent().hide();
			} else {
			    $(id_vlan_number).parent().hide();
			    $(id_number).parent().show();
			}

			if (data.hide_vlan_range == true){
			    $(id_vlan_number).parent().hide();
    			$(id_number).parent().hide();
			}

			if (data.maskv4){
			    id_prefixv4.value = data.maskv4
			}

			if (data.maskv6){
			    id_prefixv6.value = data.maskv6
			}
		},
		error: function(data) {
			console.log(data);
		}
	});
}