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