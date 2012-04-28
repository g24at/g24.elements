/*
 * SHARINGBOX INTEGRATION
 * */
(function ($) {

    var last_context=null;
    function sharingbox_remove() {
        $('#sharingbox').remove(); // first remove any sharingbox instance
        $('#sharingbox_ul_wrapper').remove(); // first remove any sharingbox instance
        $('#sharingbox_li_wrapper').remove(); // first remove any sharingbox instance
        if (last_context !== null) { $('#'+last_context).show(); }
    }
    function sharingbox_inserter(linkel, event, add) {
        event.preventDefault();
        sharingbox_remove();

        var context = $(linkel).parent().parent();
        var context_id = context.attr('id');
        last_context = context_id;
        /* ajax get */
        $.get($(linkel).attr('href'), function(data){
            if (add===true) {
                if ($(context_id + ' ul').length) {
                    $(context_id + ' ul').before('<li id="sharingbox_li_wrapper"></li>');
                } else {
                    context.after('<ul id="sharingbox_ul_wrapper"><li id="sharingbox_li_wrapper"></li></ul>');
                }
                $('#sharingbox_li_wrapper').html($(data));
            }
            else {
                context.hide();
                context.after($(data));
            }
            sharingbox_init();
        });
    }

    $(document).ready(function() {
        $('a.sharingbox_edit').click(function(event){
          sharingbox_inserter(this, event, false);
        });
        $('a.sharingbox_add').click(function(event){
          sharingbox_inserter(this, event, true);
        });
    });

}(jQuery));
