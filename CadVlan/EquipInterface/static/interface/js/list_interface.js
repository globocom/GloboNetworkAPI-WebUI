$(document).ready(function() {

    autocomplete("/autocomplete/equipment/", true, "id_equip_name", false);

    $(".btn_equip").on("click", function() {
        $("#id_equip_name").val($(this).html().trim());
        $("#search_form").submit();
    });

    $('[data-toggle="tooltip"]').tooltip();

});