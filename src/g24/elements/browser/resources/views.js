/*
 * SHARINGBOX INTEGRATION
 * */
function default_value(arg, def) {
    /* Add default parameter to argument */
    return typeof arg !== 'undefined' ? arg : def;
}
function sharingbox_remove(keep_list) {
    keep_list = default_value(keep_list, false);
    $('#sharingbox').remove(); // first remove any sharingbox instance
    if (keep_list === false) {
        $('#sharingbox_li_wrapper').remove(); // apply on all matched elements
        $('#sharingbox_ul_wrapper').remove();
    } else {
        $('#sharingbox_li_wrapper').removeAttr('id');
        $('#sharingbox_ul_wrapper').removeAttr('id');
    }
}
(function ($) {

    var EDIT = 0;
    var ADD = 1;
    var last_context=null;
    function sharingbox_inserter(linkel, event, mode) {
        /* Insert sharingbox into content.
         *
         * @param linkel: The element, which caused invocation of this function.
         * @param event:  jQuery event fired on linkel.
         * @param mode:   0..EDIT, 1..ADD
         *
         * */
        event.preventDefault();
        sharingbox_remove();
        if (last_context !== null) { $('#'+last_context).show(); }

        var context = $(linkel).closest('article');
        var context_id = context.attr('id');
        last_context = context_id;
        /* ajax get */
        $.get($(linkel).attr('href'), function(data){
            if (mode===ADD) {
                if ($(context_id + ' ul').length) {
                    /* Add (new element in existing subthread) */
                    $(context_id + ' ul').before('<li id="sharingbox_li_wrapper"></li>');
                } else {
                    /* Add (mew subthread) */
                    context.after('<ul id="sharingbox_ul_wrapper"><li id="sharingbox_li_wrapper"></li></ul>');
                }
                $('#sharingbox_li_wrapper').html($(data));
            }
            else {
                context.hide();
                context.after($(data));
            }
            sharingbox_init(context, mode);
        });
    }

    $(document).ready(function() {
    });

}(jQuery));

function sharingbox_enable() {
    (function ($) {
        $('a.sharingbox_edit').click(function(event){
          sharingbox_inserter(this, event, EDIT);
        });
        $('a.sharingbox_add').click(function(event){
          sharingbox_inserter(this, event, ADD);
        });
    }(jQuery));
}
