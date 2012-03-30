/**
 * Title: utils.js
 * Author: avanzolin / S2it
 * Copyright: ( c )  2012 globo.com todos os direitos reservados.
 */

function replaceAll(string, token, newtoken) {
	while (string.indexOf(token) != -1) {
		string = string.replace(token, newtoken);
	}
	return string;
}

function getSelectionData(oTable) {
	data = oTable.$(':checkbox').serialize();
	data = replaceAll(data, 'selection=', '');
	data = replaceAll(data, '&', ';');
	return data;
}

function autocompleteEquip(url) {
	$.ajax({
		url: url,
		dataType: "json",
		success: function(data) {
			if (data.errors.length > 0) {
				alert(data.errors)
			} else {
				$("#id_equip_name").autocomplete({
					source: data.list,
					minLength: 1,
					select: function(event, ui) {
						$("#id_equip_name").val(ui.item.label);
						$("#search_form").submit()
					}
				});
			}
		},
		beforeSend: function() {
			$(".loading").attr("style", "visibility: hidden;")
			$("#loading-autocomplete").show();
		},
		complete: function() {
			$("#loading-autocomplete").hide();
			$(".loading").removeAttr("style")
		}
	});
}