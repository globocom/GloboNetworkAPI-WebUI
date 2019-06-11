$(document).ready(function() {

    $('[data-toggle="tooltip"]').tooltip();

    autocompleteAjax ("/autocomplete/environment/", "env_list")
    fillEnvironmentField("father_env", "env_list");

    autocompleteAjax ("/autocomplete/environment/dc/", "router_env_list")
    fillEnvironmentField("router_env", "router_env_list");

    autocompleteAjax ("/autocomplete/environment/l3/", "l3_env_list")
    fillEnvironmentField("fisic_env", "l3_env_list");

    autocompleteAjax ("/autocomplete/environment/logic/", "logic_env_list")
    fillEnvironmentField("logic_env", "logic_env_list");

    autocompleteAjax ("/autocomplete/vrf/", "vrf_list")
    fillEnvironmentField("vrf", "vrf_list");

});

function fillEnvironmentField(envFieldId, storageName) {

    let jsonEnv = JSON.parse(localStorage.getItem(storageName));
    console.log(jsonEnv)
    console.log(storageName)
    let envField = document.getElementById(envFieldId);

    $.each(jsonEnv, function(){
        $(envField).append($("<option />").val(this).text(this));
    })

    console.log("oi")
}

function autocompleteAjax (url, object) {
    $.ajax({
        url: url,
        dataType: "json",
        success: function(data) {
            if (data.errors.length > 0) {
                alert(data.errors);
            } else {
                localStorage.setItem(object, JSON.stringify(data.list));
            }
	}});
}
