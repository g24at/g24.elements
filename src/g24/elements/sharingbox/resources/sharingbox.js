// TODO: wrapping in anonymous function?
// TODO: $ globally accessible, isn't it? how is mockup doing it?




function feature_toggle(el, scope, name) {
    // el .. (jQuery object) .. toggle button
    // scope .. (jQuery object) .. scope to find feature fieldset in
    // name .. (string) .. feature name, used as id on fieldset
    if (el.prop('checked')===true) {
        scope.find('fieldset#' + name).show();
    } else {
        scope.find('fieldset#' + name).hide();
    }
}


function init_feature_toggle() {
    var tmp_el;
    tmp_el = $('input#features-widgets-is_event-0');
    if (tmp_el.length>0) {
        feature_toggle(tmp_el, tmp_el.closest('form'), 'event');
        tmp_el = $('input#features-widgets-is_place-0');
        feature_toggle(tmp_el, tmp_el.closest('form'), 'place');

        $('input#features-widgets-is_event-0').change(function () {
            feature_toggle($(this), $(this).closest('form'), 'event');
        });

        $('input#features-widgets-is_place-0').change(function () {
            feature_toggle($(this), $(this).closest('form'), 'place');
        });
    }
}

$(document).bind("ajaxComplete", function(){
    // bind to sharingbox loaded via ajax
    // TODO: bind tighter to shbx call - otherwise this is called with every
    // ajax request
    init_feature_toggle();
});

$(document).ready(function() {

    init_feature_toggle();

    /*
    var features = ["event", "place"];
    var i;
    for (i = 0; i < features.length; i++) {
        var feature = features[i];
        var input = $('input#features-widgets-is_' + feature + '-0');
        input.change(function () {
            feature_toggle(input, input.closest('form'), feature);
        });
        feature_toggle(input, input.closest('form'), feature);
    }
    */

});
