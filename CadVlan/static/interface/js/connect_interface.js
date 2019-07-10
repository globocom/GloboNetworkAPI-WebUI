$(document).ready(function() {

    {% if connect_form %}

        $("#connect_form").submit(function(event) {
            event.preventDefault();
            url = "{% url interface.connect id_interface front_or_back equip_name %}";
            form = $("#connect_form").serialize();
            $.ajax({
                url: url,
                data: form,
                type: "POST",
                complete: function(xhr, status) {
                    if (xhr.status == "500") {
                        $("#dialog-form").dialog("close");
                        location.reload();
                    } else if (xhr.status == "278" || xhr.status == "302") {
                        $("#dialog-form").dialog("close");
                        window.location = xhr.getResponseHeader('Location');
                    } else if (xhr.status == "200") {
                        $("#dialog-form").html(xhr.responseText);
                    } else {
                        $("#dialog-form").dialog("close");
                    }
                }
            });
        });

        $("#dialog-form").dialog({
            width: 600,
            modal: true,
            autoOpen: false,
            draggable: false,
            resizable: false
        });

        $("#btn_can").button({ icons: {primary: "ui-icon-cancel"} }).click(function() {
            location.href = "{% url interface.list %}?search_equipment={{ equip_name }}";
        });

    {% else %}

        $("#dialog-form").dialog({
            width: 600,
            modal: true,
            autoOpen: false,
            draggable: false,
            resizable: false
        });

        autocomplete("{% url ajax.autocomplete.equipment %}", true, "search_equip", false);

        $("#search_form").submit(function(event) {
            event.preventDefault();
            url = "{% url interface.connect id_interface front_or_back equip_name %}";
            form = $("#search_form").serialize();
            console.log(url)
            $.ajax({
                url: url,
                data: form,
                type: "GET",
                complete: function(xhr, status) {
                    if (xhr.status == "500") {
                        $("#dialog-form").dialog("close");
                        location.reload();
                    } else if (xhr.status == "278" || xhr.status == "302") {
                        $("#dialog-form").dialog("close");
                        window.location = xhr.getResponseHeader('Location');
                    } else if (xhr.status == "200") {
                        $("#dialog-form").html(xhr.responseText);
                        $("#dialog-form").dialog("open");
                    } else {
                        $("#dialog-form").dialog("close");
                    }
                }
            });
        });

        $("#btn_search").button({ icons: {primary: "ui-icon-check"} }).click(function(){ $("#search_form").submit(); });

    {% endif %}
});
