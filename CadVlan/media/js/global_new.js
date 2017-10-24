$(document).ready(function() {

    $(document).ajaxStart(function() {
        $(".loading").show();
    });

    $(document).ajaxStop(function() {
        $(".loading").hide();
    });
});

function debounce(fn, delay) {
    var timer = null;
    return function () {
        var context = this, args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function () {
            fn.apply(context, args);
        }, delay);
    };
}

function checkProhibitedKeys(pressedKey, prohibitedKeys){
    for (var i = 0, len = prohibitedKeys.length; i < len; i++) {
        if(pressedKey == prohibitedKeys[i]){
            return false;
        }
    }
    return true;
}
