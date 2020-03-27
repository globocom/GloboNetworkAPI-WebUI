$(document).ready(function() {

	$("#page_tab").tabs();

	$("#btn_sav").button({ icons: {primary: "ui-icon-disk"} });

	$("#btn_can").button({ icons: {primary: "ui-icon-cancel"} }).click(function(){
		location.href = "{% url environment.list %}";
	});

	toggleIpForm();

})

function toggleIpForm(){

	var formIpv4 = $('#network_ipv4');
	var formIpv6 = $('#network_ipv6');
	var formv4CIDR = $('#cidr_v4_auto');
	var formv6CIDR = $('#cidr_v6_auto');
	var prefix = $('#prefix')

	$('input:radio[name=ip_version]').each(function(){

		$(this).on('change', function(){

			var ipVersion = $(this).val();

			formIpv4.find('p[id=error]').empty();
			formIpv6.find('p[id=error]').empty();
			$('#prefix').find('p[id=error]').empty();
			$(':input', formIpv4).val('');
			$(':input', formIpv6).val('');
			formIpv4.hide();
			formIpv6.hide();
			formv6CIDR.hide();
			formv4CIDR.hide();
			prefix.hide();

			if (ipVersion == "v4"){
				formIpv4.show('slow', function(){
				});
				prefix.show('slow', function(){
				});
			}
			else if (ipVersion == "v6"){
				formIpv6.show('slow', function(){
				});
				prefix.show('slow', function(){
				});
			}
			else if (ipVersion == "cidr_auto"){
			    formv4CIDR.show('slow', function(){
			    });
			    formv6CIDR.show('slow', function(){
			    });
			}
		});
	});
}