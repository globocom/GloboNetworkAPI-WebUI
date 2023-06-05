$(document).ready(function() {
    $("#connect_form").submit(function(event) {
        event.preventDefault();
        url = "/interface/connect/{{ id_interface }}/{{ front_or_back }}/0";
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
        height: 300,
        modal: true,
        autoOpen: false,
        draggable: false,
        resizable: false,
    });

    $("#btn_can").button({ icons: {primary: "ui-icon-cancel"} }).click(function() {
        location.href = "/interface/?search_equipment={{ equip_name }}";
    });
});
