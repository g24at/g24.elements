/*
 * SHARINGBOX INTEGRATION
 * */
(function ($) {

    var last_context=null;
    function sharingbox_inserter(linkel, event) {
        event.preventDefault();
        $('#sharingbox').remove(); // first remove any sharingbox instance
        var context = $(linkel).parent().parent();
        if (last_context !== null) { $('#'+last_context).show(); }
        last_context = context.attr('id');
        context.hide();
        $.get($(linkel).attr('href'), function(data){
            context.after($(data));
            sharingbox_init();
        });
    }

    $(document).ready(function() {
        $('a.sharingbox_edit').click(function(event){
          sharingbox_inserter(this, event);
        });
        $('a.sharingbox_add').click(function(event){
          sharingbox_inserter(this, event);
        });
    });

}(jQuery));
