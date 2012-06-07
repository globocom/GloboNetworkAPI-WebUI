/**
 * Title: utils.js
 * Author: avanzolin / S2it
 * Copyright: ( c )  2012 globo.com todos os direitos reservados.
 */

function isEmpty(str) {
    return (!str || 0 === str.length);
}

function isBlank(str) {
    return (!str || /^\s*$/.test(str));
}

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

function changeInput(input, haveBlock) {

	valor = input.value;
	nome = input.name;

	if (valor.length > 0) {

		if (valor.charAt((valor.length - 1)) == "."
				|| valor.charAt((valor.length - 1)) == ":"
				|| valor.charAt((valor.length - 1)) == "/") {

			i = parseInt(nome.charAt(3)) + 1;

			if ($("#search_form input[name='ip_version']:checked").val() == 0) {
				qnt = 4;
				if (haveBlock) { qnt = 5; }
				if (i > qnt) { return false; }
			} else {
				qnt = 8;
				if (haveBlock) { qnt = 9; }
				if (i > qnt) { return false; }
			}

			input.value = valor.substring(0, (valor.length - 1));
			$("#search_form input[name='oct" + i + "']").focus();

		}
	}
}

function autocomplete(url, submit, id, hid) {
	$.ajax({
		url: url,
		dataType: "json",
		success: function(data) {
			if (data.errors.length > 0) {
				alert(data.errors)
			} else {
				$("#" + id).autocomplete({
					source: data.list,
					minLength: 1,
					select: function(event, ui) {
						$("#" + id).val(ui.item.label);
						if (hid) {
							$("#" + id + "_id").val(ui.item.aux)
						}
						if (submit) {
							$("#search_form").submit()
						}
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

jQuery.fn.dataTableExt.oSort['ipv6-asc']  = function(a,b) {
    var m = a.split(":"), x = "";
    var n = b.split(":"), y = "";
    x = m.toString(16);
    y = n.toString(16);
    return ((x < y) ? -1 : ((x > y) ? 1 : 0));
};

jQuery.fn.dataTableExt.oSort['ipv6-desc']  = function(a,b) {
    var m = a.split(":"), x = "";
    var n = b.split(":"), y = "";
    x = m.toString(16);
    y = n.toString(16);
    return ((x < y) ? 1 : ((x > y) ? -1 : 0));
};

jQuery.fn.dataTableExt.oSort['ipv4-asc']  = function(a,b) {
    var m = a.split("."), x = "";
    var n = b.split("."), y = "";
    for(var i = 0; i < m.length; i++) {
        var item = m[i];
        if(item.length == 1) {
            x += "00" + item;
        } else if(item.length == 2) {
            x += "0" + item;
        } else {
            x += item;
        }
    }
    for(var i = 0; i < n.length; i++) {
        var item = n[i];
        if(item.length == 1) {
            y += "00" + item;
        } else if(item.length == 2) {
            y += "0" + item;
        } else {
            y += item;
        }
    }
    return ((x < y) ? -1 : ((x > y) ? 1 : 0));
};

jQuery.fn.dataTableExt.oSort['ipv4-desc']  = function(a,b) {
    var m = a.split("."), x = "";
    var n = b.split("."), y = "";
    for(var i = 0; i < m.length; i++) {
        var item = m[i];
        if(item.length == 1) {
            x += "00" + item;
        } else if (item.length == 2) {
            x += "0" + item;
        } else {
            x += item;
        }
    }
    for(var i = 0; i < n.length; i++) {
        var item = n[i];
        if(item.length == 1) {
            y += "00" + item;
        } else if (item.length == 2) {
            y += "0" + item;
        } else {
            y += item;
        }
    }
    return ((x < y) ? 1 : ((x > y) ? -1 : 0));
};