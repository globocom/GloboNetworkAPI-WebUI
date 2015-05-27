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


function __autocomplete(data, submit, id, hid){

	$("#" + id).autocomplete({
		source: data,
		minLength: 1,
		select: function(event, ui) {
			$("#" + id).val(ui.item.label);
			if (hid) {
				$("#" + id + "_id").val(ui.item.aux).trigger('change');
			}
			if (submit) {
				$("#search_form").submit();
			}
		}
	});

}

var ajax_autocomplete_control = false;
var ajax_autocomplete_cache = false;
function autocomplete(url, submit, id, hid) {

	if(ajax_autocomplete_control){
		ajax_autocomplete_control.abort();
	}

	if(ajax_autocomplete_cache){
		__autocomplete(ajax_autocomplete_cache, submit, id, hid);
	}else{
		ajax_autocomplete_control = $.ajax({
			url: url,
			dataType: "json",
			success: function(data) {
				if (data.errors.length > 0) {
					alert(data.errors);
				} else {
					ajax_autocomplete_cache = data.list;
					__autocomplete(ajax_autocomplete_cache, submit, id, hid);
				}
			},
			beforeSend: function() {
				$(".loading").attr("style", "visibility: hidden;")
				$("#loading-autocomplete").show();
			},
			complete: function() {
				$("#loading-autocomplete").hide();
				$(".loading").removeAttr("style");
				ajax_autocomplete_control = false;
			}
		});
	}
}

var ajax_autocomplete_external_control = false;
var ajax_autocomplete_external_cache = false;
function autocomplete_external(url, submit, id, hid) {

	if(ajax_autocomplete_external_control){
		ajax_autocomplete_external_control.abort();
	}

	if(ajax_autocomplete_external_cache){
		__autocomplete(ajax_autocomplete_external_cache, submit, id, hid);
	}else{
		ajax_autocomplete_external_control = $.ajax({
			url: url,
			data: { token: $("#id_token").val() },
			dataType: "json",
			success: function(data, textStatus, xhr) {

				if (xhr.status == "278")
					window.location = xhr.getResponseHeader('Location');

				else if (xhr.status == "203")
					alert(data);
				else {

					if ( data != null ) {

						if ( data != null && data.errors.length > 0) {
							alert(data.errors)
						} else {
							ajax_autocomplete_external_cache = data.list;
							__autocomplete(ajax_autocomplete_external_cache, submit, id, hid);
						}
					}
				}

			},
			beforeSend: function() {
				$(".loading").attr("style", "visibility: hidden;")
				$("#loading-autocomplete").show();
			},
			complete: function() {
				$("#loading-autocomplete").hide();
				$(".loading").removeAttr("style");
				ajax_autocomplete_external_control = false;
			}
		});
	}
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

jQuery.fn.dataTableExt.oSort['check-asc']  = function(a,b) {
    var x = "",  y = "";
    
    if ( a.split('title="')[1].split('"></span>')[0] == 'SIM'){ x = 10 }else{ x = 0 };
    if ( b.split('title="')[1].split('"></span>')[0] == 'SIM'){ y = 10 }else{ y = 0 };
    
    return ((x < y) ? -1 : ((x > y) ? 1 : 0));
};

jQuery.fn.dataTableExt.oSort['check-desc']  = function(a,b) {
    var x = "",  y = "";
    
    if ( a.split('title="')[1].split('"></span>')[0] == 'SIM'){ x = 10 }else{ x = 0 };
    if ( b.split('title="')[1].split('"></span>')[0] == 'SIM'){ y = 10 }else{ y = 0 };
    
    return ((x < y) ? 1 : ((x > y) ? -1 : 0));
};

$.fn.clearForm = function() {
    this.find(':input').each(function() {
        switch(this.type) {
            case 'password':
            case 'select-multiple':
            case 'select-one':
            case 'text':
            case 'textarea':
                $(this).val('');
                break;
            case 'checkbox':
            case 'radio':
                this.checked = false;
        }
    });
};

$.fn.disabledForm = function() {
    this.find('input').attr('disabled', 'disabled');
    this.find('select').attr('disabled', 'disabled');
    this.find('textarea').attr('disabled', 'disabled');
};

$.fn.disabledRemoveForm = function() {
    this.find('input').removeAttr("disabled");
    this.find('select').removeAttr("disabled");
    this.find('textarea').removeAttr("disabled");
};


$.fn.editableTable = function() {
	
	 $(this).editable(function(value, settings) { 
		var _value_ = "-";
			 
		if ( value != "" )
			_value_ = value;
			 
		$(this).next().val(_value_);
	    return(value);
	  }, { 
	     type    : "text",
	     tooltip : "Click para editar.",
	     submit  : 'Ok',
	 });
};


function getInputsData(seletor, key) {
	var data = "";
	data = $(seletor).serialize();
	data = replaceAll(data, key + '=', '');
	data = replaceAll(data, '&', ';');
	data = replaceAll(data, '&' + key + '=' , ';');
	return data;
}


function addMessage(data) {
	
	var divMessage = '';
	var classMessage = data.status === 'error' ? 'ui-state-error':'ui-state-highlight'
		
	divMessage += '<div class="ui-widget error-messages">';
	divMessage += '<p></p>';
	divMessage += '<div id="messagesError" class="'+classMessage+" ui-corner-all "+data.status+'">';
	divMessage += '<span class="ui-icon"></span>';
	divMessage += data.message;
	divMessage += '</div>';
	divMessage += '<p></p>';
	divMessage += '</div>';
	
	$('div#messages').append(divMessage);
	
	$(".error-messages").last().each(function() {
		var $divMessage = $(this);

		    $divMessage.click(function(){

            $divMessage.animate({ opacity: 'toggle', height: 'toggle' }, "slow");

        });
	});
}


function addMessageModal(data) {
	
	var divMessage = '';
	var classMessage = data.status === 'error' ? 'ui-state-error':'ui-state-highlight'
		
	divMessage += '<div class="ui-widget error-messages">';
	divMessage += '<p></p>';
	divMessage += '<div id="messagesError" class="'+classMessage+" ui-corner-all>";
	divMessage += '<span class="ui-icon"></span>';
	divMessage += data.message;
	divMessage += '</div>';
	divMessage += '<p></p>';
	divMessage += '</div>';
	
	$('div#messagesModal').append(divMessage);
	
	$(".error-messages").last().each(function() {
		var $divMessage = $(this);

		$divMessage.click(function(){

            $divMessage.animate({ opacity: 'toggle', height: 'toggle' }, "slow");

        });
	});
}